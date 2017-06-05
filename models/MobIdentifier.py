from collections import Counter
import os
import time

import cv2
import numpy as np
from sklearn import model_selection
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from opencv.DatasetCreator import DatasetCreator
from opencv.cropper import *


class MobIdentifier(DatasetCreator):

    def __init__(self, config):
        DatasetCreator.__init__(self, config)
        self.pixelVals = []
        self.histVals = []
        self.mobLabels = {key: val for key, val in enumerate(self.mobs)}
        self.labels = []


    def loadDataset(self, customizationPath, dim, gray=False, original=False):
        for i, mobPath in enumerate(self.mobPaths):
            if original:
                imgDir = os.path.join(mobPath, 'originals')
            else:
                imgDir = os.path.join(mobPath, customizationPath, str(dim))
            for imgName in os.listdir(imgDir):
                img = readImg(os.path.join(imgDir, imgName))
                if gray:
                    img = convertGray(img)
                for segment in segmentCrop(img):
                    resized = resize(segment, 24)
                    self.pixelVals.append(resized.flatten())
                    self.histVals.append(getImgHist(resized, gray=gray))
                    self.labels.append(i)
                # self.pixelVals.append(img.flatten())
                # self.histVals.append(getImgHist(img, gray=gray))
                # self.labels.append(i)
        self.pixelVals = np.array(self.pixelVals)
        self.histVals = np.array(self.histVals)
        self.labels = np.array(self.labels)

    def splitDataset(self, features, labels, test_size=0.25):
        self.Xtr, self.Xte, self.Ytr, self.Yte = model_selection.train_test_split(features,
                                                                                  labels,
                                                                                  test_size=test_size,
                                                                                  random_state=42)
    def createKNN(self, k=5):
        self.knn = KNeighborsClassifier(n_neighbors=k, n_jobs=-1)
        self.logger.info('Fitting KNN...')
        self.knn.fit(self.Xtr, self.Ytr)
        self.logger.info('KNN Accuracy: {0}'.format(self.knn.score(self.Xte, self.Yte)))

    def createRandomForest(self, k=10):
        self.rfc = RandomForestClassifier(n_estimators=k, random_state=42, n_jobs=-1)
        self.logger.info('Fitting RFC...')
        self.rfc.fit(self.Xtr, self.Ytr)
        self.logger.info('RFC Accuracy: {0}'.format(self.rfc.score(self.Xte, self.Yte)))

    def saveModel(self, model, path):
        if model == 'knn':
            joblib.dump(self.knn, path)
        elif model == 'rfc':
            joblib.dump(self.rfc, path)
        else:
            raise Exception('Unknown model')

    def loadModel(self, model, path):
        if model == 'knn':
            self.knn = joblib.load(path)
        elif model == 'rfc':
            self.rfc = joblib.load(path)
        else:
            raise Exception('Unknown model')

if __name__ == '__main__':
    config = {
        'img_dir': 'C:\\Users\\armentrout\\Documents\\GitHub\\MinecraftObjectRecognition\\agents\\imgs'
    }

    mi = MobIdentifier(config)
    mi.loadDataset(mi.boxPlainPath, 24, gray=False)
    #mi.splitDataset(mi.pixelVals, mi.labels)
    mi.splitDataset(mi.histVals, mi.labels)
    # mi.createKNN()
    # mi.saveModel('knn', 'knn_model.sav')
    mi.createRandomForest()
    # mi.saveModel('rfc', 'rfc_model.sav')
    # mi.loadModel('knn', 'knn_model.sav')
    # mi.loadModel('rfc', 'rfc_model.sav')

    #test = readImg(r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\agents\imgs\-pigs-and-sheep\cropped\box\plain\24\29.jpg')
    test = readImg(r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\agents\imgs\-mobs\originals\100.jpg')

    for crop in cropMobs(test):
        print('')
        # knnPixelPreds = [mi.mobLabels[mi.knn.predict(resize(crop, 24).flatten().reshape(1, -1))[0]]]
        # rfcPixelPreds = [mi.mobLabels[mi.rfc.predict(resize(crop, 24).flatten().reshape(1, -1))[0]]]
        # knnHistPreds = [mi.mobLabels[mi.knn.predict(getImgHist(resize(crop, 24)).reshape(1, -1))[0]]]
        rfcHistPreds = [mi.mobLabels[mi.rfc.predict(getImgHist(resize(crop, 24)).reshape(1,-1))[0]]]

        start = time.time()
        for i, segment in enumerate(segmentCrop(crop)):
            #resized = resize(segment, 24).flatten().reshape(1,-1)
            hist = getImgHist(resize(segment, 24)).reshape(1,-1)
            #knnPreds.append(mi.mobLabels[mi.knn.predict(resized)[0]])
            rfcHistPreds.append(mi.mobLabels[mi.rfc.predict(hist)[0]])
        #     cv2.imshow(str(i), resize(segment, 100))

        print('time to predict {0}'.format(time.time() - start))

        # print('knn predictions')
        # for mob, count in Counter(knnPreds).most_common(3):
        #     print('{0}: {1}0%'.format(mob, count))

        print('rfc predictions')
        for mob, count in Counter(rfcHistPreds).most_common(3):
            print('{0}: {1}0%'.format(mob, count))

    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
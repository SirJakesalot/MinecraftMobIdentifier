import os
import time

from sklearn import model_selection
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

from opencv.DatasetCreator import DatasetCreator
from opencv.cropper import *

import numpy as np


class MobIdentifier(DatasetCreator):
    '''Handle reading and predicting mobs on image dataset.
    
    There are several datasets to pull from:
    1) box plain - simple cropping of mob
    2) box gray - same as above but grayscale
    3) box no background - same as plain but with no background (black pixels)
    4) box edges - edge detection on the plain image
    5) aspect plain, gray, no background, edges - same as above but with aspect ratio resizing
    
    There are two types of image values to train on:
    1) raw pixel values
    2) histogram of pixel values
    '''

    def __init__(self, config):
        # read dataset values
        DatasetCreator.__init__(self, config)
        # flattened image pixel values (color or gray)
        self.pixelVals = []
        # pixel value labels
        self.pixelValLabels = []
        # flattened image color histogram of pixel values (color or gray)
        self.histVals = []
        # histogram value labels
        self.histValLabels = []
        # mapping of mob ids to mob names
        self.mobId2Label = {key: val for val, _, key in self.mobInfo}

    def loadDataset(self, customization_path, dim, use_pixels=False,
                                                   use_histogram=False,
                                                   use_whole_crop=False,
                                                   use_segments=False,
                                                   segment_dim=24):
        '''Load the specified dataset for the dimension
        customization_path: DatasetCreator customization
        dim: DatasetCreator dimension to load
        use_pixels: train dataset on pixel values
        use_hist: train dataset on histogram values
        use_whole_crop: train dataset with whole croppings
        use_segments: train dataset with segments of croppings
        segment_dim: dimensions of each segment
        '''
        # proper config checks
        assert use_pixels or use_histogram
        assert use_whole_crop or use_segments

        # reset data
        self.pixelVals = []
        self.pixelValLabels = []
        self.histVals = []
        self.histValLabels = []

        # Grab information from each image
        for mobName, mobPath, mobId in self.mobInfo:
            imgDir = os.path.join(mobPath, customization_path, str(dim))
            for imgName in os.listdir(imgDir):
                img = readImg(os.path.join(imgDir, imgName))
                if use_whole_crop:
                    if use_pixels:
                        self.pixelVals.append(img.flatten())
                        self.pixelValLabels.append(mobId)
                    if use_histogram:
                        self.histVals.append(getImgHist(img).flatten())
                        self.histValLabels.append(mobId)
                if use_segments:
                    for segment in segmentCrop(img):
                        resized = resize(segment, segment_dim)
                        if use_pixels:
                            self.pixelVals.append(resized.flatten())
                            self.pixelValLabels.append(mobId)
                        if use_histogram:
                            self.histVals.append(getImgHist(resized).flatten())
                            self.histValLabels.append(mobId)
        # cast data as np arrays
        if use_pixels:
            self.pixelVals = np.array(self.pixelVals)
            self.pixelValLabels = np.array(self.pixelValLabels)
        if use_histogram:
            self.histVals = np.array(self.histVals)
            self.histValLabels = np.array(self.histValLabels)

    def splitDataset(self, feature_set, test_size=0.25):
        if feature_set == 'pixels':
            self.Xtr, self.Xte, self.Ytr, self.Yte = model_selection.train_test_split(self.pixelVals,
                                                                                      self.pixelValLabels,
                                                                                      test_size=test_size,
                                                                                      random_state=42)
        elif feature_set == 'histograms':
            self.Xtr, self.Xte, self.Ytr, self.Yte = model_selection.train_test_split(self.histVals,
                                                                                      self.histValLabels,
                                                                                      test_size=test_size,
                                                                                      random_state=42)
        else:
            raise Exception('Unknown feature set')

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
    segment_dim = 24
    # number of non-black pixels has to be greater than this in the segment
    segment_nonzero_thresh = int((segment_dim**2) * 0.3) * 3

    # How to save a new model
    # mi.loadDataset(mi.boxNoBackgroundPath, -1, use_pixels=True, use_segments=True, segment_dim=segment_dim)
    # mi.splitDataset('pixels')
    # mi.createRandomForest()
    # mi.saveModel('rfc', 'rfc_model.sav')

    # How to load a saved model
    # mi.loadModel('knn', 'knn_model.sav')
    mi.loadModel('rfc', 'rfc_model.sav')

    #test = readImg(r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\agents\imgs\-pigs-and-sheep\cropped\box\plain\24\29.jpg')
    test = readImg(r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\agents\imgs\-mobs\originals\110.jpg')
    print('Label ordering: {0}'.format(mi.mobs))
    for crop in cropMobs(test):
        print('')

        start = time.time()
        p = []
        for i, segment in enumerate(segmentCrop(crop)):
            noBackground = rmBackground(segment)
            resized = resize(noBackground, segment_dim)
            if np.count_nonzero(resized) > segment_nonzero_thresh:
                # convert segment to feature vector

                features = resized.flatten().reshape(1,-1)
                rfcPreds = mi.rfc.predict_proba(features)[0]
                p.append(rfcPreds)
                #knnPreds = mi.knn.predict_proba(features)[0]
                print('Segment {0}: {1}'.format(i, rfcPreds))
            else:
                p.append([0,0,0,0,0])
                print('Segment {0}: Mostly background'.format(i))

            cv2.imshow('Segment ' + str(i), resize(noBackground, 100))
        centroids = findCentroids(mi.mobId2Label, np.array(p), segment_dim)
        t = resize(crop, 72)
        for mn, (x,y) in centroids.items():
            print(mn, (x,y))
            cv2.circle(t, (x,72-y), 2, [0,255,0])
        cv2.imshow('test', t)

        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print('time to predict {0}'.format(time.time() - start))
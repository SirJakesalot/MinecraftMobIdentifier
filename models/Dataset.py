import time
import os
# vendors
import cv2
import numpy as np
from collections import defaultdict
from opencv.cropper import *
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier


class Dataset:
    imgCount = 0
    subsetExt = '.txt'

    def __init__(self, dataDir, subsets):
        self.dataDir = dataDir
        self.imgDir = os.path.join(self.dataDir, 'imgs')
        self.labels = dict()
        self.subsets = subsets
        self.subsetData = dict()
        self.subsetLabels = dict()
        self.models = dict()

        if not os.path.exists(self.imgDir):
            os.makedirs(self.imgDir)
        assert os.path.isdir(self.imgDir)


    ''' --- Utilities --- '''
    def getSubdirs(self, path):
        '''Get directory subdirs but ignore the ones starting with a dash'''
        f = lambda x: os.path.isdir(x) and not os.path.basename(x).startswith('-')
        return filter(f, [os.path.join(path, d) for d in os.listdir(path)])

    def getFileParentDir(self, path):
        return os.path.basename(os.path.dirname(path))

    ''' --- Dataset Management --- '''
    def addImg(self, label, img):
        if label not in self.labels:
            id = len(self.labels)
            self.labels[label] = id
            self.labels[id] = label
            os.makedirs(os.path.join(self.imgDir, label))
        self.imgCount += 1
        imgPath = os.path.join(self.imgDir, label, '{0}.jpg'.format(self.imgCount))
        writeImg(imgPath, img)

    # def createSubsets(self):
    #     for subset in self.subsets:
    #         subsetPath = os.path.join(self.dataDir, subset)
    #         if not os.path.exists(subsetPath):


    def addToSubset(self, subset, label, features):
        imgPath = os.path.join(self.imgDir, label, '{0}.jpg'.format(self.imgCount))
        with open(os.path.join(self.dataDir, subset + self.subsetExt), 'a') as f:
            f.write(imgPath + '\n')

        if subset not in self.subsetData:
            self.subsetData[subset] = features
            self.subsetLabels[subset] = [self.labels[label]]
        else:
            self.subsetData[subset] = np.append(self.subsetData[subset], features, axis=0)
            self.subsetLabels[subset] = np.append(self.subsetLabels[subset], [self.labels[label]], axis=0)


    def trainModel(self, subset):
        rfc = RandomForestClassifier(n_estimators=10, random_state=42, n_jobs=-1)
        rfc.fit(self.subsetData[subset], self.subsetLabels[subset])
        self.models[subset] = rfc

    def loadDataset(self):
        '''Load configuration files and continue from stopping point'''
        self.subsetData = defaultdict(list)
        # {img path: [subset1 path, subset2 path]
        imgPath2Subsets = defaultdict(list)
        # load all model image paths
        for subset in self.subsets:
            with open(os.path.join(self.dataDir, subset), 'r') as f:
                for subsetImgPath in f:
                    imgPath2Subsets[subsetImgPath].append(subset)

        # load images that were reported wrong by some model
        for imgPath in imgPath2Subsets:
            img = readImg(imgPath)
            # apply manipulations and add to dataset
            for subset in imgPath2Subsets[imgPath]:
                manipulation = self.subsets[subset]
                if manipulation:
                    self.subsetData[subset].append(manipulation(img).flatten())
                else:
                    self.subsetData[subset].append(img.flatten())
                label = self.labels[self.getFileParentDir(subset)]
                self.subsetLabels[subset].append(label)

        # convert all data and labels to np arrays
        for subset in self.subsets:
            self.subsetData[subset] = np.array(self.subsetData[subset])
            self.subsetLabels[subset] = np.array(self.subsetLabels[subset])


# if __name__ == '__main__':
#     d = Dataset()
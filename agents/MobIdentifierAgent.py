import time
import os
import random
# vendors
import MalmoPython
import cv2
import numpy as np
from opencv.cropper import *
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

from BaseAgent import BaseAgent

class Dataset:
    imgCount = 0

    def __init__(self, path):
        self.path = path
        # {mob id: mob name}
        self.labels = dict()

    def addImg(self, mobName, mob):
        if mobName not in self.labels:
            #self.labels[len(self.labels)] = mob
            mobId = len(self.labels)
            self.labels[mobName] = mobId
            self.labels[mobId] = mobName
            os.makedirs(os.path.join(self.path, mobName))
        self.imgCount += 1
        writeImg(os.path.join(self.path, mobName, '{0}.jpg'.format(self.imgCount)), mob)

    def loadDataset(self, use_pixels=False,
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
                segment_dim: dimensions of each segment'''

        # proper config checks
        assert use_pixels or use_histogram
        assert use_whole_crop or use_segments

        # reset data
        pixelVals = []
        pixelValLabels = []
        histVals = []
        histValLabels = []

        # Grab information from each image
        for mob in os.listdir(self.path):
            imgDir = os.path.join(self.path, mob)
            for imgName in os.listdir(imgDir):
                img = readImg(os.path.join(imgDir, imgName))
                if use_whole_crop:
                    if use_pixels:
                        pixelVals.append(img.flatten())
                        pixelValLabels.append(self.labels[mob])
                    if use_histogram:
                        histVals.append(getImgHist(img).flatten())
                        histValLabels.append(self.labels[mob])
                if use_segments:
                    for segment in segmentCrop(img):
                        resized = resize(segment, segment_dim)
                        if use_pixels:
                            pixelVals.append(resized.flatten())
                            pixelValLabels.append(self.labels[mob])
                        if use_histogram:
                            histVals.append(getImgHist(resized).flatten())
                            histValLabels.append(self.labels[mob])
        # cast data as np arrays
        if use_pixels:
            return np.array(pixelVals), np.array(pixelValLabels)
        if use_histogram:
            return np.array(histVals), np.array(histValLabels)


class MobIdentifierAgent(BaseAgent):
    imgDir = 'imgs/-tmp'
    totals = [0, 0]
    correct = [0, 0]
    datasets = [Dataset(os.path.join(imgDir, 'color')),
                Dataset(os.path.join(imgDir, 'gray'))]
    models = [None, None]
    accs = [[],[]]

    def __init__(self, config):
        BaseAgent.__init__(self, config)
        if not os.path.exists(self.imgDir):
            os.makedirs(self.imgDir)
        assert os.path.isdir(self.imgDir)
        plt.ion()
        fig = plt.figure()
        self.ax1 = fig.add_subplot(2,2,1)
        self.ax2 = fig.add_subplot(2,2,3)
        self.ax3 = fig.add_subplot(2,2,2)
        self.ax4 = fig.add_subplot(2,2,4)

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.LATEST_FRAME_ONLY)
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)

    def agentAction(self):
        time.sleep(3)
        while self.world_state.number_of_video_frames_since_last_state < 1 and self.world_state.is_mission_running:
            self.logger.info('Waiting for frames...')
            time.sleep(0.05)
            self.world_state = self.agent_host.getWorldState()
        self.logger.info('Got frame!')

        if self.world_state.is_mission_running:
            self.processFrame(self.world_state.video_frames[-1].pixels, random.choice(['Cow', 'Pig', 'Sheep']))

    def processFrame(self, pixels, actualLabel):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()

        frame = np.asarray(pixels).reshape(480,640,3)
        # crop mob out of frame
        mob = resize(cropMob(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)), 24)
        # apply different image manipulations
        #imgs = [mob, convertGray(mob)]
        imgs = [mob, mob]

        # loop over different datasets, models, image manipulations
        for i in range(len(self.datasets)):
            # create model if not created yet and move on
            if self.models[i] == None:
                self.logger.info('Dataset {0}: Creating new label {1}'.format(i, actualLabel))
                self.datasets[i].addImg(actualLabel, imgs[i])
                X, Y = self.datasets[i].loadDataset(use_pixels=True, use_whole_crop=True)
                self.models[i] = RandomForestClassifier(n_estimators=10, random_state=42, n_jobs=-1)
                self.models[i].fit(X, Y)
            else:
                pred = self.models[i].predict(imgs[i].flatten().reshape(1,-1))
                pred = self.datasets[i].labels[pred[0].item()]
                if pred == actualLabel:
                    self.logger.info('Dataset {0}: Predicted correctly'.format(i))
                    self.correct[i] += 1
                else:
                    self.logger.info('Dataset {0}: Predicted wrongly. Actual {1} Pred {2}'.format(i, actualLabel, pred))
                    self.datasets[i].addImg(actualLabel, imgs[i])
                    X, Y = self.datasets[i].loadDataset(use_pixels=True, use_whole_crop=True)
                    self.models[i] = RandomForestClassifier(n_estimators=10, random_state=42, n_jobs=-1)
                    self.models[i].fit(X, Y)
                self.totals[i] += 1
                self.accs[i].append(float(self.correct[i])/float(self.totals[i]))


        self.ax1.set_title('RGB Image')
        self.ax1.imshow(imgs[0])
        self.ax2.set_title('Gray Image')
        self.ax2.imshow(convertGray(imgs[1]), cmap='gray')
        self.ax3.set_title('acc 1')
        self.ax3.plot(self.accs[0])
        self.ax4.plot(self.accs[1])

        plt.tight_layout()
        plt.show()
        plt.pause(0.01)

    def pickMob(self):
        return random.choice(self.mobs)

    def predictModels(self, img):
        return [model.predict(img) for model in self.models]


config = {
    'mission_file': r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\missions\flat_world.xml',
    'recording': {
                'path': 'data.tgz',
                'fps': 1,
                'bit_rate': 400000
    },
}
mia = MobIdentifierAgent(config)
mia.startMission()
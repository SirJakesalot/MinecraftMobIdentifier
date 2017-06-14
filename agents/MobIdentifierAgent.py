import time
import os
import json
import random
# vendors
import MalmoPython
import cv2
import numpy as np
from opencv.cropper import *
from sklearn import model_selection
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
from collections import defaultdict

from BaseAgent import BaseAgent
from models.Dataset import Dataset

class MobIdentifierAgent(BaseAgent):

    ''' Spawn configurations '''
    mobs = ['Chicken', 'Pig', 'Cow', 'MushroomCow', 'Sheep']
    min_dist = 3
    max_dist = 15
    spawnedMobs = []

    ''' Dataset configurations '''
    dataDir = 'data'
    subsets = {'RGB': lambda img: img,
               'Gray': convertGray,
               'Edges': lambda img: getEdges(rmBackground(img)),
               'Reds': lambda img: img[:, :, 2],
               'Blues': lambda img: img[:, :, 0],
               'Greens': lambda img: img[:, :, 1],
               'Hue': lambda img: convertHSV(img)[:, :, 0],
               'Saturation': lambda img: convertHSV(img)[:, :, 1],
               'Value': lambda img: convertHSV(img)[:, :, 2]}

    subsetPlots = {'RGB': 'img',
                   'Gray': 'img',
                   'Edges': 'img',
                   'Reds': 'hist',
                   'Blues': 'hist',
                   'Greens': 'hist',
                   'Hue': 'hist',
                   'Saturation': 'hist',
                   'Value': 'hist'}
    subsetOrder = ['RGB',
                   'Gray',
                   'Edges',
                   'Reds',
                   'Blues',
                   'Greens',
                   'Hue',
                   'Saturation',
                   'Value']

    def __init__(self, config):
        BaseAgent.__init__(self, config)
        plt.ion()

        self.dataset = Dataset('data', self.subsets)
        #self.dataset.loadDataset()
        self.accs = defaultdict(list)
        self.correct = defaultdict(int)
        fig, self.ax = plt.subplots(nrows=6, ncols=4)

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.LATEST_FRAME_ONLY)
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)

    def setupMission(self):
        BaseAgent.setupMission(self)
        self.mission.allowAllChatCommands()

    def agentAction(self):
        if self.action_count == 0:
            self.firstAction()
            time.sleep(2)
        else:
            while self.waitForStateChange():
                self.logger.info('Waiting for state change...')
                time.sleep(0.05)
                self.world_state = self.agent_host.getWorldState()
            self.logger.info('State Change!')

            if self.world_state.is_mission_running:
                time.sleep(1)
                if not self.spawnedMobs:
                    yaw = self.getYaw()
                    # make sure we have fully turned back to the origin
                    if yaw != 0:
                        self.turn(0)
                    else:
                        self.killAllMobs()
                        time.sleep(2)
                        self.spawnMobs()
                        time.sleep(4)
                else:
                    mob = self.spawnedMobs.pop()
                    self.logger.info('SEEING ' + mob)
                    self.processFrame(self.world_state.video_frames[-1].pixels, mob)
                    time.sleep(4)
                    self.turn(self.getYaw() + 90)
                    time.sleep(1)

    def firstAction(self):
        self.agent_host.sendCommand('chat /gamerule sendCommandFeedback false')
        self.agent_host.sendCommand('chat /gamerule mobGriefing false')
        self.agent_host.sendCommand('chat /gamerule doMobLoot false')
        self.spawnMobs()

    def turn(self, yaw):
        self.agent_host.sendCommand('turn {0}'.format(yaw))

    def killAllMobs(self):
        self.agent_host.sendCommand('chat /kill @e[type=!Player]')

    def processFrame(self, pixels, actualLabel):
        for row in self.ax:
            for col in row:
                col.clear()

        frame = np.asarray(pixels).reshape(480,640,3)
        # crop mob out of frame
        mob = resize(cropMob(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)), 24)
        isNewLabel = actualLabel not in self.dataset.labels
        self.dataset.addImg(actualLabel, mob)
        if isNewLabel:
            self.logger.info('Creating new label {0}'.format(actualLabel))
            for subset in self.subsetOrder:
                self.dataset.addToSubset(subset, actualLabel, self.subsets[subset](mob).flatten().reshape(1,-1))
                self.dataset.trainModel(subset)
            return

        # loop over different datasets, models, image manipulations
        for i, subset in enumerate(self.subsetOrder):
            color = 'black'
            manipulation = self.subsets[subset](mob)
            features = manipulation.flatten().reshape(1,-1)
            predId = self.dataset.models[subset].predict(features)[0].item()
            pred = self.dataset.labels[predId]
            if pred == actualLabel:
                self.logger.info(subset + ' predicted correct')
                color = 'green'
                self.correct[subset] += 1

            else:
                self.logger.info(subset + ' predicted infcorrect')
                color = 'red'
                self.dataset.addToSubset(subset, actualLabel, features)
                self.dataset.trainModel(subset)

            self.accs[subset].append(float(self.correct[subset]) / float(self.dataset.imgCount-len(self.dataset.labels)/2))
            axIndx = (i/6) * 2
            self.plotData(self.ax[i%6][axIndx], manipulation, '{0} - {1}'.format(subset, pred), color, self.subsetPlots[subset])
            stat_title = '{0}/{1} - {2:.5f} - {3} images'.format(self.correct[subset],
                                                                 self.dataset.imgCount-len(self.dataset.labels)/2,
                                                                 self.accs[subset][-1],
                                                                 len(self.dataset.subsetData[subset]))
            self.plotStats(self.ax[i%6][axIndx + 1], self.accs[subset], stat_title)
            plt.tight_layout()
            plt.show()
            plt.pause(0.01)

    def plotData(self, ax, data, title, color, type):
        ax.set_title(title, fontdict={'color': color})
        if type == 'img':
            if isGrayScale(data):
                ax.imshow(data, cmap='gray')
            else:
                ax.imshow(cv2.cvtColor(data, cv2.COLOR_BGR2RGB))
        elif type == 'graph':
            ax.plot(data.flatten())
        elif type == 'hist':
            ax.hist(data.flatten())

    def plotStats(self, ax, data, title):
        ax.set_title(title)
        ax.plot(data)

    def pickMob(self):
        return random.choice(self.mobs)
    def getDistance(self):
        return random.randint(self.min_dist, self.max_dist)

    def spawnMobs(self):
        mobs = [self.pickMob() for _ in range(4)]
        cmd = 'chat /summon {0} {1} 227.0 {2} {{Attributes:[{{Name:generic.movementSpeed,Base:0}}]}}'
        self.agent_host.sendCommand(cmd.format(mobs[3], 0.5 + self.getDistance(), 0.5))
        self.agent_host.sendCommand(cmd.format(mobs[0], 0.5, 0.5 + self.getDistance()))
        self.agent_host.sendCommand(cmd.format(mobs[1], 0.5 - self.getDistance(), 0.5))
        self.agent_host.sendCommand(cmd.format(mobs[2], 0.5, 0.5 - self.getDistance()))
        self.spawnedMobs = mobs[::-1]

    def waitForStateChange(self):
        return self.world_state.number_of_video_frames_since_last_state < 1 and \
        self.world_state.number_of_observations_since_last_state < 1 and \
        self.world_state.is_mission_running

    def getYaw(self):
        msg = self.world_state.observations[-1].text
        ob = json.loads(msg)
        entity = [ent for ent in ob['entities'] if ent[u'name'] == u'Agent'][0]
        return entity[u'yaw']

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
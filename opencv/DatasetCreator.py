import logging
from copy import deepcopy
import os
import sys
from cropper import *

class DatasetCreator:
    # out of the box configurations
    # all values that are None have to be specified by the user
    DEFAULT_CONFIG = {
        'img_dir': None,
        'dims': [-1, 24],
        'overwrite': False,
        'debug': True,
    }

    def __init__(self, config):
        # configuration management
        self.config = self.DEFAULT_CONFIG
        self.reconfigure(config)
        self.setupLogging()

        self.mobPaths = self.getSubdirs(self.config['img_dir'])
        self.mobs = [os.path.basename(mobDir) for mobDir in self.mobPaths]
        self.mobInfo = zip(self.mobs, self.mobPaths, range(len(self.mobPaths)))

        originals = [os.path.join(mob, 'originals') for mob in self.mobPaths]
        assert all(os.path.isdir(original) for original in originals)

        self.boxPlainPath = os.path.join('cropped', 'box', 'plain')
        self.boxGrayPath = os.path.join('cropped', 'box', 'gray')
        self.boxEdgePath = os.path.join('cropped', 'box', 'edge')
        self.boxNoBackgroundPath = os.path.join('cropped', 'box', 'no_background')
        self.aspectPlainPath = os.path.join('cropped', 'aspect', 'plain')
        self.aspectGrayPath = os.path.join('cropped', 'aspect', 'gray')
        self.aspectEdgePath = os.path.join('cropped', 'aspect', 'edge')
        self.aspectNoBackgroundPath = os.path.join('cropped', 'aspect', 'no_background')

        self.customizationPaths = [
            self.boxPlainPath,
            self.boxGrayPath,
            self.boxEdgePath,
            self.boxNoBackgroundPath,
            self.aspectPlainPath,
            self.aspectGrayPath,
            self.aspectEdgePath,
            self.aspectNoBackgroundPath,
        ]

    def setupLogging(self):
        '''Setup log reporting'''
        self.logger = logging.getLogger(__name__)
        if self.config['debug']:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def reconfigure(self, config):
        '''Update configuration settings'''
        new_config = deepcopy(self.config)

        for setting, val in config.items():
            if setting not in self.DEFAULT_CONFIG:
                raise Exception('Invalid reconfig: {0} is an unknown setting'.format(setting))
            new_config[setting] = val

        for setting, val in new_config.items():
            if val == None:
                raise Exception('Invalid reconfig: {0} is required to be set!'.format(setting))
        self.config = new_config
        self.setupLogging()

    def getSubdirs(self, path):
        '''Get directory subdirs but ignore the ones starting with a period'''
        f = lambda x: os.path.isdir(x) and not os.path.basename(x).startswith('-')
        return filter(f, [os.path.join(path, d) for d in os.listdir(path)])

    def createCustomizations(self):
        '''Run through and save image customizations'''
        for mobPath in self.mobPaths:
            for customization in self.customizationPaths:
                for dim in self.config['dims']:
                    p = os.path.join(mobPath, customization, str(dim))
                    if not os.path.exists(p):
                        self.logger.info('making directory: ' + p)
                        os.makedirs(p)
            for imgName in os.listdir(os.path.join(mobPath, 'originals')):
                img = readImg(os.path.join(mobPath, 'originals', imgName))
                cropping = cropMob(img, show=False)
                self.saveCustomizations(mobPath, cropping, imgName)

    def saveCustomizations(self, mobPath, cropping, imgName):
        '''Generate and save each customizations'''
        overwrite = self.config['overwrite']

        for dim in self.config['dims']:
            boxPlainFullPath = os.path.join(mobPath, self.boxPlainPath, str(dim), imgName)
            boxGrayFullPath = os.path.join(mobPath, self.boxGrayPath, str(dim), imgName)
            boxEdgeFullPath = os.path.join(mobPath, self.boxEdgePath, str(dim), imgName)
            boxNoBackgroundFullPath = os.path.join(mobPath, self.boxNoBackgroundPath, str(dim), imgName)
            aspectPlainFullPath = os.path.join(mobPath, self.aspectPlainPath, str(dim), imgName)
            aspectGrayFullPath = os.path.join(mobPath, self.aspectGrayPath, str(dim), imgName)
            aspectEdgeFullPath = os.path.join(mobPath, self.aspectEdgePath, str(dim), imgName)
            aspectNoBackgroundFullPath = os.path.join(mobPath, self.aspectNoBackgroundPath, str(dim), imgName)

            # perform box customizations
            if dim == -1:
                boxPlain = resize(cropping, max(cropping.shape[:2]), aspect=False)
            else:
                boxPlain = resize(cropping, dim, aspect=False)
            boxGray = convertGray(boxPlain)
            boxNoBackground = rmBackground(boxPlain)
            boxEdges = getEdges(boxNoBackground)

            # save box customizations
            writeImg(boxPlainFullPath, boxPlain, overwrite=overwrite)
            writeImg(boxGrayFullPath, boxGray, overwrite=overwrite)
            writeImg(boxNoBackgroundFullPath, boxNoBackground, overwrite=overwrite)
            writeImg(boxEdgeFullPath, boxEdges, overwrite=overwrite)

            # perform aspect customizations
            aspectPlain = resize(cropping, dim, aspect=True) if dim != -1 else cropping
            aspectGray = convertGray(aspectPlain)
            aspectNoBackground = rmBackground(aspectPlain)
            aspectEdges = getEdges(aspectNoBackground)

            # save aspect customizations
            writeImg(aspectPlainFullPath, aspectPlain, overwrite=overwrite)
            writeImg(aspectGrayFullPath, aspectGray, overwrite=overwrite)
            writeImg(aspectNoBackgroundFullPath, aspectNoBackground, overwrite=overwrite)
            writeImg(aspectEdgeFullPath, aspectEdges, overwrite=overwrite)

if __name__ == '__main__':
    config = {
        'img_dir': 'C:\\Users\\armentrout\\Documents\\GitHub\\MinecraftObjectRecognition\\agents\\imgs',
        # 'overwrite': True,
    }
    dc = DatasetCreator(config)
    dc.createCustomizations()
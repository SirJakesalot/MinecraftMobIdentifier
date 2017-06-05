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
        'dims': [24],
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

    def createCustomizations(self):
        '''Run through and save image customizations'''
        dims = self.config['dims']
        for mob in self.mobPaths:
            for customization in self.customizationPaths:
                for dim in dims:
                    p = os.path.join(mob, customization, str(dim))
                    if not os.path.exists(p):
                        self.logger.info('making directory: ' + p)
                        os.makedirs(p)
            for name in os.listdir(os.path.join(mob, 'originals')):
                self.saveCustomizations(mob, name)

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

    def setupLogging(self):
        '''Setup log reporting'''
        self.logger = logging.getLogger(__name__)
        if self.config['debug']:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def getSubdirs(self, path):
        '''Ignore subdirs starting with a period'''
        f = lambda x: os.path.isdir(x) and not os.path.basename(x).startswith('-')
        return filter(f, [os.path.join(path, d) for d in os.listdir(path)])

    def saveCustomizations(self, mob, name):
        dims = self.config['dims']
        overwrite = self.config['overwrite']
        img = readImg(os.path.join(mob, 'originals', name))
        crop = cropMob(img, show=False)

        for dim in dims:
            boxPlainPath = os.path.join(mob, 'cropped', 'box', 'plain', str(dim), name)
            boxGrayPath = os.path.join(mob, 'cropped', 'box', 'gray', str(dim), name)
            boxEdgePath = os.path.join(mob, 'cropped', 'box', 'edge', str(dim), name)
            boxNoBackgroundPath = os.path.join(mob, 'cropped', 'box', 'no_background', str(dim), name)
            aspectPlainPath = os.path.join(mob, 'cropped', 'aspect', 'plain', str(dim), name)
            aspectGrayPath = os.path.join(mob, 'cropped', 'aspect', 'gray', str(dim), name)
            aspectEdgePath = os.path.join(mob, 'cropped', 'aspect', 'edge', str(dim), name)
            aspectNoBackgroundPath = os.path.join(mob, 'cropped', 'aspect', 'no_background', str(dim), name)

            boxPlain = resize(crop, dim, aspect=False)
            boxGray = convertGray(boxPlain)
            boxNoBackground = rmBackground(boxPlain)
            boxEdges = getEdges(boxNoBackground)

            writeImg(boxPlainPath, boxPlain, overwrite=overwrite)
            writeImg(boxGrayPath, boxGray, overwrite=overwrite)
            writeImg(boxEdgePath, boxNoBackground, overwrite=overwrite)
            writeImg(boxNoBackgroundPath, boxEdges, overwrite=overwrite)

            aspectPlain = resize(crop, dim, aspect=True)
            aspectGray = convertGray(aspectPlain)
            aspectNoBackground = rmBackground(aspectPlain)
            aspectEdges = getEdges(aspectNoBackground)

            writeImg(aspectPlainPath, aspectPlain, overwrite=overwrite)
            writeImg(aspectGrayPath, aspectGray, overwrite=overwrite)
            writeImg(aspectNoBackgroundPath, aspectNoBackground, overwrite=overwrite)
            writeImg(aspectEdgePath, aspectEdges, overwrite=overwrite)

if __name__ == '__main__':
    config = {
        'img_dir': 'C:\\Users\\armentrout\\Documents\\GitHub\\MinecraftObjectRecognition\\agents\\imgs'
    }
    dc = DatasetCreator(config)
    dc.createCustomizations()
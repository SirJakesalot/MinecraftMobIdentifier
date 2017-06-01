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
        'overwrite': True,
        'debug': True,
    }

    def __init__(self, config):
        # configuration management
        self.config = self.DEFAULT_CONFIG
        self.reconfigure(config)
        self.setupLogging()

        mobs = self.getSubdirs(self.config['img_dir'])
        dims = self.config['dims']
        originals = [os.path.join(mob, 'originals') for mob in mobs]
        assert all(os.path.isdir(original) for original in originals)

        self.boxPlainPath = os.path.join('cropped', 'box', 'plain')
        self.boxEdgePath = os.path.join('cropped', 'box', 'edge')
        self.boxNoBackgroundPath = os.path.join('cropped', 'box', 'no_background')
        self.aspectPlainPath = os.path.join('cropped', 'aspect', 'plain')
        self.aspectEdgePath = os.path.join('cropped', 'aspect', 'edge')
        self.aspectNoBackgroundPath = os.path.join('cropped', 'aspect', 'no_background')
        _paths = [
            self.boxPlainPath,
            self.boxEdgePath,
            self.boxNoBackgroundPath,
            self.aspectPlainPath,
            self.aspectEdgePath,
            self.aspectNoBackgroundPath
        ]

        for mob in mobs:
            for path in _paths:
                for dim in dims:
                    p = os.path.join(mob, path, str(dim))
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
        return filter(os.path.isdir, [os.path.join(path, d) for d in os.listdir(path)])

    def saveCustomizations(self, mob, name):
        dims = self.config['dims']
        overwrite = self.config['overwrite']
        img = readImg(os.path.join(mob, 'originals', name))
        crop = cropMob(img, show=False)

        for dim in dims:
            boxPlainPath = os.path.join(mob, 'cropped', 'box', 'plain', str(dim), name)
            boxEdgePath = os.path.join(mob, 'cropped', 'box', 'edge', str(dim), name)
            boxNoBackgroundPath = os.path.join(mob, 'cropped', 'box', 'no_background', str(dim), name)
            aspectPlainPath = os.path.join(mob, 'cropped', 'aspect', 'plain', str(dim), name)
            aspectEdgePath = os.path.join(mob, 'cropped', 'aspect', 'edge', str(dim), name)
            aspectNoBackgroundPath = os.path.join(mob, 'cropped', 'aspect', 'no_background', str(dim), name)

            boxPlain = resize(crop, dim, aspect=False)
            boxNoBackground = rmBackground(boxPlain)
            boxEdges = getEdges(boxNoBackground)

            writeImg(boxPlainPath, boxPlain, overwrite=overwrite)
            writeImg(boxEdgePath, boxNoBackground, overwrite=overwrite)
            writeImg(boxNoBackgroundPath, boxEdges, overwrite=overwrite)

            aspectPlain = resize(crop, dim, aspect=False)
            aspectNoBackground = rmBackground(aspectPlain)
            aspectEdges = getEdges(aspectNoBackground)

            writeImg(aspectPlainPath, aspectPlain, overwrite=overwrite)
            writeImg(aspectNoBackgroundPath, aspectNoBackground, overwrite=overwrite)
            writeImg(aspectEdgePath, aspectEdges, overwrite=overwrite)

config = {
    'img_dir': 'C:\\Users\\armentrout\\Documents\\GitHub\\MinecraftObjectRecognition\\agents\\imgs'
}
dc = DatasetCreator(config)
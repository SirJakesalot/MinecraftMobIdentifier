import time
import os
# vendors
import MalmoPython
import cv2
import numpy as np

from BaseAgent import BaseAgent

class RecorderAgent(BaseAgent):
    imgCounter = 1
    imgDir = 'imgs/tmp'
    def __init__(self, config):
        BaseAgent.__init__(self, config)
        if not os.path.exists(self.imgDir):
            os.makedirs(self.imgDir)
        assert os.path.isdir(self.imgDir)

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.KEEP_ALL_FRAMES)
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)

    def agentAction(self):
        while self.world_state.number_of_video_frames_since_last_state < 1 and self.world_state.is_mission_running:
            self.logger.info('Waiting for frames...')
            time.sleep(0.05)
            self.world_state = self.agent_host.getWorldState()

        self.logger.info('Got frame!')

        if self.world_state.is_mission_running:
            self.processFrame(self.world_state.video_frames[0].pixels)

    def processFrame(self, pixels):
        frame = np.asarray(pixels).reshape(480,640,3)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgPath = os.path.join(self.imgDir, '{0}.jpg'.format(self.imgCounter))
        cv2.imwrite(imgPath, frame_rgb)
        self.imgCounter += 1

config = {
    'mission_file': r'C:\Users\armentrout\Documents\GitHub\MinecraftObjectRecognition\missions\flat_world.xml',
    'recording': {
                'path': 'data.tgz',
                'fps': 1,
                'bit_rate': 400000
    },
}
ra = RecorderAgent(config)
ra.startMission()
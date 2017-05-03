import time
import os
# vendors
import MalmoPython
import cv2
import numpy as np

from BaseAgent import BaseAgent

class RecorderAgent(BaseAgent):
    imgCounter = 0
    imgDir = 'imgs'
    def __init__(self, config):
        BaseAgent.__init__(self, config)

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        # self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)
        # self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.KEEP_ALL_FRAMES)
        self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.LATEST_FRAME_ONLY)
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)


    # def setupMission(self):
    #     self.mission = MalmoPython.MissionSpec(self.mission_xml, True)

    def agentAction(self):
        while self.world_state.number_of_video_frames_since_last_state < 1 and self.world_state.is_mission_running:
            self.logger.info("Waiting for frames...")
            time.sleep(0.05)
            self.world_state = self.agent_host.getWorldState()

        self.logger.info("Got frame!")

        if self.world_state.is_mission_running:
            self.processFrame(self.world_state.video_frames[0].pixels)
            #self.agent_host.sendCommand("turn " + str(current_yaw_delta_from_depth))

    def processFrame(self, pixels):
        frame = np.asarray(pixels).reshape(480,640,3)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        imgPath = os.path.join(self.imgDir, '{0}.jpg'.format(self.imgCounter))
        cv2.imwrite(imgPath, frame_rgb)
        self.imgCounter += 1
    # def endMission(self):
    #     pass

#if __name__ == '__main__':
config = {
    'mission_file': r'C:\Users\armentrout\Documents\PyCharm\MinecraftObjectRecognition\missions\no_mob_world.xml',
}
ra = RecorderAgent(config)
ra.startMission()
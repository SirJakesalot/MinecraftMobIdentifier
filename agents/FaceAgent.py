import time
import os
# vendors
import MalmoPython
import cv2
import numpy as np

from BaseAgent import BaseAgent

class FaceAgent(BaseAgent):
    imgCounter = 0
    imgDir = 'imgs'
    def __init__(self, config):
        BaseAgent.__init__(self, config)

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)
        self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.LATEST_FRAME_ONLY)

    def setupMission(self):
        food = {
            'Cow': 'wheat',
            'MushroomCow': 'wheat',
            'Sheep': 'wheat',
            'Chicken': 'seeds',
            'Horse': 'wheat',
            'Pig': 'carrot',
            'Wolf': 'fish',
            'Ocelot': 'fish',
            'Rabbit': 'carrot',
            'Llama': 'hay_bales'
        }
        mob_entities = ''
        mob_entity = '<DrawEntity x="{0}" y="46" z="4" type="{1}" yaw="180"/>'
        mobs = ['Sheep', 'Sheep', 'Sheep']
        #mobs = ['Pig', 'Pig', 'Pig']
        pos = 1.5
        for mob in mobs:
            mob_entities += mob_entity.format(pos, mob)
            pos += 1
        self.mission_xml = self.mission_xml.format(mob_entities, food['Cow'])
        self.mission = MalmoPython.MissionSpec(self.mission_xml, True)

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
        imgPath = os.path.join(self.imgDir, '{0}.jpg'.format(self.imgCounter))
        cv2.imwrite(imgPath, frame)
        self.imgCounter += 1
    # def endMission(self):
    #     pass

#if __name__ == '__main__':
config = {
    'mission_file': r'C:\Users\armentrout\Documents\PyCharm\MinecraftObjectRecognition\missions\mob_room.xml'
}
fa = FaceAgent(config)
fa.startMission()
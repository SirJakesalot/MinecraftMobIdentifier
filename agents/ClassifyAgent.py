from baseAgent import BaseAgent
from random import randint
from collections import namedtuple
import time
import json
import math
import sys

import MalmoPython

EntityInfo = namedtuple('EntityInfo', 'x, y, z, yaw, pitch, name, colour, variation, quantity')
EntityInfo.__new__.__defaults__ = (0, 0, 0, 0, 0, "", "", "", 1)

MAX_DIST = 15
MIN_DIST = 3

class ClassifyAgent(BaseAgent):

    def __init__(self, config):
        self.mobs = ['Chicken','Pig','Cow','MushroomCow','Sheep']
        self.initial = True
        BaseAgent.__init__(self, config)

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)

    def spawnMobs(self):
        random_mob = []
        random_distance = []

        for i in range(4):
            random_mob.append(randint(0,len(self.mobs)-1))
            random_distance.append(randint(MIN_DIST,MAX_DIST))
            
        self.agent_host.sendCommand('chat /summon ' + self.mobs[random_mob[0]]+' ~ ~ '+str(self.my_z-random_distance[0])+' {Attributes:[{Name:generic.movementSpeed,Base:0}]}')
        self.agent_host.sendCommand('chat /summon ' + self.mobs[random_mob[1]]+' ~ ~ '+str(self.my_z+random_distance[1])+' {Attributes:[{Name:generic.movementSpeed,Base:0}]}')
        self.agent_host.sendCommand('chat /summon ' + self.mobs[random_mob[2]]+' ' + str(self.my_x-random_distance[2])+' ~ ~'+' {Attributes:[{Name:generic.movementSpeed,Base:0}]}')
        self.agent_host.sendCommand('chat /summon ' + self.mobs[random_mob[3]]+' ' + str(self.my_x+random_distance[3])+' ~ ~'+' {Attributes:[{Name:generic.movementSpeed,Base:0}]}')

    def getMyLocation(self):
        msg = self.world_state.observations[-1].text
        ob = json.loads(msg)
        if "entities" in ob:
            self.entities = [EntityInfo(**k) for k in ob["entities"]]
            #print entities
            for entity in self.entities:
                if entity.name == 'Cristina':
                    self.my_x = entity.x
                    self.my_y = entity.y
                    self.my_z = entity.z
                    self.my_yaw = entity.yaw

    def startMission(self):
        '''Attempt to start mission with the given configurations'''
        assert self.agent_host
        assert self.mission
        assert self.mission_record

        max_tries, count = 3, 0
        failed = True
        while count < max_tries and failed:
            count += 1
            try:
                self.agent_host.startMission(self.mission, self.mission_record)
                failed = False
            except RuntimeError as e:
                time.sleep(2)
        if failed:
            print('Error starting mission, exiting')
            exit(1)

        print('Waiting for the mission to start')
        self.world_state = self.agent_host.getWorldState()
        while not self.world_state.has_mission_begun:
            sys.stdout.write(".")
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print('Error:', error.text)
        print('Mission running')
        self.mission.allowAllChatCommands()
        self.agent_host.sendCommand('chat /gamerule sendCommandFeedback false')
        self.agent_host.sendCommand('chat /gamerule doMobLoot false')
        while self.world_state.is_mission_running:
            sys.stdout.write(".")
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()
            for error in self.world_state.errors:
                print('Error:', error.text)
            self.agentAction()
        self.endMission()

    def agentAction(self):
        while self.world_state.number_of_observations_since_last_state < 1 and self.world_state.is_mission_running:
#            self.logger.info("Waiting for observations...")
            time.sleep(0.1)
            self.world_state = self.agent_host.getWorldState()

 #       self.logger.info("Got observations!")

        if self.world_state.is_mission_running:
            
            self.getMyLocation()

            if self.my_yaw % 360 < 10:
                if len(self.entities) == 1 and self.initial == True:
                    self.spawnMobs()
                    time.sleep(2)
                    self.prev_mob_yaw = self.my_yaw
                    self.initial = False
                elif math.fabs(self.my_yaw-self.prev_mob_yaw) > 70:
                    self.agent_host.sendCommand('chat /kill @e[type=!Player]')
                    self.agent_host.sendCommand("turn 0")
                    time.sleep(5)
                    self.spawnMobs()
                    time.sleep(2)
                    self.prev_mob_yaw = self.my_yaw
                self.agent_host.sendCommand("turn 0.1")
            elif self.my_yaw % 90 < 10:
                if math.fabs(self.my_yaw-self.prev_mob_yaw) > 70:
                    self.prev_mob_yaw = self.my_yaw
                    self.agent_host.sendCommand("turn 0")
                    time.sleep(2)
                self.agent_host.sendCommand("turn 0.1")
    


if __name__ == '__main__':
    config = {
        'mission_file': 'flat_world.xml'
    }
    ca = ClassifyAgent(config)
    ca.startMission()

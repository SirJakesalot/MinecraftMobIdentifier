from baseAgent import BaseAgent
import Tkinter as tk
import json
import time
import math
from collections import namedtuple
import sys

import MalmoPython

EntityInfo = namedtuple('EntityInfo', 'x, y, z, yaw, pitch, name, colour, variation, quantity')
EntityInfo.__new__.__defaults__ = (0, 0, 0, 0, 0, "", "", "", 1)

class FindAgent(BaseAgent):

    def __init__(self, config):
        self.mobs = {'Chicken':'yellow','Pig':'pink','Cow':'brown'}
        self.known_mobs = []
        self.draw_grid = True
        BaseAgent.__init__(self, config)

    def getMissionXML(self):
        '''Read mission xml'''
        mission_file = self.config['mission_file']
        with open(mission_file, 'r') as f:
            print('Loading mission from', mission_file)
            self.mission_xml = f.read()
 #           self.getAreaDimensions()

    def getAreaDimensions(self,user):

        self.x1 = user.x - 8
        self.x2 = user.x + 8
        self.z1 = user.z - 8
        self.z2 = user.z + 8

 #       for line in self.mission_xml.split('\n'):
#            if 'type="air"' in line:
#                for part in line.split():
#                    if 'x1' in part:
#                        self.x1 = int(part.split('"')[1])
#                    elif 'x2' in part:
#                        self.x2 = int(part.split('"')[1])
#                    elif 'z1' in part:
#                        self.z1 = int(part.split('"')[1])
#                    elif 'z2' in part:
#                        self.z2 = int(part.split('"')[1])
                        
        self.arena_width = math.fabs(self.x2 - self.x1)
        self.arena_breadth = math.fabs(self.z2 - self.z1)

       # break

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.LATEST_OBSERVATION_ONLY)


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
            self.mission.allowAllChatCommands()
            self.agent_host.sendCommand('chat /kill @e[type=!Player]')
            msg = self.world_state.observations[-1].text
            ob = json.loads(msg)
            if "entities" in ob:
                entities = [EntityInfo(**k) for k in ob["entities"]]
                #print entities
                for entity in entities:
                    if entity.name == 'Cristina':
                        user = entity
                        my_x = entity.x
                        my_z = entity.z
                        my_yaw = entity.yaw
                        #self.agent_host.sendCommand("move 1")
                
                self.getAreaDimensions(user)
                if self.draw_grid:
                    self.gridSetup()
                    self.draw_grid = False
                entities.remove(user)
                self.drawMobs(entities,user)
                closest = self.closestMob(entities,my_x,my_z)
                #print 'Closest = ' + str(closest.name)
                if closest != EntityInfo():
                    #self.move(my_x,my_z,my_yaw,closest.x,closest.z)
                    self.checkMob(my_x,my_z,closest.x,closest.z,entities)
                else:
                    #print 'Found all mobs'
                    self.agent_host.sendCommand("move 0.0")
                    self.agent_host.sendCommand("turn 0.0")
 #           if 'LineOfSight' in ob:
#                los = ob['LineOfSight']
#                print los

    def move(self,my_x,my_z,my_yaw,x,z):
        angle = math.fabs(math.degrees(math.atan2(x-my_x,z-my_z)))

        if x-my_x > 0:
            angle = angle * -1

       # print 'Angle = ' + str(angle)
       # print 'Yaw = ' + str(my_yaw)

        if my_yaw % 360 > 180:
            my_yaw = (my_yaw%360) - 360
        else:
            my_yaw = my_yaw%360

       # print 'New Yaw = ' + str(my_yaw)

        if angle < 0:
            if my_yaw > angle + 10:
                self.agent_host.sendCommand("turn -0.5")
                #print 'Turn left'
            elif my_yaw < angle - 10:
                self.agent_host.sendCommand("turn 0.5")
                #print 'Turn right'
            else:
                self.agent_host.sendCommand("turn 0.0")
 #               print 'Stop'
        else:
            if my_yaw < angle - 10:
                self.agent_host.sendCommand("turn 0.5")
 #               print 'Turn right'
            elif my_yaw > angle + 10:
                self.agent_host.sendCommand("turn -0.5")
 #               print 'Turn left'
            else:
                self.agent_host.sendCommand("turn 0.0")
 #               print 'Stop'
 #       print ''

        self.agent_host.sendCommand("move 1.0")
        

    def distance(self,my_x,my_z,x,z):
        return math.sqrt((x-my_x)**2+(z-my_z)**2)

    def checkMob(self,my_x,my_z,x,z,entities):
        if self.distance(my_x,my_z,x,z) < 1:
            for entity in range(len(entities)):
                if x == entities[entity].x and z == entities[entity].z:
                    self.known_mobs.append(entity)
                    break


    def closestMob(self,entities,my_x,my_z):
        closest = (10000,EntityInfo())

        for entity in range(len(entities)):
            if entity not in self.known_mobs:
                temp_distance = self.distance(my_x,my_z,entities[entity].x,entities[entity].z)
                if temp_distance < closest[0]:
                    closest = (temp_distance,entities[entity])
        return closest[1]

    def gridSetup(self):
        # Display parameters:
        self.canvas_width = (self.arena_width)*25
        self.canvas_height = (self.arena_breadth)*25

        
        self.root = tk.Tk()
        self.root.wm_title("Mobs")

        self.canvas = tk.Canvas(self.root, width=self.canvas_width, height=self.canvas_height, borderwidth=0, highlightthickness=0, bg="black")
        self.legend = tk.Canvas(self.root,width=self.canvas_width,height=100, borderwidth=0, highlightthickness=0, bg='#9f9f9f')

        x = 10
        y = 10

        self.total_id = self.legend.create_text(x,y+50,anchor=tk.NW,text='Total Mobs Classified: ' + str(len(self.known_mobs)))
        self.accuracy_id = self.legend.create_text(x,y+70,anchor=tk.NW,text='Accuracy: 0%')
        
        for mob,color in self.mobs.items():
            self.legend.create_rectangle(x,y,x+20,y+20,fill=color)
            self.legend.create_text(x+25,y,anchor=tk.NW,text=mob)
            x = x + 100

        self.canvas.pack()
        self.legend.pack()
        self.root.update()

    def canvasX(self,x):
        return ((x-float(self.x1))*25)

    def canvasY(self,y):
        return ((y-float(self.z1))*25)

    def drawMobs(self,entities,user):
        self.canvas.delete("all")

        self.canvas.create_rectangle(self.canvasX(-self.canvas_width/2), self.canvasY(-self.canvas_height/2), self.canvasX(self.canvas_width/2), self.canvasY(self.canvas_height/2), fill="#888888")
        for ent in range(len(entities)):
            if entities[ent].name in self.mobs.keys():
                if ent in self.known_mobs:
                    self.canvas.create_oval(self.canvasX(entities[ent].x)-3, self.canvasY(entities[ent].z)-3, self.canvasX(entities[ent].x)+3, self.canvasY(entities[ent].z)+3, fill=self.mobs[entities[ent].name])
                else:
                    self.canvas.create_oval(self.canvasX(entities[ent].x)-3, self.canvasY(entities[ent].z)-3, self.canvasX(entities[ent].x)+3, self.canvasY(entities[ent].z)+3, fill="#000000")
            
        self.canvas.create_oval(self.canvasX(user.x)-4, self.canvasY(user.z)-4, self.canvasX(user.x)+4, self.canvasY(user.z)+4, fill="#22ff44")

        self.legend.itemconfigure(self.total_id,text='Total Mobs Classified: ' + str(len(self.known_mobs)))
        self.legend.itemconfigure(self.accuracy_id,text='Accuracy: '+str((float(len(self.known_mobs))/float(len(entities)))*100)+'%')#FIX

        self.root.update()


if __name__ == '__main__':
    config = {
        'mission_file': 'flat_world.xml'
    }
    fa = FindAgent(config)
    fa.startMission()

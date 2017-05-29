# standard imports
from copy import deepcopy
import logging
import os
import sys
import time

# vendors
import MalmoPython

# flush print output immediately
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)


class BaseAgent(object):
    '''General Malmo Agent'''

    # out of the box configurations
    # all values that are None have to be specified by the user
    DEFAULT_CONFIG = {
        'mission_file': None,
        'recording': {
            'path': 'data.tgz',
            'fps': 10,
            'bit_rate': 400000
        },
        'debug': True,
    }

    def __init__(self, config):
        # configuration management
        self.config = self.DEFAULT_CONFIG
        self.reconfigure(config)

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

        # mission prerequisites
        self.setupLogging()
        self.getMissionXML()

        # create mission attributes
        self.setupMission()
        self.setupMissionRecording()
        self.setupAgentHost()

    def setupLogging(self):
        '''Setup log reporting'''
        self.logger = logging.getLogger(__name__)
        if self.config['debug']:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
        self.logger.handlers = []
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def getMissionXML(self):
        '''Read mission xml'''
        mission_file = self.config['mission_file']
        with open(mission_file, 'r') as f:
            print('Loading mission from', mission_file)
            self.mission_xml = f.read()

    def setupMission(self):
        '''Setup mission configurations'''
        # TODO: Add the ability to apply a variety of configurations to the mission xml
        assert self.mission_xml
        self.mission = MalmoPython.MissionSpec(self.mission_xml, True)

    def setupMissionRecording(self):
        '''Setup mission recordings'''
        recording = self.config['recording']
        if recording:
            # self.mission_record = MalmoPython.MissionRecordSpec(recording['path'])
            # self.mission_record.recordMP4(recording['fps'], recording['bit_rate'])
            self.mission_record = MalmoPython.MissionRecordSpec('data2.tgz')
            self.mission_record.recordMP4(1,200000)
        else:
            self.mission_record = MalmoPython.MissionRecordSpec()

    def setupAgentHost(self):
        self.agent_host = MalmoPython.AgentHost()
        # self.agent_host.setObservationsPolicy(MalmoPython.ObservationsPolicy.KEEP_ALL_OBSERVATIONS)
        # self.agent_host.setVideoPolicy(MalmoPython.VideoPolicy.KEEP_ALL_FRAMES)

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
        '''A single action from the agent at a given world state'''
        # TODO: implement the agent's action
        sys.stdout.write(".")

    def endMission(self):
        '''Anything to be done after mission'''
        print('Mission ended')
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.env.sc2_env import SC2Env, AgentInterfaceFormat, Bot, Agent
from pysc2.env.sc2_env import Race, Difficulty, Dimensions
from pysc2.lib import actions, features, units
from pysc2.lib import point
import random
from absl import app
import time
import math
from statistics import mean 
from params import *
import numpy as np
from enum import Enum
from statistics import mean 

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_HOSTILE = 4
_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL
_VISIBILITY_MAP = features.SCREEN_FEATURES.visibility_map.index

class state(Enum):
    IDLE               = 0
    FTS                = 1 #First Time Setup
    WAIT_MINERALS      = 2
    BUILD_SUPPLY_DEPOT = 3
    BUILD_BARRACA      = 4
    WAIT_BARRACK_BUILD = 5
    TRAIN_MARRINE      = 6
    

def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))

class BayesAgent(base_agent.BaseAgent):

    def __init__(self):
        super(BayesAgent, self).__init__()
        self.capture = True
        self.state = state.FTS #First Time Setup
        self.supply_location = (50,50)
        self.barraca_location = (70,50)
        self.left_to_right = False


    def scv_avg(self,obs):
        scv_y, scv_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
        scv_y = scv_y.mean()
        scv_x = scv_x.mean()
        return (scv_y,scv_x)

    def select_first_SCV(self,obs):
          scv_y, scv_x = self.scv_avg(obs)
          lim_y, lim_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
          lim_y, lim_x = (min(lim_y)+20,min(lim_x)+20)
          #select rectangle from upper left corner to middle
          return actions.FUNCTIONS.select_rect(
          "select",
          (lim_x,lim_y), 
          (scv_x,   scv_y))

    def Select_side(self,obs):# Elige de que lado va poner los supply y barracas
        cmd_center = [unit for unit in obs.observation.feature_units 
                      if unit.unit_type == units.Terran.CommandCenter]

        vespane = [unit for unit in obs.observation.feature_units 
                      if unit.unit_type == units.Neutral.VespeneGeyser]

        minerals   = [unit for unit in obs.observation.feature_units 
                      if unit.unit_type == units.Neutral.MineralField or
                      unit.unit_type == units.Neutral.MineralField450 or
                      unit.unit_type == units.Neutral.MineralField750]

        avg_minerals_x = 0
        for m in minerals:
          avg_minerals_x+=m.x

        avg_minerals_x/=len(minerals)

        cmd_center = cmd_center[0] # para evitar hacer esto -> cmd_center[0].x, quitar basicamente el [0]

        orientation_x = cmd_center.x - avg_minerals_x
        
        self.left_to_right = (orientation_x > 0)

        if(self.left_to_right == True):
          #self.supply_location = (cmd_center.x,cmd_center.y) # Assignar una cordenada al supply depot
          self.supply_location = (65,40)
          self.barraca_location = (70,50)
        else: #right_to_left
          self.supply_location = (15,30)
          self.barraca_location = (15,15)
         # self.supply_location = (cmd_center.x-10,cmd_center.y-10) # Assignar una cordenada al supply depot


    def step(self, obs):
        super(BayesAgent, self).step(obs)

        if(self.state == state.FTS): # Select an SCV
          self.state = state.WAIT_MINERALS
          self.timer = 0
          return self.select_first_SCV(obs)

        elif(self.state == state.WAIT_MINERALS):# Wait until have enought minerals
          if actions.FUNCTIONS.Build_SupplyDepot_screen.id in obs.observation.available_actions:
            self.state = state.BUILD_SUPPLY_DEPOT

        elif(self.state == state.BUILD_SUPPLY_DEPOT):# Build Suplly Depot
          self.state = state.BUILD_BARRACA
          self.Select_side(obs)
          return actions.FUNCTIONS.Build_SupplyDepot_screen("now", self.supply_location)
        
        elif(self.state ==  state.BUILD_BARRACA):
          if actions.FUNCTIONS.Build_Barracks_screen.id in obs.observation.available_actions:
            self.state = state.WAIT_BARRACK_BUILD
            return actions.FUNCTIONS.Build_Barracks_screen("now", self.barraca_location)

        elif(self.state ==  state.WAIT_BARRACK_BUILD):
          Barracks = [unit for unit in obs.observation.feature_units 
                        if unit.unit_type == units.Terran.Barracks]
          if len(Barracks) > 0 :
            if(Barracks[0][7] > 255):
              print(Barracks)
              self.state = state.TRAIN_MARRINE

        elif(self.state ==  state.TRAIN_MARRINE):
          self.state = state.IDLE
          return actions.FUNCTIONS.Train_Marine_quick("now", Barracks)
          
     


        return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = BayesAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="Simple64",
          players=[sc2_env.Agent(sc2_env.Race.terran),Bot(sc2_env.Race.terran, Difficulty.easy)],# First player is our agent
          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=84, minimap=64),#terraing visibility
              use_feature_units=True),
          step_mul=1,# related with APM, ex. 8 -> 300 APM
          game_steps_per_episode=0,#run forever, other than 0 time limit
          visualize=True) as env:
          
        agent.setup(env.observation_spec(), env.action_spec())
        
        timesteps = env.reset()
        agent.reset()
        
        while True:
          step_actions = [agent.step(timesteps[0])]
          if timesteps[0].last():
            break
          timesteps = env.step(step_actions)
      
  except KeyboardInterrupt:
    pass
  
if __name__ == "__main__":
  app.run(main)
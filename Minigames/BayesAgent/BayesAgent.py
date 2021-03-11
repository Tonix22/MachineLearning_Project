from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.env.sc2_env import SC2Env, AgentInterfaceFormat, Bot, Agent
from pysc2.env.sc2_env import Race, Difficulty, Dimensions
from pysc2.lib import actions, features, units
import random
from absl import app
import time
import math
from statistics import mean 
from params import *
import numpy as np

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_HOSTILE = 4
_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL
_VISIBILITY_MAP = features.SCREEN_FEATURES.visibility_map.index


def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))

class BayesAgent(base_agent.BaseAgent):

    def __init__(self):
        super(BayesAgent, self).__init__()
        self.capture = True
        

    def step(self, obs):
        super(BayesAgent, self).step(obs)


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
          step_mul=.3,# related with APM, ex. 8 -> 300 APM
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
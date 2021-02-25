from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app
import time

_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL



def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))



class FogAgent(base_agent.BaseAgent):

    def __init__(self):
        super(FogAgent, self).__init__()
        self.capture = True
        self.marines = []
        self.zergs   = []

    def get_fighters(self,obs,fighter_type):
        
        actors = [unit for unit in obs.observation.feature_units
            if unit.unit_type == fighter_type]
        
        for N in actors:
            print("pos: "+str(N.x)+","+str(N.y)+": "+str(N.health))

        if len(actors) > 0:
            return actors
        else :
            return None

    def step(self, obs):
        super(FogAgent, self).step(obs)
        if(self.capture == True):
            self.capture = False
            print("zerings")
            self.zergs = self.get_fighters(obs,units.Zerg.Zergling)
            print("Marines")
            self.marines = self.get_fighters(obs,units.Terran.Marine)
            return actions.FUNCTIONS.select_army("select")

        if actions.FUNCTIONS.Attack_screen.id in obs.observation.available_actions:
          return actions.FUNCTIONS.Attack_screen("now", (self.zergs[0].x,self.zergs[0].y))
        
        return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = FogAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="FindAndDefeatZerglings",
          players=[sc2_env.Agent(sc2_env.Race.terran)],# First player is our agent
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
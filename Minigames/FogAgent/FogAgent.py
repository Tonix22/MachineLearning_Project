from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app
import time
from statistics import mean 
_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_HOSTILE = 4
_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL

_VISIBILITY_MAP = features.SCREEN_FEATURES.visibility_map.index

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
        self.seenEnemies = set()
        self.estado = 0
        self.destino = (0,0)

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
        vision = obs.observation["feature_minimap"][_VISIBILITY_MAP]
        marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
        if(self.capture == True):
            self.capture = False
            #print("zerings")
            #self.zergs = self.get_fighters(obs,units.Zerg.Zergling)
            enemy_y, enemy_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
            #enemy_y, enemy_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
            #print(len(enemy_y))
            return actions.FUNCTIONS.select_army("select")
        if (self.estado == 0):
          self.estado = 1
          enemy_y, enemy_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
          marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
          
          if actions.FUNCTIONS.Attack_minimap.id in obs.observation.available_actions:
            if(len(enemy_y > 0)):
              self.destino = (enemy_x[0],enemy_y[0])
              return actions.FUNCTIONS.Attack_minimap("now", self.destino)
            else:
              self.destino = (random.randint(5, 61),random.randint(5, 55))
              return actions.FUNCTIONS.Attack_minimap("now", self.destino)
        
        if (self.estado == 1 and (self.destino[1] in range(marine_y.min()-2,marine_y.max()+2) ) and (self.destino[0] in range(marine_x.min()-2,marine_x.max()+2) )):
          self.estado = 0
          #input('Pause')

        else:
          return actions.FUNCTIONS.Attack_minimap("now", (self.destino[0],self.destino[1]))

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
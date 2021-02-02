from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app
import numpy

_PLAYER_SELF = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL

def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))

#1. Select Army 
#2. Army is selected now we could say there are availabe actions
#3. Get relative player pos
class BeaconAgent(base_agent.BaseAgent):
  def step(self, obs):
    super(BeaconAgent, self).step(obs)    
    if actions.FUNCTIONS.Move_screen.id in obs.observation.available_actions:
      player_relative = obs.observation.feature_screen.player_relative
      beacon = _xy_locs(player_relative == _PLAYER_NEUTRAL)

      print (beacon)
      #input("stop")
      if not beacon:
        return actions.FUNCTIONS.no_op()
      beacon_center = numpy.mean(beacon, axis=0).round()
      return actions.FUNCTIONS.Move_screen("now", beacon_center)
    else:
      return actions.FUNCTIONS.select_army("select")


def main(unused_argv):
  agent = BeaconAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="MoveToBeacon",
          players=[sc2_env.Agent(sc2_env.Race.terran)], # First player is our agent
          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=84, minimap=64), #terraing visibility
              use_feature_units=True),
          step_mul=1, # related with APM, ex. 8 -> 300 APM
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
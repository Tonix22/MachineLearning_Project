from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app

class BeaconAgent(base_agent.BaseAgent):
  def step(self, obs):
    super(BeaconAgent, self).step(obs)
    #soldados = [unit for unit in obs.observation.feature_units]
    
    
    soldado = obs.observation.feature_units[0]
    if len(soldado!=None) :  
        return actions.FUNCTIONS.select_point("select_all_type", (soldado.x,soldado.y))

    return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = BeaconAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="MoveToBeacon",
          players=[sc2_env.Agent(sc2_env.Race.terran)],
          agent_interface_format=features.AgentInterfaceFormat(
              feature_dimensions=features.Dimensions(screen=84, minimap=64),
              use_feature_units=True),
          step_mul=1,
          game_steps_per_episode=0,
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
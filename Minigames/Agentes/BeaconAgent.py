from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app

class BeaconAgent(base_agent.BaseAgent):
  #esta funci[on verifica que el eprsonaje este seleccionado]
  def unit_type_is_selected(self, obs, unit_type):
        if (len(obs.observation.single_select) > 0 and obs.observation.single_select[0].unit_type == unit_type):
            return True

        if (len(obs.observation.multi_select) > 0 and obs.observation.multi_select[0].unit_type == unit_type):
            return True

        return False
  
  def __init__(self):
    super(BeaconAgent, self).__init__()
    self.x = random.randint(4, 79)#variable x para establecer el punto a llegar
    self.y = random.randint(4,58) #variable y para establecer el punto a llegar
    self.bandera = 0 #esta variable nos sirve para que no este dando clicks todo el tiempo solo hasta que se alcanza el objetivo


  def step(self, obs):
    super(BeaconAgent, self).step(obs)
    soldado = obs.observation.feature_units[0]
    if (self.unit_type_is_selected(obs, units.Terran.Marine)): #si el Marine esta seleccionado mueve al personaje
      if(soldado.x!=self.x and soldado.y!=self.y and self.bandera == 0 ):
        print("Ejecutando movimiento")
        self.bandera = 1 #significa que se esta moviendo al objetivo no necesita cambiar la direcci[on]
        return actions.FUNCTIONS.Move_screen("now", (self.x,self.y))
      #si alcanzo el objetivo cambia de direccion
      elif ((soldado.x>=self.x-2 and soldado.x<=self.x+2 ) and (soldado.y>=self.y-2 and soldado.y<=self.y+2 ) and self.bandera ==1 ):
        self.x = random.randint(4, 79)
        self.y = random.randint(4,58)
        self.bandera = 0 
    else:
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
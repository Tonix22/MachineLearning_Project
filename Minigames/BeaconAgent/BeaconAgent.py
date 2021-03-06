from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app
import numpy
import IDS
from BellmanFord import *
from Params import *
import time

_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL



def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))

#1. Select Army 
#2. Army is selected now we could say there are availabe actions
#3. Get relative player pos
class BeaconAgent(base_agent.BaseAgent):
  #esta funci[on verifica que el eprsonaje este seleccionado]

  def __init__(self):
    super(BeaconAgent, self).__init__()
    self.x = 0#variable x para establecer el punto a llegar
    self.y = 0 #variable y para establecer el punto a llegar
    self.estado = 0 #0=Idle 1=Calcular Ruta 2=Movimiento
    self.beacon_center = (0,0)
    self.Bell = BellmanImplicit() #build bell man map
    self.soldado = (0,0)
    self.way = []

  def beaconCapture(self,obs):
    player_relative = obs.observation.feature_screen.player_relative
    beacon = _xy_locs(player_relative == _PLAYER_NEUTRAL)
    self.beacon_center = numpy.mean(beacon, axis=0).round()
  
  def marineCapture(self,obs):
    player_relative = obs.observation.feature_screen.player_relative
    marine = _xy_locs(player_relative == _PLAYER_SELF)
    if (len(marine)!=0):
      temp = numpy.mean(marine, axis=0).round()
      self.soldado = (int(temp[0]),int(temp[1]))

  def step(self, obs):
    super(BeaconAgent, self).step(obs)
    #time.sleep(0.1)
    
    #soldado = obs.observation.feature_units[0]
    #soldado = [unit for unit in obs.observation.feature_units if unit.unit_type == units.Terran.Marine]
    
    #self.x=self.beacon_center[0]
    #self.y=self.beacon_center[1]
    if actions.FUNCTIONS.Move_screen.id in obs.observation.available_actions: #si el Marine esta seleccionado mueve al personaje
      self.marineCapture(obs)  
      if(self.estado == 0 ):
        
        print("Calcula ruta")
        self.estado = 1 
        self.beaconCapture(obs)

        if(run_BELL):
          if(len(self.way) == 0 ):
            self.way = self.Bell.ImplicitBellmanFord(self.soldado,self.beacon_center)
            self.x, self.y = self.way.pop()
            return actions.FUNCTIONS.Move_screen("now", (self.x,self.y))

        if(run_IDS):
          self.x, self.y = IDS.IDS_BeaconSearchCenterScreen(self.beacon_center)
          

      elif (self.estado==1):
        print("Ejecutando movimiento")
        if(run_BELL):
          if ((self.soldado[0]>=self.x-3 and self.soldado[0]<=self.x+3 ) and (self.soldado[1]>=self.y-3 and self.soldado[1]<=self.y+3 ) and self.estado ==1 ):
            self.x, self.y = self.way.pop()
            if(len(self.way) == 0 ): #hasta que llegue al ultimo del way
                self.estado = 3
                self.x = int(self.beacon_center[0])
                self.y = int(self.beacon_center[1])
                return actions.FUNCTIONS.Move_screen("now", (self.x,self.y))
            return actions.FUNCTIONS.Move_screen("now", (self.x,self.y))
          
        if(run_IDS):
          self.estado = 2
          return actions.FUNCTIONS.Move_screen("now", (self.x,self.y))
          
      elif (self.estado>2):
        self.estado+=1
        if self.estado==10:
          self.estado=2
        return actions.FUNCTIONS.Move_screen("now", (self.x,self.y))

      #si alcanzo el objetivo cambia de direccion      
      
      elif ((self.soldado[0]>=self.x and self.soldado[0]<=self.x ) and (self.soldado[1]>=self.y and self.soldado[1]<=self.y ) and self.estado ==2 ):
        print("Llegue, cambiame la ruta //IDLE")
        self.estado = 0
    else:
      return actions.FUNCTIONS.select_army("select")
    
    return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = BeaconAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="MoveToBeacon",
          players=[sc2_env.Agent(sc2_env.Race.terran)],# First player is our agent
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
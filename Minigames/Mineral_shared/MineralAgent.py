from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app
import numpy
from params import *
from Annealing import *
from A_star import *
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
class MineralAgent(base_agent.BaseAgent):
  #esta funci[on verifica que el eprsonaje este seleccionado]

  def __init__(self):
    super(MineralAgent, self).__init__()
    self.flag = 1
    self.flagMov = 1
    self.Mineral_cords = (0,0)
    self.Marine_cords=0
    self.marine = 0
    self.marine2 = 0
    self.error = 0
    self.Mineral_cords_A = 0
  
  def marineCoordinates(self,obs):
    player_relative = obs.observation.feature_screen.player_relative
    coordinates = _xy_locs(player_relative == _PLAYER_SELF)
    coordinates = sorted(coordinates , key=lambda k: [k[1], k[0]])
    coor = list()#lista de coordenadas final
    #patron de pixeles relativos del cristal
    pixeles=[(1,0),(2,0),(0,1),(1,1),(2,1),(0,2),(1,2),(2,2)]
    while (len(coordinates)>0):
        temp = coordinates[0]        
        aciertosC=0#aciertos centro
        aciertosI=0#aciertos Izquierda
        aciertosD=0#aciertos Derecha
        #En caso de traslape se verifica la mejor posici�n comparando entre izquierda centro y derecha
        for pixel in pixeles:
            if ((temp[0]+pixel[0],temp[1]+pixel[1]) in coordinates):
                aciertosC += 1
        for pixel in pixeles:
            if ((temp[0]-1+pixel[0],temp[1]+pixel[1]) in coordinates):
                aciertosI += 1
        for pixel in pixeles:
            if ((temp[0]+1+pixel[0],temp[1]+pixel[1]) in coordinates):
                aciertosD += 1
        # selecci�n de mejor opci�n de posici�n
        if(aciertosD>aciertosC and aciertosD>aciertosI):
            temp=(temp[0]+1,temp[1])
        elif(aciertosI>aciertosC and aciertosI>aciertosC):
            temp=(temp[0]-1,temp[1])
        #borrar coordenadas
        del coordinates[0]
        coor.append((temp[0]+1,temp[1]+1))#agrega coordenada
        for pixel in pixeles:
            if ((temp[0]+pixel[0],temp[1]+pixel[1]) in coordinates):
                del coordinates[coordinates.index((temp[0]+pixel[0],temp[1]+pixel[1]))]

    return coor
  def mineralCoordinates(self,obs):
    player_relative = obs.observation.feature_screen.player_relative
    coordinates = _xy_locs(player_relative == _PLAYER_NEUTRAL)
    coordinates = sorted(coordinates , key=lambda k: [k[1], k[0]])
    coor = list()#lista de coordenadas final
    #patron de pixeles relativos del cristal
    pixeles=[(1,0),(-1,1),(0,1),(1,1),(2,1),(-1,2),(0,2),(1,2),(2,2),(0,3),(1,3)]
    while (len(coordinates)>0):
        temp = coordinates[0]        
        aciertosC=0#aciertos centro
        aciertosI=0#aciertos Izquierda
        aciertosD=0#aciertos Derecha
        #En caso de traslape se verifica la mejor posici�n comparando entre izquierda centro y derecha
        for pixel in pixeles:
            if ((temp[0]+pixel[0],temp[1]+pixel[1]) in coordinates):
                aciertosC += 1
        for pixel in pixeles:
            if ((temp[0]-1+pixel[0],temp[1]+pixel[1]) in coordinates):
                aciertosI += 1
        for pixel in pixeles:
            if ((temp[0]+1+pixel[0],temp[1]+pixel[1]) in coordinates):
                aciertosD += 1
        # selecci�n de mejor opci�n de posici�n
        if(aciertosD>aciertosC and aciertosD>aciertosI):
            temp=(temp[0]+1,temp[1])
        elif(aciertosI>aciertosC and aciertosI>aciertosC):
            temp=(temp[0]-1,temp[1])
        #borrar coordenadas
        del coordinates[0]
        coor.append((temp[0],temp[1]+1))#agrega coordenada
        for pixel in pixeles:
            if ((temp[0]+pixel[0],temp[1]+pixel[1]) in coordinates):
                del coordinates[coordinates.index((temp[0]+pixel[0],temp[1]+pixel[1]))]

    return coor

  def marinesCapture(self,obs,index):

    marines = [unit for unit in obs.observation.feature_units
              if unit.unit_type == units.Terran.Marine]

    if len(marines) > 0:
      return marines[index]
    else :
      return None

  def step(self, obs):
    super(MineralAgent, self).step(obs)
    self.Marine_cords = self.marineCoordinates(obs)
    #self.marine   = self.marinesCapture(obs,0)
    #self.marine2   = self.marinesCapture(obs,1)
    if self.flag == 1:
      #setup
      self.flag = 2
    if self.flag == 2:
      #calcular
      print("Calculando ruta")
      minerals = self.mineralCoordinates(obs)

      MAP.stampsOnMap(minerals,brush.array) 

      if len(minerals) > 5:
        HILL_CLIMB = False
        
      else:
        HILL_CLIMB = True
        BRUSH_DIAMETER = 10
        BRUSH_DECREMENT = 20
        brush.resize(BRUSH_DIAMETER,BRUSH_DECREMENT) 

      search = annealing(TEMPERATURE_INIT,ALPHA)
      if (self.Marine_cords[1][0] < X_SIZE and self.Marine_cords[1][1] < Y_SIZE):
        print(f"Cordenadas x{self.Marine_cords[1][0]},y{self.Marine_cords[1][1]}")
        a = A(MAP.map,(self.Marine_cords[1][0],self.Marine_cords[1][1]))
        self.Mineral_cords_A = a.aplus()

      self.Mineral_cords = search.Algo(ITERATIONS)
      


      #search2 aqui?
      #mineral_cords2 aqui?
      self.flag=3
    if self.flag == 3:
      #clicks : selection and moves
      if self.flagMov == 1:
        self.marine = self.Marine_cords[0]
        self.marine2 = self.Marine_cords[1]
        self.flagMov = 2
        return actions.FUNCTIONS.select_point("select",(self.marine[0],self.marine[1]))
        #return actions.FUNCTIONS.select_army("select")
      if self.flagMov ==2:
        self.flagMov = 3
        #self.flagMov = 1 #reinicia
        #self.flag = 4
        if actions.FUNCTIONS.Move_screen.id in obs.observation.available_actions:
            return actions.FUNCTIONS.Move_screen("now", ( self.Mineral_cords[0], self.Mineral_cords[1]))
      if self.flagMov == 3:
        self.flagMov = 4
        return actions.FUNCTIONS.select_point("select",(self.marine2[0],self.marine2[1]))
        #return actions.FUNCTIONS.select_army("select")
      if self.flagMov ==4:
        self.flagMov = 1 #reinicia
        self.flag = 4
        if actions.FUNCTIONS.Move_screen.id in obs.observation.available_actions:
            return actions.FUNCTIONS.Move_screen("now", self.Mineral_cords_A)
    if self.flag == 4:
      #Wait for arrival of marines
      print("Cordenadas de minarales")
      print(self.Mineral_cords)
      print("Cordenadas de soldados")
      print(self.Marine_cords)
      self.error += 1
      if((self.Mineral_cords[0],self.Mineral_cords[1]) in self.Marine_cords or self.error > 100):
        self.error = 0
        self.flag = 2
    
    #if self.flag == 2 :
      #marine   = self.marinesCapture(obs,0)
      #minerals = self.mineralCoordinates(obs)
      #print (minerals)
      #self.flag == 0 # TODO DELETE THIS LINE
      #return actions.FUNCTIONS.select_point("select",(marine.x,marine.y))
       
    return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent = MineralAgent()
  try:
    while True:
      with sc2_env.SC2Env(
          map_name="CollectMineralShards",
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
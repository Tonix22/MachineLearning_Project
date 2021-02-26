from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.lib import actions, features, units
import random
from absl import app
import time
import math
from statistics import mean 
from matrix import MapMatrix
from MinMax import *
from params import *
import numpy as np

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_HOSTILE = 4
_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL
_VISIBILITY_MAP = features.SCREEN_FEATURES.visibility_map.index
class far():
  def __init__(self):
    self.valores = self.inicializaMatriz()

  def inicializaMatriz(self):
    temp = list()
    for x in range(56): 
      temp.append([(22+int(x/8)*5,14+(x%8)*5),0])
    return temp

  def density(self,matriz,coor,distancia,densidad):
      imagen =[(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(0,-2),(0,-1),(0,0),(0,1),(0,2),(1,-2),(1,-1),(1,0),(1,1),(1,2),(2,-2),(2,-1),(2,0),(2,1),(2,2)]
      density = list()
      point_a = np.array(coor)      
      for x in self.valores:
          point_b = np.array((x[0][1],x[0][0]))
          distance = np.linalg.norm(point_a - point_b) * distancia
          temp = 0
          for y in imagen:
              if (matriz[x[0][0]+y[0]][x[0][1]+y[1]]==0):
                temp += 1
          density.append(temp)
          x[1] = temp * densidad + distance
      temp = self.valores[0]
      for node in self.valores:
        if (node[1]>temp[1]):
          temp=node
      return temp[0]  

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
        self.estado = 0
        self.destino = (0,0)
        self.visitedZergs = list()
        self.underAttackZergs = list()
        self.seenZergs=0
        self.killedZergs=0
        self.map = MapMatrix(64,64)
        self.algo = MinMax()
        self.far = far()

    def get_fighters(self,obs,fighter_type):
        
        actors = [unit for unit in obs.observation.feature_units
            if unit.unit_type == fighter_type]
        #actors = [unit for unit in obs.observation.feature_units
        #    if unit.unit_type == fighter_type]
        
        #for N in actors:
        #    print("pos: "+str(N.x)+","+str(N.y)+": "+str(N.health))

        if len(actors) > 0:
            return actors
        else :
            return None
    def EnemyCounter(self,enemy_x,enemy_y,marine_x,marine_y):
      for r in range(0,len(enemy_y)):
        existVisited=False
        existUnderAttack=False
        attackDistance=10
        #verifica si se movio poquito comparado a alguno en nuestra listas
        for v in self.visitedZergs:
          if(abs(v[0]-enemy_x[r])<=2 and abs(v[1]-enemy_y[r])<=2):
            v=(enemy_x[r],enemy_y[r])
            existVisited=True
            break
        for w in self.underAttackZergs:
          if(abs(w[0]-enemy_x[r])<=2 and abs(w[1]-enemy_y[r])<=2):
            w=(enemy_x[r],enemy_y[r])
            existUnderAttack=True
            break
        #si no existia en visitados o attacker, agregar a visitados
        if(existVisited==False and existUnderAttack==False):
          self.visitedZergs.append((enemy_x[r],enemy_y[r]))
          self.seenZergs+=1
          print(f"Se agrego un Zerg: {self.seenZergs}, coordenada agregada: {enemy_x[r]},{enemy_y[r]} ")
          #input('Pause')
        #Revisar si esta en area 'atacable'
      # print(f"Distance x: {abs(enemy_x[r]-marine_x[0])}; Distance Y: {abs(enemy_y[r]-marine_y[0])}")
      #  if((abs(enemy_x[r]-marine_x[0])+abs(enemy_y[r]-marine_y[0])<attackDistance) and existVisited):
      #    self.visitedZergs.remove((enemy_x[r],enemy_y[r]))
      #    self.underAttackZergs.append((enemy_x[r],enemy_y[r]))
      #Fuera del for , Si deja de existir en under attack
      #toRemove=list()
      #for i in range(0,len(self.underAttackZergs)):#revisar si hay algun exist under attack que no este en 
      #  n=(self.underAttackZergs[i][0],self.underAttackZergs[i][1])
      #  if(n[0] not in enemy_x or n[1] not in enemy_y):
      #    toRemove.append(n)
      #    self.killedZergs+=1
      #    print(f"Se elimino un Zerg: {self.killedZergs}, coordenada agregada: {n} ")
      #    input('Pause')
      #for j in toRemove:
      #  self.underAttackZergs.remove(j) 

    def step(self, obs):
        super(FogAgent, self).step(obs)
        vision = obs.observation["feature_minimap"][_VISIBILITY_MAP]
        pathable = obs.observation["feature_minimap"][9]

        enemy_y, enemy_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
        marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
        if(len(marine_y)==0):
          input('Pause')
        self.EnemyCounter(enemy_x,enemy_y,marine_x,marine_y)

        if(self.capture == True):
            self.capture = False
            #enemy_y, enemy_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
            return actions.FUNCTIONS.select_army("select")
        if (self.estado == 0):
          self.estado = 1
          #enemy_y, enemy_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_HOSTILE).nonzero()
          #marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()

          if actions.FUNCTIONS.Attack_minimap.id in obs.observation.available_actions:
            if(len(enemy_y > 0)):
              #SI HAY ENEMIGOS A LA VISTA
              self.destino = (enemy_x[0],enemy_y[0])
              return actions.FUNCTIONS.Attack_minimap("now", self.destino)
            else:
              #SI NO HAY ENEMIGOS A LA VISTA
              #if (len(self.visitedZergs)>0):
              #    self.destino = self.visitedZergs[0]
              #else:
              #Min Max
                  
              
              self.map.regenerateCenter((marine_x[0],marine_y[0]))   
              self.map.calculateMapChances(vision,pathable)
              
              self.algo.set_mapa(self.map)
              value, coor = self.algo.minimax(15, infinity*(-1), infinity, True, (marine_x[0],marine_y[0]))
              self.destino = coor
              #topleft(11,20) #bottomright(53,54)
              self.destino = (max(11+1,self.destino[0]),max(20+1,self.destino[1]))
              self.destino = (min(53-1,self.destino[0]),min(54-1,self.destino[1]))
              self.destino = (random.randint(11+5, 30+5),random.randint(53-5, 54-5)) if self.destino[0] > 50 else self.destino
              marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
              coor = self.far.density(obs.observation["feature_minimap"][_VISIBILITY_MAP],(marine_x[0],marine_y[0]),20,1000)
              self.destino = (coor[1],coor[0])
              for i in self.far.valores:
                print (i)
              print((coor[1],coor[0]))
              #input('Pause')

              #error = 0
              #Random position
              #self.destino = (random.randint(5, 59),random.randint(5, 53))
              #self.destino = (coor)
              #while(pathable[coor[1]][coor[0]] == 0):
              #  error += 1
              #  value, coor = self.algo.minimax(3, infinity*(-1), infinity, True, (marine_x[0],marine_y[0]))
              #  if (error > 10):
              #    self.destino = (random.randint(5, 59),random.randint(5, 53))

              return actions.FUNCTIONS.Attack_minimap("now", self.destino)

        if (self.estado == 1 and (self.destino[1] in range(marine_y.min()-2,marine_y.max()+2) ) and (min(self.destino[0],55) in range(marine_x.min()-2,marine_x.max()+2) )):
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
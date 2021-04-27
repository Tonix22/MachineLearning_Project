import random
import numpy as np
import os
from absl import app
from pysc2.agents import base_agent
from pysc2.lib import actions, features, units
from pysc2.env import sc2_env, run_loop
import math
from inteligencia import *
from pathlib import Path
from Enums_and_Data import *
from csvFileData import *

class Agent(base_agent.BaseAgent):
  actions = ("do_nothing",
             "harvest_minerals", 
             "build_supply_depot", 
             "build_barracks", 
             "train_marine", 
             "attack",
             "build_refinery",
             "harvest_gas",
             "build_lab",
             "train_marauder",
             "attack_marauder") #generación de tuplas de las acciones posibles para este Bot
  
  def get_my_units_by_type(self, obs, unit_type): #retorna un arreglo de las unidades solicitadas que son propias aún y cuando se encuentran en producción
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.alliance == features.PlayerRelative.SELF]
  
  def is_my_unit_tag_alive(self,obs, unit_tag): #retorna true si el tag aún existe y false en caso contrario
    tag = [unit for unit in obs.observation.raw_units
          if unit.tag == tag
          and unit.alliance == features.PlayerRelative.SELF]
    return len(tag)==1

  def get_enemy_units_by_type(self, obs, unit_type): #retorna un arreglo de las unidades solicitadas que son Enemigas aún y cuando se encuentran en producción
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.alliance == features.PlayerRelative.ENEMY]
  
  def get_my_completed_units_by_type(self, obs, unit_type): #retorna un arreglo de las unidades solicitadas que son propias completadas
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.build_progress == 100
            and unit.alliance == features.PlayerRelative.SELF]
    
  def get_enemy_completed_units_by_type(self, obs, unit_type): #retorna un arreglo de las unidades solicitadas que son Enemigas Completadas
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.build_progress == 100
            and unit.alliance == features.PlayerRelative.ENEMY]
    
  def get_distances(self, obs, units, xy):
    units_xy = [(unit.x, unit.y) for unit in units]
    return np.linalg.norm(np.array(units_xy) - np.array(xy), axis=1) #total de distancia en tre coordenadas y la coordenada de unidad

  def step(self, obs):
    super(Agent, self).step(obs)
    if obs.first(): #Si es el inicio del juego verifica en donde se encuentra el centro de comando 1 si se encuentra en arriba o 0 si esta abajo.
      command_center = self.get_my_units_by_type(
          obs, units.Terran.CommandCenter)[0]
      self.base_top_left = (command_center.x < 32)

  def do_nothing(self, obs):
    return actions.RAW_FUNCTIONS.no_op() # No hacer nada
  
  def harvest_minerals(self, obs): #La 
    scvs = self.get_my_units_by_type(obs, units.Terran.SCV)
    idle_scvs = [scv for scv in scvs if scv.order_length == 0]
    if len(idle_scvs) > 0:
      mineral_patches = [unit for unit in obs.observation.raw_units
                         if unit.unit_type in [
                           units.Neutral.BattleStationMineralField,
                           units.Neutral.BattleStationMineralField750,
                           units.Neutral.LabMineralField,
                           units.Neutral.LabMineralField750,
                           units.Neutral.MineralField,
                           units.Neutral.MineralField750,
                           units.Neutral.PurifierMineralField,
                           units.Neutral.PurifierMineralField750,
                           units.Neutral.PurifierRichMineralField,
                           units.Neutral.PurifierRichMineralField750,
                           units.Neutral.RichMineralField,
                           units.Neutral.RichMineralField750
                         ]]
      scv = random.choice(idle_scvs)
      distances = self.get_distances(obs, mineral_patches, (scv.x, scv.y))
      mineral_patch = mineral_patches[np.argmin(distances)] 
      return actions.RAW_FUNCTIONS.Harvest_Gather_unit(
          "now", scv.tag, mineral_patch.tag)
    return actions.RAW_FUNCTIONS.no_op()
  
  def harvest_gas(self,obs):
    scvs = self.get_my_units_by_type(obs, units.Terran.SCV)
    idle_scvs = [scv for scv in scvs if scv.order_length == 0]
    refiniries = self.get_my_units_by_type(obs, units.Terran.Refinery)

    if( len(idle_scvs)  > 0 and 
        len(refiniries) > 0):

      vespene_patches = [unit for unit in obs.observation.raw_units
                         if unit.unit_type in [
                           units.Terran.Refinery,
                         ]]
      scv = random.choice(idle_scvs)
      distances = self.get_distances(obs, vespene_patches, (scv.x, scv.y))
      vespene_patch = vespene_patches[np.argmin(distances)] 
      return actions.RAW_FUNCTIONS.Harvest_Gather_unit(
          "now", scv.tag, vespene_patch.tag)
    else:
      return self.train_scv(obs)
    return actions.RAW_FUNCTIONS.no_op()

  def build_supply_depot(self, obs):
    supply_depots = self.get_my_units_by_type(obs, units.Terran.SupplyDepot)
    scvs = self.get_my_units_by_type(obs, units.Terran.SCV)
    if (len(supply_depots) < 3 and obs.observation.player.minerals >= 100 and
        len(scvs) > 0):
      if(len(supply_depots) == 0):
        supply_depot_xy = (16, 26) if self.base_top_left else (40, 42)
      elif(len(supply_depots) == 1):
        supply_depot_xy = (19, 26) if self.base_top_left else (38, 42)
      elif(len(supply_depots) == 2):
        supply_depot_xy = (19, 28) if self.base_top_left else (42, 40)

      distances = self.get_distances(obs, scvs, supply_depot_xy)
      scv = scvs[np.argmin(distances)]
      return actions.RAW_FUNCTIONS.Build_SupplyDepot_pt(
          "now", scv.tag, supply_depot_xy)
    return actions.RAW_FUNCTIONS.no_op()
   
  def build_refinery(self, obs):
    vespene = [unit for unit in obs.observation.raw_units 
            if unit.unit_type == units.Neutral.VespeneGeyser]
    ##
    #closest to command center
    cmdCenter = [unit for unit in obs.observation.raw_units
            if unit.unit_type == units.Terran.CommandCenter 
            and unit.alliance == features.PlayerRelative.SELF]
    
    if(len(cmdCenter) > 0):
      #list of positions
      vespeneDist = list()
      for i in range(len(vespene)):
        d=math.sqrt(((vespene[i].x - cmdCenter[0].x)**2 + ((vespene[i].y -  cmdCenter[0].y)**2)))
        vespeneDist.append(d)
      #from list, get the index of smallest value
      minDistIndex= np.argmin(vespeneDist) #index of min value
      vespene = vespene[minDistIndex]
      ##

      #vespene = vespene[0]

      refinerys = self.get_my_units_by_type(obs, units.Terran.Refinery)
      scvs = self.get_my_units_by_type(obs, units.Terran.SCV)

      if (len(refinerys) == 0 and obs.observation.player.minerals >= 100 and
          len(scvs) > 0):
        refinery_xy = (vespene.x, vespene.y)
        distances = self.get_distances(obs, scvs, refinery_xy)
        scv = scvs[np.argmin(distances)]
        return actions.RAW_FUNCTIONS.Build_Refinery_pt(
            "now", scv.tag, vespene.tag) #vespene[29]
    return actions.RAW_FUNCTIONS.no_op()
    
  def build_barracks(self, obs):
    completed_supply_depots = self.get_my_completed_units_by_type(
        obs, units.Terran.SupplyDepot)
    barrackses = self.get_my_units_by_type(obs, units.Terran.Barracks)
    scvs = self.get_my_units_by_type(obs, units.Terran.SCV)
    if (len(completed_supply_depots) > 0 and len(barrackses) < 3 and 
        obs.observation.player.minerals >= 150 and len(scvs) > 0):
      if(len(barrackses) == 0):
        barracks_xy = (22, 21) if self.base_top_left else (35, 42)
      if(len(barrackses) == 1):
        barracks_xy = (22, 24) if self.base_top_left else (35, 45)
      if(len(barrackses) == 2):
        barracks_xy = (22, 27) if self.base_top_left else (35, 48)

      if(len(scvs) > 3):
        scv = scvs[random.randint(0, 3)]
      elif len(scvs) > 0:
        scv = scvs[len(scvs)-1]

      return actions.RAW_FUNCTIONS.Build_Barracks_pt(
          "now", scv.tag, barracks_xy)

    return actions.RAW_FUNCTIONS.no_op()

  def build_lab(self,obs):
    
    completed_supply_depots = self.get_my_completed_units_by_type(
        obs, units.Terran.SupplyDepot)
    barrackses = self.get_my_units_by_type(obs, units.Terran.Barracks)
    scvs       = self.get_my_units_by_type(obs, units.Terran.SCV)
    lab        = self.get_my_units_by_type(obs, units.Terran.BarracksTechLab)
    if (len(completed_supply_depots) > 0 and 
        len(barrackses) > 0 and
        len(lab) < 2        and 
        obs.observation.player.minerals >= 50  and 
        obs.observation.player.vespene >= 25   and
        len(scvs) > 0):
        barrack = random.choice(barrackses)
        return actions.RAW_FUNCTIONS.Build_TechLab_Barracks_quick("now",barrack.tag)
    return actions.RAW_FUNCTIONS.no_op()

  def train_scv(self,obs):

    scvs = self.get_my_units_by_type(obs, units.Terran.SCV)
    marines    = self.get_my_units_by_type(obs, units.Terran.Marine)

    if (len(scvs) <= SCVS_NUM ) :
      completed_comandCenter = self.get_my_completed_units_by_type(
          obs, units.Terran.CommandCenter)

      free_supply = (obs.observation.player.food_cap - 
                    obs.observation.player.food_used)
                    
      if (len(completed_comandCenter) > 0 and obs.observation.player.minerals >= 50
          and free_supply > 0):
        comandcenter = self.get_my_units_by_type(obs, units.Terran.CommandCenter)[0]
        if comandcenter.order_length < 2:
          return actions.RAW_FUNCTIONS.Train_SCV_quick("now", comandcenter.tag)
      return actions.RAW_FUNCTIONS.no_op()

    return actions.RAW_FUNCTIONS.no_op()

  def train_marine(self, obs):
    completed_barrackses = self.get_my_completed_units_by_type(
        obs, units.Terran.Barracks)
    free_supply = (obs.observation.player.food_cap - 
                   obs.observation.player.food_used)
    if (len(completed_barrackses) > 0 and obs.observation.player.minerals >= 100
        and free_supply > 0):
      barracks = self.get_my_units_by_type(obs, units.Terran.Barracks)[0]
      if barracks.order_length < 5:
        return actions.RAW_FUNCTIONS.Train_Marine_quick("now", barracks.tag)
    return actions.RAW_FUNCTIONS.no_op()

  def train_marauder(self, obs):
    completed_barrackses = self.get_my_completed_units_by_type(
        obs, units.Terran.Barracks)
    free_supply = (obs.observation.player.food_cap - 
                   obs.observation.player.food_used)
    if (len(completed_barrackses) > 0          and 
        obs.observation.player.minerals >= 100 and 
        obs.observation.player.vespene >=  25  and
        free_supply > 1):

      barracks = self.get_my_units_by_type(obs, units.Terran.Barracks)[0]
      if barracks.order_length < 5:
        return actions.RAW_FUNCTIONS.Train_Marauder_quick("now", barracks.tag)
    return actions.RAW_FUNCTIONS.no_op()

  def train_reaper(self, obs):
    completed_barrackses = self.get_my_completed_units_by_type(
        obs, units.Terran.Barracks)
    free_supply = (obs.observation.player.food_cap - 
                   obs.observation.player.food_used)
    if (len(completed_barrackses) > 0 and obs.observation.player.minerals >= 100
        and free_supply > 0 and obs.observation.player.vespene >=50):
      barracks = self.get_my_units_by_type(obs, units.Terran.Barracks)[0]
      if barracks.order_length < 5:
        return actions.RAW_FUNCTIONS.Train_Reaper_quick("now", barracks.tag)
    return actions.RAW_FUNCTIONS.no_op()
  
  def attack(self, obs):
    marines = self.get_my_units_by_type(obs, units.Terran.Marine)
    if len(marines) > 0:
      attack_xy = (38, 44) if self.base_top_left else (19, 23)
      distances = self.get_distances(obs, marines, attack_xy)
      marine = marines[np.argmax(distances)]
      x_offset = random.randint(-4, 4)
      y_offset = random.randint(-4, 4)
      return actions.RAW_FUNCTIONS.Attack_pt(
          "now", marine.tag, (attack_xy[0] + x_offset, attack_xy[1] + y_offset))
    return actions.RAW_FUNCTIONS.no_op()

  def attack_marauder(self, obs):
    marauder = self.get_my_units_by_type(obs, units.Terran.Marauder)

    if len(marauder) > 0:
      attack_xy = (38, 44) if self.base_top_left else (19, 23)
      distances = self.get_distances(obs, marauder, attack_xy)
      marine = marauder[np.argmax(distances)]
      x_offset = random.randint(-4, 4)
      y_offset = random.randint(-4, 4)
      return actions.RAW_FUNCTIONS.Attack_pt(
          "now", marine.tag, (attack_xy[0] + x_offset, attack_xy[1] + y_offset))

    return actions.RAW_FUNCTIONS.no_op()

class RandomAgent(Agent):
  def step(self, obs):
    super(RandomAgent, self).step(obs)
    action = random.choice(self.actions)
    return getattr(self, action)(obs)

class NNAgent(Agent):
  def __init__(self):
    super(NNAgent, self).__init__()
    self.NN_net = nnq(25,11,0.33) # 21 data in , 6 actions
    self.new_game()
                      #0,1,2,3,4,5,6,7,8,9,10,11,12
    self.scores =     [0,0,0,0,0,0,0,0,0,0,0, 0, 0]
    self.last_score = [0,0,0,0,0,0,0,0,0,0,0, 0, 0]
    self.juego  = 0
    self.promedios = []
    self.items_cordenates = []
    self.ai_reward = 0
    self.stepsnum = 0

  def reset(self):
    super(NNAgent, self).reset()
    self.new_game()
    
  def new_game(self):
    self.base_top_left = None
    self.previous_state = None
    self.previous_action = None
    self.stepsnum = 0

  def get_state(self, obs):
    scvs = self.get_my_units_by_type(obs, units.Terran.SCV) # Selección de de todos los robots utilizando la funsión por tipo
    idle_scvs = [scv for scv in scvs if scv.order_length == 0] # selección de SCV que no tiene acciones en cola osea esta en al hueva
    command_centers = self.get_my_units_by_type(obs, units.Terran.CommandCenter) # seleccionar el centro de comando
    supply_depots = self.get_my_units_by_type(obs, units.Terran.SupplyDepot) # Se seleccionan los centros de suministros aunque no esten terminados
    completed_supply_depots = self.get_my_completed_units_by_type(
        obs, units.Terran.SupplyDepot)# Se seleccionan los centros de suministros completados
    barrackses = self.get_my_units_by_type(obs, units.Terran.Barracks)# Se seleccionan las barracas aunque no esten completas
    completed_barrackses = self.get_my_completed_units_by_type(
        obs, units.Terran.Barracks)# Se seleccionan las barracas completadas
    marines = self.get_my_units_by_type(obs, units.Terran.Marine) #Total de marines con los que se cuentan
    
    marauders = self.get_my_units_by_type(obs, units.Terran.Marauder) 
    TechLabs  = self.get_my_units_by_type(obs, units.Terran.BarracksTechLab)

    queued_marines = (completed_barrackses[0].order_length 
                      if len(completed_barrackses) > 0 else 0) #Regresa el total de soldados en cola de entrenamiento.
    
    free_supply = (obs.observation.player.food_cap - 
                   obs.observation.player.food_used) # Total de comida disponible
    can_afford_supply_depot = obs.observation.player.minerals >= 100 #Valor Booleano que no dice si se puede construir un Supply depot
    can_afford_barracks = obs.observation.player.minerals >= 150 #Valor Booleano que no dice si se puede construir una Barraca
    can_afford_marine = obs.observation.player.minerals >= 100 #Valor Booleano que no dice si se puede construir un Marine
    
    enemy_scvs = self.get_enemy_units_by_type(obs, units.Terran.SCV) #Cantidad de SCV del enemigo
    enemy_idle_scvs = [scv for scv in enemy_scvs if scv.order_length == 0] #Cantidad de SCV que no estan haciendo nada
    enemy_command_centers = self.get_enemy_units_by_type(
        obs, units.Terran.CommandCenter) #Centro de comando del enemigo
    enemy_supply_depots = self.get_enemy_units_by_type(
        obs, units.Terran.SupplyDepot) #centros de suministros del enemigo aunque no esten completos
    enemy_completed_supply_depots = self.get_enemy_completed_units_by_type(
        obs, units.Terran.SupplyDepot) #centros de suministros del enemigo completos
    enemy_barrackses = self.get_enemy_units_by_type(obs, units.Terran.Barracks) #barracas de los enemigos aun que no esten termiandas
    enemy_completed_barrackses = self.get_enemy_completed_units_by_type(
        obs, units.Terran.Barracks) #barracas de los enemigos terminadas
    enemy_marines = self.get_enemy_units_by_type(obs, units.Terran.Marine) #MArines enemigos.
    enemy_marauder = self.get_enemy_units_by_type(obs, units.Terran.Marauder) #MArines enemigos.
    enemy_TechLab = self.get_enemy_units_by_type(obs, units.Terran.BarracksTechLab)
    # cordenas x,  }{} y
   
    #data, normalized
    return (len(command_centers)/COMANDCENTERS, #0
            len(scvs)/SCVS_NUM,  #1
            len(idle_scvs)/SCVS_NUM, #2
            len(supply_depots)/3, #3
            len(completed_supply_depots)/3, #4
            len(barrackses)/3, #5
            len(completed_barrackses)/3, #6
            len(marines)/MARINES_NUM, #7
            queued_marines/MARINES_NUM, #8
            free_supply/SUPPLY, #9
            can_afford_supply_depot, #10
            can_afford_barracks, #11
            can_afford_marine, #12
            len(enemy_command_centers)/COMANDCENTERS, #13
            len(enemy_scvs)/SCVS_NUM, #14
            len(enemy_idle_scvs)/SCVS_NUM, #15
            len(enemy_supply_depots)/BUILDINGS, #16
            len(enemy_completed_supply_depots)/BUILDINGS, #17
            len(enemy_barrackses)/BUILDINGS, #18
            len(enemy_completed_barrackses)/BUILDINGS, #19
            len(enemy_marines)/MARINES_NUM,
            len(enemy_marauder)/20,
            len(enemy_TechLab)/10,
            len(marauders)/10,
            len(TechLabs)/3) #Se regresan todos nuestros valores necesarios. #20

  def update_reward(self,prev_obs, current_obs):

    #NEGATIVE REWARD
    if  current_obs[ITEM.MARINES_LEN] < prev_obs[ITEM.MARINES_LEN] :
      self.ai_reward-=1
    if current_obs[ITEM.SCVS_LEN] < prev_obs[ITEM.SCVS_LEN] :
      self.ai_reward-=4
    if current_obs[ITEM.ENEMY_MARINES_LEN] > prev_obs[ITEM.ENEMY_MARINES_LEN]:
      self.ai_reward-=1
    if current_obs[ITEM.BARRACKSES_LEN] < prev_obs[ITEM.BARRACKSES_LEN]:
      self.ai_reward-=1
    if current_obs[ITEM.ENEMY_COMPLETED_SUPPLY_DEPOTS_LEN] > prev_obs[ITEM.ENEMY_COMPLETED_SUPPLY_DEPOTS_LEN]:
      self.ai_reward-=3
    if current_obs[ITEM.IDLE_SCVS_LEN] > prev_obs[ITEM.IDLE_SCVS_LEN]:
      self.ai_reward-=1
    if current_obs[ITEM.ENEMY_BARRACKSES_LEN] > prev_obs[ITEM.ENEMY_BARRACKSES_LEN]  :
      self.ai_reward-=1
    if current_obs[ITEM.ENEMY_MARAUDER] > prev_obs[ITEM.ENEMY_MARAUDER]  :
      self.ai_reward-=5
    if current_obs[ITEM.ENEMY_TECHLAB] > prev_obs[ITEM.ENEMY_TECHLAB]  :
      self.ai_reward-=5

    #POSITIVE REWARDS
    
    if current_obs[ITEM.CAN_AFFORD_MARINE] or current_obs[ITEM.QUEUED_MARINES]:
      self.ai_reward+=1
    if current_obs[ITEM.SUPPLY_DEPOTS_LEN] > prev_obs[ITEM.SUPPLY_DEPOTS_LEN]:
      self.ai_reward+=1
    if current_obs[ITEM.BARRACKSES_LEN] > prev_obs[ITEM.BARRACKSES_LEN]:
      self.ai_reward+=1
    if current_obs[ITEM.MARINES_LEN] > prev_obs[ITEM.MARINES_LEN]:
      self.ai_reward+=1
    if current_obs[ITEM.ENEMY_MARINES_LEN] <  prev_obs[ITEM.ENEMY_MARINES_LEN] :
      self.ai_reward+=1
    if current_obs[ITEM.ENEMY_BARRACKSES_LEN] < prev_obs[ITEM.ENEMY_BARRACKSES_LEN]  :
      self.ai_reward+=1
    if current_obs[ITEM.ENEMY_SCVS_LEN] < prev_obs[ITEM.ENEMY_SCVS_LEN]:
      self.ai_reward+=1
    if current_obs[ITEM.MARAUDERS] < prev_obs[ITEM.MARAUDERS]:
      self.ai_reward+=5
    if current_obs[ITEM.TECHLABS] < prev_obs[ITEM.TECHLABS]:
      self.ai_reward+=5

  def step(self, obs):
    super(NNAgent, self).step(obs)

    self.stepsnum +=1
    self.ai_reward = 0 #ai reward
    state  = self.get_state(obs)
    action = self.NN_net.choose_action(state)
    if self.previous_action is not None:
      self.update_reward(self.previous_state,state)
      self.ai_reward+=obs.reward
      self.NN_net.learn(self.previous_state,
                        self.previous_action,
                        self.ai_reward,
                        state)
    self.previous_state  = state
    self.previous_action = action
    
    if obs.last():
      for i in range (13):
        self.scores[i] = obs.observation['score_cumulative'][i]
      
      CSVFileData(self.episodes,obs.reward,self.scores,self.stepsnum,stepmultiplier)

      print("current score: "+ str(self.scores))

      if self.episodes % 100 == 0 and self.episodes !=0:
        T.save(self.NN_net.Q.state_dict(), f"modelo{self.episodes//100}.pth")

    return getattr(self, self.actions[action])(obs)


class PacifistaAgent(Agent):
  def step(self, obs):
    super(PacifistaAgent, self).step(obs)
    return actions.FUNCTIONS.no_op()

stepmultiplier=20
def main(unused_argv):
  
  agent1 = NNAgent()
  
  agent1.episodes = 0 # donde se quedo el ultimo training
  #load trained
  if(agent1.episodes>0):
    numModel = agent1.episodes//100
    model = agent1.NN_net.Q
    path = str(Path().absolute())+"/Minigames/FinalAgent/modelo"+str(numModel)+".pth"
    model.load_state_dict(T.load("modelo"+str(numModel)+".pth"))#if not fails 
    #model.load_state_dict(path)
    model.eval()

  #agent2 = RandomAgent()
  agent2 = PacifistaAgent()
  try:
    with sc2_env.SC2Env(
        map_name="Simple64",
        players=[sc2_env.Agent(sc2_env.Race.terran), 
                 sc2_env.Bot(sc2_env.Race.terran,sc2_env.Difficulty.easy)],
                 #sc2_env.Agent(sc2_env.Race.terran)],
        agent_interface_format=features.AgentInterfaceFormat(
            action_space=actions.ActionSpace.RAW,
            feature_dimensions=features.Dimensions(screen=84, minimap=64),#terraing visibility
            use_raw_units=True,
            raw_resolution=64,
        ),
        step_mul=stepmultiplier,
        disable_fog=False,
        visualize=True,
    ) as env:
      run_loop.run_loop([agent1, agent2], env, max_episodes=10000)
  except KeyboardInterrupt:
    pass
  

if __name__ == "__main__":
  app.run(main)
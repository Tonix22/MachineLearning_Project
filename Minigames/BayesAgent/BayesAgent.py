
from pysc2.agents import base_agent
from pysc2.env import sc2_env
from pysc2.env.sc2_env import SC2Env, AgentInterfaceFormat, Bot, Agent
from pysc2.env.sc2_env import Race, Difficulty, Dimensions
from pysc2.lib import actions, features, units
from pysc2.lib import point
import random
from absl import app
import time
import math
from statistics import mean 
from params import *
import numpy as np
from enum import Enum
from enum import IntEnum
from statistics import mean 
from test import *
from Explorer import *

_PLAYER_RELATIVE = features.SCREEN_FEATURES.player_relative.index
_PLAYER_HOSTILE = 4
_PLAYER_SELF    = features.PlayerRelative.SELF
_PLAYER_NEUTRAL = features.PlayerRelative.NEUTRAL
_VISIBILITY_MAP = features.SCREEN_FEATURES.visibility_map.index

class state(Enum):
    IDLE               = 0
    FTS                = 1 #First Time Setup
    WAIT_MINERALS      = 2
    BUILD_SUPPLY_DEPOT = 3
    BUILD_BARRACA      = 4
    BUILD_VESPENE      = 5
    BUILD_MARINE       = 6
    BUILD_EXPLORADOR   = 7
    WAIT_BUILD         = 8
    SELECT_EXPLORER    = 9
    EXPLORE            = 10

class Observed(IntEnum):
  COMMAND_CENTERS = 0
  SCVS = 1
  IDLE_SCVS = 2
  SUPPLY_DEPOTS = 3
  COMPLETED_SUPPLY_DEPOTS = 4
  BARRACKSES = 5
  COMPLETED_BARRACKSES = 6
  MARINES = 7
  QUEUED_MARINES = 8
  FREE_SUPPLY = 9
  CAN_AFFORD_SUPPLY_DEPOT = 10
  CAN_AFFORD_BARRACKS     = 11
  CAN_AFFORD_MARINE = 12
  REAPER = 13
  REFINERIES = 14
  COMPLETED_REFINERIES = 15
  CAN_AFFORD_REAPER = 16

def _xy_locs(mask):
  """Mask should be a set of bools from comparison with a feature layer."""
  y, x = mask.nonzero()
  return list(zip(x, y))


class BayesAgent(Agent):

    def __init__(self):
        super(BayesAgent, self).__init__()
        self.capture = True
        self.state = state.FTS #First Time Setup
        self.supply_location = (50,50)
        self.barraca_location = (70,50)
        self.left_to_right = False
        self.bayes = Explorer()
        self.comancenter_enemy = 0
        self.explorer_tag = 0
        self.one_refinery = False

    def get_state(self, obs):
        scvs = self.get_my_units_by_type(obs, units.Terran.SCV) # Selección de de todos los robots utilizando la funsión por tipo
        idle_scvs = [scv for scv in scvs if scv.order_length == 0] # selección de SCV que no tiene acciones en cola osea esta en al hueva
        command_centers = self.get_my_units_by_type(obs, units.Terran.CommandCenter) # seleccionar el centro de comando
        supply_depots = self.get_my_units_by_type(obs, units.Terran.SupplyDepot) # Se seleccionan los centros de suministros aunque no esten terminados
        refineries = self.get_my_units_by_type(obs, units.Terran.Refinery)
        completed_refineries = self.get_my_completed_units_by_type(
            obs, units.Terran.Refinery)
        
        completed_supply_depots = self.get_my_completed_units_by_type(
            obs, units.Terran.SupplyDepot)# Se seleccionan los centros de suministros completados
        barrackses = self.get_my_units_by_type(obs, units.Terran.Barracks)# Se seleccionan las barracas aunque no esten completas
        completed_barrackses = self.get_my_completed_units_by_type(
            obs, units.Terran.Barracks)# Se seleccionan las barracas completadas
        marines = self.get_my_units_by_type(obs, units.Terran.Marine) #Total de marines con los que se cuentan
        
        queued_marines = (completed_barrackses[0].order_length 
                          if len(completed_barrackses) > 0 else 0) #Regresa el total de soldados en cola de entrenamiento.
        
        free_supply = (obs.observation.player.food_cap - 
                      obs.observation.player.food_used) # Total de comida disponible
        can_afford_supply_depot = obs.observation.player.minerals >= 100 #Valor Booleano que no dice si se puede construir un Supply depot
        can_afford_barracks = obs.observation.player.minerals >= 150 #Valor Booleano que no dice si se puede construir una Barraca
        can_afford_marine = obs.observation.player.minerals >= 100#Valor Booleano que no dice si se puede construir un Marine
        can_afford_reaper = obs.observation.player.minerals >= 100 and obs.observation.player.vespene >= 50
        reapers = self.get_my_completed_units_by_type(
            obs, units.Terran.Reaper)

        return (len(command_centers),
                len(scvs),
                len(idle_scvs),
                len(supply_depots),
                len(completed_supply_depots),
                len(barrackses),
                len(completed_barrackses),
                len(marines),
                queued_marines,
                free_supply,
                can_afford_supply_depot,
                can_afford_barracks,
                can_afford_marine,
                len(reapers),
                len(refineries),
                len(completed_refineries),
                can_afford_reaper) #Se regresan todos nuestros valores necesarios.

    def scv_avg(self,obs):
        scv_y, scv_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
        scv_y = scv_y.mean()
        scv_x = scv_x.mean()
        return (scv_y,scv_x)

    def select_first_SCV(self,obs):
          scv_y, scv_x = self.scv_avg(obs)
          lim_y, lim_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
          lim_y, lim_x = (min(lim_y)+20,min(lim_x)+20)
          #select rectangle from upper left corner to middle
          return actions.FUNCTIONS.select_rect(
          "select",
          (lim_x,lim_y), 
          (scv_x,   scv_y))

    def Select_side(self,obs):# Elige de que lado va poner los supply y barracas
        cmd_center = [unit for unit in obs.observation.feature_units 
                      if unit.unit_type == units.Terran.CommandCenter]



        minerals   = [unit for unit in obs.observation.feature_units 
                      if unit.unit_type == units.Neutral.MineralField or
                      unit.unit_type == units.Neutral.MineralField450 or
                      unit.unit_type == units.Neutral.MineralField750]

        avg_minerals_x = 0
        for m in minerals:
          avg_minerals_x+=m.x

        avg_minerals_x/=len(minerals)

        cmd_center = cmd_center[0] # para evitar hacer esto -> cmd_center[0].x, quitar basicamente el [0]

        orientation_x = cmd_center.x - avg_minerals_x
        
        self.left_to_right = (orientation_x > 0)

        if(self.left_to_right == True):
          #self.supply_location = (cmd_center.x,cmd_center.y) # Assignar una cordenada al supply depot
          self.supply_location = (65,40)
          self.barraca_location = (70,50)
        else: #right_to_left
          self.supply_location = (15,30)
          self.barraca_location = (15,15)
         # self.supply_location = (cmd_center.x-10,cmd_center.y-10) # Assignar una cordenada al supply depot


    def step(self, obs):
        super(BayesAgent, self).step(obs)
        estado = self.get_state(obs)

        #estado[int(Observed.CAN_AFFORD_SUPPLY_DEPOT)]
        #estado[int(Observed.COMPLETED_BARRACKSES)]

        if(self.state == state.FTS): # Select an SCV
          if (estado[Observed.CAN_AFFORD_SUPPLY_DEPOT] and 
              estado[Observed.SUPPLY_DEPOTS] == 0):
            return self.build_supply_depot(obs)

          if (estado[Observed.IDLE_SCVS]):
            self.state = state.BUILD_VESPENE
            return actions.FUNCTIONS.no_op()
        
        elif(self.state == state.BUILD_VESPENE):# Polling
          
          if (estado[Observed.REFINERIES] == 0 and 
              self.one_refinery == False):
            
            self.one_refinery = True
            return self.build_refinery(obs)
            
          if (estado[Observed.REFINERIES]>=1):
            self.state = state.BUILD_BARRACA
            return actions.FUNCTIONS.no_op()

        elif(self.state == state.BUILD_BARRACA):# Polling
          if (estado[Observed.BARRACKSES]==0 and 
              estado[Observed.COMPLETED_SUPPLY_DEPOTS] >=1):
            self.state = state.BUILD_EXPLORADOR
            return self.build_barracks(obs)
          
        elif(self.state == state.BUILD_EXPLORADOR):
          if (estado[Observed.IDLE_SCVS] >= 1):
            return self.harvest_minerals(obs)
        
          if(estado[Observed.COMPLETED_BARRACKSES] >= 1 and 
             estado[Observed.CAN_AFFORD_REAPER]):
            self.state = state.EXPLORE
            return self.train_reaper(obs)
        
        elif(self.state == state.SELECT_EXPLORER):
            if(estado[Observed.REAPER] == 1):
              reaper = self.get_my_completed_units_by_type(obs, units.Terran.Reaper)
              #marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
              reaper = reaper[0]
              self.explorer_tag = reaper.tag
              self.state = state.EXPLORE

          
        elif(self.state == state.EXPLORE):
          
          if(estado[Observed.REAPER] == 1):


            marine = self.get_my_completed_units_by_type(obs, units.Terran.Reaper)
            #marine_y, marine_x = (obs.observation["feature_minimap"][_PLAYER_RELATIVE] == _PLAYER_SELF).nonzero()
            marine = marine[0]
            
            destino = (marine.x,marine.y)

            if(marine.order_length == 0):
              vision   = obs.observation["feature_minimap"][_VISIBILITY_MAP]
              pathable = obs.observation["feature_minimap"][9]
              possibleDirections = self.bayes.returnBeliefDestination((marine.x,marine.y),vision,pathable) 
              
              if(possibleDirections == Directions.Right):
                destino = (marine.x+10, marine.y) 

              elif(possibleDirections == Directions.Left):
                destino = (marine.x-10, marine.y) 

              elif(possibleDirections == Directions.Down):
                destino = (marine.x, marine.y-10) 

              elif(possibleDirections == Directions.Up):
                destino = (marine.x, marine.y+10)                 

            return actions.RAW_FUNCTIONS.Attack_pt(
            "now", marine.tag, destino)
          
        return actions.FUNCTIONS.no_op()

class PacifistaAgent(Agent):
  def step(self, obs):
    super(PacifistaAgent, self).step(obs)
    return actions.FUNCTIONS.no_op()

def main(unused_argv):
  agent1 = BayesAgent()
  agent2 = PacifistaAgent()
  try:
    with sc2_env.SC2Env(
        map_name="Simple64",
        players=[sc2_env.Agent(sc2_env.Race.terran), 
                 sc2_env.Agent(sc2_env.Race.terran)],
        agent_interface_format=features.AgentInterfaceFormat(
            action_space=actions.ActionSpace.RAW,
            use_raw_units=True,
            raw_resolution=64,
            feature_dimensions=features.Dimensions(screen=84, minimap=64),
            use_feature_units=True
        ),
        step_mul=10,
        disable_fog=False,
        visualize=True #visualize: Whether to pop up a window showing the camera and feature layers. This won't work without access to a window manager.
    ) as env:
  
      #agent1.setup(env.observation_spec(), env.action_spec())
      run_loop.run_loop([agent1, agent2], env, max_episodes=1000)
  
  except KeyboardInterrupt:
    pass


if __name__ == "__main__":
  app.run(main)

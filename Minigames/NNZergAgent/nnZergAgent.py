import random
import numpy as np
import pandas as pd
import os
from absl import app
from pysc2.agents import base_agent
from pysc2.lib import actions, features, units
from pysc2.env import sc2_env, run_loop
from inteligencia import *
from collections import deque
import enum

class phase(enum.Enum):
    IDLE     = 0
    NN_QUERY = 1
    REPORT_TO_MARINES = 2
    REPORT_COMPLETE   = 3



class Agent(base_agent.BaseAgent):
  actions = ("atacar_zerglings",
             "atacar_banelings", 
             "correr_maricamente")
  
  def get_my_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.alliance == features.PlayerRelative.SELF]
  
  def get_enemy_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.alliance == features.PlayerRelative.ENEMY]
  
  def get_my_completed_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.build_progress == 100
            and unit.alliance == features.PlayerRelative.SELF]
    
  def get_enemy_completed_units_by_type(self, obs, unit_type):
    return [unit for unit in obs.observation.raw_units
            if unit.unit_type == unit_type 
            and unit.build_progress == 100
            and unit.alliance == features.PlayerRelative.ENEMY]
    
  def get_distances(self, obs, units, xy):
    units_xy = [(unit.x, unit.y) for unit in units]
    return np.linalg.norm(np.array(units_xy) - np.array(xy), axis=1)

  def step(self, obs):
    super(Agent, self).step(obs)
    

  def do_nothing(self, obs):
    return actions.RAW_FUNCTIONS.no_op()
  
  #Function.raw_ability(3, "Attack_unit", raw_cmd_unit, 3674), attack_pt 
  def attack(self, obs,atacante, victima):
    return actions.RAW_FUNCTIONS.Attack_unit("now", atacante, victima )


class SmartAgent(Agent):
  def __init__(self):
    self.nnq = nnq(input_dims=6, n_actions=2, lr=0.5)
    self.victima = 0 #ID del objetivo
    self.marines = [] #Lista de marines activos
    self.zerlings = [] #Lista de Zerglings Vivos
    self.banelings = [] #Lista de bannelings
    self.previous_state = None
    self.previous_action = None
    self.new_game()
    self.phase = phase.IDLE
    self.marine_idx = 0
    self.marine_tmp_list = []
    self.juego = 0
    self.ganados=0
    self.perdidos=0
    self.previous_reward=0
    self.scores=0
    self.promedios = []
    self.paso = 1
    self.actual = 1


    #dentro las tropas [2] hp y [29] ID

    super(SmartAgent, self).__init__()
    self.new_game()

  def reset(self):
    super(SmartAgent, self).reset()
    self.new_game()
    
  def new_game(self):
    self.previous_state = None
    self.previous_action = None
    self.victima = 0
    self.previous_reward=0

  def get_ID_lowestHp(self, arrayCharacters):
    #revisa quien tiene el menor hp y regresa su id
    id_lowest  = None
    hp_lowest  = 1000000
    for character in arrayCharacters:
      if(character[2]<hp_lowest):
        hp_lowest = character[2]
        id_lowest = character[29]
    return id_lowest
    
  def rewardHpCheck(self, state):
    #suma de hp de ese tipo de personaje
    #1 marines, 3 zerlings, 5 banelings
    myHp              = self.previous_state[1]-state[1] # la sangre
    averageHpEnemies  = ((self.previous_state[3]-state[3])+(self.previous_state[5]-state[5]))/2 # 
    if myHp<averageHpEnemies:
      return 1
    elif myHp==averageHpEnemies:
      return 0
    else:
      return -1
   
  def dispatch(self,enemy):
    if not hasattr(queue,"queue"):
        q = deque()
    
    id_lowest = enemy[29] #ID
    # Si ya se murio
    if (id_lowest != None):
      q.append(id_lowest)

  
    # decidir
    # pasar la cola de ataque 
  def isAlive(self, obs, id):
    marines = self.get_my_units_by_type(obs, units.Terran.Marine)
    for m in marines:
      if m[29]==id:
        return 1
    zergs = self.get_enemy_units_by_type(obs, units.Zerg.Zergling)
    for z in zergs:
      if z[29]==id:
        return 1
    bane = self.get_enemy_units_by_type(obs, units.Zerg.Baneling)
    for b in bane:
      if b[29]==id:
        return 1
    return 0
  def get_state(self, obs):
    
    self.marines = self.get_my_units_by_type(obs, units.Terran.Marine)
    self.zergling = self.get_enemy_units_by_type(obs, units.Zerg.Zergling)
    self.baneling = self.get_enemy_units_by_type(obs, units.Zerg.Baneling)
    marines_hp=0
    for m in self.marines:
      marines_hp += m[2]
    zergling_hp=0
    for z in self.zergling:
      zergling_hp += z[2]
    baneling_hp=0
    for b in self.baneling:
      baneling_hp += b[2]

    return ([len (self.marines),
             marines_hp,
             len (self.zergling),
             zergling_hp,
             len (self.baneling),
             baneling_hp])

  def step(self, obs):
    super(SmartAgent, self).step(obs)
    if obs.first():
      self.new_game() # limpiamos variables
    state = self.get_state(obs)
    if obs.last():
      self.scores += self.reward
      self.reward = 0
      if self.episodes % 100 == 0 and self.episodes !=0:
        self.promedios.append(self.scores/100)
        self.scores = 0
        if(self.paso < 20):
          self.paso += 1
        print(self.promedios)
        T.save(self.nnq.Q.state_dict(), f"modelo{self.episodes//100}.pth")

      self.juego += 1
    else : #estado
      if (self.victima == 0 or self.isAlive(obs,self.victima)==0 ):
        if   self.victima != 0 and self.previous_state[0] >= self.get_state(obs)[0]:
          #como venimos de tomar una acción necesitamos aprender
          #print ("aprendi")
          self.nnq.learn(self.previous_state,self.previous_action,self.rewardHpCheck(self.get_state(obs)),self.get_state(obs))
        
        #nos preparamos para la nueva toma de  desición
        self.previous_reward = self.reward
        self.previous_state = state
        self.previous_action = self.nnq.choose_action(self.get_state(obs))
        #si la accion es 0 se selecciona un zergling si es 1 se selecciona un baneling
        if (self.previous_action == 0):
          self.victima = self.get_ID_lowestHp(self.get_enemy_units_by_type(obs, units.Zerg.Zergling))
        elif(self.previous_action == 1):
          self.victima = self.get_ID_lowestHp(self.get_enemy_units_by_type(obs, units.Zerg.Baneling))
        self.phase   = phase.REPORT_TO_MARINES
        self.marine_tmp_list.clear()
        self.marine_idx = 0
        for m in self.get_my_units_by_type(obs, units.Terran.Marine):
          self.marine_tmp_list.append(m[29])


      if self.phase == phase.REPORT_TO_MARINES:
        if(len(self.marine_tmp_list)>self.marine_idx):
          if(self.actual == self.paso):
            self.marine_idx += 1
            self.actual = 1
            if (self.isAlive(obs,self.marine_tmp_list[self.marine_idx-1])==1 and self.isAlive(obs,self.victima)==1):
              return self.attack(obs,self.marine_tmp_list[self.marine_idx-1],self.victima)
          else:
            self.actual += 1
        else:
          self.phase = phase.REPORT_COMPLETE
    
    return actions.RAW_FUNCTIONS.no_op()


def main(unused_argv):
  agent1 = SmartAgent() 
  try:
    with sc2_env.SC2Env(
        map_name="DefeatZerglingsAndBanelings",
        players=[sc2_env.Agent(sc2_env.Race.terran)],
        agent_interface_format=features.AgentInterfaceFormat(
            action_space=actions.ActionSpace.RAW,
            use_raw_units=True,
            raw_resolution=64,
        ),
        step_mul=1,
        disable_fog=False,
    ) as env:
      run_loop.run_loop([agent1], env, max_episodes=1000)
  except KeyboardInterrupt:
    pass


if __name__ == "__main__":
  app.run(main)
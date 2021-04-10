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
    self.nnq = nnq(input_dims=6, n_actions=2, lr=0.2)
    self.victima = 0 #ID del objetivo
    self.marines = [] #Lista de marines activos
    self.zerlings = [] #Lista de Zerglings Vivos
    self.banelings = [] #Lista de bannelings
    self.previous_state = None
    self.previous_action = None
    self.new_game()

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
    elif myHP==averageHpEnemies:
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
  
  def get_state(self, obs):
    
    marines = self.get_my_units_by_type(obs, units.Terran.Marine)
    zergling = self.get_enemy_units_by_type(obs, units.Zerg.Zergling)
    baneling = self.get_enemy_units_by_type(obs, units.Zerg.Baneling)
    marines_hp=0
    for m in marines:
      marines_hp += m[2]
    zergling_hp=0
    for z in zergling:
      zergling_hp += z[2]
    baneling_hp=0
    for b in baneling:
      baneling_hp += b[2]

    
    """return ({"marines": marines,
             "total_marines" : len (marines),
             "total_hp_marines" : marines_hp,
             "zerglings": zergling,
             "total_zerglings" : len (zergling),
             "total_hp_zerglings" : zergling_hp,
             "banelings": baneling,
             "total_banelings" : len (baneling),
             "total_hp_banelings" : baneling_hp})"""

    return ([len (marines)/9,
             marines_hp/405,
             len (zergling)/6,
             zergling_hp/210,
             len (baneling)/4,
             baneling_hp/120])

  def step(self, obs):
    super(SmartAgent, self).step(obs)
    if obs.first():
      self.new_game()
      
      
    state = self.get_state(obs)
    print (state)
    #obs.reward
    #'terminal' if obs.last() else state #
    #return getattr(self, action)(obs)
    return actions.RAW_FUNCTIONS.no_op()


def main(unused_argv):
  agent1 = SmartAgent()
  juego = 0
  scores = []
  eps_history = []
  
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
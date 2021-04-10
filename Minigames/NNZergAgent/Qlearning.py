import random
import numpy as np
import pandas as pd
import os
from absl import app
from pysc2.agents import base_agent
from pysc2.lib import actions, features, units
from pysc2.env import sc2_env, run_loop

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

class SmartAgent(Agent):
  def __init__(self):
    super(SmartAgent, self).__init__()
    self.new_game()

  def reset(self):
    super(SmartAgent, self).reset()
    self.new_game()
    
  def new_game(self):
    self.previous_state = None
    self.previous_action = None

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

    
    return ({"marines": marines,
             "total_marines" : len (marines),
             "total_hp_marines" : marines_hp,
             "zerglings": zergling,
             "total_zerglings" : len (zergling),
             "total_hp_zerglings" : zergling_hp,
             "banelings": baneling,
             "total_banelings" : len (baneling),
             "total_hp_banelings" : baneling_hp})

  def step(self, obs):
    super(SmartAgent, self).step(obs)
    state = self.get_state(obs)
    print (state)
    
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
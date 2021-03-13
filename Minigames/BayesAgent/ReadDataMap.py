"""
class ScoreCumulative(enum.IntEnum):
  #Indices into the `score_cumulative` observation.
  score = 0
  idle_production_time = 1
  idle_worker_time = 2
  total_value_units = 3
  total_value_structures = 4
  killed_value_units = 5
  killed_value_structures = 6
  collected_minerals = 7
  collected_vespene = 8
  collection_rate_minerals = 9
  collection_rate_vespene = 10
  spent_minerals = 11
  spent_vespene = 12


class ScoreByCategory(enum.IntEnum):
  #Indices for the `score_by_category` observation's first dimension.
  food_used = 0
  killed_minerals = 1
  killed_vespene = 2
  lost_minerals = 3
  lost_vespene = 4
  friendly_fire_minerals = 5
  friendly_fire_vespene = 6
  used_minerals = 7
  used_vespene = 8
  total_used_minerals = 9
  total_used_vespene = 10

  class ScoreCategories(enum.IntEnum):
  #Indices for the `score_by_category` observation's second dimension.
  none = 0
  army = 1
  economy = 2
  technology = 3
  upgrade = 4


class ScoreByVital(enum.IntEnum):
  #Indices for the `score_by_vital` observation's first dimension.
  total_damage_dealt = 0
  total_damage_taken = 1
  total_healed = 2


class ScoreVitals(enum.IntEnum):
  #Indices for the `score_by_vital` observation's second dimension.
  life = 0
  shields = 1
  energy = 2


class Player(enum.IntEnum):
  #Indices into the `player` observation.
  player_id = 0
  minerals = 1
  vespene = 2
  food_used = 3
  food_cap = 4
  food_army = 5
  food_workers = 6
  idle_worker_count = 7
  army_count = 8
  warp_gate_count = 9
  larva_count = 10
"""
"""
#Informacion cumulativa
_COLLECTED_MINERALS = features.ScoreCumulative.collected_minerals 
minerals = obs.observation["score_cumulative"][_COLLECTED_MINERALS]
minerals = obs.observation["score_cumulative"][7]

#RECURSOS UTILIZADOS EN DIFERENTES CATEGORIAS
_FOOD_USED = features.ScoreByCategory.food_used
_CATEGORY_ARMY = features.ScoreCategories.army
foodUsed = obs.observation["score_by_category"][_FOOD_USED][_CATEGORY_ARMY]

#Minerales y comida
minerals = obs.observation["player"][1]
foodUsed = obs.observation["player"][3] 
foodCap = obs.observation["player"][4]
foodAvailable = foodCap-foodUsed
"""

import pandas as pd
import numpy as np

actions = ("do_nothing",
             "harvest_minerals", 
             "build_supply_depot", 
             "build_barracks", 
             "train_marine", 
             "attack")
q_table = pd.DataFrame(columns=actions, dtype=np.float64)
#print(q_table)

state=(1, 12, 0, 1, 1, 1, 1, 1, 4, 9, True, True, True, 1, 12, 12, 1, 1, 1, 1, 3)
q_table = q_table.append(pd.Series([0] * len(actions), index=q_table.columns, name=str(state)))
q_table.loc[str(state), actions[2]] += 0.5
print(q_table)
state_action=q_table.loc[str(state), :]
#print( state_action[state_action == np.max(state_action)].index)

action = np.random.choice(
          state_action[state_action == np.max(state_action)].index)
#print(action)
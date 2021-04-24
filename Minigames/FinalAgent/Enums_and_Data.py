from enum import IntEnum

COMANDCENTERS = 5
SCVS_NUM    = 50
BUILDINGS   = 10 
MARINES_NUM = 100 
SUPPLY      = 200

Quantity   = 0
Cordenates = 1

class ITEM(IntEnum):
  COMMAND_CENTERS_LEN = 0, #0
  SCVS_LEN            = 1, #1
  IDLE_SCVS_LEN       = 2, #2
  SUPPLY_DEPOTS_LEN   = 3, #3
  COMPLETED_SUPPLY_DEPOTS_LEN = 4, #4
  BARRACKSES_LEN              = 5, #5
  COMPLETED_BARRACKSES_LEN    = 6, #6
  MARINES_LEN                 = 7, #7
  QUEUED_MARINES              = 8, #8
  FREE_SUPPLY                 = 9, #9
  CAN_AFFORD_SUPPLY_DEPOT     = 10, #10
  CAN_AFFORD_BARRACKS         = 11, #11
  CAN_AFFORD_MARINE           = 12, #12
  ENEMY_COMMAND_CENTERS_LEN   = 13, #13
  ENEMY_SCVS_LEN              = 14, #14
  ENEMY_IDLE_SCVS_LEN         = 15, #15
  ENEMY_SUPPLY_DEPOTS_LEN     = 16, #16
  ENEMY_COMPLETED_SUPPLY_DEPOTS_LEN = 17, #17
  ENEMY_BARRACKSES_LEN              = 18, #18
  ENEMY_COMPLETED_BARRACKSES_LEN    = 19, #19
  ENEMY_MARINES_LEN                 = 20 #20
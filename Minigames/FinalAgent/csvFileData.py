import numpy as np
import pandas as pd
from datetime import datetime
import os 

def CSVFileData(ep,r,s):
  now = datetime.now()
  dt_string = now.strftime("%d_%m_%Y %Hh%Mmin%Sseg")
  ruta = os.path.join(os.path.dirname(__file__),'Saved_v00.csv')
  
  data = {'time'     : [dt_string],
            'episode': [ep],
            'winLose': [r],
            'score'  : [s[0]],
            'idle_production_time':[s[1]],
            'idle_worker_time'    : [s[2]],
            'total_value_units'   : [s[3]],
            'total_value_structures'  : [s[4]],
            'killed_value_units'      : [s[5]],
            'killed_value_structures' : [s[6]],
            'collected_minerals' : [s[7]],
            'collected_vespene'  : [s[8]],
            'collection_rate_minerals' : [s[9]],
            'collection_rate_vespene'  : [s[10]],
            'spent_minerals' : [s[11]],
            'spent_vespene'  : [s[12]]}


            
  df = pd.DataFrame(data)
  if(os.path.exists(ruta)==False):
    df.to_csv(ruta,index=False)
    print("Archivo creado")
  else:
    #df = pd.read_csv(ruta)
    df.to_csv(ruta, mode='a', index=False , header=False)
    print("Añadido")

#CSVFileData(5,0,1500)
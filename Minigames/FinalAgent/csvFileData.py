import numpy as np
import pandas as pd
from datetime import datetime
import os 

def CSVFileData(ep,r,s):
  now = datetime.now()
  dt_string = now.strftime("%d_%m_%Y %Hh%Mmin%Sseg")
  ruta = os.path.join(os.path.dirname(__file__),'Saved_v00.csv')
  
  data = {'time': [dt_string],
            'episode': [ep],
            'winLose': [r],
            'score': [s]}
  df = pd.DataFrame(data)
  if(os.path.exists(ruta)==False):
    df.to_csv(ruta,index=False)
    print("Archivo creado")
  else:
    #df = pd.read_csv(ruta)
    df.to_csv(ruta, mode='a', index=False , header=False)
    print("Añadido")

#CSVFileData(5,0,1500)
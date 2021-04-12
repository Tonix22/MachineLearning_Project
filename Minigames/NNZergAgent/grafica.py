import os
import math
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

array0_2 = [22.16, 23.37, 26.39, 37.58, 43.31, 56.02, 62.69, 71.96, 77.15, 80.69]

def CreateGraph(results, lr):
    thispath = os.path.abspath(os.path.dirname(__file__))
    #x = range(0, len(results))
    x = np.arange(start=0, stop=len(results)*100, step=100)
    fig, ax = plt.subplots()
    ax.set(xlabel='# episodes', ylabel='Average score', title='Training set lr = '+str(lr))
    ax.plot(x, results)
    #fig.savefig('test.png')
    fig.savefig(os.path.join(thispath, "TrainingSet"+str(lr)+".png"))
    plt.show()
    

    
CreateGraph(array0_2,0.2)
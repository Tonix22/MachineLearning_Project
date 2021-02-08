import random
import math
import numpy as np
from scipy.ndimage.interpolation import rotate
from mpl_toolkits import mplot3d 
import matplotlib.pyplot as plt 

from params import *

class annealing:

    def __init__(self,Initial_temp,alpha):
            #0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
        self.height = MAP.map
   
        self.current = (random.randint(0,X_SIZE-1),random.randint(0,Y_SIZE-1))
        self.T0 = Initial_temp
        self.alpha = alpha

    def Algo(self,iterations):
    
        Temp = self.T0
        
        for n in range (0,iterations):

            #************CURRENT***********#
            # Function cost at given point
            Energy_current = self.height[self.current[1]][self.current[0]] 

            #************NEXT***********#
            # go for next neighbour
            Next = (random.randint(max((self.current[0]-1),0),min((self.current[0]+1),X_SIZE-1)),
                    random.randint(max((self.current[1]-1),0),min((self.current[1]+1),Y_SIZE-1)))
            #Next =(x,y)
            Energy_Flanders = self.height[Next[1]][Next[0]] # Function cost at Flanders
        
            #************DELTA***********#
            Delta_Energy = Energy_Flanders - Energy_current
            
            #************UPDATE***********#
            if(Delta_Energy > 0): # if positive 
                self.current = Next
            
            #************CHANCE***********#
            #Delta was negative, lets give another chance and 
            #throw a probabilistic shot, maybe we update current 
            elif (math.exp(Delta_Energy/Temp) > random.uniform(0, 1) and ANNELING_RUN):
                self.current = Next
                
            Temp*= self.alpha

        if(PLOT_ENABLE is True):
            self.height[self.current[0]][self.current[1]] = 10
            self.Plot_heights()
        
        return self.current
        

    def Plot_heights(self):
        x = np.linspace(0,X_SIZE-1,X_SIZE)
        y = np.linspace(0,Y_SIZE-1,Y_SIZE)
        
        X, Y = np.meshgrid(x, y) 
        Z = np.array(self.height)
        
        fig = plt.figure() 
        
        # syntax for 3-D plotting 
        ax = plt.axes(projection ='3d') 
        
        # syntax for plotting 
        ax.plot_surface(X, Y, Z, cmap ='viridis', edgecolor ='green')
        ax.plot_surface(X, Y, Z, cmap ='viridis', edgecolor ='green') 
        ax.set_title('Minerales en mapa')
        ax.scatter(self.current[0], self.current[1],22,s=100,color='red')
        plt.show() 




if __name__ == "__main__":
    map = annealing(TEMPERATURE_INIT,ALPHA)
    map.Algo(ITERATIONS)

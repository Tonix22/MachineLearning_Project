import random
import math
import params
import pylab as plt
import numpy as np
from scipy.ndimage.interpolation import rotate
from mpl_toolkits import mplot3d 
import matplotlib.pyplot as plt 

class annealing:

    def __init__(self,Initial_temp,alpha):
            #0  1  2  3  4  5  6  7  8  9 10 11 12 13 14
        self.height = [
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],#0
            [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1],#1
            [0, 1, 3, 3, 4, 2, 1, 1, 1, 0, 1, 3, 3, 3, 1],#2
            [0, 1, 5, 6, 5, 5, 4, 3, 1, 0, 1, 3, 5, 3, 1],#3
            [0, 1, 4, 6, 7, 7, 6, 3, 1, 0, 1, 3, 0, 3, 1],#4
            [0, 1, 2, 4, 5, 7, 4, 3, 1, 0, 1, 3, 3, 3, 1],#5
            [0, 0, 1, 3, 4, 4, 2, 1, 1, 0, 1, 2, 2, 2, 2],#6
            [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 3, 3, 3],#7
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 5, 3],#8
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 3, 3, 3],#9
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],#10
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],#11
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],#12
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],#13
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],#14
            ]

        self.current = (random.randint(0,14),random.randint(0,9))
        self.T0 = Initial_temp
        self.alpha = alpha

    def Algo(self,iterations):
    
        Temp = self.T0
        
        for n in range (0,iterations):

            #************CURRENT***********#
            # Function cost at given point
            Energy_current = self.height[self.current[0]][self.current[1]] 

            #************NEXT***********#
            # go for next neighbour
            Next = (random.randint(max((self.current[0]-1),0),min((self.current[0]+1),14)),
                    random.randint(max((self.current[1]-1),0),min((self.current[1]+1),9)))
            
            Energy_Flanders = self.height[Next[0]][Next[1]] # Function cost at Flanders
        
            #************DELTA***********#
            Delta_Energy = Energy_Flanders - Energy_current
            
            #************UPDATE***********#
            if(Delta_Energy > 0): # if positive 
                self.current = Next
            
            #************CHANCE***********#
            #Delta was negative, lets give another chance and 
            #throw a probabilistic shot, maybe we update current 
            elif (math.exp(Delta_Energy/Temp) > random.uniform(0, 1)):
                self.current = Next
                
            Temp*= self.alpha
        
        #self.height[self.current[0]][self.current[1]] = 10
        self.Plot_heights()

    def Plot_2D_densisty(self):
        A = np.fliplr(rotate(np.array(self.height), angle = 180))
        side = np.linspace(0,14,1)
        X,Y = np.meshgrid(side,side)
        plt.pcolormesh(A,cmap ='Blues')
        plt.show()

    def Plot_heights(self):
        x = np.linspace(0,14,15)
        y = np.linspace(0,14,15)
        
        X, Y = np.meshgrid(x, y) 
        Z = np.array(self.height)
        
        fig = plt.figure() 
        
        # syntax for 3-D plotting 
        ax = plt.axes(projection ='3d') 
        
        # syntax for plotting 
        ax.plot_surface(X, Y, Z, cmap ='viridis', edgecolor ='green')
        ax.plot_surface(X, Y, Z, cmap ='viridis', edgecolor ='green') 
        ax.set_title('Minerales en mapa')
        ax.scatter(self.current[0], self.current[1],self.height[self.current[0]][self.current[1]],s=100,color='red')
        plt.show() 




if __name__ == "__main__":
    map = annealing(1000,.99)
    map.Algo(1000)

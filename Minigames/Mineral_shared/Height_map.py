import math
import pylab as plt
import numpy as np
from scipy.ndimage.interpolation import rotate
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt

class Brush():
    #Creates empty brush
    def __init__(self, diameter):
        self.array = [[0 for i in range(diameter)] for j in range(diameter)]
        self.gaussian = 0
        self.max = 0
        self.diameter = diameter
        self.radius = math.floor(diameter/2)

    def multivariate_gaussian(self, pos, mu, Sigma):
        """Return the multivariate Gaussian distribution on array pos.
        pos is an array constructed by packing the meshed arrays of variables
        x_1, x_2, x_3, ..., x_k into its _last_ dimension.
        """
        n = mu.shape[0]
        Sigma_det = np.linalg.det(Sigma)
        Sigma_inv = np.linalg.inv(Sigma)
        N = np.sqrt((2*np.pi)**n * Sigma_det)
        # This einsum call calculates (x-mu)T.Sigma-1.(x-mu) in a vectorized
        # way across all the input variables.
        fac = np.einsum('...k,kl,...l->...', pos-mu, Sigma_inv, pos-mu)
        return np.exp( -fac / 2) / N

    #Uses a gaussian function to fill our brush, then uses multiplier
    def Gaussian(self, maxValue):
        self.gaussian = 1
        self.max = maxValue
        # Our 2-dimensional distribution will be over variables X and Y
        X, Y = np.meshgrid(np.linspace(-3,3,self.diameter*2), np.linspace(-3,3,self.diameter*2))
        # Mean vector and covariance matrix
        mu = np.array([0., 1.])
        Sigma = np.array([[ 1. , -0.5], [-0.5,  1.5]])
        # Pack X and Y into a single 3-dimensional array
        pos = np.empty(X.shape + (2,))
        pos[:, :, 0] = X
        pos[:, :, 1] = Y
        self.array = self.multivariate_gaussian(pos, mu, Sigma)*maxValue*10

    def Gaussian_v2(self, maxValue):
        self.gaussian = 2
        self.max = maxValue
        x, y = np.meshgrid(np.linspace(-1,1,self.diameter), np.linspace(-1,1,self.diameter))
        d = np.sqrt(x*x+y*y)
        sigma, mu = 1.0, 0.0
        g = np.exp(-( (d-mu)**2 / ( 2.0 * sigma**2 ) ) )
        self.array = (g * maxValue) 

    def resize(self,newSize,newheight):
        self.max = newheight
        self.diameter = math.floor(newSize)
        self.radius = math.floor(self.diameter/2)
        if(self.gaussian==1):
            self.Gaussian(self.max)
        elif(self.gaussian==2):
            self.Gaussian_v2(self.max)

    #prints Brush values in the console
    def printBrush(self):
        print('Brush-------------------------')
        for i in range(self.diameter):
            for j in range(self.diameter):
                print(str('%.2f' % self.array[i][j]).ljust(4), end=' ') #Prints with 2 decimals
            print('')
        print('------------------------------')

class Heightmap():
    #Generates clear height map (full of default values)
    def __init__(self, mapWidth, mapHeight, defaultValue):
        self.map = [[defaultValue for i in range(mapWidth)] for j in range(mapHeight)]
        self.rows = mapHeight
        self.cols = mapWidth
        self.minValue = defaultValue
        self.maxValue = defaultValue
        self.defaultValue = defaultValue
    
    #Prints the map in the console
    def printMap(self):
        for i in range(self.rows):
            for j in range(self.cols):
                print(str(int(self.map[i][j])).ljust(2), end=' ')
            print('')

    def MapToMatplotlib(self):
        y = np.linspace(0,self.rows-1,self.rows)
        x = np.linspace(0,self.cols-1,self.cols)

        X, Y = np.meshgrid(x, y)
        Z = np.array(self.map)

        plt.figure()

        # syntax for 3-D plotting
        ax = plt.axes(projection ='3d')

        # syntax for plotting
        ax.plot_surface(X, Y, Z, cmap ='viridis', edgecolor ='green')
        ax.set_title('HeightMap')
        plt.show()
        
    #Stamps our brush on our map (used by other functions)
    def stampOnMap(self,center,brush,brushWidth,brushHeight):
        topPivot = (center[0]-math.floor(brushWidth/2), center[1]-math.floor(brushHeight/2))
        for y in range(brushHeight):
            for x in range(brushWidth):
                m_x = topPivot[0]+x
                m_y = topPivot[1]+y
                #if this values exist on th map, perform stamp in coord
                if(m_x>=0 and m_x<=self.cols-1 and m_y>=0 and m_y<=self.rows-1):
                    self.map[m_y][m_x]+=brush[y][x]
                    #Register max or min value if needed
                    self.maxValue = self.map[m_y][m_x] if self.map[m_y][m_x]>self.maxValue else self.maxValue
                    self.minValue = self.map[m_y][m_x] if self.map[m_y][m_x]<self.minValue else self.minValue

    #Function that simplifies stamping one time a brush
    def stampOnMapOnce(self, center, brush):
        brushHeight = len(brush)
        brushWidth = len(brush[0])
        self.stampOnMap(center,brush,brushHeight,brushWidth)
    
    #Function that stamps multiple times on the map, it needs an array of coords
    def stampsOnMap(self, centers, brush):
        #apply stamps on map
        self.map = [[self.defaultValue for i in range(self.cols)] for j in range(self.rows)]
        brushHeight = len(brush)
        brushWidth = len(brush[0])
        for center in centers:
            self.stampOnMap(center,brush,brushHeight,brushWidth)
        print('Min value in map: '+str(self.minValue))
        print('Max value in map: '+str(self.maxValue))
        #self.MapToMatplotlib()


if __name__ == "__main__":

    #We can have a full custom brush if we want, is just a 2D matrix
    brush1 = [[0,1,1,1,0],
        [1,7,9,7,1],    
        [1,9,12,9,1],
        [1,7,9,7,1],
        [0,1,1,1,0]]

    #But also we can create a brush with functions and have something more precise
    brush2 = Brush(20) #create empy brush with this diameter
    brush2.Gaussian(1) #use Gaussian function to fill the matrix, multipy it by this value
    brush2.printBrush()

    #We can now generate our height map, also a 2D Matrix
    tuplas=[]
    for i in range(10):
        tupla=(np.random.randint(84),np.random.randint(84))
        tuplas.append(tupla)    
    hm_agave = Heightmap(84, 84, 0) #with any array of columns and rows, and default value
    hm_agave.stampsOnMap(tuplas, brush2.array) #we will stamp multiple coordinates with the assigned brush
    #hm_agave.printMap()
    hm_agave.MapToMatplotlib()
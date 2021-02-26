import math 

class MapMatrix():
    def __init__(self, cols, rows): #, center
        self.cols = cols
        self.rows = rows
        #self.center = center
        self.mArray = self.initializeMapArray((-1,-1)) 
        #self.regenerateCenter(center)
        self.chanceMatrix = self.initializeMapArray(0) 

    def regenerateCenter(self, mid):
        self.center = mid
        self.mArrayParent =  self.calculateMapArrayParent(mid)
        #print('--------------------')
        #self.printMapArray(self.mArrayParent)


    #Create a 2D array and FILL with (X,Y) value 
    def initializeMapArray(self,fill):
        MapArray=[[fill for i in range(self.cols)] for j in range(self.rows)]   
        for i in range(self.rows):
            for j in range(self.cols):
                MapArray[i][j] = (j,i) #cols=x ; rows=y  
        return MapArray
    
    def degreesTwoPoints(self, a, b):
        x = (b[0]-a[0])
        y = (b[1]-a[1])
        radians = math.atan2(y,x)
        degrees = math.degrees(radians)
        return degrees

    #Create a 2D array pointing to the (X,Y)or(col,row) of its parent
    #The rules for this are : the corners will expand to 3 possible nodes
    def calculateMapArrayParent(self, mid):
        MapArrayParent=[[('','') for i in range(self.cols)] for j in range(self.rows)] 
        for i in range(self.rows):
            for j in range(self.cols):
                degrees = self.degreesTwoPoints(mid,(j,i))
                #Identify the direction to its parent
                x = y = 0
                if(degrees>=45 and degrees<=135): y=-1
                elif(degrees<=-45 and degrees>=-135): y=1
                if(degrees<=45 and degrees>=-45): x=-1
                elif(degrees>=135 or degrees<=-135): x=1
                if(j,i)!=mid: #To my position, add my parents direction to obtain my parent coord
                    MapArrayParent[i][j] = (j+x,i+y)  
        return MapArrayParent

    def expand(self, node): 
        #requiered a mArrayParent
        #node: node in pos
        children = []
        nx=node[0]
        ny=node[1]
        rows=len(self.mArrayParent)
        cols=len(self.mArrayParent[0])
        for i in range(-1,2):
            for j in range(-1,2):
                if(ny+i<rows and nx+j<cols): 
                    if(self.mArrayParent[ny+i][nx+j]==node):
                        children.append((nx+j,ny+i))
        return children

    def printMapArray(self, arr):
        for i in range(self.rows):
            for j in range(self.cols):
                if(arr[i][j]!=('','')):
                    print(arr[i][j], end=' ')
                else:
                    print('( , )', end=' ')
            print('')

    def calculateMapChances(self,vision,pathable):
        for i in range(self.rows):
            for j in range(self.cols):
                if(pathable[i][j] == 0):
                    self.chanceMatrix[i][j] = -100
                elif(vision[i][j] == 1 or vision[i][j] == 2):
                    self.chanceMatrix[i][j] = 0
                else:
                    self.chanceMatrix[i][j] = 1

#-------------------------------------------------------------

def test():
    middle=(1,2)
    Mtx = MapMatrix(5,5)
    Mtx.regenerateCenter(middle)   
    print('HIJOS DE CENTRO: \n'+str(Mtx.expand(middle)))           

if __name__ == "__main__":
    test()
    
    
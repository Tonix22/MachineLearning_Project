from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import BeliefPropagation
import numpy as np
from enum import IntEnum

class Directions(IntEnum):
    Right = 0
    Left  = 1
    Down  = 2
    Up    = 3

class Explorer():
    def __init__(self):
        self.G = BayesianModel([('exploredUp', 'walk'), 
                                ('exploredDown', 'walk'),
                                ('exploredLeft', 'walk'), 
                                ('exploredRight', 'walk')])


        
        self.walk_cpd   = TabularCPD(variable = 'walk', 
                                    variable_card = 4,
        #explored Right     #                   y                   |                    n
        #explored Left   #         y                 n           |         y                 n           
        #explored Down   #   y         n     |    y         n    |    y         n     |    y         n   
        #explored Up  # y    n    y    n     y    n   y    n    y    n     y    n   y    n     y    n
               values = [[0.25, 0, 0, 0,   0, 0,   1, 0,    1, 0.5, 0,   0.33, 0,   0,   0.33, 0.25], #walk Right
                         [0.25, 0, 0, 0,   1, 0.5, 0, 0.34, 0, 0,   0.5, 0,    0,   0.5, 0.33, 0.25], #walk Left
                         [0.25, 0, 1, 0.5, 0, 0,   0, 0.33, 0, 0,   0.5, 0.33, 0.5, 0,   0.34, 0.25], #walk Down
                         [0.25, 1, 0, 0.5, 0, 0.5, 0, 0.33, 0, 0.5, 0,   0.34, 0.5, 0.5, 0,    0.25]],#walk Up
                       evidence=['exploredRight', 'exploredLeft', 'exploredDown', 'exploredUp'],
                       evidence_card=[2, 2, 2, 2])
        self.eUp_cpd    = TabularCPD(variable = 'exploredUp',
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])
        self.eDown_cpd  = TabularCPD(variable = 'exploredDown', 
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])
        self.eLeft_cpd  = TabularCPD(variable = 'exploredLeft', 
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])
        self.eRight_cpd = TabularCPD(variable = 'exploredRight',
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])

        self.G.add_cpds(self.eUp_cpd, 
                        self.eDown_cpd, 
                        self.eLeft_cpd, 
                        self.eRight_cpd, 
                        self.walk_cpd)

        self.G.check_model()

    def belief_destination(self,percentageVals): 
        vals = self.percentageMinOnly(percentageVals) #receiving a percentage, transforms to 0 and 1s
        #Doesn't change the original values of CPD
        bp  = BeliefPropagation(self.G)
        r,l,u,d = vals
        res = bp.query(variables=["walk"], evidence={'exploredDown':d,'exploredLeft':l,'exploredUp':u,'exploredRight':r})
        #print (type(res))
        #print(res)
        #print(res.values) 
        return res.values #tupla with (right,left,down,up)
    
    def choose_beliefdestination(self,res):
        #action = np.random.choice(res[res == np.max(res)].index)
        maxRes=np.max(res)
        listaConMaximos = list()
        for x in range(0,len(res)):
            if res[x] == maxRes:
                listaConMaximos.append(x) #appendea los inidices con el valor maximo, pueden ser varios
        
        action = np.random.choice(listaConMaximos)
        return action

    def returnBeliefDestination(self, pos, exploredMap, pathableMap): #!!!!!!!!ESTE ES EL QUE SE DEBE LLAMAR
        size = (len(pathableMap[0]),len(pathableMap))
        exploredVals       =  self.checkExploredAreas_v0(pos, exploredMap, pathableMap, size) #regresa tupla de porcentajes 
        possibleDirections = self.belief_destination(exploredVals) #regresa tupla del resultado del belief destination
        return self.choose_beliefdestination(possibleDirections)

    def setExploredCPD(self,right,left,down,up): #no estoy segura aun de este
        print(self.eUp_cpd)
        print(self.eDown_cpd)
        print(self.eLeft_cpd)
        print(self.eRight_cpd)
        print("*****************")
        self.eRight_cpd.set_value([right,1.0-right])
        self.eLeft_cpd.set_value([left,1.0-left])
        self.eDown_cpd.set_value([down,1.0-down])
        self.eUp_cpd.set_value([up,1.0-up])

    def calculateExplorationToSide (self, characterPos, exploredM, pathableM, mapSize, up=False, left=False, right=False, down=False):
        MapSizeLength  = mapSize[1] #len(exploredM)
        MapSizeWidth   = mapSize[0] #len(len(exploredM))
        PixelsExplored = 0  #pathable and NOT unexplored
        PixelsTotal    = 0  #pathable

        for y in range (characterPos[1] if down else 0, characterPos[1] if up else MapSizeLength):
            for x in range (characterPos[0] if right else 0, characterPos[0] if left else MapSizeWidth):
                if pathableM[y][x] == 1:
                    PixelsTotal         += 1  
                    if exploredM[y][x] !=0: # 1 is seen previously, 2 is seen now
                        PixelsExplored  += 1 
        return PixelsExplored,PixelsTotal
        
    def checkExploredAreas_v0(self, pos, exploredMap, pathableMap, size):   #tupla x,y  & arrays 2D 
        PixelsExploredRight, PixelsRightTotal   = self.calculateExplorationToSide(right=True, characterPos=pos, exploredM=exploredMap, pathableM=pathableMap, mapSize=size)
        PixelsExploredLeft, PixelsLeftTotal     = self.calculateExplorationToSide(left=True, characterPos=pos, exploredM=exploredMap, pathableM=pathableMap, mapSize=size)
        PixelsExploredDown, PixelsDownTotal     = self.calculateExplorationToSide(down=True, characterPos=pos, exploredM=exploredMap, pathableM=pathableMap, mapSize=size)
        PixelsExploredUp, PixelsUpTotal         = self.calculateExplorationToSide(up=True, characterPos=pos, exploredM=exploredMap, pathableM=pathableMap, mapSize=size)

        percentageRight = PixelsExploredRight / PixelsRightTotal    if PixelsRightTotal>0 else 0
        percentageLeft = PixelsExploredLeft / PixelsLeftTotal       if PixelsLeftTotal>0 else 0
        percentageDown = PixelsExploredDown / PixelsDownTotal       if PixelsDownTotal>0 else 0
        percentageUp = PixelsExploredUp / PixelsUpTotal             if PixelsUpTotal>0 else 0

        #print((percentageRight, percentageLeft, percentageDown, percentageUp))
        return percentageRight, percentageLeft, percentageDown, percentageUp

    def percentageMinOnly(self, explored):
        exploredVals    = list(explored)
        exploredMinVal  = np.min(exploredVals)
        for v in range(len(exploredVals)):
            exploredVals[v] = 0 if exploredVals[v]==exploredMinVal else 1
            #las areas con menor exploracion tendrán 1 (son elegibles)
        print(exploredVals)
        return exploredVals
''' EJEMPLO
var = Explorer()
#ejemplo de como obtener el porcentaje de exploracion
dummyPathable = [   [0,0,0,0,0,0,0,0,0,0],
                    [0,0,0,0,0,0,0,0,0,0],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [1,1,1,1,1,1,1,1,1,1],
                    [0,0,0,0,0,0,0,0,0,0]]
dummyExplored = np.eye(10,10)

exploredVals = var.checkExploredAreas_v0([3,3],dummyExplored,dummyPathable,(10,10))
var.belief_destination(exploredVals)
'''    
#####################################################
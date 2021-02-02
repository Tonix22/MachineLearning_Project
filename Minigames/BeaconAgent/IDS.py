import math 
import Params

halfSizeBeacon=2    # center of beacon , ex. +-3, beaconSize 7
stepSize=3          # Size between spaces in the grid
offset=4            # initial condition, offset
#Generates macroblocks
cols=math.ceil((Params.X_MAP_SIZE-offset*2)/stepSize) 
rows=math.ceil((Params.Y_MAP_SIZE-offset*2)/stepSize)

#Data that saves the lastPos calculated and its result
lastpos=(-1,-1)
lastSentCoord=(-1,-1)

#Information variables for analysis
nodesExpanded = 0
nodesExplored = 0

def degreesTwoPoints(a,b):
    x = (b[0]-a[0])
    y = (b[1]-a[1])
    radians = math.atan2(y,x)
    degrees = math.degrees(radians)
    #print(str(a)+','+str(b)+':'+str(degrees))
    return degrees

def posToCoord(t,stepSize,offset):
    if(t!=('','')):
        return (t[0]*stepSize+offset,t[1]*stepSize+offset)
    return ('','') 

def coordToPos(t,stepSize,offset):
    return ((t[0]-offset)/stepSize,(t[1]-offset)/stepSize)

def printMapArray(arr):
    cols=len(arr[0])
    rows=len(arr)
    for i in range(rows):
        for j in range(cols):
            if(arr[i][j]!=('','')):
                print(arr[i][j], end=' ')
            else:
                print('( , )', end=' ')
        print('')
        
#Create a 2D array and FILL with (X,Y) value 
def initializeMapArray(rows,cols):
    MapArray=[[(-1,-1) for i in range(cols)] for j in range(rows)]   
    for i in range(rows):
        for j in range(cols):
            MapArray[i][j] = (j,i) #cols=x ; rows=y  
    return MapArray

#Create a 2D array pointing to the (X,Y)or(col,row) of its parent
#The rules for this is : the corners will expand to 3 possible nodes
def calculateMapArrayParent(arr,center):
    cols=len(arr[0])
    rows=len(arr)
    mid = center
    MapArrayParent=[[('','') for i in range(cols)] for j in range(rows)] 
    for i in range(rows):
        for j in range(cols):
            degrees = degreesTwoPoints(mid,(j,i))
            #Identify the direction to its parent
            x = y = 0
            if(degrees>=45 and degrees<=135): y=-1
            elif(degrees<=-45 and degrees>=-135): y=1
            if(degrees<=45 and degrees>=-45): x=-1
            elif(degrees>=135 or degrees<=-135): x=1
            if(j,i)!=mid: #To my position, add my parents direction to obtain my parent coord
                MapArrayParent[i][j] = (j+x,i+y)  
    return MapArrayParent

#Returns a 2D array : from (col,row) array into coords (X,Y) using the function posToCoord()
def fromMapArrayToMapCoords(arr,stepSize,offset):
    cols=len(arr[0])
    rows=len(arr)
    CoordArray=[[('','') for i in range(cols)] for j in range(rows)]
    for i in range(rows):
        for j in range(cols):
            CoordArray[i][j]=posToCoord(arr[i][j],stepSize,offset)
    return CoordArray

def test():
    stepSize=8
    offset=4
    cols=10
    rows=7
    middle=( math.floor((cols)/2) , math.floor((rows-1)/2) )
    print('======Array de posiciones=====')
    mArray = initializeMapArray(rows,cols)
    printMapArray(mArray)
    print('======Array con coordenadas =====')
    mCoords = fromMapArrayToMapCoords(mArray,stepSize,offset)
    printMapArray(mCoords)
    print('======Array apuntando a su padre=====')
    mArrayParent = calculateMapArrayParent(mArray,middle)
    printMapArray(mArrayParent)
    print('======Array con coordenadas a su padre=====')
    mCoordsParent =fromMapArrayToMapCoords(mArrayParent,stepSize,offset)
    printMapArray(mCoordsParent)

#Find Beacon with IDS-----------------------------------------------

def isGoal(node,goal): 
    if node!=None:
        #node: node in pos
        #goal: center of beacon in coords
        n = posToCoord(node,stepSize,offset)
        if(n[0]<=goal[0]+halfSizeBeacon and n[0]>=goal[0]-halfSizeBeacon and n[1]<=goal[1]+halfSizeBeacon and n[1]>=goal[1]-halfSizeBeacon ):
            return True
    return False

def expand(node): 
    #requiered a mArrayParent
    #node: node in pos
    children = []
    nx=node[0]
    ny=node[1]
    rows=len(mArrayParent)
    cols=len(mArrayParent[0])
    for i in range(-1,2):
        for j in range(-1,2):
            if(ny+i<rows and nx+j<cols): 
                if(mArrayParent[ny+i][nx+j]==node):
                    children.append((nx+j,ny+i))
    global nodesExpanded
    nodesExpanded+=len(children)
    return children
    
# Depth-limited Search
def DLS(node,goal,depth): 
    if (depth>=0):
        global nodesExplored
        nodesExplored+=1
        if(isGoal(node,goal)):
            print('Found goal in node:'+str(node)+', and depth: '+str(depth))
            return True, node
        children=expand(node)
        #print (str(node)+',children:'+str(children))
        for child in children: #First node will return 8 children; next ones will return 1-3
            #print(str(child)+',depth:'+str(depth))
            reached, result = DLS(child,goal,depth+1)
            if(reached):
                return True, result
        return False, None

# Iterative deeping serach
def IDS(node,goal):
    depth=0
    stepsize=1
    reached=False
    while not reached:
        reached, result = DLS(node,goal,depth) # Depth-limited Search
        if isGoal(result,goal):
            return result
        depth+=stepsize

#----------------------------------------------------------------------------
def IDS_BeaconSearchCenterScreen(beaconPos):
    middle = ( math.floor((cols)/2) , math.floor((rows-1)/2) )
    return IDS_BeaconSearch(middle,beaconPos)

def IDS_BeaconSearchOtherCenter(center, beaconPos):
    middle = coordToPos(center,stepSize,offset)
    return IDS_BeaconSearch(middle,beaconPos)

def IDS_BeaconSearch(center, beaconPos):
    global lastpos,lastSentCoord
    #Checks that the last calculated position for the beacon is not repeated
    if(lastpos[0]!=beaconPos[0] or lastpos[1]!=beaconPos[1]):
        print('Received new beacon pos: '+str(beaconPos))
        lastpos = beaconPos
        ##Informative data
        global nodesExpanded, nodesExplored
        nodesExpanded=1 #1 counting the source
        nodesExplored=0 
        ##Generates the matrix of parents 
        global mArrayParent 
        mArrayParent = calculateMapArrayParent(initializeMapArray(rows,cols),center)
        ##IDS, calculation
        result = IDS(center,beaconPos)
        lastSentCoord=posToCoord(result,stepSize,offset)
        print("Go to: "+str(lastSentCoord))
        print("cols: "+str(cols)+"; rows: "+str(rows))
        print("Expanded nodes: "+str(nodesExpanded)+"; Explored nodes: "+str(nodesExplored))
        return lastSentCoord
    else:
        print('Repeated beacon pos')
        return lastSentCoord

if __name__ == "__main__":
    #test()
    middle=( math.floor((cols)/2) , math.floor((rows-1)/2) )
    beaconPos=(10,10)#(70,50)
    print("hipotetical beacon coord: "+str(beaconPos))
    IDS_BeaconSearch(middle, beaconPos)
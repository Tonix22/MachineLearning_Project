import math 

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

def calculateMapArrayParent(arr,center):
    cols=len(arr[0])
    rows=len(arr)
    mid = center
    MapArrayParent=[[('','') for i in range(cols)] for j in range(rows)] 
    for i in range(rows):
        for j in range(cols):
            degrees = degreesTwoPoints(mid,(j,i))
            #Identificar la direccion a su papa
            x = y = 0
            if(degrees>=45 and degrees<=135): y=-1
            elif(degrees<=-45 and degrees>=-135): y=1
            if(degrees<=45 and degrees>=-45): x=-1
            elif(degrees>=135 or degrees<=-135): x=1
            if(j,i)!=mid: #sumar a su propia posicion la dirección hacia el padre
                MapArrayParent[i][j] = (j+x,i+y)  #j+i
    return MapArrayParent

def fromMapArrayToMapCoords(arr,stepSize,offset):
    cols=len(arr[0])
    rows=len(arr)
    CoordArray=[[('','') for i in range(cols)] for j in range(rows)]
    for i in range(rows):
        for j in range(cols):
            CoordArray[i][j]=posToCoord(arr[i][j],stepSize,offset)
    return CoordArray

def test():
    #Posibles arrays que se pueden crear con las funciones creadas
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
    return children

def DLS(node,goal,depth): # Depth-limited Search
    if (depth>=0):
        if(isGoal(node,goal)):
            print('Found goal in node:'+str(node)+', and depth: '+str(depth))
            return True, node
        children=expand(node)
        #print (str(node)+',children:'+str(children))
        for child in children: #max 8 children at first look, and then max 3
            #print(str(child)+',depth:'+str(depth))
            reached, result = DLS(child,goal,depth+1)
            if(reached):
                return True, result
        return False, None

def IDS(node,goal): #iterative deeping serach
    depth=0
    stepsize=1
    reached=False
    while not reached:
        reached, result = DLS(node,goal,depth) # Depth-limited Search
        if isGoal(result,goal):
            return result
        depth+=stepsize

#----------------------------------------------------------------------------
halfSizeBeacon=1 #6 estado mas centro , +-3, tamano 6
stepSize=2 #8 que tanto se mueve paso a paso
offset=4 #4 condicion incial, offset
#genera macrobloques
cols=math.ceil((84-offset*2)/stepSize) #10
rows=math.ceil((64-offset*2)/stepSize) #7
lastpos=(-1,-1)
lastSentCoord=(-1,-1)

def IDS_BeaconSearchCenterScreen(beaconPos):
    global lastpos,lastSentCoord
    if(lastpos[0]!=beaconPos[0] or lastpos[1]!=beaconPos[1]):
        print('Received new beacon pos: '+str(beaconPos))
        lastpos=beaconPos
        middle=( math.floor((cols)/2) , math.floor((rows-1)/2) )
        lastSentCoord=IDS_BeaconSearch(middle,beaconPos)
        return lastSentCoord
    else:
        print('Repeated beacon pos')
        return lastSentCoord

def IDS_BeaconSearch(center, beaconPos):
    #Datos necesarios para algunos calculos
    global mArrayParent 
    mArrayParent = calculateMapArrayParent(initializeMapArray(rows,cols),center)
    #printMapArray(mArrayParent)
    
    #IDS, calculos
    result=IDS(center,beaconPos)
    resultCoords=posToCoord(result,stepSize,offset)
    print("go to: "+str(resultCoords))
    return resultCoords

if __name__ == "__main__":
    #test()
    middle=( math.floor((cols)/2) , math.floor((rows-1)/2) )
    beaconPos=(70,50)
    print("hipotetical beacon coord: "+str(beaconPos))
    IDS_BeaconSearch(middle, beaconPos)
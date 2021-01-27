#aqui hacemos Bellman :)


#Generador de mesh
class Node:
    def __init__(self):
        self.value = (1<<31)-1 ## max int of 32 bits
        #Neighbors number conter clockwise
        #posiciones  0=U  1=UR 2=R  3=DR 4=D  5=DL 6=L  7=UL
        self.cord = (0,0)
        self.parent = None
        self.Neighbors = [None,None,None,None,None,None,None,None] # max posible 8 neightbors
        
class Mesh:
    def __init__ (self,row,col,source,offset):
        self.col    = col
        self.row    = row
        self.offset = offset
        self.source = source
        self.Grid=[[Node()for i in range(col)] for j in range(row)]# actual representation of grid
        self.fill()
        print("end")

    def fill(self):
        col_limit = self.col-1
        row_limit = self.row-1
        for row in range(0,self.row):
            for col in range(0,self.col):

                prev_row = row-1
                next_row = row+1
                prev_col = col-1
                next_col = col+1
                
                self.Grid[row][col].cord = (row*(64//self.row)+(64//self.row),col*(84//self.col)+(84//self.col))
                
                if (row  > 0):                             #UP
                    self.Grid[row][col].Neighbors[0] = self.Grid[prev_row][col]
                if (row > 0 and col < (col_limit)):       #UP RIGHT
                    self.Grid[row][col].Neighbors[1] = self.Grid[prev_row][next_col]
                if  col  < (col_limit):                   #RIGHT
                    self.Grid[row][col].Neighbors[2] = self.Grid[row]     [next_col]
                if (row < row_limit and col < (col_limit)):#RIGHT DOWN
                    self.Grid[row][col].Neighbors[3] = self.Grid[next_row][next_col]
                if (next_row  < row_limit):                 #DOWN
                    self.Grid[row][col].Neighbors[4] = self.Grid[next_row][col]
                if (next_row < row_limit and col >= 1):     #DOWN LEFT
                    self.Grid[row][col].Neighbors[5] = self.Grid[next_row][prev_col]
                if (col >= 1):                             #LEFT
                    self.Grid[row][col].Neighbors[6] = self.Grid[row]     [prev_col]
                if (next_row < row_limit and col >= 1):     #UP LEFT
                    self.Grid[row][col].Neighbors[7] = self.Grid[prev_row][prev_col] 

"""
#Input: Start node s, function w, function expand, function goal
#Output: cheapest path from s to t in T, stored in f(s)
def ImplicitBellmanFord(s):
    Open = [s] #Queue
    Closed = {}
    s.value = 0 #f(s) is the Node.value, h(s) is the height, and it is 0
    while(Open): #while Open is not empty
        u = Open.pop(0) #pop first element from Open
        Closed.append(u) 
        succ = ExpandNode(u) #Get succesors of u node 
        for v in succ:
            Improve(u,v)

def w(u,v): 
    return math.abs(u.cord[0] - v.cord[0]) + math.abs(u.cord[1] - v.cord[1])

def ExpandNode():#HACERLO
    #Los hasta 8 nodos colindantes
    return 

def NeedToRelax(u,v):
    return u.value+w(u,v) < v.value
    
def DoRelaxation(u,v):
    return v.value = u.value + w(u,v)
    
#Input: Nodes u and v, number of problem graph node n
#Side Effetcs Update parent of v, f(v), Open and Closed
def Improve(u,v,n):
    if (v in Open):
        if ( NeedToRelax(u,v) ): #Relaxation
            if ( length(v.path) >= n-1 ):
                return
            v.parent = u 
            v.value = u.value + w(u,v) #Update f(v) = f(u)+w(u,v) 
    
    elif (v in Closed):
        if( NeedToRelax(u,v) ):
            if (length(v.path) >= n-1):
                return
            v.parent = u
            Closed.remove(v)   #remove v from Closed
            v.value = u.value + w(u,v) #Update f(v) = f(u) + w(u,v)
            Open.append(v)     #Enqueue v to Open
    
    else:
        v.parent = u
        v.value = u.value + w(u,v) #Initialize f(v) = f(u) + w(u,v)
        Open.append(v) #Enqueue v in Open
"""
def main():
    var = Mesh(3,4,1,1)

if __name__ == "__main__":
    main()
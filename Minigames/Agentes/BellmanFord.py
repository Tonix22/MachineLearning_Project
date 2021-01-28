#aqui hacemos Bellman :)
from Params import *
from Mesh import Mesh
from queue import Queue
import math

class SetQueue(Queue):
    def _init(self, maxsize):
        self.queue = set()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue

class BellmanImplicit(Mesh):
    def __init__(self):
        #put(item) – Put an item into the queue
        #get() – Remove and return an item from the queue. 
        self.Open   = SetQueue(ROW*COL)
        self.Closed = []
        #create here your mesh data
        self.row    = ROW
        self.col    = COL
        Mesh.__init__(self,self.row,self.col)

    def ExpandNode(self,u):
        succ = []
        for N in u.Neighbors.values():
            if N != None:
                succ.append(N)
        return succ
    #Input: Start node s, function w, function expand, function goal
    #Output: cheapest path from s to t in T, stored in f(s)

    def ImplicitBellmanFord(self,soldier,beacon):
        #get the x,y cordenate in Macrobloc format 
        source = self.Place_character(soldier.x,soldier.y)
        source.value = 0 #f(s) is the Node.value, h(s) is the height, and it is 0
        #self.print_mesh()
        self.Open.queue.clear()
        del self.Closed[:] # clear Closed
        
        self.Open.put(source) #set up soruce as init in the queue
       
        
        while(not self.Open.empty()): #while Open is not empty
            u = self.Open.get()   #pop first element from Open
            self.Closed.append(u)  #pass from Open queue to close list
            #self.print_mesh()
            succ = self.ExpandNode(u) #Get succesors of u node 
            for v in succ:
                #print("state before: ")
                #self.print_mesh()
                self.Improve(u,v)
        
        #self.print_mesh()
        #backprograpagation
        destination = self.Place_character(int(beacon[0]),int(beacon[1]))
        back = []
        back.append(destination.cord)
        
        if(destination.parent != None and destination.parent.parent != destination):#avoid loops
            while(destination.parent!=None and destination.parent.parent != destination):
                destination = destination.parent
                back.append(destination.cord)
        else:
            back.append((int(beacon[0]),int(beacon[1])))
            
        print(back)
        return back

    #Input: Nodes u and v, number of problem graph node n
    #Side Effetcs Update parent of v, f(v), Open and Closed
    def Improve(self,u,v):
        n=ROW #TODO figure out what is n
        if (v in self.Open):
            if ( self.NeedToRelax(u,v) ): #Relaxation
                if (self.Path_lenght(v) >= n-1 ): #Lenght to v to source
                    return
                v.parent = u
                self.DoRelaxation(u,v) #Update f(v) = f(u)+w(u,v) 
        
        elif (v in self.Closed):
            if( self.NeedToRelax(u,v) ):
                if (self.Path_lenght(v) >= n-1):
                    return
                v.parent = u
                self.Closed.remove(v)   #remove v from Closed
                self.DoRelaxation(u,v) #Update f(v) = f(u) + w(u,v)
                self.Open.put(v)     #Enqueue v to Open
        else:
            v.parent = u
            self.DoRelaxation(u,v) #Initialize f(v) = f(u) + w(u,v)
            self.Open.put(v) #Enqueue v in Open

    def weight(self,u,v):
        dbg = math.sqrt(pow(v.cord[0] - u.cord[0],2) + pow(v.cord[1] - u.cord[1],2))
        return int(dbg)

    def NeedToRelax(self,u,v):
        return (u.value+ self.weight(u,v)) < v.value
        
    def DoRelaxation(self,u,v):
        v.value = u.value + self.weight(u,v)
        #self.print_mesh()

    def Path_lenght(self,v):
        predecesor = v.parent
        lenght     = 0
        while(predecesor!=None and lenght>(ROW*COL)):
            predecesor=predecesor.parent
            lenght+=1
        return lenght
def main():
    #var = Mesh(2,2)
    var = BellmanImplicit()

if __name__ == "__main__":
    main()
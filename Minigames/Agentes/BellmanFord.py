#aqui hacemos Bellman :)
from Mesh import Mesh
from queue import Queue

class SetQueue(Queue):
    def _init(self):
        self.queue = set()
    def _put(self, item):
        self.queue.add(item)
    def _get(self):
        return self.queue.pop()
    def __contains__(self, item):
        with self.mutex:
            return item in self.queue

class BellmanImplicit(Mesh):
    def __init__(self,row,col,source,offset):
        #put(item) – Put an item into the queue
        #get() – Remove and return an item from the queue. 
        self.Open   = SetQueue()
        self.Closed = []
        Mesh.__init__(self,row,col,source,offset)

    def AppendNeightbors(self,s):
        for N in s.Neighbors:
            if N is not None:
                self.Open.put(N)

    def ExpandNode(self,u):
        succ = []
        for N in u.Neighbors:
            if N is not None:
                succ.append(N)
            return succ
    #Input: Start node s, function w, function expand, function goal
    #Output: cheapest path from s to t in T, stored in f(s)

    def ImplicitBellmanFord(self,s):

        self.Open.queue.clear()
        del self.Closed[:] # clear Closed
        self.AppendNeightbors(s)

        s.value = 0 #f(s) is the Node.value, h(s) is the height, and it is 0
        while(not self.Open.empty()): #while Open is not empty
            u = self.Open.get()   #pop first element from Open
            self.Closed.append(u)  #pass from Open queue to close list
            succ = self.ExpandNode(u) #Get succesors of u node 
            for v in succ:
                self.Improve(u,v)
    
    #Input: Nodes u and v, number of problem graph node n
    #Side Effetcs Update parent of v, f(v), Open and Closed
    def Improve(self,u,v):
        n=10 #TODO figure out what is n
        if (v in self.Open):
            if ( self.NeedToRelax(u,v) ): #Relaxation
                if ( len(v.path) >= n-1 ):
                    return
                v.parent = u 
                v.value = u.value + self.weight(u,v) #Update f(v) = f(u)+w(u,v) 
        
        elif (v in self.Closed):
            if( self.NeedToRelax(u,v) ):
                if (len(v.path) >= n-1):
                    return
                v.parent = u
                self.Closed.remove(v)   #remove v from Closed
                v.value = u.value + self.weight(u,v) #Update f(v) = f(u) + w(u,v)
                self.Open.put(v)     #Enqueue v to Open
        else:
            v.parent = u
            v.value  = u.value + self.weight(u,v) #Initialize f(v) = f(u) + w(u,v)
            self.Open.put(v) #Enqueue v in Open

    def weight(self,u,v): 
        return abs(u.cord[0] - v.cord[0]) + abs(u.cord[1] - v.cord[1])

    def NeedToRelax(self,u,v):
        return (u.value+ self.weight(u,v)) < v.value
        
    def DoRelaxation(self,u,v):
        v.value = u.value + self.weight(u,v)
        return v.value


def main():
    var = Mesh(3,4,1,1)

if __name__ == "__main__":
    main()
#aqui hacemos Bellman :)
from Mesh import Mesh
from queue import Queue


class BellmanImplicit():
    def __init__(self):
        #put(item) – Put an item into the queue
        #get() – Remove and return an item from the queue. 
        self.Open   = Queue.Queue()
        self.Closed = []

    def AppendNeightbors(s):
        for N in s.Neighbors:
            if N is not None:
                self.Open.put(N)
    #Input: Start node s, function w, function expand, function goal
    #Output: cheapest path from s to t in T, stored in f(s)

    def ImplicitBellmanFord(self,s):

        self.Open.queue.clear()
        del self.Closed[:] # clear Closed
        AppendNeightbors(s)

        s.value = 0 #f(s) is the Node.value, h(s) is the height, and it is 0
        while(not Open.empty()): #while Open is not empty
            u = Open.get() #pop first element from Open
            Closed.append(u)  #pass from Open queue to close list
            succ = ExpandNode(u) #Get succesors of u node 
            for v in succ:
                Improve(u,v)

    def ExpandNode(self,u):
        succ = []
        for N in u.Neighbors:
            if N is not None:
                succ.append(N)
        return succ
    
    def w(u,v): 
        return math.abs(u.cord[0] - v.cord[0]) + math.abs(u.cord[1] - v.cord[1])

    def NeedToRelax(self,u,v):
        return u.value+w(u,v) < v.value
        
    def DoRelaxation(self,u,v):
        return v.value = u.value + w(u,v)
        
    #Input: Nodes u and v, number of problem graph node n
    #Side Effetcs Update parent of v, f(v), Open and Closed
    def Improve(self,u,v,n):
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
                Open.put(v)     #Enqueue v to Open
        
        else:
            v.parent = u
            v.value = u.value + w(u,v) #Initialize f(v) = f(u) + w(u,v)
            self.Open.put(v) #Enqueue v in Open




def main():
    var = Mesh(3,4,1,1)

if __name__ == "__main__":
    main()
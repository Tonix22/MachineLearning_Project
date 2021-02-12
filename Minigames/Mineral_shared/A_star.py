class nodoA:
    def __init__(self,valor,coordenada):
        self.coordenada = coordenada
        self.valor = valor
    def __repr__(self):
        return self.valor
class A:

    def enCola(self,coordenada):
        for x in self.open:
            if (x.coordenada == coordenada):
                return True
        for x in self.close:
            if (x.coordenada == coordenada):
                return True
        return False

    def __init__(self,mapa,inicio):
        self.mapa = mapa
        self.open = list()
        self.close = list()
        self.inicio = inicio
        self.valorInicial = mapa[inicio[1]][inicio[0]]
        self.area = [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]
    
    def aplus(self):
        nodo1 = nodoA(self.mapa[self.inicio[1]][self.inicio[0]],self.inicio)
        self.open.append(nodo1)
        while(len(self.open)>0):
            #exploración modo de termino en caso de que no existan numeros mayores alrededor
            actual = self.open.pop()
            maxVal = actual.valor
            for pixel in self.area:
                if(actual.coordenada[0]+pixel[0]>=0 and actual.coordenada[0]+pixel[0]<=83 and actual.coordenada[1]+pixel[1]>=0 and actual.coordenada[1]+pixel[1]<=63):
                    print(f"Cordenadas x{actual.coordenada[0]},y{actual.coordenada[1]}")
                    val=self.mapa[actual.coordenada[1]+pixel[1]][actual.coordenada[0]+pixel[0]]
                    c = (actual.coordenada[0]+pixel[0],actual.coordenada[1]+pixel[1])
                    nodo = nodoA(val,c)
                    maxVal=max(maxVal,val)
                    if (self.enCola(c)== False):
                        self.open.append(nodo)
            if (actual.valor !=self.valorInicial and maxVal == actual.valor):
                return(actual.coordenada) #finaliza la busqueda
            self.open.sort(key=lambda x: x.valor, reverse = False)
            self.close.append(actual)
        return ((0,0))


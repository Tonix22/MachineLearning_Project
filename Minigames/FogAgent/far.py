import random
import numpy as np
class far():
  def __init__(self):
    self.valores = self.inicializaMatriz()

  def inicializaMatriz(self):
    temp = list()
    for x in range(56): 
      temp.append([(23+int(x/8)*5,15+(x%8)*5),0])
    return temp

  def density(self,matriz,coor,distancia,densidad):
      imagen =[(-2,-2),(-2,-1),(-2,0),(-2,1),(-2,2),(-1,-2),(-1,-1),(-1,0),(-1,1),(-1,2),(0,-2),(0,-1),(0,0),(0,1),(0,2),(1,-2),(1,-1),(1,0),(1,1),(1,2),(2,-2),(2,-1),(2,0),(2,1),(2,2)]
      density = list()
      point_a = np.array(coor)      
      for x in self.valores:
          point_b = np.array((x[0][1],x[0][0]))
          distance = distancia/ np.linalg.norm(point_a - point_b)
          temp = 0
          for y in imagen:
              if (matriz[x[0][0]+y[0]][x[0][1]+y[1]]==0):
                temp += 1
          density.append(temp)
          x[1] = temp * densidad + distance

      temp = self.valores[0]
      for node in self.valores:
        if (node[1]>temp[1]):
          temp=node
      return temp[0]        



matriz = [[0]*64]*64
for row in range(64):
    for col in range(64):
        matriz[row][col]=random.randint(0,2)

x= far()
#x.inicializaMatriz()
x.density(matriz,(30,30),100,1)
for i in x.valores:
    print (i)
print("El mayor es:")
print (x.density(matriz,(30,30),100,1))
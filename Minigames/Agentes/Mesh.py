from Params import *
class Node:
    def __init__(self):
        self.value = (1<<31)-1 ## max int of 32 bits
        #Neighbors number conter clockwise
        #posiciones  0=U  1=UR 2=R  3=DR 4=D  5=DL 6=L  7=UL
        self.cord = (0,0)
        self.parent = None
        #self.Neighbors = [None,None,None,None,None,None,None,None] # max posible 8 neightbors
        self.Neighbors = {
            'UP'         : None,
            'UP_RIGHT'   : None,
            'RIGHT'      : None,
            'RIGHT_DOWN' : None,
            'DOWN'       : None,
            'DOWN_LEFT'  : None,
            'LEFT'       : None,
            'UP_LEFT'    : None
        }


class Mesh:
    def __init__ (self,row,col):
        self.col_size    = col
        self.row_size    = row
        self.Grid=[[Node()for i in range(col)] for j in range(row)]# actual representation of grid
        self.fill()
    def Place_character(self,x,y):
        block_size = (X_MAP_SIZE// self.col_size)//2
        for row in self.Grid:
            for elem in row:
                if( x < (elem.cord[0]+block_size)
                and x >= (elem.cord[0]-block_size)):
                    if( y < (elem.cord[1]+block_size)
                    and y >= (elem.cord[1]-block_size)):
                        return elem



    def fill(self):
        col_limit = self.col_size-1
        row_limit = self.row_size-1
        for row in range(0,self.row_size):
            for col in range(0,self.col_size):

                prev_row = row-1
                next_row = row+1
                prev_col = col-1
                next_col = col+1
                
                self.Grid[row][col].cord = (((X_MAP_SIZE//(self.col_size*2))*((col+1)*2-1)),\
                                            ((Y_MAP_SIZE//(self.row_size*2)*((row+1)*2-1))))
                
                if (row  > 0):                                 #UP
                    self.Grid[row][col].Neighbors['UP']         = self.Grid[prev_row][col]
                if (row > 0 and col < (col_limit)):            #UP RIGHT
                    self.Grid[row][col].Neighbors['UP_RIGHT']   = self.Grid[prev_row][next_col]
                if  col  < (col_limit):                        #RIGHT
                    self.Grid[row][col].Neighbors['RIGHT']      = self.Grid[row]     [next_col]
                if (row < row_limit and col < (col_limit)):    #RIGHT DOWN
                    self.Grid[row][col].Neighbors['RIGHT_DOWN'] = self.Grid[next_row][next_col]
                if (next_row  < row_limit):                    #DOWN
                    self.Grid[row][col].Neighbors['DOWN']       = self.Grid[next_row][col]
                if (next_row < row_limit and col >= 1):        #DOWN LEFT
                    self.Grid[row][col].Neighbors['DOWN_LEFT']  = self.Grid[next_row][prev_col]
                if (col >= 1):                                 #LEFT
                    self.Grid[row][col].Neighbors['LEFT']       = self.Grid[row]     [prev_col]
                if (next_row < row_limit and col >= 1):        #UP LEFT
                    self.Grid[row][col].Neighbors['UP_LEFT']    = self.Grid[prev_row][prev_col]

def main():
    var = Mesh(2,2)
    var.Place_character(10,70)

if __name__ == "__main__":
    main()
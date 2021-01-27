
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
        self.col    = col
        self.row    = row
        self.Grid=[[Node()for i in range(col)] for j in range(row)]# actual representation of grid
        self.fill()

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
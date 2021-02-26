import sys
from params import *


class MinMax:
	def __init__(self):
		self.marines = 3
		self.mapa = None

	def set_mapa(self,mapa):
		self.mapa = mapa


	def minimax(self,depth, alpha, beta, maximizingPlayer,coor):
		hijos = self.mapa.expand(coor)
		if depth == 0 or len(hijos)==0:
			return self.mapa.chanceMatrix[coor[1]][coor[0]], coor

		if maximizingPlayer:
			maxEval = (-1)*infinity
			for child in hijos:
				eval, fromCoor = self.minimax(depth - 1, alpha, beta, False,child)
				maxEval = max(maxEval, eval)
				alpha = max(alpha, eval)
				if beta <= alpha:
					break
			return maxEval, fromCoor

		else:
			minEval = infinity
			for child in hijos:
				eval, fromCoor = self.minimax(depth - 1, alpha, beta, True,child)
				minEval = min(minEval, eval)
				beta = min(beta, eval)
				if beta <= alpha :
					break
			return minEval, fromCoor


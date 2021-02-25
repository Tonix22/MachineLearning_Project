import sys

intinity = (2<<31)-1
marines = 3

def minimax(position, depth, alpha, beta, maximizingPlayer):
	if depth == 0 or marines == 0:
		return 

	if maximizingPlayer:
		maxEval = (-1)*infinity
		for each child of position
			eval = minimax(child, depth - 1, alpha, beta false)
			maxEval = max(maxEval, eval)
			alpha = max(alpha, eval)
			if beta <= alpha
				break
		return maxEval

	else:
		minEval = infinity
		for each child of position
			eval = minimax(child, depth - 1, alpha, beta true)
			minEval = min(minEval, eval)
			beta = min(beta, eval)
			if beta <= alpha
				break
		return minEval


minimax(currentPosition, 3, intinity*(-1), intinity, true)
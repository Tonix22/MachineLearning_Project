import Height_map as hm

#MAP data
X_SIZE = 84
Y_SIZE = 64
BRUSH_DIAMETER = 5
BRUSH_DECREMENT = 10

MAP = hm.Heightmap(X_SIZE, Y_SIZE, 0)
brush = hm.Brush(BRUSH_DIAMETER)
brush.Gaussian(BRUSH_DECREMENT)
#MAP.stampsOnMap([],brush)

#ALGORITHM


HILL_CLIMB    = False
ANNELING_RUN  = not HILL_CLIMB


#Anneling
ITERATIONS = 100000
TEMPERATURE_INIT = 2000
ALPHA = .96
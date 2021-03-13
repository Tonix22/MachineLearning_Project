from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import BeliefPropagation

class Explorer():
    def __init__(self):
        self.G = BayesianModel([('exploredUp', 'walk'), ('exploredDown', 'walk'),
                   ('exploredLeft', 'walk'), ('exploredRight', 'walk')])
        self.eUp_cpd = TabularCPD('exploredUp', 2, [[0.5], [0.5]])
        self.eDown_cpd = TabularCPD('exploredDown', 2, [[0.5], [0.5]])
        self.eLeft_cpd = TabularCPD('exploredLeft', 2, [[0.5], [0.5]])
        self.eRight_cpd = TabularCPD('exploredRight', 2, [[0.5], [0.5]])
        self.walk_cpd = TabularCPD('walk', 4,
        #exploredUp     #                   y                   |                    n
        #exploredDown   #         y                 n           |         y                 n           
        #exploredLeft   #   y         n     |    y         n    |    y         n     |    y         n   
        #exploredRight  # y    n    y    n     y    n   y    n    y    n     y    n   y    n     y    n
                       [[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], #walk up
                        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], #walk down
                        [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1], #walk left
                        [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7]], #walk right
                       evidence=['exploredUp', 'exploredDown', 'exploredLeft', 'exploredRight'],
                       evidence_card=[2, 2, 2, 2]) 
        G.add_cpds(self.eUp_cpd, self.eDown_cpd, self.eLeft_cpd, self.eRight_cpd, self.walk_cpd)
        bp = BeliefPropagation(G)
        bp.calibrate()
        
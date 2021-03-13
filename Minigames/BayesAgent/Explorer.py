from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import BeliefPropagation

class Explorer():
    def __init__(self):
        self.G = BayesianModel([('exploredUp', 'walk'), 
                                ('exploredDown', 'walk'),
                                ('exploredLeft', 'walk'), 
                                ('exploredRight', 'walk')])


        self.eUp_cpd    = TabularCPD(variable = 'exploredUp', 
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])
        self.eDown_cpd  = TabularCPD(variable = 'exploredDown', 
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])
        self.eLeft_cpd  = TabularCPD(variable = 'exploredLeft', 
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])
        self.eRight_cpd = TabularCPD(variable = 'exploredRight',
                                    variable_card = 2, 
                                    values = [[0.5], [0.5]])

        self.walk_cpd   = TabularCPD(variable = 'walk', 
                                    variable_card = 4,
        #explored Right     #                   y                   |                    n
        #explored Left   #         y                 n           |         y                 n           
        #explored Down   #   y         n     |    y         n    |    y         n     |    y         n   
        #explored Up  # y    n    y    n     y    n   y    n    y    n     y    n   y    n     y    n
               values = [[0.25, 0, 0, 0,   0, 0,   1, 0,    1, 0.5, 0,   0.33, 0,   0,   0.33, 0.25], #walk Right
                         [0.25, 0, 0, 0,   1, 0.5, 0, 0.34, 0, 0,   0.5, 0,    0,   0.5, 0.33, 0.25], #walk Left
                         [0.25, 0, 1, 0.5, 0, 0,   0, 0.33, 0, 0,   0.5, 0.33, 0.5, 0,   0.34, 0.25], #walk Down
                         [0.25, 1, 0, 0.5, 0, 0.5, 0, 0.33, 0, 0.5, 0,   0.34, 0.5, 0.5, 0,    0.25]],#walk Up
                       evidence=['exploredRight', 'exploredLeft', 'exploredDown', 'exploredUp'],
                       evidence_card=[2, 2, 2, 2])

        self.G.add_cpds(self.eUp_cpd, 
                        self.eDown_cpd, 
                        self.eLeft_cpd, 
                        self.eRight_cpd, 
                        self.walk_cpd)

        self.G.check_model()


        bp  = BeliefPropagation(self.G)
        res = bp.query(variables=["walk"], evidence={'exploredDown':0})
        print (res)

var = Explorer()
        
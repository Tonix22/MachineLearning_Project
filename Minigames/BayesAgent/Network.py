from pgmpy.models import BayesianModel
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import BeliefPropagation


#model conection
weather_model = BayesianModel([ ('Cloudy', 'Rain'),
                                ('Cloudy', 'Sprinkler'),
                                ('Sprinkler', 'Wet'),
                                ('Rain', 'Wet')])

#define values                              

cpd_poll  = TabularCPD(variable='Cloudy', variable_card=2,
                      values=[[0.5], [0.5]])


cpd_rain = TabularCPD(variable='Rain', variable_card=2,
                        values=[[0.8, 0.2], [0.2, 0.8]],
                        evidence=['Cloudy'],
                        evidence_card=[2])

cpd_sprinkler = TabularCPD(variable='Sprinkler', variable_card=2,
                        values=[[0.1, 0.5], [0.9, 0.5]],
                        evidence=['Cloudy'],
                        evidence_card=[2])                        


cpd_wet = TabularCPD(variable='Wet', variable_card=2,
                        values=[[0.99, 0.9, 0.9, 0],
                                [0.01, 0.1, 0.1, 1]],
                        evidence=['Rain', 'Sprinkler'],
                        evidence_card=[2, 2])



# Associating the parameters with the model structure.
weather_model.add_cpds(cpd_poll, cpd_rain, cpd_sprinkler, cpd_wet)

# Checking if the cpds are valid for the model.
weather_model.check_model()

bp = BeliefPropagation(weather_model)
#bp.calibrate()
#print(weather_model.get_cpds("Cancer"))
res = bp.query(variables=["Rain"], evidence={'Cloudy':1})
#print(weather_model.get_cpds("Wet"))

print (res)


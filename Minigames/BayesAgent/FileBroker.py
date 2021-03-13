import pandas as pd
class Bayes:
    def __init__(self):
        try:
            self.probabilities = pd.read_csv('probabilities.csv',header=0)
        except: 
            self.probabilities = pd.DataFrame([(0 , 0 , 0, 0, 0, 0, 0, 0, 0, 0)],
            columns=('A', 'B', 'C','D' ,'E','F','G','H','I','W'))
            self.save_file()

    def save_file(self):
        self.probabilities.to_csv('probabilities.csv',index=False)
    
    def del_node(self,var):#'X'
        del self.probabilities[var]

    def add_node(self,name,value):
        self.probabilities[name]= value 



a = Bayes()

#read data value
a.probabilities['A'][0] += 5
a.save_file()

print(a.probabilities)



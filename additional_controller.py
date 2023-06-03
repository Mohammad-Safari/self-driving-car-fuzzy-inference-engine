from fuzzy_controller import LinearMembership, Utils

GAS='gas'
LOW='low'
MEDIUM='medium'
HIGH='high'

CENTER_DIST='center_dist'
CLOSE='close'
MODERATE='moderate'
FAR='far'

class Gas(LinearMembership):
    def __init__(self):
        self.fuzzify_params = {
            LOW: lambda x: self.membership(x,(0,5),(0,1))+\
                self.membership(x,(5,10),(1,0)),
            MEDIUM: lambda x: self.membership(x,(0,15),(0,1))+\
                self.membership(x,(15,30),(1,0)),
            HIGH: lambda x: self.membership(x,(25,30),(0,1))+\
                self.membership(x,(30,90),(1,0))
        }
        self.fuzzy_labels = self.fuzzify_params.keys()
        
class Center(LinearMembership):
    def __init__(self):
        self.fuzzify_params = {
            CLOSE: lambda x: self.membership(x,(0,50),(1,0)),
            
            MODERATE: lambda x: self.membership(x,(40,50),(0,1))+\
                self.membership(x,(50,100),(1,0)),
            FAR: lambda x: self.membership(x,(90,200),(0,1))+\
                self.membership(x,(200,9999999),(1,1))            
        }
        self.fuzzy_labels = self.fuzzify_params.keys()

class FuzzyGasController():
    def __init__(self):
        self.rules=Utils.read_rules('additional_rules.txt')
         # Right distance membership
        self.center_dist_membership = Center()
        # Left distance membership
        self.gas_pedal_membership = Gas()
        
    def fuzzify(self, center_dist):
        return self.center_dist_membership.fuzzify(center_dist)
    
    def defuzzify(self, fuzzy_gas_pedal):
        return self.gas_pedal_membership.defuzzify(fuzzy_gas_pedal, space_range=(0,100,0.01))
    
    def inference(self, center_dist):
        return Utils.generic_inference(center_dist, self.rules)

    def decide(self, center_dist):
        """
        main method for doin all the phases and returning the final answer for gas
        """
        fuzzy_values = self.fuzzify(center_dist)
        fuzzy_output = self.inference(fuzzy_values)
        final_output = self.defuzzify(fuzzy_output)

        return final_output
    
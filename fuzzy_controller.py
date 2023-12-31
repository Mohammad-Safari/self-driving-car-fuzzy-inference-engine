import re
import numpy as np

D_R = 'd_R'
CLOSE_R = 'close_R'
MODERATE_R = 'moderate_R'
FAR_R = 'far_R'

D_L = 'd_L'
CLOSE_L = 'close_L'
MODERATE_L = 'moderate_L'
FAR_L = 'far_L'

ROTATE = 'Rotate'
LOW_RIGHT = 'low_right'
HIGH_RIGHT = 'high_right'
NOTHING = 'nothing'
LOW_LEFT = 'low_left'
HIGHT_LEFT = 'high_left'

class LinearMembership():
    def __init__(self):
        """
        in this part self.fuzzify_params and self.fuzzify_lables must be initialized
        """
        pass
    
    def membership(self, x, x_range, m_range):
        """
        according to output range and input range, it calulcates 
        the linear membership of given point(x) based on the line
        """
        linear_growth = (m_range[1]-m_range[0])/(x_range[1]-x_range[0])
        return (x-x_range[0])*linear_growth+m_range[0] if x>=x_range[0] and x<x_range[1] else 0
    
    def fuzzify(self, x):
        return {key:fn(x) for key, fn in self.fuzzify_params.items()}
    
    def defuzzify(self, fuzzy_output, space_range=(-50,50,0.01)):
        space = np.arange(*space_range)
        max_values = [self.fuzzify(v) for v in space]
        membership_values = [max([min([max_value[flabel], fuzzy_output[flabel]]) for flabel in self.fuzzy_labels])
                            for max_value in max_values]
        marginal_sum = np.sum(membership_values)
        return 0 if marginal_sum==0 else np.sum(space * membership_values) / marginal_sum 
    
class Right(LinearMembership):
    def __init__(self):
        self.fuzzify_params = {
            CLOSE_R:self.close_R,
            MODERATE_R:self.moderate_R,
            FAR_R:self.far_R
        }
        self.fuzzy_labels = self.fuzzify_params.keys()
    
    def close_R(self, x):
        return self.membership(x, (0,50), (1, 0))

    def moderate_R(self, x):
        return self.membership(x, (35, 50), (0, 1)) + \
            self.membership(x, (50, 65), (1, 0))

    def far_R(self, x):
        return self.membership(x, (50, 100), (0, 1))
    
class Left(LinearMembership):
    def __init__(self):
        self.fuzzify_params = {
            CLOSE_L:self.close_L,
            MODERATE_L:self.moderate_L,
            FAR_L:self.far_L
        }
        self.fuzzy_labels = self.fuzzify_params.keys()
    
    def close_L(self, x):
        return self.membership(x, (0,50), (1, 0))

    def moderate_L(self, x):
        return self.membership(x, (35, 50), (0, 1)) + \
            self.membership(x, (50, 65), (1, 0))

    def far_L(self, x):
        return self.membership(x, (50, 100), (0, 1))

class Rotation(LinearMembership):
    def __init__(self):
        self.fuzzify_params = {
            LOW_RIGHT: self.low_right,
            HIGH_RIGHT: self.high_right,
            NOTHING: self.nothing,
            LOW_LEFT: self.low_left,
            HIGHT_LEFT: self.high_left
        }
        self.fuzzy_labels = self.fuzzify_params.keys()
    
    def high_right(self, x):
        return self.membership(x, (-50, -20), (0, 1)) + \
            self.membership(x, (-20, -5), (1, 0))
            
    def low_right(self, x):
        return self.membership(x, (-20, -10), (0, 1)) + \
            self.membership(x, (-10, 0), (1, 0))

    def nothing(self, x):
        return self.membership(x, (-10, 0), (0, 1)) + \
            self.membership(x, (0, 10), (1, 0))

    def low_left(self, x):
        return self.membership(x, (0, 10), (0, 1)) + \
            self.membership(x, (10, 20), (1, 0))

    def high_left(self, x):
        return self.membership(x, (5, 20), (0, 1)) + \
            self.membership(x, (20, 50), (1, 0))

class Utils:
    def parse_rule(rule_string):
        pattern = r'IF \((\w+) IS (\w+) \)( (AND|OR) \((\w+) IS (\w+)\))?  THEN ([\s+(\w+) IS (\w+)]+)'    
        match = re.match(pattern, rule_string)
        if not match:
            raise ValueError(f"Invalid rule: {rule_string}")
        groups = match.groups()

        antecedent = {groups[0]: groups[1]}
        if groups[3:6] != [None]*3 :
            antecedent['Operator'] = groups[3]
            antecedent[groups[4]] = groups[5]

        consequents = re.findall(r'(\w+) IS (\w+)', groups[-1])
        return {'antecedent': antecedent, 'consequent': dict(consequents)}

    def read_rules(file_path):
        with open(file_path) as f:
            return [Utils.parse_rule(line.strip()) for line in f]

    def generic_inference(fuzzy_values, rules):
        output = {}
        for rule in rules:
            ant, cons = [list(ruleValue.values()) for ruleValue in rule.values()]
            if 'AND' in ant or 'OR' in ant:
                activation = min([fuzzy_values[ant[0]], fuzzy_values[ant[2]]]) if str(ant[1]).lower()=='and' \
                    else max([fuzzy_values[ant[0]], fuzzy_values[ant[2]]]) # OR operator
            else:
                activation = fuzzy_values[ant[0]]
                
            for act in cons:
                if act in output:
                    output[act] = max(output[act], activation)
                else:
                    output[act] = activation

        return output

class FuzzyController:
    def __init__(self):
        self.rules = Utils.read_rules('rules.txt')
        # Right distance membership
        self.right_membership = Right()
        # Left distance membership
        self.left_membership = Left()
        # Wheel rotation membership
        self.rotate_membership = Rotation()

    # Fuzzification method
    def fuzzify(self, left_dist, right_dist):
        return {
            # Fuzzify right distance
            **self.right_membership.fuzzify(right_dist),
            # Fuzzify left distance
            **self.left_membership.fuzzify(left_dist)
        }
    
    # Inference method
    def inference(self, fuzzy_values):
        return Utils.generic_inference(fuzzy_values, self.rules)

    # Defuzzification method
    def defuzzify(self, fuzzy_output):
        return self.rotate_membership.defuzzify(fuzzy_output)
        
    # Main decision-making method
    def decide(self, left_dist, right_dist):
        fuzzy_values = self.fuzzify(left_dist, right_dist)
        fuzzy_output = self.inference(fuzzy_values)
        final_output = self.defuzzify(fuzzy_output)

        return final_output
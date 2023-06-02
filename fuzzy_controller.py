import re

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
    def membership(self, x, x_range, m_range):
        linear_growth = (m_range[1]-m_range[0])/(x_range[1]-x_range[0])
        return (x-x_range[0])*linear_growth+m_range[0] if x>=x_range[0] and x<x_range[1] else 0
    
    def fuzzify(self, x):
        pass
    
class Right(LinearMembership):
    def close_R(self, x):
        return self.membership(x, (0,50), (1, 0))

    def moderate_R(self, x):
        return self.membership(x, (35, 50), (0, 1)) + \
            self.membership(x, (50, 65), (1, 0))

    def far_R(self, x):
        return self.membership(x, (50, 1), (0, 1))

    def fuzzify(self, x):
        fuzzy_values = {}
        fuzzy_values[CLOSE_R] = self.close_R(x)
        fuzzy_values[MODERATE_R] = self.moderate_R(x)
        fuzzy_values[FAR_R] = self.far_R(x)
        return fuzzy_values
    
class Left(LinearMembership):
    def close_L(self, x):
        return self.membership(x, (0,50), (1, 0))

    def moderate_L(self, x):
        return self.membership(x, (35, 50), (0, 1)) + \
            self.membership(x, (50, 65), (1, 0))

    def far_L(self, x):
        return self.membership(x, (50, 1), (0, 1))
    
    def fuzzify(self, x):
        fuzzy_values = {}
        fuzzy_values[CLOSE_L] = self.close_L(x)
        fuzzy_values[MODERATE_L] = self.moderate_L(x)
        fuzzy_values[FAR_L] = self.far_L(x)
        return fuzzy_values

class Rotation(LinearMembership):
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
            
    def fuzzify(self, x):
        fuzzy_values = {}
        fuzzy_values[LOW_RIGHT] = self.low_right(x)
        fuzzy_values[HIGH_RIGHT] = self.high_right(x)
        fuzzy_values[NOTHING] = self.nothing(x)
        fuzzy_values[LOW_LEFT] = self.low_left(x)
        fuzzy_values[HIGHT_LEFT] = self.high_left(x)
        return fuzzy_values


class FuzzyController:
    def __init__(self):
        self.rules = self.read_rules('rules.txt')
        # Right distance membership
        self.right_membership = Right()
        # Left distance membership
        self.left_membership = Left()
        # Wheel rotation membership
        self.rotate_membership = Rotation()

    def parse_rule(self, rule_string):
        m = re.match(r'IF \((\w+) IS (\w+) \) (AND|OR) \((\w+) IS (\w+)\)  THEN  (\w+) IS (\w+)', rule_string)
        if not m:
            raise ValueError(f"Invalid rule: {rule_string}")
        # TODO: implement possibility of single antecedent and multiple consequent in rules
        return {
            'antecedent': {m.group(1): m.group(2), 'Operator':m.group(3), m.group(4): m.group(5)},
            'consequent': {m.group(6): m.group(7)}
        }

    def read_rules(self, file_path):
        with open(file_path) as f:
            return [self.parse_rule(line.strip()) for line in f]

    # Fuzzification method
    def fuzzify(self, left_dist, right_dist, wheel_rotation):
        return {
            # Fuzzify right distance
            **self.right_membership.fuzzify(right_dist),
            # Fuzzify left distance
            **self.left_membership.fuzzify(left_dist),
            # Fuzzify wheel rotation
            **self.rotate_membership.fuzzify(wheel_rotation)
        }
    
    # Inference method
    def inference(self, fuzzy_values):
        rules = self.rules
        output = {}
        for rule in rules:
            ant, cons = [list(ruleValue.values()) for ruleValue in rule.values()]
            if 'Operator' in ant:
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

    # Defuzzification method
    def defuzzify(self, fuzzy_output):
        pass        

    # Main decision-making method
    def decide(self, left_dist, right_dist):
        pass

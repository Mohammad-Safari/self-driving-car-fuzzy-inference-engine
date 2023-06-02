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
    def __init__(self):
        """
        in this part self.fuzzify_params and self.fuzzify_lables must be initialized
        """
        pass
    
    def membership(self, x, x_range, m_range):
        linear_growth = (m_range[1]-m_range[0])/(x_range[1]-x_range[0])
        return (x-x_range[0])*linear_growth+m_range[0] if x>=x_range[0] and x<x_range[1] else 0
    
    def fuzzify(self, x):
        return {key:fn(x) for key, fn in self.fuzzify_params.items()}
    
    def defuzzify(self, x, fuzzy_output):
        max_value = self.fuzzify(x)
        return max([min([max_value[flabel], fuzzy_output[flabel]]) for flabel in self.fuzzy_labels])
    
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
        return self.membership(x, (50, 1), (0, 1))
    
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
        return self.membership(x, (50, 1), (0, 1))

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
    def defuzzify(self, fuzzy_output, rng=(-50,50), delta=1):
        space = list(range(*rng,delta))
        merged_membership = [self.rotate_membership.defuzzify(v, fuzzy_output) for v in space]
        return sum(merged_membership)/len(space)
        
    # Main decision-making method
    def decide(self, left_dist, right_dist):
        pass

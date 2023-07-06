# self driving car by fuzzy inference engine

## Structure

In this project, along with the class of fuzzy controllers used in the simulator, the classes related to the membership in each of the fuzzy sets of proximity to the left, right, center(accross), wheel rotation, and gas pedal are also defined.
`membership` , `fuzzify` , and `defuzzify` all have common implementations in their parent class. In the `Right`, `Left` and `Rotate` classes, in the `__init__` method, only the set parameters including the **set labels** and **membership functions** 
of each of them are stored in a dictionary in the parameters variable and the names of the sets (labels) are stored in the fuzzy_labels variable of the class.

Finally, the `fuzzify` and `defuzzify` methods of the controller use the **methods of the belonging classes** and the main controller is not directly involved in their calculations.
The implementation of the `inference` method is general purpose and completely placed in the Utils class. The `decide` method is also used as the interface used in the `simulator.py`.

In addition to `inference`, the `Utils` class contains functions that read the rules and parse them for use. The structure of the speed fuzzy controller is similar to the steering wheel rotation controller.

## Functionality

In the `decide` method, which is actually the interface between the controller and the simulator, first the absolute distances from the left and right are given as input to the method, and finally an absolute output is given to the simulator to rotate the steering wheel.

Bsides, in the `decide` method, the first task is to fuzzify the input values, which is done by the fuzzify method of the controller, and the values of the distance from the left and the right are grouped in three labels/groups, close, balanced, and far, and returned to decide.

Then the `inference` method, according to the rules that were loaded from the file during the construction of the controller with the help of the `parse_rule` and `read_rules` method, 
* based on the membership status of the antecedent combination,
* based on the AND and OR operators,
* and the percentage of consequent activity (if several different rules lead to activation, they share consequences, the level of activation of the consequence of the rule with the highest percentage of activation)
is return by the method.

Finally, in the `defuzzify` method, by approximately calculating the **center of mass** of the output parameter, i.e. the **rotation of the command** and **gas pedal**, it calculates the center of mass of the active area and returns the **absolute value** through its defuzzify call.
One of the important parameters of this step is the integration delta, which is effective in the accuracy of center of mass approximation and finally decision making.

## usage
run `python simulator.py` in the terminal

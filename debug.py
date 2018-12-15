# debug usage for newly defined methods

from game import *
from agent import *
s1 = Shape(2)
s2 = Shape(4)
conf1 = Configuration(5, 10)
conf2 = Configuration(5, 10)
conf3 = Configuration(5, 10)
conf1.fall(s2, 1)
conf2.copyGrid(conf1)
conf3.copyGrid(conf1)
conf2.fall(s1, 1)
conf3.fall(s1, 2)
agent = Agent()
print conf1
print conf2
print agent.contact(conf1, conf2)
print conf3
print agent.contact(conf1, conf3)

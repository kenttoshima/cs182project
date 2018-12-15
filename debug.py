# debug usage for newly defined methods

from game import *
from agent import *
from random import randint

width, height = 5, 10

s = []
s.append(Shape(0))
s.append(Shape(1))
s.append(Shape(2))
s.append(Shape(3))
s.append(Shape(4))
s.append(Shape(5))
s.append(Shape(6))
s.append(Shape(7))
conf1 = Configuration(width, height)
conf2 = Configuration(width, height)
conf3 = Configuration(width, height)
conf1.fall(s[randint(1, 7)], 1)
conf1.fall(s[randint(1, 7)], 2)
conf1.fall(s[randint(1, 7)], 1)
conf2.copyGrid(conf1)
conf3.copyGrid(conf1)
nextfalltype = randint(1, 7)
conf2.fall(s[nextfalltype], 1)
conf3.fall(s[nextfalltype], 2)
agent = Agent()
print conf1
print conf2
print agent.line_fill(conf1, conf2)
print conf3
print agent.line_fill(conf1, conf3)

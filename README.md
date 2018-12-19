# Vanilla Agent 
Please refer to Sections 2.1, 2.1 and 2.3 in the paper Obstacles in Abstracting and Learning Tetris

## Getting Started
```
python test.py
```
Input the number of times you want the agent to learn. In the paper, the number of times to run is 10,000. However, this can be more or less. 

At the end, it'll show a plot with scores in blue and Q-value hit rates in green. 
Then, it'll show a dump of the Q-value table. The following is the format of the table:

```
([State space], Next piece)|(column, rotation)   <Q-Value>
```

## Try These

Every parameter that needs to be tweaked can be modified in test.py. 
The parameters of EPSILON, LEARNING_RATE, SCORE_WEIGHT, GAMEOVER_PENALTY, HOLE_WEIGHT, LIVING_REWARD and DELAY can all be changed to your liking.

Try setting GAMEOVER_PENALTY to a really high value like +100000. Observe the gameplay afterwards; you will see a rather suicidal agent
Try setting different values for HOLE_WEIGHT, both positive and negative, and see how it impacts the number of holes created.
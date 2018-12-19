# Vanilla Agent 
Please refer to Sections 2.4 in the paper Obstacles in Abstracting and Learning Tetris

## Getting Started
```
python test.py
```
Input the number of times you want the agent to learn. In the paper, the number of times to run is 10,000. However, this can be more or less. 

At the end, it'll show a plot with scores in blue and Q-value hit rates in green. 
Then, it'll show a dump of the Q-value table. The following is the format of the table:

```
([Active Layer], Next piece)|(column, rotation)   <Q-Value>
```

## Try These

Play around with different levels of the exploration eagerness and observe the hit rates. You will see that with the exploration function, the hit rate is only around 50% and even less for higher values of eagerness. It would be interesting to dump the q-values and run various statistics on the q-values to determine precisely why this is happening.
from agent import Agent
import matplotlib.pyplot as plt

#computes a rolling average over a list, to smooth out the data
def moving_average(in_list, window_size=200):
    ret = []
    for i in range(len(in_list)-window_size):
        to_average = in_list[i:i+window_size]
        ret.append(sum(to_average)/float(window_size))
    return ret 


EAGERNESS = 500           #How eager we want to be when exploring using our exploration function. Higher = more willing to explore the unknown
LEARNING_RATE = (.33,500) #(n,k) where alpha = (k*n)/(n+iter). First parameter controls initial alpha, second is rate of decay (lower is faster)
SCORE_WEIGHT = 1          #In most cases, set this to 1. In determining rewards, how are scores weighed relative to GAMEOVER_PENALTY, HOLE_WEIGHT and LIVING_REWARD?
GAMEOVER_PENALTY = -100   #Reward for a Q-State that results in no successor states (ie. game over) Set this to a positive value like +10000 for a suicidal agent
HOLE_WEIGHT = -50         #Reward for each new hole that a move creates 
LIVING_REWARD = 0         #Not discussed in the paper, but feel free to mess around with this 
DELAY = 1                 #In the "rolling window" reward model, setting the value of DELAY sets the size of the sliding window. 
                          #In updating a Q-Value, the agent counts all rewards within DELAY moves ahead of the move

if __name__ == '__main__':
    stop = input("How many times do you want to learn? (Recommended: 10,000): ")

    agent = Agent(width = 4, height = 6, delay = DELAY, learning_rate = LEARNING_RATE, exploration_eagerness = EAGERNESS, \
        gameover_penalty = GAMEOVER_PENALTY, score_weight = SCORE_WEIGHT, hole_weight = HOLE_WEIGHT, living_reward = LIVING_REWARD)
    query_hit_rate = []
    
    #Below is the learning process. query_hit_rate measures percentage of Q-value hits. Scores are stored in agent.results.
    for i in range(stop):
        agent.learn()
        query_hit_rate.append( (agent.query_hit*100.0)/agent.query_count )

    #Make a plot. Blue line represents score over time
    #Green plot represents %-hit rate over time
    #Data is plotted as a moving average because an individual game is very varied.
    plt.plot(moving_average(agent.results))
    plt.plot(moving_average(query_hit_rate))
    plt.show()

    #Dump the Q-value table to stdout
    for key in agent.qvalues:
        print key + "\t" + str(agent.qvalues[key])

    #Play a game using the now-trained agent 
    agent.play(visualize=True)
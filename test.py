from agent import Agent
import matplotlib.pyplot as plt

#computes a rolling average over a list, to smooth out the data
def moving_average(in_list, window_size=200):
    ret = []
    for i in range(len(in_list)-window_size):
        to_average = in_list[i:i+window_size]
        ret.append(sum(to_average)/float(window_size))
    return ret 

#Do not change these parameters, or else the heuristics may break
#See below comment for more details on why.
EAGERNESS = 500          
LEARNING_RATE = (.33,500)
SCORE_WEIGHT = 1        
GAMEOVER_PENALTY = -100  
HOLE_WEIGHT = -50      
LIVING_REWARD = 0     
DELAY = 1            
                      

#Some nice heuristics to try. 
heuristic_handcrafted = [10,-20,100,-0.5]  #This heuristic has fitness of approximately 25000
heuristic_strong = [0.09698179424782494, -0.14876088409189406, 0.9840940704671141, -0.004857099971925686] #fitness approximately 31240
heuristic_weak = [-0.5668391570991367, -0.01505282799932104, 0.4121633349098923, -0.713153677480751] #fitness approximately 19520
#Tests the agent running ONLY the heuristic (Does not use any learning)
#Displays the scores (which should be pretty constant over the number of runs because it's not learning anything)
#then dumps the Heuristic Q-value table to stdout. All Q-values in the table are calculated lazily by the heuristic being passed into this function
def test_heuristic(h):
    stop = input("How many times do you want to learn? (Recommended: 10,000): ")
    agent = Agent(width = 4, height = 6, delay = 1, learning_rate = (0,100), exploration_eagerness = 0, \
        gameover_penalty = 0, score_weight = 0, hole_weight = 0, living_reward = 0)
    agent.edit_weights(h)
    for i in range(stop):
        agent.play()
    plt.plot(moving_average(agent.results))
    plt.show()
    #Dump the Q-value table to stdout
    for key in agent.qvalues:
        print key + "\t" + str(agent.qvalues[key])

if __name__ == '__main__':
    test_heuristic(heuristic_strong)

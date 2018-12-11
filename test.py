if __name__ == '__main__':
    from agent import Agent
    from time import time
    agent = Agent(width = 10, height = 20, delay = 25, alpha = 0.8, epsilon = 0.8)
    stop = input("How many times do you want to learn?: ")
    start_time = time()
    for i in range(stop):
        if i % 100 == 0:
            elapsed_time = time() - start_time
            print elapsed_time
            print i
        agent.learn()
    for key in agent.qvalues:
        if agent.qvalues[key] != 0.:
            state, action = key
            print str(state) + ", " + str(action) + ": " + str(agent.qvalues[key])
    agent.plotresults()

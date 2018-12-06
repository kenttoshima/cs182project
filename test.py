if __name__ == '__main__':
    from agent import Agent
    agent = Agent(width = 6, height = 15, delay = 10, alpha = 0.6, epsilon = 0.8)
    stop = input("How many times do you want to learn?: ")
    for i in range(stop):
        agent.learn()
    for key in agent.qvalues:
        if agent.qvalues[key] != 0.:
            state, action = key
            print str(state) + ", " + str(action) + ": " + str(agent.qvalues[key])
    agent.plotresults()

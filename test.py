if __name__ == '__main__':
    from agent import Agent
    agent = Agent(width = 10, height = 20, delay = 30, alpha = 0.6, epsilon = 0.8)
    stop = input("How many times do you want to learn?: ")
    for i in range(stop):
        agent.learn()
    for key in agent.qvalues:
        if agent.qvalues[key] != 0.:
            state, action = key
            print str(state) + ", " + str(action) + ": " + str(agent.qvalues[key])

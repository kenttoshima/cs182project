if __name__ == '__main__':
    from agent import Agent
    agent = Agent(width = 4, height = 12, delay = 2, alpha = 0.6, epsilon = 0.8)
    stop = input("How many times do you want to learn?: ")

    query_hit_rate = []
    for i in range(stop):
        agent.learn()
        query_hit_rate.append( (agent.query_hit*1.0)/agent.query_count )

    for key in agent.qvalues:
        if agent.qvalues[key] != 0.:
            state, action = key
            print str(state) + ", " + str(action) + ": " + str(agent.qvalues[key])


    agent.learn(True)


    agent.plotresults([2000*i for i in query_hit_rate])

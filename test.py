if __name__ == '__main__':
    from agent import Agent
    agent = Agent(width = 4, height = 12, delay = 2, alpha = 0.6, epsilon = 0.8)
    stop = input("How many times do you want to learn?: ")

    display_times = [100, 1000, 5000, 10000, 25000, 50000, 75000, 100000, 125000, 150000, 175000, 200000]

    query_hit_rate = []
    for i in range(stop):
        agent.learn()
        query_hit_rate.append( (agent.query_hit*1.0)/agent.query_count )
        if(i in display_times):
            print i 
            agent.plotresults([2000*j for j in query_hit_rate])

    qlist = agent.qvalues.items()
    qlist = sorted(qlist, key=lambda x: x[1])
    for (key, value) in qlist:
        if value != 0.:
            state, action = key
            print str(state) + ", " + str(action) + ": " + str(value)
#    for key in sorted(agent.qvalues, key=agent.qvalues.__getitem__):
#        if agent.qvalues[key] != 0.:
#            state, action = key
#            print str(state) + ", " + str(action) + ": " + str(agent.qvalues[key])


    agent.learn(True)


    agent.plotresults([2000*i for i in query_hit_rate])

if __name__ == '__main__':
    from agent import Agent
    agent = Agent(width = 4, height = 5, delay = 2, alpha = .05, epsilon = .3)
    stop = input("How many times do you want to learn?: ")

    display_times = [100, 1000, 5000, 10000, 25000, 50000, 75000, 100000, 125000, 150000, 175000, 200000]

    query_hit_rate = []
    for i in range(stop):
        agent.learn()
        query_hit_rate.append( (agent.query_hit*1.0)/agent.query_count )
        if(i in display_times):
            print i 
            print len([1 for key in agent.qvalues if (len(agent.q_val_history[key]) > 1) ])
            print sum(query_hit_rate)/float(len(query_hit_rate))
            agent.plotresults([500*j for j in query_hit_rate])


    for key in agent.qvalues:
        qvals = agent.q_val_history[key]
        if(len(qvals) > 1):
            (state, action) = agent.actual_state_action_pair[key]
            state.vis_state_action(action)
            print qvals
            print "-------------------------------------"



    # qlist = agent.qvalues.items()
    # qlist = sorted(qlist, key=lambda x: x[1])
    # for (key, value) in qlist:
    #     if value != 0.:
    #         state, action = key
    #         print str(state) + ", " + str(action) + ": " + str(value)
#    for key in sorted(agent.qvalues, key=agent.qvalues.__getitem__):
#        if agent.qvalues[key] != 0.:
#            state, action = key
#            print str(state) + ", " + str(action) + ": " + str(agent.qvalues[key])


    # agent.learn(True)


    agent.plotresults([2000*i for i in query_hit_rate])

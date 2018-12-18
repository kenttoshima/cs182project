if __name__ == '__main__':
    from agent import Agent
    agent = Agent(width = 4, height = 6, delay = 1, learning_rate = (.25,6000), exploration_eagerness = 100)
    #agent = Agent(width = 4, height = 6, delay = 1, learning_rate = (0,5000), exploration_eagerness = 0)
    agent.edit_weights([0.13036662567730464, -0.2264597794306298, 0.711253407422427, -0.6525634847581736])
    stop = input("How many times do you want to learn?: ")

    display_times = [800000]

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
        print key + "\t" + str(agent.qvalues[key])

    # for item in agent.results:
    #     print item 


    # for key in agent.qvalues:
    #     qvals = agent.q_val_history[key]
    #     if(len(qvals) > 1):
    #         (state, action) = agent.actual_state_action_pair[key]
    #         state.vis_state_action(action)
    #         print qvals
    #         print "-------------------------------------"



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


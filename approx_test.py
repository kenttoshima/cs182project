if __name__ == '__main__':
    from agent import ApproxQLearnAgent
    agent = ApproxQLearnAgent(width = 6, height = 12, delay = 12, alpha = 1/250.5, epsilon = 0.2)
    stop = input("How many times do you want to learn?: ")
    for i in range(stop):
        agent.learn()
    print agent.weight
    agent.plotresults()

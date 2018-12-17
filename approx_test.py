if __name__ == '__main__':
    from agent import ApproxQLearnAgent
    agent = ApproxQLearnAgent(width = 5, height = 10, delay = 10, alpha = 0.2, epsilon = 0.2)
    stop = input("How many times do you want to learn?: ")
    for i in range(stop):
        agent.learn()

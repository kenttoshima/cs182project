if __name__ == '__main__':
    from agent import Agent
    agent = Agent()
    agent.learn()
    print agent.qvalues
    agent.learn()
    print agent.qvalues
    agent.learn()
    print agent.qvalues

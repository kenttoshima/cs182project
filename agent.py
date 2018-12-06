from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError

class Agent(object):
    def __init__(self, width = 6, height = 22, delay = 10):
        self.width = width
        self.height = height
        self.delay = delay
        self.qvalues = {}

    def learn(self):
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        while True:
            tetris.next_turn()
            successor_list = self.getSuccessor(tetris)
            maxQvalue = float("-inf")
            bestStateAndAction = None
            for stateAndAction in successor_list:
                print stateAndAction[0], stateAndAction[1]
                if self.query(stateAndAction) > maxQvalue:
                    bestStateAndAction = stateAndAction
                    maxQvalue = self.query(stateAndAction)
            # if all the successors raise GameOverError
            if bestStateAndAction == None:
                nextAction = Action(1, 0)
            else:
                state, nextAction = bestStateAndAction
            try:
                tetris.drop(nextAction)
            except GameOverError as gameover:
                raise GameOverError

    def query(self, key):
        if key not in self.qvalues:
            print "new key: " + str(key[0]) + str(key[1])
            self.qvalues[key] = 0.0
        else:
            print "key exists" + str(key[0]) + str(key[1])
        print self.qvalues[key]
        return self.qvalues[key]

    def getSuccessor(self, tetris):
        nextShape = tetris.shape_list[tetris.turn]
        successor_list = []
        for i in range(4):
            nextShape.rotate()
            for i in range(tetris.width):
                x = i + 1
                newConfig = Configuration(tetris.width, tetris.height)
                newConfig.copyGrid(tetris)
                try:
                    newConfig.fall(nextShape, x)
                    # def of successor = (action, (active layer, height of baseline))
                    successor_list.append((State(newConfig, nextShape.type), (Action(x, nextShape.rotation))))
                except (InvalidMoveError, GameOverError):
                    pass
        # if successor_list is empty, meaning gameover in the next turn
        return successor_list

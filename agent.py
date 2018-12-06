from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError

class Agent(object):
    def __init__(self, width = 6, height = 20, delay = 10):
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
                if self.query(stateAndAction) > maxQvalue:
                    bestStateAndAction = stateAndAction
                    maxQvalue = self.query(stateAndAction)
            if bestStateAndAction == None:
                raise GameOverError
            state, nextAction = bestStateAndAction
            tetris.drop(nextAction)
            print state


    def query(self, key):
        if key not in self.qvalues:
            self.qvalues[key] = 0.
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

# TODO: test does not work
if __name__ == '__main__':
    tetris = Tetris(6, 10, False, [1,4,2,5,2,3,2,6,3])
    while True:
        tetris.run()

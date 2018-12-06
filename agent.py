from game import Tetris, Configuration, Action, InvalidMoveError, GameOverError

class State(object):
    def __init__(self, tetris):
        self.active_layer, base_height = tetris.active_layer()
        self.base_zone = base_height / (tetris.height / 3.0)
        self.nextShapeType = tetris.shape_list[tetris.turn].type

    def __str__(self):
        return str((self.active_layer, self.base_zone, self.nextShapeType))

class Agent(object):
    def __init__(self, width, height, delay, )
        # TODO: need to be able to learn from a lot of games
        tetris = Tetris(6, 10, True, [])



    def getSuccessor(self):
        nextShape = tetris.shape_list[self.turn]
        successor_list = []
        for i in range(4):
            nextShape.rotate()
            for i in range(tetris.width):
                x = i + 1
                newConfig = Configuration(tetris.width, tetris.height)
                newConfig.copyGrid(tetris)
                try:
                    newConfig.fall(nextShape, x)
                    print newConfig
                    # def of successor = (action, (active layer, height of baseline))
                    successor_list.append((Action(x, nextShape.rotation), newConfig.active_layer()))
                except (InvalidMoveError, GameOverError):
                    pass
        # if successor_list is empty, meaning gameover in the next turn
        return successor_list

# TODO: test does not work
if __name__ == '__main__':
    tetris = Tetris(6, 10, False, [1,4,2,5,2,3,2,6,3])
    while True:
        tetris.run()

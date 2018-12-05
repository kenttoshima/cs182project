from game import Tetris, Configuration, InvalidMoveError, GameOverError

class Agent(Tetris):
    def __init__
        pass

    def getSuccessor(self):
        nextShape = self.shape_list[self.turn]
        successor_list = []
        for i in range(4):
            nextShape.rotate()
            for i in range(self.width):
                x = i + 1
                newConfig = Configuration(self.width, self.height)
                newConfig.copyGrid(self)
                try:
                    newConfig.fall(nextShape, x)
                    print newConfig
                    # def of successor = (x coordinate, no. of rotation, active layer, height of baseline)
                    successor_list.append((x, nextShape.rotation, newConfig.active_layer()))
                except (InvalidMoveError, GameOverError):
                    pass
        # if successor_list is empty, meaning gameover in the next turn
        return successor_list

if __name__ == '__main__':
    tetris = Tetris(6, 10, False, [1,4,2,5,2,3,2,6,3])
    while True:
        tetris.run()
        print getSuccessor(tetris)

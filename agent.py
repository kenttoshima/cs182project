from game import Tetris, Configuration, InvalidMoveError, GameOverError

def getSuccessor(tetris):
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
                print newConfig
                successor_list.append((x, nextShape.rotation, newConfig.active_layer()))
            except (InvalidMoveError, GameOverError):
                pass
    return successor_list

if __name__ == '__main__':
    tetris = Tetris(6, 10, False, [1,4,2,5,2,3,2,6,3])
    while True:
        tetris.run()
        print getSuccessor(tetris)

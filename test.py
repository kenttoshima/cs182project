if __name__ == '__main__':
    from game import Tetris
    tetris = Tetris(10, 20, True, [])
    while True:
        tetris.run()

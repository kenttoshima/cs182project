from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError
from random import random, choice

class Agent(object):
    def __init__(self, width = 10, height = 20, delay = 20, alpha = 0.6, epsilon = 0.8):
        self.width = width
        self.height = height
        self.delay = delay
        self.alpha = alpha
        self.epsilon = epsilon
        self.qvalues = {}

    def learn(self):
        alpha = self.alpha
        epsilon = self.epsilon
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        while True:
            tetris.next_turn()
            successor_list = self.getSuccessor(tetris)
            maxQvalue = float("-inf")
            bestStateAndAction = None
            if not successor_list:
                nextAction = Action(1, 0)
            elif random() > (1 - epsilon):
                (state, nextAction) = choice(successor_list)
                self.query((state, nextAction))
            else:
                for stateAndAction in successor_list:
                    # print stateAndAction[0], stateAndAction[1]
                    if self.query(stateAndAction) > maxQvalue:
                        bestStateAndAction = stateAndAction
                        maxQvalue = self.query(stateAndAction)
                _state, nextAction = bestStateAndAction
            try:
                alpha *= 0.99
                epsilon *= 0.8
                tetris.drop(nextAction)
                prev_turn = tetris.turn - self.delay
                if prev_turn > 0:
                    reward = tetris.score - tetris.history[prev_turn][1]
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha)
            except GameOverError:
                prev_turn = tetris.turn - self.delay
                if prev_turn > 0:
                    reward = tetris.score - tetris.history[prev_turn][1] - 1000
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha)
                print tetris
                print "Game Over with score " + str(tetris.score)
                break

    def query(self, key):
        if key not in self.qvalues:
            # print "new key: " + str(key[0]) + str(key[1])
            self.qvalues[key] = 0.0
        # else:
        #     print "key exists" + str(key[0]) + str(key[1])
        # print self.qvalues[key]
        return self.qvalues[key]

    def qvalueUpdate(self, key, updateValue, alpha):
        self.qvalues[key] = (1 - alpha) * self.query(key) + alpha * updateValue

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

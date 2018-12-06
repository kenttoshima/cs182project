from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError
from random import random, choice

GAMEOVER_PENALTY = -1000

class Agent(object):
    def __init__(self, width = 10, height = 20, delay = 30, alpha = 0.6, epsilon = 0.8):
        self.width = width
        self.height = height
        self.delay = delay
        self.alpha = alpha
        self.epsilon = epsilon
        self.learning_no = 0
        self.qvalues = {}

    # Q value learning function
    def learn(self):
        alpha = self.alpha
        epsilon = self.epsilon
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        self.learning_no += 1
        while True:
            tetris.next_turn()
            nextAction = self.getAction(tetris, epsilon)
            try:
                alpha *= 0.99
                epsilon *= 0.8
                tetris.drop(nextAction)
                prev_turn = tetris.turn - 1
                delay_turn = tetris.turn - self.delay
                if delay_turn > 0:
                    reward = tetris.score - tetris.history[delay_turn][1]
                    self.qvalueUpdate(tetris.history[delay_turn][0], reward, alpha)
                if prev_turn > 0:
                    reward = tetris.score - tetris.history[prev_turn][1]
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha)
            except GameOverError:
                prev_turn = tetris.turn - 1
                delay_turn = tetris.turn - self.delay
                if delay_turn > 0:
                    reward = tetris.score - tetris.history[delay_turn][1] + GAMEOVER_PENALTY
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha)
                if prev_turn > 0:
                    reward = tetris.score - tetris.history[delay_turn][1] + GAMEOVER_PENALTY
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha)
                print ""
                print str(self.learning_no) + "th learning"
                print tetris
                print "Game Over at " + str(tetris.turn) + "th turn with score " + str(tetris.score)
                break

    def query(self, key):
        if key not in self.qvalues:
            self.qvalues[key] = 0.0
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

    def getAction(self, tetris, epsilon):
        successor_list = self.getSuccessor(tetris)
        if not successor_list:
            nextAction = Action(1, 0)
        elif random() > (1 - epsilon):
            (state, nextAction) = choice(successor_list)
            _qvalue = self.query((state, nextAction))
        else:
            nextAction = self.computeActionFromQvalues(successor_list)
        return nextAction

    def computeActionFromQvalues(self, successor_list):
        for stateAndAction in successor_list:
            maxQvalue = float("-inf")
            if self.query(stateAndAction) > maxQvalue:
                _state, nextAction = stateAndAction[1]
                maxQvalue = self.query(stateAndAction)
        return nextAction

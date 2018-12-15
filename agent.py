########################
#### LEARNING AGENT ####
########################

from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError
from random import random, choice

LEARNING_RATE_DECAY = 0.95
EPSILON_DECAY = 0.98
GAMMA = 0.50

#weights
GAMEOVER_PENALTY = -100
SCORE_WEIGHT = 1
HOLE_WEIGHT = -50

class Agent(object):
    def __init__(self, width = 10, height = 20, delay = 30, alpha = 0.6, epsilon = 0.8):
        self.width = width
        self.height = height
        self.delay = delay
        self.alpha = alpha
        self.epsilon = epsilon
        self.learning_no = 0
        self.qvalues = {}
        self.results = []

    # Q value learning function
    def learn(self, debug = False):
        self.query_count = 0
        self.query_hit = 0
        alpha = self.alpha
        epsilon = self.epsilon
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        self.learning_no += 1
        while True:
            tetris.next_turn()
            nextAction = self.getAction(tetris, epsilon)
            prev_turn = tetris.turn - 1
            delay_turn = tetris.turn - self.delay
            alpha *= LEARNING_RATE_DECAY
            epsilon *= EPSILON_DECAY
            try:
                #pre_state = State(tetris, tetris.shape_list[tetris.turn].type)
                #print "bumpiness of {} is {} and the config is {}".format(pre_state, pre_state.to_config().bumpiness(), pre_state.to_config())
                #pre_state.to_config
                tetris.drop(nextAction)
                state_prime = State(tetris, tetris.shape_lookahead().type)
                actions_prime = [action for (state,action) in self.getSuccessor(tetris)]
                if delay_turn > 0:
                    reward = self.reward(delay_turn, tetris, False) #reward takes in the old turn number to calculate change
                    self.qvalueUpdate(tetris.history[delay_turn][0], reward, alpha, state_prime, actions_prime) #...and we then use it to update the old turn
                if prev_turn > 0:
                    reward = self.reward(prev_turn, tetris, False)
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha, state_prime, actions_prime)
            except GameOverError:
                for turn_offset in range(1, 1 + self.delay):
                    if tetris.turn - turn_offset > 0:
                        reward = self.reward(tetris.turn - turn_offset, tetris, True)
                # print ""
                # print str(self.learning_no) + "th learning"
                # print tetris

                # print "Game Over at " + str(tetris.turn) + "th turn with score " + str(tetris.score)
                self.results.append(tetris.score)
                break

            if(debug):
                print ""
                print tetris.shape_list[tetris.turn]
                print tetris
                print "Score: {}, Number of holes {}".format(tetris.score,tetris.num_holes)

    # either returns the q-value on given key or initialize query for that key if it hasn't been initialized
    def query(self, key):
        self.query_count += 1
        if key not in self.qvalues:
            self.qvalues[key] = 0.0
        val = self.qvalues[key]
        self.query_hit = (self.query_hit + 1 ) if val != 0.0 else (self.query_hit)
        return val

    # update Q-value based on alpha
    def qvalueUpdate(self, key, updateValue, alpha, next_state, actions_prime):
        next_qvals = [self.query( (next_state, a) ) for a in actions_prime]


        #here's the janky part based on the fact that the max would become zero if all the initialized successor q-values are negative
        #and even one of the q-vals is uninitialized. If we only query initialized q-vals or use a heuristic-initialized Q-vals and more learning, this would not be needed.
        filtered_next = filter(lambda x : x != 0, next_qvals)
        max_next = max(filtered_next) if (len(filtered_next) > 0) else 0

        self.qvalues[key] = (1 - alpha) * self.query(key) + alpha * (updateValue + GAMMA * max_next)

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

    # return reward on given game and turn you want to calculate the score increase
    # if isGameOver == True, then return gameover penalty
    def reward(self, turn, tetris, isGameOver):
        if isGameOver:
            return GAMEOVER_PENALTY
        else:
            past_score = tetris.history[turn][1]
            past_holes = tetris.history[turn][2]
            score_change = tetris.score - past_score
            holes_change = tetris.num_holes - past_holes
            return SCORE_WEIGHT*score_change + HOLE_WEIGHT*holes_change

    # decide action based on epsilon-greedy Q-value iteration
    def getAction(self, tetris, epsilon):
        successor_list = self.getSuccessor(tetris)
        if not successor_list:
            nextAction = Action(1, 0)
        elif not random() < epsilon:
            (state, nextAction) = choice(successor_list)
            _qvalue = self.query((state, nextAction))
        else:
            nextAction = self.computeActionFromQvalues(successor_list)
        return nextAction

    # return action from given successor list based on Q-value
    def computeActionFromQvalues(self, successor_list):
        valueList = []
        for successor in successor_list:
            valueList.append((self.query(successor), successor[1]))
            return max(valueList, key = lambda x : x[0])[1]

    # plotting the learning result
    def plotresults(self, additional_plt):
        mean_sum = []
        sumsofar = 0
        for i, score in enumerate(self.results):
            sumsofar += score
            mean_sum.append(sumsofar / float((i + 1)))
        import matplotlib.pyplot as plt
        plt.plot(self.results)
        plt.plot(mean_sum)
        plt.plot(additional_plt)
        plt.show()

    # takes in 2 configs and return how many edges the fallen object touches the original grid
    def contact(self, preConfig, config):
        cord_list = []
        for ridx in range(config.height):
            for cidx in range(config.width):
                if config.cell(ridx, cidx) - preConfig.cell(ridx, cidx) > 0:
                    cord_list.append((ridx, cidx))
        neighbor_list = []
        for (r, c) in cord_list:
            if not r - 1 < 0 and not (r - 1, c) in cord_list:
                neighbor_list.append((r - 1, c))
            if r + 1 < config.height and not (r + 1, c) in cord_list:
                neighbor_list.append((r + 1, c))
            if not c - 1 < 0 and not (r, c - 1) in cord_list:
                neighbor_list.append((r, c - 1))
            if c + 1 < config.width and not (r, c + 1) in cord_list:
                neighbor_list.append((r, c + 1))
        return len(filter(lambda (r, c) : config.cell(r, c) != 0, neighbor_list))

########################
#### LEARNING AGENT ####
########################

from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError, Shape
from random import random, choice
from math import exp

EPSILON_DECAY = 0.999
GAMMA = 0.9

def convert_key(key):
    state,action = key
    return str(state) + '|' + str(action)

class Agent(object):
    def __init__(self, width = 10, height = 20, delay = 30, learning_rate = (.25,5000), epsilon = 0.8, \
        gameover_penalty = 0, score_weight = 1, hole_weight = -50, living_reward = 0):
        self.width = width
        self.height = height
        self.delay = delay
        self.learning_rate = learning_rate #For any given iteration of learning, alpha = (learning_rate[0]*learning_rate[1])/(learning_rate[1] + iter)
        self.epsilon = epsilon
        self.gameover_penalty = gameover_penalty
        self.score_weight = score_weight
        self.hole_weight = hole_weight
        self.living_reward = living_reward
        self.learning_no = 0
        self.qvalues = {}
        self.q_val_history = {}
        self.actual_state_action_pair = {} #This dict is a mapping from convert_key(key) back to key. For debugging purposes mainly
        self.results = []

    #run the game until lose, then return score at the end.
    def play(self, visualize=False):
        self.query_count = 0
        self.query_hit = 0
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        while True:
            tetris.next_turn()
            nextAction = self.getAction(tetris, 0) #run with epsilon = 0 for most greedy 
            try:
                tetris.drop(nextAction)
            except GameOverError:
                self.results.append((tetris.score, 100* tetris.turn))
                return (tetris.score, tetris.turn)
            if(visualize):
                print ""
                print tetris.shape_list[tetris.turn]
                print tetris
                print "Score: {}, Number of holes {}".format(tetris.score,tetris.num_holes)

    # Q value learning function
    def learn(self):
        self.query_count = 0
        self.query_hit = 0
        self.learning_no += 1
        alpha = (self.learning_rate[0]*self.learning_rate[1])/(self.learning_rate[1] + self.learning_no)
        self.epsilon *= EPSILON_DECAY
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        while True:
            tetris.next_turn()
            nextAction = self.getAction(tetris, self.epsilon)
            prev_turn = tetris.turn - 1
            delay_turn = tetris.turn - self.delay
            try:
                pre_state = State(tetris, tetris.shape_list[tetris.turn].type)
                tetris.drop(nextAction)
                state_prime = State(tetris, tetris.shape_lookahead().type)
                actions_prime = [action for (state,action) in self.getSuccessor(tetris, get_future_shape = True)]
                if delay_turn > 0:
                    reward = self.reward(delay_turn, self.delay, tetris, False) #reward takes in the old turn number to calculate change
                    reward = reward / float(self.delay) #we want to scale this down by delay so that we get the *average* reward over the delay window
                    self.qvalueUpdate(tetris.history[delay_turn][0], reward, alpha, state_prime, actions_prime) #...and we then use it to update the old turn
                if prev_turn > 0:
                    reward = self.reward(prev_turn, 1, tetris, False)
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha, state_prime, actions_prime)
            except GameOverError:
                if prev_turn > 0:
                    reward = self.reward(prev_turn, 1, tetris, True)
                    self.qvalueUpdate(tetris.history[prev_turn][0], reward, alpha, state_prime, actions_prime)
                self.results.append(tetris.score)
                break

    def heuristic_q_val(self, state_action_pair):
        return 0 #disable heuristics in this vanilla version of the Q-learning agent and instead initialize all Q-vals to 0

    # either returns the q-value on given key or initialize query for that key if it hasn't been initialized
    def query(self, key):
        self.query_count += 1
        if convert_key(key) not in self.qvalues:
            self.qvalues[convert_key(key)] = self.heuristic_q_val(key)
            self.q_val_history[convert_key(key)] = [self.qvalues[convert_key(key)]]
            self.actual_state_action_pair[convert_key(key)] = key

        val = self.qvalues[convert_key(key)]
        self.query_hit = (self.query_hit + 1 ) if len(self.q_val_history[convert_key(key)]) > 1 else (self.query_hit)
        return val

    # update Q-value based on alpha
    def qvalueUpdate(self, key, updateValue, alpha, next_state, actions_prime):
        next_qvals = [self.query( (next_state, a) ) for a in actions_prime]
        max_next = self.gameover_penalty if (len(next_qvals) == 0) else max(next_qvals)

        self.qvalues[convert_key(key)] = (1 - alpha) * self.query(key) + alpha * (updateValue + GAMMA * max_next)
        self.q_val_history[convert_key(key)].append(self.qvalues[convert_key(key)])

    #get_future_shape == True fetches the next shape rather than the current one.
    def getSuccessor(self, tetris, get_future_shape=False):
        nextShape = tetris.shape_lookahead() if get_future_shape else tetris.shape_list[tetris.turn] 
        successor_list = []
        for i in range(4):
            nextShape.rotate()
            for i in range(tetris.width):
                x = i + 1
                newConfig = Configuration(tetris.width, tetris.height)
                newConfig.copyGrid(tetris)
                old_config = Configuration(tetris.width, tetris.height)
                old_config.copyGrid(tetris)
                try:
                    newConfig.fall(nextShape, x)
                    # def of successor = (action, (active layer, height of baseline))
                    successor_list.append((State(old_config, nextShape.type), (Action(x, nextShape.rotation))))    
                except (InvalidMoveError, GameOverError):
                    pass
        # if successor_list is empty, meaning gameover in the next turn
        return successor_list

    # return reward on given game and turn you want to calculate the score increase
    # if isGameOver == True, then return gameover penalty
    def reward(self, turn, forward, tetris, isGameOver):
        if isGameOver:
            return self.gameover_penalty
        else:
            past_score = tetris.history[turn][1]
            past_holes = tetris.history[turn][2]
            current_score = tetris.history[turn+forward][1]
            current_holes = tetris.history[turn+forward][2] 
            score_change = current_score - past_score
            holes_change = current_holes - past_holes
            return (self.score_weight)*score_change + (self.hole_weight)*holes_change + (self.living_reward)

    # decide action based on epsilon-greedy Q-value iteration
    def getAction(self, tetris, epsilon):
        successor_list = self.getSuccessor(tetris)
        # for item in successor_list:
        #     print "state {} action {}".format(item[0],item[1])  
        # if there is no possible valid move, return vanilla action
        if not successor_list:
            nextAction = Action(1, 0)
        # flipping a coin to decide if we explore random action
        elif (random() < epsilon) :
            (state, nextAction) = choice(successor_list)
            _qvalue = self.query((state, nextAction))
        # if we don't explore return current optimal move based on qvalue
        else:
            nextAction = self.computeActionFromQvalues(successor_list)
        return nextAction

    # return action from given successor list based on Q-value
    def computeActionFromQvalues(self, successor_list):
        #print "computing action from qvals {}".format(len(successor_list))
        valueList = []
        for successor in successor_list:
            #print "Doing q-value query for: {}".format(str(successor[1]))
            valueList.append((self.query(successor), successor[1]))
        return max(valueList, key = lambda x : x[0])[1]



# possible heuristics

    # takes in tuple: (config before a move, config after a move)
    # return how many edges the fallen shape touches in original config
    # does messy operations but works fine
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

    # the deeper the line is filled, the higher the value
    # the closer the line is completed, the higher the valued
    def line_fill(self, preConfig, config):
        sum = 0.
        for y in range(1, config.height):
            add = self.negexp(config.blank_by_row(y)) - self.negexp(preConfig.blank_by_row(y))
            sum += self.negexp(y) * add
        return sum

    def negexp(self, x):
        return exp(x * -1.)

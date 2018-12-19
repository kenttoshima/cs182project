########################
#### LEARNING AGENT ####
########################

from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError, Shape
from random import random, choice
from math import exp

GAMMA = 0.9

def convert_key(key):
    state,action = key
    return str(state) + '|' + str(action)

class Agent(object):
    def __init__(self, width = 10, height = 20, delay = 30, learning_rate = (.25,5000), exploration_eagerness = 500, \
        gameover_penalty = 0, score_weight = 1, hole_weight = -50, living_reward = 0):
        self.width = width
        self.height = height
        self.delay = delay
        self.learning_rate = learning_rate #For any given iteration of learning, alpha = (learning_rate[0]*learning_rate[1])/(learning_rate[1] + iter)
        self.exploration_eagerness = exploration_eagerness
        self.gameover_penalty = gameover_penalty
        self.score_weight = score_weight
        self.hole_weight = hole_weight
        self.living_reward = living_reward
        self.edit_weights([10,-20,100,-0.5]) #initialize score weight to 10, hole weight to -20, fit weight to 100, bumpiness to -0.5
        self.learning_no = 0
        self.qvalues = {}
        self.q_val_history = {}
        self.actual_state_action_pair = {} #This dict is a mapping from convert_key(key) back to key. For debugging purposes mainly
        self.results = []

    #setter function to set the weights of the heuristic Q-value function.
    def edit_weights(self, weights):
        self.HSCORE_WEIGHT, self.HHOLE_WEIGHT, self.HFIT_WEIGHT, self.HBUMPINESS_WEIGHT = (weights)
    
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
                self.results.append(tetris.score)
                return tetris.score
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
        tetris = Tetris(self.width, self.height, infinite=True, type_list=[])
        while True:
            tetris.next_turn()
            nextAction = self.getAction(tetris, epsilon = 0) #Since we are already using an exploration function, there is no longer need to randomize exploration
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
        (pre_state, action) = state_action_pair
        fall_col = action.x
        fall_rot = action.rotation
        shape_to_fall = Shape(pre_state.nextShapeType)
        for i in range(fall_rot % 4):
            shape_to_fall.rotate()
        #Pre_config is the configuration of the state before the action
        pre_config = pre_state.to_config()
        pre_config_save = pre_config.copy()
        try:
            pre_config.fall(shape_to_fall, fall_col) 
            holes_generated = pre_config.hole()
        except GameOverError: 
            raise InvalidMoveError #this should not happen in practice, because we are querying on moves that aren't gameover.
        except InvalidMoveError:
            raise InvalidMoveError #this should not happen in practice, since we are always querying on valid moves
        post_config = pre_config.copy() #This is the state after executing the fall but before clearing
        score_increase = pre_config.scoring(pre_config.clear())
        post_config_flat = State(pre_config, 0).to_config() #This is the "flattened" version of post_config where lines are cleared and holes are removed (ie. converted to an activelayer, then back)
        num_contact = self.contact(pre_config_save, post_config)
        bumpiness_change = post_config_flat.bumpiness()-pre_config_save.bumpiness()

        raw_vals = [holes_generated, score_increase, num_contact, bumpiness_change]
        weights = [self.HHOLE_WEIGHT, self.HSCORE_WEIGHT, self.HFIT_WEIGHT, self.HBUMPINESS_WEIGHT]
        weighted_heuristic =  sum([x*y for x,y in zip(raw_vals,weights)]) #dot product of weights and heuristic values.
        return weighted_heuristic

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
        next_qvals = [self.exploration_function(self.query((next_state, a)), self.num_hits((next_state, a)) )for a in actions_prime]
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


    def num_hits(self, key):
        if convert_key(key) not in self.q_val_history:
            return 1
        else:
            return len(self.q_val_history[convert_key(key)])

    #adds a particular bonus to a q-value for being unexplored
    def exploration_function(self, q, n): 
        return q + float(self.exploration_eagerness)/float(n)

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

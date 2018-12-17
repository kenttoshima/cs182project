########################
#### LEARNING AGENT ####
########################

from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError, Shape
from random import random, choice
from math import exp

LEARNING_RATE_DECAY = 1
EPSILON_DECAY = 0.9999
GAMMA = 0.9

#weights
GAMEOVER_PENALTY = -100
SCORE_WEIGHT = 10
HOLE_WEIGHT = -500
LIVING_REWARD = 100

def convert_key(key):
    state,action = key
    return str(state) + str(action)


class Agent(object):
    def __init__(self, width = 10, height = 20, delay = 30, alpha = 0.6, epsilon = 0.8):
        self.width = width
        self.height = height
        self.delay = delay
        self.alpha = alpha
        self.epsilon = epsilon
        self.learning_no = 0
        self.qvalues = {}
        self.q_val_history = {}
        self.actual_state_action_pair = {} #This dict is a mapping from convert_key(key) back to key. For debugging purposes mainly
        self.results = []

    #run the game until lose, then return score at the end.
    def play(self):
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
            # print ""
            # print tetris.shape_list[tetris.turn]
            # print tetris
            # print "Score: {}, Number of holes {}".format(tetris.score,tetris.num_holes)

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
            # print "-=-=-= NEW MOVE =-=-=-"
            # print tetris.shape_list[tetris.turn]
            # print tetris
            nextAction = self.getAction(tetris, epsilon)
            # print "-=-=-= NEXT ACTION {} =-=-=-".format(nextAction)
            prev_turn = tetris.turn - 1
            delay_turn = tetris.turn - self.delay
            alpha *= LEARNING_RATE_DECAY
            epsilon *= EPSILON_DECAY
            try:
                pre_state = State(tetris, tetris.shape_list[tetris.turn].type)
                #print "bumpiness of {} is {} and the config is {}".format(pre_state, pre_state.to_config().bumpiness(), pre_state.to_config())
                #pre_state.to_config
                tetris.drop(nextAction)
                state_prime = State(tetris, tetris.shape_lookahead().type)
                # print str(state_prime)
                # for (state,action) in self.getSuccessor(tetris, get_future_shape = True):
                #     print str(state)
                actions_prime = [action for (state,action) in self.getSuccessor(tetris, get_future_shape = True)]
                if delay_turn > 0:
                    reward = self.reward(delay_turn, self.delay, tetris, False) #reward takes in the old turn number to calculate change
                    self.qvalueUpdate(tetris.history[delay_turn][0], reward, alpha, state_prime, actions_prime) #...and we then use it to update the old turn
                if prev_turn > 0:
                    reward = self.reward(prev_turn, 1, tetris, False)
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


    #Heuristic Q value formula: -(change in bumpiness) +(score increase) -(Hole increase) +(shape fit)
    #Flat negative value if it's a game over
    def heuristic_q_val(self, state_action_pair):
        self.HSCORE_WEIGHT = 10
        self.HHOLE_WEIGHT = -20
        self.HFIT_WEIGHT = 100
        self.HBUMPINESS_WEIGHT = -0.5

        (pre_state, action) = state_action_pair
        # print "-----QUERY ON-- {}, {}".format(pre_state, action)
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
            # return GAMEOVER_HEURISTIC_VAL #Gives a Flat number Q value if the move fails
        except InvalidMoveError:
            raise InvalidMoveError #this should not happen in practice, since we are always querying on valid moves
            #return -1*float('inf')
        post_config = pre_config.copy() #This is the state after executing the fall but before clearing
        score_increase = pre_config.scoring(pre_config.clear())
        post_config_flat = State(pre_config, 0).to_config() #This is the "flattened" version of post_config where lines are cleared and holes are removed (ie. converted to an activelayer, then back)
        # print str(pre_config_save)        
        # print str(post_config)
        # print str(post_config_flat)
        num_contact = self.contact(pre_config_save, post_config)
        bumpiness_change = post_config_flat.bumpiness()-pre_config_save.bumpiness()

        raw_vals = [holes_generated, score_increase, num_contact, bumpiness_change]
        weights = [self.HHOLE_WEIGHT, self.HSCORE_WEIGHT, self.HFIT_WEIGHT, self.HBUMPINESS_WEIGHT]
        weighted_heuristic =  sum([x*y for x,y in zip(raw_vals,weights)]) #dot product of weights and heuristic values.
        # print "pre"
        # print str(pre_config_save)
        # print "post"
        # print str(post_config)
        # print "Holes {};Score {};Contact {};Bumpiness {};Heuristic {}".format(holes_generated, score_increase, num_contact, bumpiness_change, weighted_heuristic)
        return 0
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
        # print "The following move has reward of {}".format(updateValue)
        # (state_, action_) = key 
        # state_.vis_state_action(action_)
        next_qvals = [self.query( (next_state, a) ) for a in actions_prime]
        max_next = GAMEOVER_PENALTY if (len(next_qvals) == 0) else max(next_qvals)

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
            return GAMEOVER_PENALTY
        else:
            past_score = tetris.history[turn][1]
            past_holes = tetris.history[turn][2]
            current_score = tetris.history[turn+forward][1]
            current_holes = tetris.history[turn+forward][2] 
            score_change = current_score - past_score
            holes_change = current_holes - past_holes
            return SCORE_WEIGHT*score_change + HOLE_WEIGHT*holes_change + LIVING_REWARD

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

    # plotting the learning result
    def plotresults(self, additional_plt):
        # mean_sum = []
        # sumsofar = 0
        # for i, score in enumerate(self.results):
        #     sumsofar += score
        #     mean_sum.append(sumsofar / float((i + 1)))
        import matplotlib.pyplot as plt
        plt.plot(self.results)
        # plt.plot(mean_sum)
        plt.plot(additional_plt)
        plt.show()

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

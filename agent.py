########################
#### LEARNING AGENT ####
########################

from game import Tetris, Configuration, Action, State, InvalidMoveError, GameOverError, Shape
from random import random, choice
from math import exp

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
        self.weight = []

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
            # print tetris.shape_list[tetris.turn]
            # print tetris
            nextAction = self.getAction(tetris, epsilon)
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

            # if(debug):
            #     print ""
            #     print tetris.shape_list[tetris.turn]
            #     print tetris
            #     print "Score: {}, Number of holes {}".format(tetris.score,tetris.num_holes)


    #Heuristic Q value formula: -(change in bumpiness) +(score increase) -(Hole increase) +(shape fit)
    #Flat negative value if it's a game over
    def heuristic_q_val(self, state_action_pair):
        GAMEOVER_HEURISTIC_VAL = -1000
        SCORE_WEIGHT = 1
        HOLE_WEIGHT = -1500
        FIT_WEIGHT = 10
        BUMPINESS_WEIGHT = -0.05

        (pre_state, action) = state_action_pair
        #print "-----QUERY ON-- {}, {}".format(pre_state, action)
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
            return GAMEOVER_HEURISTIC_VAL #Gives a Flat number Q value if the move fails
        except InvalidMoveError:
            return -1*float('inf')
        post_config = pre_config.copy() #This is the state after executing the fall but before clearing
        score_increase = pre_config.scoring(pre_config.clear())
        post_config_flat = State(pre_config, 0).to_config() #This is the "flattened" version of post_config where lines are cleared and holes are removed (ie. converted to an activelayer, then back)
        # print str(pre_config_save)
        # print str(post_config)
        # print str(post_config_flat)
        num_contact = self.contact(pre_config_save, post_config)
        bumpiness_change = post_config_flat.bumpiness()-pre_config_save.bumpiness()

        raw_vals = [holes_generated, score_increase, num_contact, bumpiness_change]
        weights = [HOLE_WEIGHT, SCORE_WEIGHT, FIT_WEIGHT, BUMPINESS_WEIGHT]
        weighted_heuristic =  sum([x*y for x,y in zip(raw_vals,weights)])
        # print "pre"
        # print str(pre_config_save)
        # print "post"
        # print str(post_config)
        # print "Holes {};Score {};Contact {};Bumpiness {};Heuristic {}".format(holes_generated, score_increase, num_contact, bumpiness_change, weighted_heuristic)
        return weighted_heuristic



    # either returns the q-value on given key or initialize query for that key if it hasn't been initialized
    def query(self, key):
        self.query_count += 1
        if key not in self.qvalues:
            self.qvalues[key] = self.heuristic_q_val(key)
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
            for x in range(1, tetris.width + 1):
                newConfig = Configuration(tetris.width, tetris.height)
                newConfig.copyGrid(tetris)
                old_config = Configuration(tetris.width, tetris.height)
                old_config.copyGrid(tetris)
                try:
                    newConfig.fall(nextShape, x)
                    # if fall is successful then pair that action with config and add to list
                    successor_list.append((State(old_config, nextShape.type), (Action(x, nextShape.rotation))))
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

class ApproxQLearnAgent(object):
    def __init__(self, width = 10, height = 20, delay = 30, alpha = 0.6, epsilon = 0.8):
        self.width = width
        self.height = height
        self.delay = delay
        self.alpha = alpha
        self.epsilon = epsilon
        self.learning_no = 0
        self.results = []
        self.weight = [1., 1., 1.]

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
                pre_state = State(tetris, tetris.shape_list[tetris.turn].type)
                tetris.drop(nextAction)
                state_prime = State(tetris, tetris.shape_lookahead().type)
                actions_prime = [action for (state, action) in self.getSuccessor(tetris)]
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

            # if(debug):
            #     print ""
            #     print tetris.shape_list[tetris.turn]
            #     print tetris
            #     print "Score: {}, Number of holes {}".format(tetris.score,tetris.num_holes)

    # return a list of successor of the game
    def getSuccessor(self, tetris):
        nextShape = tetris.shape_list[tetris.turn]
        successor_list = []
        for i in range(4):
            nextShape.rotate()
            for x in range(1, tetris.width + 1):
                newConfig = Configuration(tetris.width, tetris.height)
                newConfig.copyGrid(tetris)
                oldConfig = Configuration(tetris.width, tetris.height)
                oldConfig.copyGrid(tetris)
                try:
                    newConfig.fall(nextShape, x)
                    # if fall is successful then pair that action with config and add to list
                    successor_list.append((State(oldConfig, nextShape.type), (Action(x, nextShape.rotation))))
                except (InvalidMoveError, GameOverError):
                    pass
        # if successor_list is empty, meaning gameover in the next turn
        return successor_list

    # decide action based on epsilon-greedy Q-value iteration
    def getAction(self, tetris, epsilon):
        successor_list = self.getSuccessor(tetris)
        if not successor_list:
            nextAction = Action(1, 0)
        # flipping a coin to decide if we explore random action
        elif random() < epsilon:
            _state, nextAction = choice(successor_list)
        # if we don't explore return current optimal move based on qvalue
        else:
            nextAction = self.computeActionFromQvalues(successor_list)
        return nextAction

    # return action from given successor list based on Q-value
    def computeActionFromQvalues(self, successor_list):
        value_list = []
        for successor in successor_list:
            state, action = successor
            value = self.computeQvalue(state, action)
            value_list.append((value, successor[1]))
        return max(value_list, key = lambda x : x[0])[1]

    # compute Q(s,a) on given s = state, a = action
    def computeQvalue(self, state, action):
        return self.weight[0] * self.contact(state, action) + self.weight[1] * self.hole(state, action) + self.weight[2] * self.fill(state, action)

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

    """ features """

    def contact(self, state, action):
        preConfig, postConfig = self.transition(state, action)
        cord_list = []
        for ridx in range(postConfig.height):
            for cidx in range(postConfig.width):
                if postConfig.cell(ridx, cidx) - preConfig.cell(ridx, cidx) > 0:
                    cord_list.append((ridx, cidx))
        neighbor_list = []
        for (r, c) in cord_list:
            if not r - 1 < 0 and not (r - 1, c) in cord_list:
                neighbor_list.append((r - 1, c))
            if r + 1 < postConfig.height and not (r + 1, c) in cord_list:
                neighbor_list.append((r + 1, c))
            if not c - 1 < 0 and not (r, c - 1) in cord_list:
                neighbor_list.append((r, c - 1))
            if c + 1 < postConfig.width and not (r, c + 1) in cord_list:
                neighbor_list.append((r, c + 1))
        return len(filter(lambda (r, c) : postConfig.cell(r, c) != 0, neighbor_list))

    def hole(self, state, action):
        preConfig, postConfig = self.transition(state, action)
        return postConfig.hole() - preConfig.hole()

    def fill(self, state, action):
        preConfig, postConfig = self.transition(state, action)
        sum = 0.
        for y in range(1, postConfig.height + 1):
            add = self.negexp(postConfig.blank_by_row(y)) - self.negexp(preConfig.blank_by_row(y))
            sum += self.negexp(y) * add
        return sum

    """ utilities """

    def negexp(self, x):
        return exp(x * -1.)

    def transition(self, state, action):
        preconfig = state.config
        postConfig = Configuration(state.config.width, state.config.height)
        actionX, actionRotation = action
        postConfig.copyGrid(state.config)
        postConfig.fall(actionX, actionRotation)
        return preconfig, postConfig

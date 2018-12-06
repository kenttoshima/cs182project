########################
### TETRIS FRAMEWORK ###
########################

from random import randint
SHAPE_TYPES = [
            [[0]],

            [[1, 1, 1],
            [0, 1, 0]],

            [[0, 2, 2],
            [2, 2, 0]],

            [[3, 3, 0],
            [0, 3, 3]],

            [[4, 0, 0],
            [4, 4, 4]],

            [[0, 0, 5],
            [5, 5, 5]],

            [[6, 6, 6, 6]],

            [[7, 7],
            [7, 7]]
            ]

class Error(Exception):
    """Base class for other exceptions"""
    pass

class GameOverError(Error):
    pass

class InvalidMoveError(Error):
    def __init__(self, x):
        self.x = x

    def __str__(self):
        return(repr(self.x))

class CollisionError(Error):
    def __init__(self, r, c):
        self.rowidx = r
        self.colidx = c

    def __str__(self):
        return(repr(self.rowidx), repr(self.colidx))

class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for x in range(width)] for y in range(height)]

    def __str__(self):
        string = "+ " + "- " * len(self.grid[0]) + "+\n"
        for i, row in enumerate(self.grid):
            string += "|"
            for cell in row:
                string += " " + str(cell if cell else " ")
            string += " | "  + str(self.height - i) + "\n"
        string += "+ " + "- " * len(self.grid[0]) + "+\n"
        string += "  "
        for i in range(1, len(self.grid[0]) + 1):
            string += str(i) + " "
        string += "\n"
        return string

    # return (row, column) on given (x, y) coordinate
    def cord(self, x = 0, y = 0):
        return self.height - y, x - 1

    # return the value of the cell at self.grid[r][c]
    def cell(self, r, c):
        return self.grid[r][c]

    # copy the given grid to self
    def copyGrid(self, givenGrid):
        for ridx, row in enumerate(self.grid):
            for cidx in range(len(row)):
                self.grid[ridx][cidx] = givenGrid.cell(ridx, cidx)

    # return list of active height for each column
    def active_y(self):
        active_list = [0 for i in range(self.width)]
        for ridx, row in enumerate(self.grid):
            for cidx, cell in enumerate(row):
                if cell != 0 and active_list[cidx] == 0:
                    active_list[cidx] = self.height - ridx
        return active_list

    # return active layer i.e. list of active_y - min(active_y) and baseline
    def active_layer(self):
        return map(lambda x: x - min(self.active_y()), self.active_y()), min(self.active_y())

    # TODO: count number of holes
    # def hole(self):

    # add given shape to given coordinate on down_left point. Should not call upon playing game.
    def add_shape(self, shape, x, y):
        idx_r, idx_c = self.cord(x, y)
        for off_y, row in enumerate(shape.aslist()):
            for off_x, cell in enumerate(row):
                r, c = off_y + idx_r - len(shape.aslist()) + 1, off_x + idx_c
                if self.grid[r][c] != 0 and cell != 0:
                    # should not be raised because of sanitized Configuration.fall function
                    raise CollisionError(r, c)
                else:
                    self.grid[r][c] += cell

    # remove row of given y if the row is filled.
    def remove_row(self, c):
        row = self.grid[c]
        if 0 not in row:
            del self.grid[c]
            self.grid.insert(0, [0 for i in range(self.width)])
        else:
            raise ValueError("Row not filled")

class Shape(object):
    def __init__(self, type):
        self.type = type
        self.shape = SHAPE_TYPES[type]
        self.shapeHeight = len(self.shape)
        self.shapeWidth = len(self.shape[0])
        self.rotation = 0

    def __str__(self):
        string = ""
        for row in self.shape:
            for cell in row:
                string += " " + str(cell if cell else " ")
            string += "\n"
        return string

    def copy(self):
        shape = Shape(self.type)
        for i in range(self.rotation):
            shape.rotate()
        return shape

    def aslist(self):
        return list(self.shape)

    def rotate(self):
        self.shape = [ [ self.shape[y][x]
			            for y in range(len(self.shape)) ]
		                for x in range(len(self.shape[0]) - 1, -1, -1) ]
        self.shapeHeight = len(self.shape)
        self.shapeWidth = len(self.shape[0])
        self.rotation = (self.rotation + 1) % 4

class Shapes(Shape):
    def __init__(self, infinite = True, type_list = []):
        super(Shapes, self).__init__(0)
        self.infinite = infinite
        self.shape_list = [self] + map(lambda type: Shape(type), type_list)

    # generate shapes based on given number of turn. Works for both infinite and finite game.
    def generate(self, turn):
        if self.infinite and len(self.shape_list) <= turn:
            self.shape_list.append(Shape(randint(1, len(SHAPE_TYPES) - 1)))
        if turn > len(self.shape_list):
            raise ValueError
        else:
            return self.shape_list[turn]

class Configuration(Grid):
    def __init__(self, width, height):
        super(Configuration, self).__init__(width, height)

    # drop given shape on grid at given x coordinate
    def fall(self, shape, x):
        if x < 1 or x - 1 + shape.shapeWidth > self.width:
            raise InvalidMoveError(x)
        idx_c = self.cord(x = x)[1]
        height_list = self.active_y()[idx_c:idx_c + len(shape.aslist()[0])]
        fallingOffset = [True for i in range(len(height_list))]
        for row in shape.aslist()[::-1]:
            for off_x, cell in enumerate(row):
                if cell == 0 and fallingOffset[off_x]:
                    height_list[off_x] -= 1
                else:
                    fallingOffset[off_x] = False
        y = max(height_list) + 1
        if y - 1 + shape.shapeHeight > self.height:
            raise GameOverError
        else:
            self.add_shape(shape, x, y)

    # clear fullfilled row in the grid
    def clear(self):
        cleared = 0
        for i in range(len(self.grid)):
            try:
                self.remove_row(i)
                cleared += 1
            except ValueError:
                pass
        return cleared

    # return score on the number of lines that were cleared
    def scoring(self, line):
        switcher = {
            1: 40,
            2: 100,
            3: 300,
            4: 1200
        }
        return switcher.get(line, 0)

class Tetris(Configuration, Shapes):
    def __init__(self, width, height, infinite, type_list):
        super(Tetris, self).__init__(width, height)
        Shapes.__init__(self, infinite, type_list)
        self.turn = 0
        self.score = 0
        # history for turn 0: should not be considered
        state = State(self, self.shape_list[self.turn].type)
        action = Action(0, 0)
        self.history = [((state, action), self.score)]

    # # run the whole tetris game
    # def run(self):
    #     self.turn += 1
    #     shape = self.generate(self.turn)
    #     print "turn: " + str(self.turn)
    #     print "next object"
    #     print shape
    #     print self
    #     while True:
    #         for i in range(4):
    #             shape.rotate()
    #             print i + 1
    #             print shape
    #         r = input("input rotation number r: ")
    #         for i in range(r % 4):
    #             shape.rotate()
    #         print "next object: "
    #         print shape
    #         print self
    #         x = input("input x coordinate: ")
    #         self.move_list.append((shape.type, r, x, self.active_y()))
    #         try:
    #             self.fall(shape, x)
    #             break
    #         except InvalidMoveError as e:
    #             print "Placing on x = " + str(e) + " is an invalid move."
    #         except GameOverError:
    #             print "Game over with score: " + str(self.score)
    #             exit()
    #     print self
    #     self.score += self.scoring(self.clear())
    #     print "score: " + str(self.score)

    def next_turn(self):
        self.turn += 1
        shape = self.generate(self.turn)
        print "turn: " + str(self.turn)
        print "next object"
        print shape
        print self

    def drop(self, action):
        shape = self.generate(self.turn)
        copyState = State(self, shape.type)
        self.history.append(((copyState, action), self.score))
        for i in range(action.rotation % 4):
            shape.rotate()
        self.fall(shape, action.x)
        # for hist in self.history:
        #     print hist[0], hist[1]
        print self
        self.score += self.scoring(self.clear())
        print "score: " + str(self.score)

# abstract action for tetris
class Action(object):
    def __init__(self, x, rotation):
        self.x = x
        self.rotation = rotation

    def __eq__(self, other):
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return self.x == other.x and self.rotation == other.rotation

    def __str__(self):
        return str((self.x, self.rotation))

# abstract state for agent usage
class State(object):
    def __init__(self, config, shape_type):
        self.active_layer, base_height = config.active_layer()
        self.base_zone = int(base_height / (config.height / 3.0)) + 1
        self.nextShapeType = shape_type

    def __eq__(self, other):
        if self is other:
            return True
        elif type(self) != type(other):
            return False
        else:
            return self.active_layer == other.active_layer and self.base_zone == other.base_zone and self.nextShapeType == other.nextShapeType

    def __str__(self):
        return str((self.active_layer, self.base_zone, self.nextShapeType))

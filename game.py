from random import randint

class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for x in range(width)] for y in range(height)]
    
    def __str__(self):
        string = ""
        for row in self.grid:
            for cell in row:
                string += " " + str(cell)
            string += "\n"
        return string

    # return (row, column) on given (x, y) coordinate
    def cord(self, x = 0, y = 0):
        return self.height - y, x - 1

    # return the value of the cell at (x, y)
    def cell(self, x, y):
        row, column = self.cord(x, y)
        return self.grid[row][column]

    # return list of active height for each column
    def active_y(self):
        active_list = [0 for i in range(self.width)]
        for ridx, row in enumerate(self.grid):
            for cidx, cell in enumerate(row):
                if cell != 0 and active_list[cidx] == 0:
                    active_list[cidx] = self.height - ridx
        return active_list
    
    # add given shape to given coordinate on down_left point
    def add_shape(self, shape, x, y):
        idx_r, idx_c = self.cord(x, y)
        if y - 1 + shape.shapeHeight > self.height or x - 1 + shape.shapeWidth > self.width:
            raise ValueError
        for off_y, row in enumerate(shape.aslist()):
            for off_x, cell in enumerate(row):
                self.grid[off_y + idx_r - len(shape.aslist()) + 1][off_x + idx_c] += cell
    
    # remove row of given y if the row is filled
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
        self.shape_types = [
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
        self.shape = self.shape_types[type]
        self.shapeHeight = len(self.shape)
        self.shapeWidth = len(self.shape[0])
    
    def __str__(self):
        string = ""
        for row in self.shape:
            for cell in row:
                string += " " + str(cell)
            string += "\n"
        return string

    def aslist(self):
        return list(self.shape)

    def rotate(self):
        self.shape = [ [ self.shape[y][x]
			            for y in range(len(self.shape)) ]
		                for x in range(len(self.shape[0]) - 1, -1, -1) ]
        self.shapeHeight = len(self.shape)
        self.shapeWidth = len(self.shape[0])

class Shapes(Shape):
    def __init__(self, infinite = True, type_list = []):
        super(Shapes, self).__init__(0)
        self.infinite = infinite
        self.shape_list = [self.shape] + map(lambda type: Shape(type), type_list)
        
    def generate(self, turn):
        if self.infinite:
            self.shape_list.append(Shape(randint(1, len(self.shape_types) - 1)))
        if turn > len(self.shape_list):
            raise ValueError
        else:
            return self.shape_list[turn]

class Configuration(Grid):
    def __init__(self, width, height):
        super(Configuration, self).__init__(width, height)

    def fall(self, shape, x):
        if x < 1 or x + self.width < len(shape.aslist()[0]):
            # TODO raise error that object does not fit in the x axis
            raise IndexError        
        idx_c = self.cord(x = x)[1]
        height_list = self.active_y()[idx_c:idx_c + len(shape.aslist()[0])]
        fallingOffset = [True for i in range(len(height_list))]
        for row in shape.aslist()[::-1]:
            for off_x, cell in enumerate(row):
                if cell == 0 and fallingOffset[off_x]:
                    height_list[off_x] -= 1
                else:
                    fallingOffset[off_x] = False
        try:
            self.add_shape(shape, x, max(height_list) + 1)
        except ValueError as g:
            print g
    
    def clear(self):
        cleared = 0
        for i in range(len(self.grid)):
            try:
                self.remove_row(i)
                cleared += 1
            except ValueError:
                pass
        return cleared
    
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
        # TODO: fugure out what 
        super(Tetris, self).__init__(width, height)
        Shapes.__init__(self, infinite, type_list)
        self.turn = 0
        self.score = 0

    def run(self):
        self.turn += 1
        shape = self.generate(self.turn)
        print shape
        print self
        r = input("input rotation number: ") % 4
        for i in range(r):
            shape.rotate()
        print shape
        print self
        x = input("input x coordinate: ")
        self.fall(shape, x)
        print self
        self.score += self.scoring(self.clear())
        print self.score
        
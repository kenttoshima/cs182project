from random import choice

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
        if y - 1 + shape.height > self.height or x - 1 + shape.width > self.width:
            raise ValueError
        for off_y, row in enumerate(shape.aslist()):
            for off_x, cell in enumerate(row):
                self.grid[off_y + idx_r - len(shape.aslist()) + 1][off_x + idx_c] += cell
    
    # remove row of given y if the row is filled
    def remove_row(self, y):
        row = self.grid[self.cord(y = y)[0]]
        if 0 not in row:
            del row
            self.grid.insert(0, [0 for i in range(self.width)])
        else:
            raise ValueError("Row not filled")

class Shape:
    def __init__(self, type):
        self.type = type
        self.shape_types = [
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
        self.height = len(self.shape)
        self.width = len(self.shape[0])
    
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
        self.height = len(self.shape)
        self.width = len(self.shape[0])

class Shapes(Shape):
    def __init__(self, infinite = True, type_list = []):
        self.infinite = infinite
        self.shape_list = map(lambda x: super(Shapes, self).__init__(type), type_list)
    
    def generate(self, turn = 0):
        if self.infinite:
            self.shape_list.append(choice(self.shape_types))
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

class Tetris(Configuration):
    pass
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
    
    # add given shape to given coordinate on left-up point
    def add_shape(self, shape, x, y):
        idx_r, idx_c = self.cord(x, y)
        for off_y, row in enumerate(shape.aslist()):
            for off_x, cell in enumerate(row):
                try:
                    self.grid[off_y + idx_r - len(shape.aslist())][off_x + idx_c] += cell
                except IndexError, e:
                    print "Grid error: " + str(e)
    
    
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

class Configuration(Grid):
    def __init__(self, width, height):
        super(Configuration, self).__init__(width, height)
        self.score = 0
        self.turn = 0

    def fall(self, shape, x):
        if x < 1 or x + self.width < len(shape.aslist()[0]):
            # TODO raise error that object does not fit in the x axis
            pass        
        idx_c = self.cord(x = x)[1]
        height_list = self.active_y()[idx_c:idx_c + len(shape.aslist()[0])]
        for off_y, row in enumerate(shape.aslist()):
            for off_x, cell in enumerate(row):
                if not off_y > len(shape.aslist()) / 2 and cell == 0:
                    height_list[off_x] -= 1
        self.add_shape(shape, x, max(height_list))

if __name__ == '__main__':
    tetris = Configuration(6, 10)
    s = []
    s.append(Shape(0))
    s.append(Shape(1))
    s.append(Shape(2))
    s.append(Shape(3))
    s.append(Shape(4))
    s.append(Shape(5))
    s[2].rotate()
    s[4].rotate()
    s[0].rotate()
    tetris.fall(s[0], 1)
    tetris.fall(s[1], 2)
    tetris.fall(s[2], 4)
    tetris.fall(s[3], 3)
    tetris.fall(s[4], 2)
    tetris.fall(s[5], 4)
    print tetris
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
    
    def active_y(self):
        active_list = [0 for i in range(self.width)]
        for ridx, row in enumerate(self.grid):
            for cidx, cell in enumerate(row):
                if cell != 0 and active_list[cidx] == 0:
                    active_list[cidx] = ridx
        return active_list

    def add_shape(self, shape, col):
        if col < 0 and self.width <= col:
            raise ValueError("Invalid column number")
        height_list = [0 for i in range(self.width)]
        for cidx in range(len(shape.aslist()[0])):
            for ridx, row in enumerate(shape.aslist()):
                if row[cidx] != 0:
                    height_list[cidx] = self.active_y()[cidx] - ridx
        return height_list



    
    def remove_row(self, parameter_list):
        pass

class Shape(object):
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

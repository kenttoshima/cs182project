from random import choice

class Grid(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for x in range(width)] for y in range(height)]
    
    def remove_row(self, parameter_list):
        del self.grid[row]

class shape(object):
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

    def rotate(self):
        self.shape = [ [ self.shape[y][x]
			            for y in range(len(self.shape)) ]
		                for x in range(len(self.shape[0]) - 1, -1, -1) ]
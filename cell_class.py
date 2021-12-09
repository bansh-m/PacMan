import pygame, random
from settings import *

vec = pygame.math.Vector2

class Cell:
    def __init__(self, pos, app, state = None):
        self.app = app
        self.grid_pos = pos
        self.directions = [UP, LEFT, RIGHT, DOWN]
        self.left_cell = None
        self.up_cell = None
        self.right_cell = None
        self.down_cell = None
        self.neighbors = []
        self.state = state

    def cell_connect(self):
        for direction in self.directions:
            if direction == UP:
                for cell in self.app.cells:
                    if self.grid_pos + UP == cell.grid_pos:
                        self.up_cell = cell
                        self.neighbors.append(cell)
            if direction == LEFT:
                for cell in self.app.cells:
                    if self.grid_pos + LEFT == cell.grid_pos:
                        self.left_cell = cell
                        self.neighbors.append(cell)
            if direction == RIGHT:
                for cell in self.app.cells:
                    if self.grid_pos + RIGHT == cell.grid_pos:
                        self.right_cell = cell
                        self.neighbors.append(cell)
            if direction == DOWN:
                for cell in self.app.cells:
                    if self.grid_pos + DOWN == cell.grid_pos:
                        self.down_cell = cell
                        self.neighbors.append(cell)

    # def get_neighbors(self):
    #     if self.left_cell != None:
    #         return self.left_cell
    #     if self.up_cell != None:
    #         return self.up_cell
    #     if self.right_cell != None:
    #         return self.right_cell
    #     if self.down_cell != None:
    #         return self.down_cell

    # def get_neighbors(self):
    #     if self.left_cell in self.app.cells:
    #         self.neighbors.append(self.left_cell)
    #     if self.up_cell in self.app.cells:
    #         self.neighbors.append(self.up_cell)
    #     if self.right_cell in self.app.cells:
    #         self.neighbors.append(self.right_cell)
    #     if self.down_cell in self.app.cells:
    #         self.neighbors.append(self.down_cell)

    def return_neighbors(self):
        return self.neighbors

    def set_state(self):
        if self.state == None:
            rand = random.randint(1, 2)
            if rand == 1:
                self.state = 'wall'
            else:
                self.state = 'coin'
    
    def shuffle_state(self):
        neighbor_wall = 0       
        random.shuffle(self.neighbors)
        for neighbor in self.neighbors:
            if neighbor not in self.app.stable_cells:
                if neighbor.state == 'wall':
                    neighbor_wall += 1
                if neighbor_wall > 1:
                    neighbor.state = 'coin'
                    neighbor_wall -= 1
                

            
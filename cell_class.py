import pygame, random
from settings import *

vec = pygame.math.Vector2

class Cell:
    def __init__(self, pos, app):
        self.app = app
        self.grid_pos = pos
        self.directions = [UP, LEFT, RIGHT, DOWN]
        self.left_cell = None
        self.up_cell = None
        self.right_cell = None
        self.down_cell = None
        self.neighbors = []
        self.state = None

    def cell_connect(self):
        for direction in self.directions:
            if direction == UP:
                for cell in self.app.cells:
                    if self.grid_pos + UP == cell.grid_pos:
                        self.up_cell = cell
            if direction == LEFT:
                for cell in self.app.cells:
                    if self.grid_pos + LEFT == cell.grid_pos:
                        self.left_cell = cell
            if direction == RIGHT:
                for cell in self.app.cells:
                    if self.grid_pos + RIGHT == cell.grid_pos:
                        self.right_cell = cell
            if direction == DOWN:
                for cell in self.app.cells:
                    if self.grid_pos + DOWN == cell.grid_pos:
                        self.down_cell = cell

    def get_neighbors(self):
        if self.left_cell in self.app.cells:
            self.neighbors.append(self.left_cell)
        if self.up_cell in self.app.cells:
            self.neighbors.append(self.up_cell)
        if self.right_cell in self.app.cells:
            self.neighbors.append(self.right_cell)
        if self.down_cell in self.app.cells:
            self.neighbors.append(self.down_cell)

    def random_state(self):  
        if len(self.neighbors) != 4:
            self.state = 'wall'
        else:
            number = random.randint(1, 2)
            if number == 1:
                self.state = 'wall'
            else:
                self.state = 'coin'


    def unrandom_state(self):
        neighbor_wall = 0       
        random.shuffle(self.neighbors)
        for neighbor in self.neighbors:
            if len(neighbor.neighbors) == 4:
                if neighbor.state == 'wall':
                        neighbor_wall += 1 
                if neighbor_wall > 1:
                    neighbor.state = 'coin'
                    neighbor_wall -= 1

            
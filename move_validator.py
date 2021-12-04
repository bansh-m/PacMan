import pygame
from pygame.math import Vector2 as vec

class Movement:
    def __init__(self):
        pass

    @staticmethod
    def moveable(self):
        if int(self.pix_pos.x) % self.app.cell_width == 15:
            if self.direction == vec(1,0) or self.direction == vec(-1,0) or self.direction == vec(0, 0):
                return True

        if int(self.pix_pos.y) % self.app.cell_height == 15:
            if self.direction == vec(0,1) or self.direction == vec(0,-1) or self.direction == vec(0, 0):
                return True
    
    staticmethod
    def can_move(self):
        if vec(self.grid_pos + self.direction) in self.app.walls:
            return False
        return True

    
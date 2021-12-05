import pygame
from settings import *


vec = pygame.math.Vector2

class Player:
    def __init__(self, app, pos):
        self.app = app
        self.grid_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0,0)
        self.stored_direction = None
        self.able_to_move = True
        self.speed = 3
        self.lives = 4
        self.score = 0
        self.multiplier = 1
        
    def update(self):
        if self.able_to_move: 
            self.pix_pos += self.direction*self.speed
            self.grid_to_pix_pos()
            self.on_coin()
            self.on_buff()
           
        if self.moveable():
            if self.stored_direction != None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()
        
    def grid_to_pix_pos(self):
        self.grid_pos[0] = (self.pix_pos[0] - self.app.cell_width//2)//self.app.cell_width
        self.grid_pos[1] = (self.pix_pos[1] - self.app.cell_height//2)//self.app.cell_height

    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (self.pix_pos.x, self.pix_pos.y), self.app.cell_width//2-3)

        for life in self.app.lives:
            self.app.screen.blit(self.app.heart, (life.x*self.app.cell_width + self.app.cell_width//2, 
            life.y*self.app.cell_height + self.app.cell_height//2))

    def move(self, direction):
        self.stored_direction = direction

    def can_move(self):
        if self.app.map_mode == 'classic':
            if vec(self.grid_pos + self.direction) in self.app.walls:
                return False
            return True   
        if self.app.map_mode == 'random':
            for cell in self.app.cells:
                if cell.grid_pos == vec(self.grid_pos + self.direction):
                    if cell.state == 'wall':
                        return False
                    return True
            
    def moveable(self):
        if int(self.pix_pos.x) % self.app.cell_width == 15:
            if self.direction == vec(1,0) or self.direction == vec(-1,0) or self.direction == vec(0, 0):
                return True

        if int(self.pix_pos.y) % self.app.cell_height == 15:
            if self.direction == vec(0,1) or self.direction == vec(0,-1) or self.direction == vec(0, 0):
                return True

    def get_pix_pos(self):
        return vec(self.grid_pos[0]*self.app.cell_width + self.app.cell_width//2, 
        self.grid_pos[1]*self.app.cell_height + self.app.cell_height//2)

    def on_buff(self):
        if self.grid_pos in self.app.buffs:
            if self.moveable():
                self.app.buff_timer = 10
                pygame.time.set_timer(pygame.USEREVENT, 1000)
                self.app.buffs.remove(self.grid_pos)
                for enemy in self.app.enemies:
                    enemy.state = 'eatable'    

    def on_coin(self):
        if self.app.map_mode == 'classic':        
            if self.grid_pos in self.app.coins:
                if self.moveable():
                    self.app.coins.remove(self.grid_pos)
                    self.score += 1* self.multiplier
        elif self.app.map_mode == 'random':
            if self.moveable():
                for cell in self.app.cells:
                        if cell.grid_pos == self.grid_pos and cell.state == 'coin':
                            cell.state = 'not wall'
                            self.score += 1* self.multiplier

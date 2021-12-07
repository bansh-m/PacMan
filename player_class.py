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
        self.routes = []
        self.alg = 'bfs'
        
        
    def update(self):
        if self.app.path_finder:
            self.get_path()
        if self.able_to_move: 
            self.pix_pos += self.direction*self.speed
            self.on_coin()
            self.on_buff()
        if self.moveable():
            self.grid_to_pix_pos()
            if self.stored_direction != None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()

    def set_alg(self):
        if self.alg == 'bfs':
            self.alg = 'dfs'
            print('dfs')
        elif self.alg == 'dfs': 
            self.alg = 'ucs'
            print('ucs')
        elif self.alg == 'ucs': 
            self.alg = 'bfs'
            print('bfs')
        
#DFS
    def dfs(self, start, target):
        stack = [(start, [start])]
        visited = []
        while stack:
            (current, path) = stack.pop()
            if current not in visited:
                if current == target:
                    return path
                visited.append(current)
                for neighbor in current.neighbors:
                    if neighbor.state != 'wall':
                        stack.append((neighbor, path + [neighbor]))
                
#UCS
    def usc(self, start, target):
        frontier = [(start, 0)]
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while frontier:
            (current, cost) = frontier.pop(0)
            if current == target:
              break
            for neighbor in current.neighbors:
                new_cost = cost
                if neighbor in cost_so_far:
                    new_cost = cost + cost_so_far[neighbor]
                elif neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:   
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost
                    if neighbor.state != 'wall':
                        frontier.append((neighbor, priority))
                        came_from[neighbor] = current
        current = target 
        path = [current]
        while current != start: 
            current = came_from[current]
            path.append(current)
        return path
        
#BFS
    def bfs(self, start, target):     
        frontier = [start]
        came_from = {}
        came_from[start] = None
        while frontier:
            current = frontier[0]
            frontier.remove(frontier[0])
            if current == target: 
                break           
            else:
                for neighbor in current.neighbors:
                    if neighbor not in came_from:
                        if neighbor.state != 'wall':
                            frontier.append(neighbor)
                            came_from[neighbor] = current
        current = target 
        path = [current]
        while current != start: 
            current = came_from[current]
            path.append(current)
        return path

#POS FUNCTIONS   
    def grid_to_pix_pos(self):
        self.grid_pos[0] = (self.pix_pos[0] - self.app.cell_width//2)//self.app.cell_width
        self.grid_pos[1] = (self.pix_pos[1] - self.app.cell_height//2)//self.app.cell_height
    
    def get_pix_pos(self):
        return vec(self.grid_pos[0]*self.app.cell_width + self.app.cell_width//2, 
        self.grid_pos[1]*self.app.cell_height + self.app.cell_height//2)

#DRAW FUNCTIONS
    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (self.pix_pos.x, self.pix_pos.y), self.app.cell_width//2-3)
        if self.app.map_mode == 'classic':
            for life in self.app.lives:
                self.app.screen.blit(self.app.heart, (life.x*self.app.cell_width + self.app.cell_width//2, 
                life.y*self.app.cell_height + self.app.cell_height//2))
        if self.app.path_finder:
            for route in self.routes:
                colour = route[1]
                for cell in route[0]:
                    pygame.draw.circle(self.app.screen, colour,
                    (cell.grid_pos.x*self.app.cell_width + self.app.cell_height//2, 
                    cell.grid_pos.y*self.app.cell_width + self.app.cell_height//2), 5)

# MOVE FUNCTIONS
    def move(self, direction):
        self.stored_direction = direction
    
    def get_path(self):
        self.routes.clear()
        start = next(cell for cell in self.app.cells if cell.grid_pos == self.grid_pos)  
        for enemy in self.app.enemies:
            target = next(cell for cell in self.app.cells if cell.grid_pos == enemy.grid_pos)
            if self.alg == 'bfs':                    
                self.routes.append([self.bfs(start, target), enemy.colour])
            elif self.alg == 'dfs':
                path = self.dfs(start, target)
                self.routes.append([path, enemy.colour])
            elif self.alg == 'ucs':                    
                self.routes.append([self.usc(start, target), enemy.colour])
                
    def can_move(self):
        if self.app.map_mode == 'classic' or 'shining':
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
        if int(self.pix_pos.x) % self.app.cell_width == self.app.cell_width//2:
            if self.direction == vec(1,0) or self.direction == vec(-1,0) or self.direction == vec(0, 0):
                return True

        if int(self.pix_pos.y) % self.app.cell_height == self.app.cell_height//2:
            if self.direction == vec(0,1) or self.direction == vec(0,-1) or self.direction == vec(0, 0):
                return True

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

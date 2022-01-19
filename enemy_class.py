import pygame, random
from settings import*


vec = pygame.math.Vector2

class Enemy:
    def __init__(self, app, pos, indx, lvl = 'random'):
        self.app = app
        self.indx = indx
        self.lvl = lvl
        self.grid_pos = pos
        self.start_pos = [pos.x, pos.y]
        self.direction = vec(0, 0)
        self.state = "origin"
        self.pix_pos = self.get_pix_pos()
        self.able_to_move = True
        self.speed = 0
        self.first_move = True
        self.colour = self.get_colour()
        self.path = []

    def update(self):
        if self.able_to_move:
            self.pix_pos += self.direction * self.speed           

        if self.moveable():
            self.grid_to_pix_pos()
            self.move()
            self.set_speed()
            self.able_to_move = self.can_move()
                
    def grid_to_pix_pos(self):
            self.grid_pos.x = (self.pix_pos.x - self.app.cell_width//2)//self.app.cell_width
            self.grid_pos.y = (self.pix_pos.y - self.app.cell_height//2)//self.app.cell_height

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
        while current != start: 
            current = came_from[current]    
            self.path.append(current)
        if self.path:        
            self.path.pop()

    def curr_cell(self):
        for cell in self.app.cells:
            if cell.grid_pos == self.grid_pos:
                return cell

    def curr_cells(self):
        cells = []
        for enemy in self.app.enemies:
            cells.append(enemy.curr_cell)
        return cells

    def get_bfs_direction(self):
        self.path.clear()
        self.bfs(self.curr_cell(), self.app.player.curr_cell())
        if self.path:
            self.direction = self.path.pop().grid_pos - self.grid_pos
        
    

    def move(self):
        if self.lvl == 'random':
            self.get_random_direction()
        elif self.lvl == 'smart':
            self.get_bfs_direction()

    def can_move(self):
        if self.app.map_mode == 'classic':
            if vec(self.grid_pos + self.direction) in self.app.walls:
                return False
            return True   

        if self.app.map_mode == 'shining':
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

    def get_random_direction(self):
        if self.first_move:
            while True:
                number = random.randint(1,4)
                if number == 1:
                   x_dir, y_dir = 1, 0
                elif number == 2:
                    x_dir, y_dir = 0, 1
                elif number == 3:
                    x_dir, y_dir = -1, 0
                else:
                    x_dir, y_dir = 0, -1       
                next_pos = vec(self.grid_pos.x + x_dir, self.grid_pos.y + y_dir)
                if next_pos not in self.app.walls:
                    self.first_move = False
                    break
            self.direction = vec(x_dir, y_dir) 
        else: 
            if not self.can_move():      
                number = random.randint(1,4)
                if number == 1:
                   x_dir, y_dir = 1, 0
                elif number == 2:
                    x_dir, y_dir = 0, 1
                elif number == 3:
                    x_dir, y_dir = -1, 0
                else:
                    x_dir, y_dir = 0, -1                        
                self.direction = vec(x_dir, y_dir)              

    def get_pix_pos(self):
            return vec(self.grid_pos.x*self.app.cell_width + self.app.cell_width//2, 
            self.grid_pos.y*self.app.cell_height + self.app.cell_height//2)

    def draw(self):
        pygame.draw.circle(self.app.screen, self.get_colour(), (self.pix_pos.x, self.pix_pos.y), self.app.cell_width//2-3)

        # if self.lvl == 'smart':
        #     if len(self.path) != 0:    
        #         for cell in self.path:
        #             pygame.draw.circle(self.app.screen, self.get_colour(),
        #                 (cell.grid_pos.x*self.app.cell_width + self.app.cell_height//2, 
        #                 cell.grid_pos.y*self.app.cell_width + self.app.cell_height//2), 3)

    def set_speed(self):
        if self.state == 'eatable':
            self.speed = 1
        else:
            self.speed = 2
        
    def get_colour(self):
        if self.state == 'origin':    
            if self.indx == 0:
                return PURPLE
            elif self.indx == 1:
                return GREEN
            elif self.indx == 2:
                return LIGHT_BLUE
            elif self.indx == 3:
                return RED
            else: return GREEN
        else:
            return (154, 205, 50)
    

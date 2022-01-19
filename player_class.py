import pygame, random
from settings import *
from timer import Timer

vec = pygame.math.Vector2

class Player:
    def __init__(self, app, pos, alg = 'bfs'):
        self.app = app
        self.grid_pos = [pos.x, pos.y]
        self.pix_pos = self.get_pix_pos()
        self.direction = vec(0,0)
        self.stored_direction = None
        self.able_to_move = True
        self.speed = 2
        self.lives = 4
        self.score = 0
        self.multiplier = 1
        self.routes = []
        self.alg = alg
        self.timer = Timer()
        self.max = 100000000
        self.min = -100000000
        self.depth = 2
        self.game_state = {}
        self.successor_score = 0
        self.successor_coins = []

    def update(self):
        if self.alg != None:
            self.timer.start()
            self.get_path()
            self.timer.stop()
        if self.able_to_move: 
            self.pix_pos += self.direction*self.speed
            self.grid_to_pix_pos()
            self.on_coin()
            self.on_buff()
        if self.moveable():
            if self.alg == 'minimax' or self.alg == 'expectimax':
                if self.routes:
                    self.stored_direction = self.routes[0].grid_pos - self.grid_pos
            elif self.alg == 'a*':
                if self.routes:    
                    self.stored_direction = self.routes.pop().grid_pos - self.grid_pos
            if self.stored_direction != None:
                self.direction = self.stored_direction
            self.able_to_move = self.can_move()

    def set_alg(self):
        if self.alg == 'bfs':
            print("bfs search time -", "%.5f" % self.timer.elapsed)
            self.alg = 'dfs'
            print('dfs')
        elif self.alg == 'dfs': 
            print("dfs search time -", "%.5f" % self.timer.elapsed)
            self.alg = 'ucs'
            print('ucs')
        elif self.alg == 'ucs': 
            print("ucs search time -", "%.5f" % self.timer.elapsed)
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

#A* 
    def heuristic(self, target, neighbor):    
        return abs(target.grid_pos.x - neighbor.grid_pos.x) + abs(target.grid_pos.y - neighbor.grid_pos.y)

    def a_star(self, start, target):
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
                    if neighbor.state != 'wall':
                        priority = new_cost + self.heuristic(target, neighbor)
                        frontier.append((neighbor, priority))
                        came_from[neighbor] = current
        current = target
        self.routes.append(target)
        while current != start:
            current = came_from[current]
            self.routes.append(current)

#Minimax
    def minimax(self, depth, current, is_max, alpha, beta, path):
        
        neighbors = list(set(current.return_roads()) - set(path))
        if depth == 0 or len(neighbors) == 0:
            return self.get_score(path)

        if is_max:

            best = self.min
            best_path = path.copy()
            placed = False

            for cell in list(set(current.return_roads()) - set(path)):
                path.append(cell)
                val = self.minimax(depth - 1, cell, False, alpha, beta, path)
                best = max(best, val[0])
                if best == val[0]:
                    if placed:
                        best_path.pop()
                    best_path.append(cell)
                    placed = True
                path.remove(cell)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break
                
            return best, best_path

        else:
            best = self.max
            best_path = path.copy()
            placed = False

            for cell in list(set(current.return_roads()) - set(path)):
                path.append(cell)
                val = self.minimax(depth - 1, cell, True, alpha, beta, path)
                best = min(best, val[0])
                if best == val[0]:
                    if placed:
                        best_path.pop()
                    best_path.append(cell)
                    placed = True
                path.remove(cell)
                beta = min(beta, best)
                if beta <= alpha:
                    break

            return best, best_path

    def get_score(self, path):
        priority = 0
        for cell in path:
            if cell.state == 'coin':
                priority += 10
            if cell.state == 'buff':
                priority += 25
            elif cell.state == 'empty':
                priority -= 5
            for enemy in self.app.enemies:
                if enemy.grid_pos == cell.grid_pos:
                    priority -= 100
        
        return priority, path

#MINMAX#2

    def current_game_state(self):
        for enemy in self.app.enemies:
            self.game_state[enemy.indx] = next(cell for cell in self.app.cells if cell.grid_pos == enemy.grid_pos)
        self.game_state[4] = self.curr_cell()
    
    def successor_game_state(self, agent_indx, cell):  
        self.game_state[agent_indx] = cell
        if agent_indx == 4:
            if cell.state == 'empty':
                self.successor_score -= 10
            elif cell.state == 'coin':
                self.successor_score += 10
        return self.game_state

    def minmax(self, game_state):

        PACMAN = 4
        def max_agent(game_state, depth, alpha, beta):
            cells = game_state[PACMAN].return_roads()
            best_score = self.min
            score = best_score
            best_cell = game_state[PACMAN]
            for cell in cells:
                score = min_agent(self.successor_game_state(PACMAN, cell), depth, 1, alpha, beta)
                if score > best_score:
                    best_score = score
                    best_cell = cell
                alpha = max(alpha, best_score)
                if best_score > beta:
                    self.current_game_state()
                    return best_score
            if depth == 0:
                print(best_score)
                return best_cell
            else:
                return best_score

        def min_agent(game_state, depth, ghost_indx, alpha, beta):
            next_agent = ghost_indx + 1
            if ghost_indx == 3:
                next_agent = PACMAN
            cells = game_state[ghost_indx].return_roads()
            best_score = self.max
            score = best_score
            for cell in cells:
                if next_agent == PACMAN:
                    if depth == self.depth - 1:
                        score = self.evaluationFunction(self.successor_game_state(ghost_indx, cell))
                    else:
                        score = max_agent(self.successor_game_state(ghost_indx, cell), depth + 1, alpha, beta)
                else:
                    score = min_agent(self.successor_game_state(ghost_indx, cell), depth, next_agent, alpha, beta)
                if score < best_score:
                    best_score = score
                beta = min(beta, best_score)
                if best_score < alpha:
                    return best_score
            return best_score
        
        return max_agent(game_state, 0, self.min, self.max)
    
    def evaluationFunction(self, game_state):
        score = self.successor_score
        self.successor_score = 0
        p_pos = game_state[4]
        
        def closest_dot():
            distances = []
            for coin in self.app.coins:
                distances.append(self.manhattanDistance(coin, p_pos))
            return min(distances) if len(distances) > 0 else 1

        def closest_ghost():
            distances = []
            for key in game_state:
                if key < 4:
                    ghost = game_state[key]
                    distances.append(self.manhattanDistance(ghost, p_pos))
            return min(distances)
        
        # score = score * 2 if closest_dot() < closest_ghost() + 3 else score
        return score

    def manhattanDistance(self, target, goal):
        return abs(target.grid_pos.x - goal.grid_pos.x) + abs(target.grid_pos.y - goal.grid_pos.y)

#EXPECTIMAX
    def expectimax(self, depth, current, path, is_max):
        neighbors = list(set(current.return_roads()) - set(path))
        if depth == 0 or len(neighbors) == 0:
            return self.get_score(path)

        if is_max:
            best = self.min
            best_path = path.copy()
            placed = False
            
            for cell in current.return_roads():
                path.append(cell)
                val = self.expectimax(depth-1, cell, path, False)
                if best < val[0]:
                    if placed:
                        best_path.pop()
                    best_path.append(cell)
                    placed = True
                    best = val[0]
                path.remove(cell)
            return best, best_path
        else:
            best = 0
            best_path = path.copy()
            count = 0

            for cell in current.return_roads():
                path.append(cell)
                count += 1
                best += self.expectimax(depth - 1, cell, path, True)[0]
                path.remove(cell)
            if count != 0:
                best = best/count
            return best, best_path

#POS FUNCTIONS   
    def grid_to_pix_pos(self):
        self.grid_pos[0] = (self.pix_pos[0] - self.app.cell_width//2)//self.app.cell_width
        self.grid_pos[1] = (self.pix_pos[1] - self.app.cell_height//2)//self.app.cell_height
    
    def get_pix_pos(self):
        return vec(self.grid_pos[0]*self.app.cell_width + self.app.cell_width//2, 
        self.grid_pos[1]*self.app.cell_height + self.app.cell_height//2)

# MOVE FUNCTIONS
    def move(self, direction):
        self.stored_direction = direction

    def random_target(self):
        while True:
            rand_target = random.choice(self.app.cells) 
            if rand_target.state == 'coin':
                self.targ = rand_target
                return
            
    def on_target(self):
        if self.moveable():
            if self.grid_pos == self.targ.grid_pos:
                return True
            return False

    def curr_cell(self):
        for cell in self.app.cells:
            if cell.grid_pos == self.grid_pos:
                return cell

    def get_path(self):
        start = next(cell for cell in self.app.cells if cell.grid_pos == self.grid_pos)
        if self.alg == 'a*':
            if len(self.routes) == 0:
                self.random_target()
                self.a_star(self.curr_cell(), self.targ)
                # self.routes.pop()
        
        elif self.alg == 'expectimax':
            self.routes.clear()
            _, path = self.expectimax(5, start, [start], True)
            self.routes.append(path[1])

        elif self.alg == 'minimax':
            self.routes.clear()
            # cost, path = self.minimax(3, start, True, self.min, self.max, [start])
            self.current_game_state()
            path = self.minmax(self.game_state)
            self.routes.append(path)
          
        else:
            self.routes.clear()
            for enemy in self.app.enemies:
                target = next(cell for cell in self.app.cells if cell.grid_pos == enemy.grid_pos)
                if self.alg == 'bfs':                    
                    self.routes.append([self.bfs(start, target), enemy.colour])
                elif self.alg == 'dfs':
                    self.routes.append([self.dfs(start, target), enemy.colour])
                elif self.alg == 'ucs':                    
                    self.routes.append([self.usc(start, target), enemy.colour])

    def can_move(self):
        if self.app.map_mode == 'shining':
            if vec(self.grid_pos + self.direction) in self.app.walls:
                return False
            return True
        
        elif self.app.map_mode == 'random' or self.app.map_mode == 'classic':
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
        if self.app.map_mode == 'classic':   
            if self.grid_pos in self.app.buffs:
                if self.moveable():
                    self.app.buff_timer = 10
                    pygame.time.set_timer(pygame.USEREVENT, 1000)
                    self.app.buffs.remove(self.grid_pos)
                    for enemy in self.app.enemies:
                        enemy.state = 'eatable'    

    def on_coin(self):
        if self.app.map_mode == 'shining':        
            if self.grid_pos in self.app.coins:
                if self.moveable():
                    self.app.coins.remove(self.grid_pos)
                    self.score += 1* self.multiplier
        
        elif self.app.map_mode == 'random' or self.app.map_mode == 'classic':
            if self.moveable():
                for cell in self.app.cells:
                        if cell.grid_pos == self.grid_pos and cell.state == 'coin':
                            cell.state = 'empty'
                            self.score += 1* self.multiplier

#DRAW FUNCTIONS
    def draw(self):
        pygame.draw.circle(self.app.screen, PLAYER_COLOUR, (self.pix_pos.x, self.pix_pos.y), self.app.cell_width//2-3)
        
        if self.app.map_mode == 'classic':
            for life in self.app.lives:
                self.app.screen.blit(self.app.heart, (life.x*self.app.cell_width + self.app.cell_width//2, 
                life.y*self.app.cell_height + self.app.cell_height//2))
        
        if self.alg == 'a*':
            if len(self.routes) != 0:    
                for cell in self.routes:
                    pygame.draw.circle(self.app.screen, YELLOW,
                        (cell.grid_pos.x*self.app.cell_width + self.app.cell_height//2, 
                        cell.grid_pos.y*self.app.cell_width + self.app.cell_height//2), 5)

        if self.alg == 'minimax':
             for cell in self.routes:
                    pygame.draw.circle(self.app.screen, YELLOW,
                        (cell.grid_pos.x*self.app.cell_width + self.app.cell_height//2, 
                        cell.grid_pos.y*self.app.cell_width + self.app.cell_height//2), 5)

        if self.alg == 'bfs' or self.alg == 'dfs' or self.alg == 'ucs': 
            for route in self.routes:
                colour = route[1]
                for cell in route[0]:
                    pygame.draw.circle(self.app.screen, colour,
                    (cell.grid_pos.x*self.app.cell_width + self.app.cell_height//2, 
                    cell.grid_pos.y*self.app.cell_width + self.app.cell_height//2), 5)
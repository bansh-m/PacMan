from random import shuffle
import pygame, sys

from pygame.constants import USEREVENT
from cell_class import Cell
from settings import *
from player_class import *
from enemy_class import *


pygame.init()
vec = pygame.math.Vector2

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((PLAYING_WIDTH, PLAYING_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'start'
        self.cell_width = CELL_WIDTH
        self.cell_height = CELL_HEIGHT
        self.p_pos = 0
        self.e_pos = []
        self.walls = []
        self.coins = []
        self.enemies = []
        self.e_zone = []
        self.lives = []
        self.buffs = []
        self.cells = []
        self.stable_cells = []
        self.text_pos = []
        self.win_lose = None
        self.buff_timer = 0
        self.start_ticks = pygame.time.get_ticks()
        self.current_text_pos = 0
        self.enemy_mode = 'random'
        self.map_mode = 'random'
        self.alg = None

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw()
            elif self.state == 'game over':
                if self.win_lose == 'lose':   
                    self.game_over_events()
                    self.game_over_update()
                    self.game_over_draw()
                else:
                    self.game_over_events()
                    self.win_game_over_draw()
            else:
                self.running = False
            self.clock.tick(FPS)
        pygame.quit()
        sys.exit()
   
#HELP FUNCTIOS    
    def draw_text(self, inscr, size, pos, colour, font_name, changeable, id = ''):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(inscr, False, colour)
        text_size = text.get_size()
        pos[0] = pos[0] - text_size[0]//2
        pos[1] = pos[1] - text_size[1]//2
        if changeable:
            if self.on_text(pos, text_size, id):
                colour = WHITE
                text = font.render(inscr, False, colour)
        self.screen.blit(text, pos)

    def on_text(self, pos, text_size, id):
        cursor_posx ,cursor_posy = pygame.mouse.get_pos()
        if pos[0] <= cursor_posx <= pos[0] + text_size[0] and pos[1] <= cursor_posy <= pos[1] + text_size[1]:
            self.current_text_pos = id
            return True
        return False

    def load(self):
        self.background = pygame.image.load('images/maze.png')
        self.background = pygame.transform.scale(self.background, (PLAYING_WIDTH, PLAYING_HEIGHT))
        self.heart = pygame.image.load('images/heart.png')
        self.heart = pygame.transform.scale(self.heart, (25, 30))
        self.buff = pygame.image.load('images/buff.png')
        self.buff = pygame.transform.scale(self.buff,(28, 28))
     
        if self.map_mode == 'shining':
            with open("mazes/shining_maze.txt", 'r') as file:
                 for yidx, line in enumerate(file):
                    for xidx, char in enumerate(line):
                        if char == "1":
                            self.walls.append(vec(xidx, yidx))
                        elif char == "0":
                            self.coins.append(vec(xidx, yidx))
                        elif char == 'P':
                            self.p_pos = [xidx, yidx]
                        elif char == 'E':
                            self.e_pos.append(vec(xidx, yidx))

        elif self.map_mode == 'random':
            with open("mazes/rand_grid.txt", 'r') as file:
                for yidx, line in enumerate(file):
                    for xidx, char in enumerate(line):
                        if char == "1":
                            self.stable_cells.append(Cell(vec(xidx, yidx), self, 'wall'))
                        if char == "2":
                            self.stable_cells.append(Cell(vec(xidx, yidx), self, 'coin'))
        
        elif self.map_mode == 'classic':
            with open("mazes/grid.txt", 'r') as file:
                for yidx, line in enumerate(file):
                    for xidx, char in enumerate(line):
                        if char == "1":
                            self.walls.append(vec(xidx, yidx))
                        elif char == "0":
                            self.coins.append(vec(xidx, yidx))
                        elif char == 'P':
                            self.p_pos = [xidx, yidx]
                        elif char in ["2", "3", "4", "5"]:
                            self.e_pos.append(vec(xidx, yidx))
                        elif char == 'L':
                            self.lives.append(vec(xidx, yidx))
                        elif char == 'B':
                            self.buffs.append(vec(xidx, yidx))

    def create_cells(self):
        for x in range(2, 26):
            for y in range(2, 29):
                pos = vec(x, y)
                self.cells.append(Cell(pos, self))
        self.cells.extend(self.stable_cells) 
        for cell in self.cells:
            cell.cell_connect()
            # cell.get_neighbors()
            cell.set_state()
            cell.shuffle_state()
            if cell.grid_pos == vec(13, 14):
                if cell.state != 'wall':
                    self.p_pos = cell.grid_pos
                else:
                    for neighbor in cell.neighbors:
                        if neighbor.state == 'coin':
                            self.p_pos = neighbor.grid_pos
                            break
    
    def make_ememies(self):
        if self.map_mode == 'classic':
            for indx, pos in enumerate(self.e_pos):
                self.enemies.append(Enemy(self, vec(pos), indx))

        elif self.map_mode == 'shining':
            for indx, pos in enumerate(self.e_pos):
                self.enemies.append(Enemy(self, vec(pos), indx))
        
        elif self.map_mode == 'random':
            if self.enemy_mode == 'random': 
                e_pos = [vec(1, 1), vec(26, 1), vec(1, 29), vec(26, 29)]
                for indx, pos in enumerate(e_pos):
                    self.enemies.append(Enemy(self, vec(pos), indx))
            elif self.enemy_mode == 'smart':
                e_pos = [vec(1, 1), vec(26, 1), vec(1, 29), vec(26, 29)]
                for indx, pos in enumerate(e_pos):
                    self.enemies.append(Enemy(self, vec(pos), indx, 'smart'))

    def draw_grid(self):
        for x in range(50):
            pygame.draw.line(self.screen, GREY, (x*22, 0), (x*22, PLAYING_HEIGHT))

        for x in range(50):
            pygame.draw.line(self.screen, GREY, (0, x*22), (PLAYING_WIDTH, x*22))
        
        
    def draw_walls(self):
        if self.map_mode == 'shining':
            for wall in self.walls:
                pygame.draw.rect(self.screen, (1, 50, 32),
                (wall.x*SHINING_CELL_WIDTH, wall.y*SHINING_CELL_HEIGHT, 16, 16))

        elif self.map_mode == 'classic':
            for wall in self.walls:
                pygame.draw.rect(self.screen, (145, 163, 176),
                (wall.x*CELL_WIDTH, wall.y*CELL_HEIGHT, 28, 28))

        elif self.map_mode == 'random':
            for cell in self.cells:
                if cell.state == 'wall':
                    pygame.draw.rect(self.screen, (51, 51, 153),
                    (cell.grid_pos.x*self.cell_width, cell.grid_pos.y*self.cell_height, 28, 28))

    def draw_coins(self):
        if self.map_mode == 'classic':
            for coin in self.coins:
                pygame.draw.circle(self.screen, (157, 241, 230), 
                (coin.x*self.cell_width + self.cell_width//2, coin.y*self.cell_height + self.cell_height//2), 5)

        elif self.map_mode == 'shining':
            for coin in self.coins:
                pygame.draw.circle(self.screen, (157, 241, 230), 
                (coin.x*SHINING_CELL_WIDTH + SHINING_CELL_WIDTH//2, coin.y*SHINING_CELL_WIDTH + SHINING_CELL_HEIGHT//2), 5)

        elif self.map_mode == 'random':
            for cell in self.cells:
                if cell.state == 'coin':
                    pygame.draw.circle(self.screen, (157, 241, 230), 
                    (cell.grid_pos.x*self.cell_width + self.cell_width//2, cell.grid_pos.y*self.cell_height + self.cell_height//2), 4)

    def draw_buffs(self):
        for buff in self.buffs:
            self.screen.blit(self.buff, (buff.x*self.cell_width, buff.y*self.cell_height)) 

    def remove_life(self):
        self.player.lives -= 1
        self.lives.pop()
        if self.player.lives == 0:
            self.win_lose = 'lose'
            self.state = "game over"
        else:
            self.player.grid_pos = vec(self.p_pos)
            self.player.pix_pos = self.player.get_pix_pos()
            self.player.direction *= 0
            for enemy in self.enemies:
                enemy.first_move = True
                enemy.grid_pos = vec(enemy.start_pos)
                enemy.pix_pos = enemy.get_pix_pos()
                enemy.direction *= 0
        
    def reset(self):
        self.player.lives = 4
        self.player.score = 0
        self.player.grid_pos = vec(self.p_pos)
        self.player.pix_pos = self.player.get_pix_pos()
        self.player.direction *= 0
        for enemy in self.enemies:
            enemy.first_move = True
            enemy.grid_pos = vec(enemy.start_pos)
            enemy.pix_pos = enemy.get_pix_pos()
            enemy.direction *= 0

        self.coins = []
        with open("grid.txt", 'r') as file:
            for yidx, line in enumerate(file):
                for xidx, char in enumerate(line):
                    if char == '0':
                        self.coins.append(vec(xidx, yidx))
                    elif char == 'L':
                        self.lives.append(vec(xidx, yidx))
                    elif char == 'B':
                        self.buffs.append(vec(xidx, yidx)) 
        self.state = "playing"

#START FUNCTIONS 
    def start_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.load()
                if self.map_mode == 'random':
                    self.create_cells()
                self.make_ememies()               
                self.player = Player(self, vec(self.p_pos), self.alg)
                self.state = 'playing'

            if event.type == pygame.MOUSEBUTTONDOWN and self.on_text:
                if self.current_text_pos == 'play':
                    self.load()
                    if self.map_mode == 'random':
                        self.create_cells()
                    self.make_ememies()               
                    self.player = Player(self, vec(self.p_pos), self.alg)
                    self.state = 'playing'
                elif self.current_text_pos == 'classic_map':
                    self.map_mode = 'classic'
                elif self.current_text_pos == 'random_enemy':
                    self.enemy_mode = 'random' 
                elif self.current_text_pos == 'random_map':
                    self.map_mode = 'random'
                elif self.current_text_pos == 'path_finder':
                    self.alg = 'bfs'
                elif self.current_text_pos == 'smart_enemy':
                    self.enemy_mode = 'smart'
                elif self.current_text_pos == 'shining_map':
                    self.cell_width = SHINING_CELL_WIDTH
                    self.cell_height = SHINING_CELL_HEIGHT
                    self.map_mode = 'shining'
                elif self.current_text_pos == 'a*':
                    self.alg = 'a*'
                    
    def start_update(self):
        pass
            
    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUC-MAN', START_TEXT_SIZE + 50, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 - 200], YELLOW, START_FONT, False)
        self.draw_text('PLAY', START_TEXT_SIZE + 30, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 + 300], GREY, START_FONT,  True, 'play')
        self.draw_text('MAP MODE:', START_TEXT_SIZE - 15, [PLAYING_WIDTH//4, PLAYING_HEIGHT//2+50], WHITE, START_FONT, False)
        self.draw_text('ENEMY MODE:', START_TEXT_SIZE -15, [PLAYING_WIDTH - PLAYING_WIDTH//4, PLAYING_HEIGHT//2 + 50], WHITE, START_FONT, False)
        self.draw_text('CLASSIC', START_TEXT_SIZE - 20, [PLAYING_WIDTH//4, PLAYING_HEIGHT//2 + 100], GREY, START_FONT, True, 'classic_map')
        self.draw_text('RANDOM', START_TEXT_SIZE - 20, [PLAYING_WIDTH//4, PLAYING_HEIGHT//2 + 145], GREY, START_FONT, True, 'random_map')
        self.draw_text('RANDOM', START_TEXT_SIZE - 20, [PLAYING_WIDTH - PLAYING_WIDTH//4, PLAYING_HEIGHT//2 + 100], GREY, START_FONT, True, 'random_enemy')
        self.draw_text('SHINING', START_TEXT_SIZE - 20, [PLAYING_WIDTH//4, PLAYING_HEIGHT//2 + 190], GREY, START_FONT, True, 'shining_map')
        self.draw_text('SMART', START_TEXT_SIZE - 20, [PLAYING_WIDTH -  PLAYING_WIDTH/4, PLAYING_HEIGHT//2 + 145], GREY, START_FONT, True, 'smart_enemy')
        self.draw_text('BFS/DFS/UCS', START_TEXT_SIZE - 25, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 + 145], GREY, START_FONT, True, 'path_finder')
        self.draw_text('A*', START_TEXT_SIZE - 25, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 + 190], GREY, START_FONT, True, 'a*')
        pygame.display.update()    

#PLAYING FUNCTIONS
    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.reset()
                self.state = 'start'
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move(vec(-1, 0))
                if event.key == pygame.K_RIGHT:
                    self.player.move(vec(1, 0))
                if event.key == pygame.K_UP:
                    self.player.move(vec(0, -1))
                if event.key == pygame.K_DOWN:
                    self.player.move(vec(0, 1))
                if event.key == pygame.K_z:
                    self.player.set_alg()
            if event.type == pygame.USEREVENT:
                self.buff_timer -= 1
                if self.buff_timer == 0:
                    for enemy in self.enemies:
                        enemy.state = 'origin'
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                           
    def playing_update(self):       
        self.player.update()
        for enemy in self.enemies:
            enemy.update() 
            if enemy.grid_pos == self.player.grid_pos:
                if enemy.state == 'origin':
                    self.remove_life()
                else:
                    self.player.score += 50 * self.player.multiplier
                    enemy.state = 'origin'
                    enemy.first_move = True
                    enemy.grid_pos = vec(enemy.start_pos)
                    enemy.pix_pos = enemy.get_pix_pos()
                    enemy.direction *= 0   
        if self.coins == 0:
            self.win_lose = 'win'
            self.state = "game over"

    def playing_draw(self): 
        if self.map_mode == 'classic':
            self.screen.fill(BLACK)
            self.player.draw()
            self.draw_walls()
            self.draw_coins()
            self.draw_buffs()
            for enemy in self.enemies:
                enemy.draw() 
            
            self.draw_text('SCORE: ' + str(self.player.score), START_TEXT_SIZE - 20, 
                [SCORE_POS_X, SCORE_POS_Y], (255, 255, 255), START_FONT, False)

            self.draw_text('X' + str(self.player.multiplier), START_TEXT_SIZE - 20, 
                [SCORE_POS_X, SCORE_POS_Y + 30], (255, 255, 255), START_FONT, False)

            self.draw_text('BUFF: ' + str(self.buff_timer), START_TEXT_SIZE - 20, 
                [SCORE_POS_X, SCORE_POS_Y + 170], (255, 255, 255), START_FONT, False)    

        elif self.map_mode == 'random':
            self.screen.fill(BLACK)
            self.player.draw()
            self.draw_walls()
            for enemy in self.enemies:
                enemy.draw()
            # self.draw_coins()

        elif self.map_mode == 'shining':
            self.screen = pygame.display.set_mode((SHINING_MAZE_WIDTH, SHINING_MAZE_HEIGHT))
            self.screen.fill(BROWN)
            self.draw_walls()
            self.player.draw()
            for enemy in self.enemies:
                enemy.draw()

        pygame.display.update()

#GAME OVER FUNCTIONS
    def game_over_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.reset()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
                self.running = False
    
    def game_over_update(self):
        pass

    def game_over_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('YOUR SCORE: ' + str(self.player.score), END_TEXT_SIZE, 
            [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 - 100], (145, 92, 131), START_FONT, False)
        self.draw_text('PUSH SPACE BAR TO RESTART', END_TEXT_SIZE, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2], (170, 132, 58), START_FONT, False)
        self.draw_text('PUSH ESC TO QUIT', END_TEXT_SIZE, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 + 100], (0, 106, 255), START_FONT, False)
        pygame.display.update()

    def win_game_over_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('YOUR SCORE: ' + str(self.player.score),
            END_TEXT_SIZE, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2 - 100], (145, 92, 131), START_FONT, False)
        self.draw_text('PUSH SPACE BAR TO RESTART', END_TEXT_SIZE, [PLAYING_WIDTH//2, PLAYING_HEIGHT//2], (170, 132, 58), START_FONT, False)
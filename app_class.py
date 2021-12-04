import pygame, sys, copy

from pygame.constants import USEREVENT
from cell_class import Cell
from settings import *
from player_class import *
from enemy_class import *

pygame.init()
vec = pygame.math.Vector2

class App:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
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
        self.win_lose = None
        # self.load()
        self.player = Player(self, vec(self.p_pos))
        self.make_ememies()
        self.create_cells()
        self.buff_timer = 0
        self.start_ticks = pygame.time.get_ticks()

    def run(self):
        while self.running:
            if self.state == 'start':
                self.start_events()
                self.start_update()
                self.start_draw()
            elif self.state == 'playing':
                self.playing_events()
                self.playing_update()
                self.playing_draw1()
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
    def draw_text(self, inscr, size, pos, colour, font_name):
        font = pygame.font.SysFont(font_name, size)
        text = font.render(inscr, False, colour)
        text_size = text.get_size()
        pos[0] = pos[0] - text_size[0]//2
        pos[1] = pos[1] - text_size[1]//2
        self.screen.blit(text, pos)

    def load(self):
        self.background = pygame.image.load('images/maze.png')
        self.background = pygame.transform.scale(self.background, (WIDTH, HEIGHT))
        self.heart = pygame.image.load('images/heart.png')
        self.heart = pygame.transform.scale(self.heart, (25, 30))
        self.buff = pygame.image.load('images/buff.png')
        self.buff = pygame.transform.scale(self.buff,(28, 28))
     
        #Placing objects in reference to their pos in maze.txt
        with open("grid.txt", 'r') as file:
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
        for x in range(0, 27+1):
            for y in range(0, 30+1):
                pos = vec(x, y)
                self.cells.append(Cell(pos, self))

        for cell in self.cells:
            cell.cell_connect()
            cell.get_neighbors()
            cell.random_state()
            cell.unrandom_state()
            
    def make_ememies(self):
        for indx, pos in enumerate(self.e_pos):
            self.enemies.append(Enemy(self, vec(pos), indx))

    def draw_grid(self):
        for x in range(28):
            pygame.draw.line(self.screen, GREY, (x*self.cell_width, 0), (x*self.cell_width, HEIGHT))

        for x in range(31):
            pygame.draw.line(self.screen, GREY, (0, x*self.cell_height), (WIDTH, x*self.cell_height))
        
        # for wall in self.walls:
        #     pygame.draw.rect(self.background, (112, 55, 163),
        #      (wall.x*self.cell_width, wall.y*self.cell_height, self.cell_width, self.cell_height)) 
        # for coin in self.coins:
        #     pygame.draw.rect(self.background, (157, 241, 230),
        #      (coin.x*self.cell_width, coin.y*self.cell_height, self.cell_width, self.cell_height))  

    def draw_coins(self):
        for coin in self.coins:
            pygame.draw.circle(self.screen, (157, 241, 230), 
            (coin.x*self.cell_width + self.cell_width//2, coin.y*self.cell_height + self.cell_height//2), 5)

    def draw_cells(self):
        for cell in self.cells:
            if cell.state == 'wall':
                pygame.draw.rect(self.screen, (42, 52, 57),
                (cell.grid_pos.x*self.cell_width, cell.grid_pos.y*self.cell_height, self.cell_width, self.cell_height))
            else:
                pygame.draw.circle(self.screen, (157, 241, 230), 
                (cell.grid_pos.x*self.cell_width + self.cell_width//2, cell.grid_pos.y*self.cell_height + self.cell_height//2), 5)

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
                self.state = 'playing'

    def start_update(self):
        pass                

    def start_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('PUSH SPACE BAR TO PLAY', START_TEXT_SIZE, [WIDTH//2, HEIGHT//2], (170, 132, 58), START_FONT)
        pygame.display.update()    

#PLAYING FUNCTIONS
    def playing_events(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE or event.type == pygame.QUIT:
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
            if event.type == pygame.USEREVENT:
                self.buff_timer -= 1
                if self.buff_timer == 0:
                    for enemy in self.enemies:
                        enemy.state = 'origin'
                    pygame.time.set_timer(pygame.USEREVENT, 0)
                           
    def playing_update(self):
        self.seconds = (pygame.time.get_ticks() - self.start_ticks)/1000
        self.player.update()
        for enemy in self.enemies:
            enemy.update() 
            if enemy.grid_pos == self.player.grid_pos:
                if enemy.state == 'origin':
                    self.remove_life()
                else:
                    self.player.score += 100 * self.player.multiplier
                    enemy.state = 'origin'
                    enemy.first_move = True
                    enemy.grid_pos = vec(enemy.start_pos)
                    enemy.pix_pos = enemy.get_pix_pos()
                    enemy.direction *= 0   
        if len(self.coins) == 0:
            self.win_lose = 'win'
            self.state = "game over"

    def playing_draw1(self):
        self.screen.fill(BLACK)
        self.draw_cells()
        self.draw_grid()
        pygame.display.update()
    
    def playing_draw(self): 
        self.screen.blit(self.background, (0,0))
        self.player.draw()
        self.draw_coins()
        self.draw_buffs()
        for enemy in self.enemies:
            enemy.draw() 
        self.draw_text('SCORE: ' + str(self.player.score), START_TEXT_SIZE - 20, 
            [SCORE_POS_X, SCORE_POS_Y], (255, 255, 255), START_FONT)
        
        self.draw_text('X' + str(self.player.multiplier), START_TEXT_SIZE - 20, 
            [SCORE_POS_X, SCORE_POS_Y + 30], (255, 255, 255), START_FONT)
        
        self.draw_text('TIME: ' + str(int(self.seconds)), START_TEXT_SIZE - 20, 
            [SCORE_POS_X, SCORE_POS_Y + 60], (255, 255, 255), START_FONT)
        
        self.draw_text('BUFF: ' + str(self.buff_timer), START_TEXT_SIZE - 20, 
            [SCORE_POS_X, SCORE_POS_Y + 170], (255, 255, 255), START_FONT)        
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
            [WIDTH//2, HEIGHT//2 - 100], (145, 92, 131), START_FONT)
        self.draw_text('PUSH SPACE BAR TO RESTART', END_TEXT_SIZE, [WIDTH//2, HEIGHT//2], (170, 132, 58), START_FONT)
        self.draw_text('PUSH ESC TO QUIT', END_TEXT_SIZE, [WIDTH//2, HEIGHT//2 + 100], (0, 106, 255), START_FONT)
        pygame.display.update()

    def win_game_over_draw(self):
        self.screen.fill(BLACK)
        self.draw_text('YOUR SCORE: ' + str(self.player.score),
            END_TEXT_SIZE, [WIDTH//2, HEIGHT//2 - 100], (145, 92, 131), START_FONT)
        self.draw_text('PUSH SPACE BAR TO RESTART', END_TEXT_SIZE, [WIDTH//2, HEIGHT//2], (170, 132, 58), START_FONT)
import skimage
import torch
import random
import numpy as np
from matplotlib import pyplot as plt
from collections import deque

from settings import *
from app_class import *
from model import Linear_QNet, QTrainer
from plotter import plot

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001
ACTIONS = 4
INPUT_SIZE = 28 * 31


class Agent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0
        self.gamma = 0.9
        self.memory = deque(maxlen=MAX_MEMORY)
        self.model = Linear_QNet(INPUT_SIZE, 256, ACTIONS)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    @staticmethod
    def get_state(game):
        image = skimage.color.rgb2gray(game.get_state())
        image = skimage.transform.resize(image, (28, 31))
        return np.array(image).flatten()

    def remember(self, state, action, reward, next_state, game_over):
        self.memory.append((state, action, reward, next_state, game_over))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, game_overs = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, game_overs)

    def train_short_memory(self, state, action, reward, next_state, game_over):
        self.trainer.train_step(state, action, reward, next_state, game_over)

    def get_action(self, state):
        self.epsilon = 180 - self.n_games
        final_move = np.zeros(ACTIONS)
        if random.randint(0, 400) < self.epsilon:
            move = random.randint(0, ACTIONS-1)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move


def train():
    record = 0
    game = App()
    agent = Agent()
    game.run()
    
    while True:
        
        state_old = agent.get_state(game)

        final_move = agent.get_action(state_old)

        reward, game_over, score = game.play_step(final_move)

        state_new = agent.get_state(game)

        agent.train_short_memory(state_old, final_move, reward, state_new, game_over)

        agent.remember(state_old, final_move, reward, state_new, game_over)

        if game_over:
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()
            if score > record:
                record = score
                agent.model.save()

            print("Game", agent.n_games, 'Score', score, 'Record', record)
train()
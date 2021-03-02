# Modified from https://gist.github.com/timurbakibayev/1f683d34487362b0f36280989c80960c

# Modified from https://gist.github.com/timurbakibayev/1f683d34487362b0f36280989c80960c

import gym
import random
import numpy as np
from gym import Env

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Figure:
    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = np.random.randint(len(self.figures))
        self.orientations = len(self.figures[self.type])
        self.rotation = 0
        self.image = self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation += 1
        self.rotation %= self.orientations
        self.image = self.figures[self.type][self.rotation]
        self.orientations = len(self.figures[self.type])

    def reverse_rotate(self):
        self.rotation -= 1
        self.rotation %= self.orientations
        self.image = self.figures[self.type][self.rotation]
        self.orientations = len(self.figures[self.type])

class Tetris(Env):
    width = 10
    height = 20
    x = 0
    y = 0
    zoom = 20

    def __init__(self):
        self.action_space = gym.spaces.Discrete(3)
        self.observation_space = gym.spaces.Box(low = 0, high = 0, shape = (self.height, self.width, 4))
        self.screen = None

    def intersects(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image:
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0              or \
                            self.board[i + self.figure.y, j + self.figure.x]:
                        return True
        return False

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.board[i, j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for j in range(i, 1, -1):
                    for k in range(self.width):
                        self.board[j, k] = self.board[j - 1, k]
        self.score *= (lines + 1)
        # self.score += lines ** 2
        # regular reward type

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image:
                    self.board[i + self.figure.y, j + self.figure.x] = 1
                    self.score += 1
                    # alternative reward type
        self.break_lines()
        self.next_figure()
        if self.intersects():
            self.terminal = True

    def go_side(self, dx):
        self.figure.x += dx
        if self.intersects():
            self.figure.x -= dx

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.reverse_rotate()

    def next_figure(self):
        self.figure = Figure(3, 0)

    def observe(self):
        """
        position_plane = np.zeros((self.height, self.width))
        position_plane[self.figure.y, self.figure.x] = 1
        shape_plane = np.full((self.height, self.width), (self.figure.type + 1) / 7)
        rotation_plane = np.full((self.height, self.width), (self.figure.rotation + 1) / self.figure.orientations)
        observation = np.stack((self.board, position_plane, shape_plane, rotation_plane), axis = -1)
        """
        y = np.zeros((self.height,))
        y[self.figure.y] = 1
        x = np.zeros((self.width,))
        x[self.figure.x] = 0
        t = np.zeros((7,))
        t[self.figure.type] = 1
        rot = np.zeros((4,))
        rot[self.figure.rotation] = 1

        observation = np.concatenate((self.board.flatten(), y, x, t, rot))
        return observation

    def reset(self):
        self.board = np.zeros((self.height, self.width), dtype = int)
        self.score = 0
        self.next_figure()
        self.terminal = False
        return self.observe()

    def step(self, action):
        last_score = self.score
        self.go_down()

        if action == 0:
            self.rotate()
        elif action == 1:
            self.go_side(-1)
        else:
            self.go_side(1)

        reward = self.score - last_score
        return self.observe(), reward, self.terminal, {}

    def render(self):
        try:
            pygame
        except:
            import pygame

        if not pygame.get_init():
            pygame.init()
            pygame.display.set_caption("Tetris")

        if self.screen is None:
            size = (200, 400)
            self.screen = pygame.display.set_mode(size)

        self.screen.fill(WHITE)

        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(self.screen, GRAY, [self.x + self.zoom * j, self.y + self.zoom * i, self.zoom, self.zoom], 1)
                if self.board[i, j] > 0:
                    pygame.draw.rect(self.screen, RED if self.board[i, j] else BLACK,
                                    [self.x + self.zoom * j + 1, self.y + self.zoom * i + 1, self.zoom - 2, self.zoom - 1])

        if self.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in self.figure.image:
                        pygame.draw.rect(self.screen, BLUE,
                                        [self.x + self.zoom * (j + self.figure.x) + 1,
                                        self.y + self.zoom * (i + self.figure.y) + 1,
                                        self.zoom - 2, self.zoom - 2])

        font = pygame.font.SysFont('Calibri', 25, True, False)
        font1 = pygame.font.SysFont('Calibri', 65, True, False)
        text = font.render(str(self.score), True, BLUE)
        text_game_over = font1.render("Game Over", True, (255, 125, 0))
        text_game_over1 = font1.render("Press ESC", True, (255, 215, 0))

        self.screen.blit(text, [10, 10])
        if self.terminal:
            self.screen.blit(text_game_over, [20, 200])
            self.screen.blit(text_game_over1, [25, 265])

        pygame.display.flip()

    def close(self):
        if not self.screen is None:
            pygame.display.quit()

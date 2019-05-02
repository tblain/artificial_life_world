from tkinter import Tk, Canvas
import numpy as np
import random
import time

from map import Map
from bot import Bot


class Simulation:
    def __init__(self, nb_bots):
        self.master = Tk()
        self.w = Canvas(self.master, width=1500, height=900)
        self.w.pack()
        self.map = Map(20, 20, 2)
        self.map.spawn_tree(50, 10)
        self.load_bots(nb_bots, reset=False)
        self.nb_step = 0

    def load_bots(self, nb_bots, reset=True):
        pos = np.random.randint(self.map.height, size=(nb_bots, 2))

        if reset:
            pass
        else:
            self.bots = []
            for i in range(nb_bots):
                x = pos[i, 0]
                y = pos[i, 1]
                while self.map.board[x, y, 0] != 0:
                    x = random.randint(0, self.map.height-1)
                    y = random.randint(0, self.map.height-1)

                bot = Bot(self.map, x, y)
                self.map.board[x, y, 0] = 1
                self.bots.append(bot)

    def step(self):
        self.nb_step += 1
        # print(len(self.bots))
        if len(self.bots) > 0:
            for i in range(len(self.bots) -1, -1, -1):
                bot = self.bots[i]
                if bot.energy > 0:
                    bot.step()
                else:
                    # print("dead: ", bot.x, " / ", bot.y)
                    self.map.board[bot.x, bot.y] = [0, 0]
                    # self.map.display()
                    # print(self.map.board[bot.x, bot.y])
                    # print(self.map.board)
                    self.bots.remove(bot)
        else:
            print("==========")
            print("No bots left")
            print("Respawning bots and trees")
            self.load_bots(10, False)
            self.map.spawn_tree(10, 10)

    def play(self):
        print("La Simulation commence")
        self.map.display()
        while True:
            print("Step: ", self.nb_step)
            self.step()
            self.map.display()
            time.sleep(0.5)
            self.nb_step += 1

    def reset(self):
        pass

import numpy as np
import random
import time

from map import Map
from bot import Bot
from al_bot import Al_bot


class Simulation:
    def __init__(self, nb_bots):
        self.map = Map(350, 350, 12)
        self.map.spawn_outer_walls()
        self.map.spawn_tree(80000, 30)

        self.bots = []
        self.train_bots = []

        self.load_bots(10, reset=False, train=True)
        self.load_bots(nb_bots, reset=False)

        self.total_nb_step = 0
        self.total_max_bot_steps = 0

        self.current_nb_step = 0
        self.current_max_bot_steps = 0

        self.nb_generation = 0
        self.next_bots = []

        # self.bots.append(Al_bot(self.map, 3, 3, self))
        # self.map.board[3, 3, 0] = 1

    def load_bots(self, nb_bots, reset=True, train=False):
        pos = np.random.randint(self.map.height, size=(nb_bots, 2))

        if reset:
            pass
        else:
            for i in range(nb_bots):
                x = pos[i, 0]
                y = pos[i, 1]
                while self.map.board[x, y, 0] != 0:
                    x = random.randint(0, self.map.height - 1)
                    y = random.randint(0, self.map.height - 1)

                bot = Bot(self.map, x, y, self, train=train)
                if train:
                    self.train_bots.append(bot)
                self.map.board[x, y, 0] = 1
                self.bots.append(bot)

    def add_bots(self, bots=[]):
        if len(bots) > 0:
            for bot in bots:
                self.next_bots.append(bot)
        else:
            x = random.randint(0, self.map.height - 1)
            y = random.randint(0, self.map.height - 1)
            while self.map.board[x, y, 0] != 0:
                x = random.randint(0, self.map.height - 1)
                y = random.randint(0, self.map.height - 1)

            bot = Bot(self.map, x, y, self)
            self.map.board[x, y, 0] = 1
            self.next_bots.append(bot)

    def step(self):
        print("len ", len(self.bots))
        if len(self.bots) > 0:
            for i in range(len(self.bots) - 1, -1, -1):
                bot = self.bots[i]
                if i < 5:
                    print(
                        bot.type, ": ", bot.nb_steps, " / ", bot.g_energy(), end=" | "
                    )
                if bot.g_energy() > 0:
                    bot.step()
                else:
                    self.map.board[bot.x, bot.y, 0] = 0
                    self.map.board[bot.x, bot.y, 1] = 0
                    self.map.board[bot.x, bot.y, 2] = 0
                    self.current_max_bot_steps = max(
                        self.current_max_bot_steps, bot.nb_steps
                    )
                    self.bots.remove(bot)
                    bot.nb_steps = 0

            # if len(self.bots) < 1000:
            #    for i in range(1000 - len(self.bots)):
            #        self.add_bots()

            for bot in self.next_bots:
                self.bots.append(bot)
                self.map.board[bot.x, bot.y, 0] = 1

            self.next_bots = []

        else:
            # TODO: sauvegarder les meilleurs bots pour les mettre dans la gen d'apres et aussi les sauvegarder sur le disque
            # TODO: centrer la camera sur le premier de la liste
            print()
            print()
            print("=|=|=|=|=|=|=|=|=|=")
            print()
            print("No bots left")
            print("Respawning bots and trees")
            print("Generation duration: ", self.current_nb_step)
            print("Generation best bot duration: ", self.current_max_bot_steps)
            print()
            print()

            self.total_max_bot_steps = max(
                self.total_max_bot_steps, self.current_max_bot_steps
            )
            self.total_nb_step = max(self.total_nb_step, self.current_nb_step)

            self.bots = []

            for bot in self.train_bots:
                self.bots.append(bot)
                x = random.randint(0, self.map.height - 1)
                y = random.randint(0, self.map.height - 1)
                while self.map.board[x, y, 0] != 0:
                    x = random.randint(0, self.map.height - 1)
                    y = random.randint(0, self.map.height - 1)
                bot.x = x
                bot.y = y
                self.map.board[x, y, 0] = 1
                bot.incr_energy(10)

            self.load_bots(10000, False)
            self.map.spawn_tree(1000, 30)
            self.reset()

    def play(self):
        print("La Simulation commence")

        for i in range(1000000000000000):
            print("=================")
            print("Total max nb steps: ", self.total_nb_step)
            print("Total elder: ", self.total_max_bot_steps)
            print("------")
            print("Generation ", self.nb_generation)
            print("Current max nb step: ", self.current_nb_step)
            print("Current elder: ", self.current_max_bot_steps)
            print("Nb bots: ", len(self.bots))
            print("------")
            if len(self.bots) > 0:
                print("Elder: x=", self.bots[0].x, " / y=", self.bots[0].y)
                x1 = max(self.bots[0].x - 20, 0)
                y1 = max(self.bots[0].y - 20, 0)
            else:
                x1 = 0
                y1 = 0

            self.step()
            self.map.display(style=2, nb_cell_to_display=40, x1=x1, y1=y1)
            print()
            print()
            # time.sleep(0.5)
            if self.current_nb_step % 2 == 0:
                self.map.spawn_tree(60, 30)
            self.current_nb_step += 1

    def reset(self):
        self.current_nb_step = 0
        self.current_max_bot_steps = 0
        self.nb_generation += 1

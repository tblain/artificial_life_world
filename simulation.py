import numpy as np
import random
import time

from map import Map
from bot import Bot
from al_bot import Al_bot
from genetic import croisement, mutate

from tqdm import tqdm


class Simulation:
    def __init__(self, nb_bots):
        self.map = Map(450, 450, 12, self)
        self.map.spawn_outer_walls()
        self.map.spawn_tree(400000, 30)

        self.display = False

        self.bots = []
        self.train_bots = []

        self.load_bots(10, reset=False, train=True)
        self.load_bots(nb_bots, reset=False)

        self.total_nb_step = 0
        self.total_max_bot_steps = 0
        self.total_nb_death = 0

        self.current_nb_step = 0
        self.current_max_bot_steps = 0
        self.current_nb_death = 0

        self.nb_generation = 0
        self.next_bots = []

        # self.bots.append(Al_bot(self.map, 3, 3, self))
        # self.map.board[3, 3, 0] = 1

    def load_bots(self, nb_bots, reset=False, train=False):
        pos = np.random.randint(self.map.height, size=(nb_bots, 2))

        if reset:
            pass
        else:
            for i in tqdm(range(nb_bots)):
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
            x, y = self.g_free_xy()
            bot = Bot(self.map, x, y, self)
            self.map.board[x, y, 0] = 1
            self.next_bots.append(bot)

    def step(self):
        if len(self.bots) > 0:
            if self.current_nb_step % 10 == 1:
                self.spawn_child()

            for i in range(len(self.bots) - 1, -1, -1):
                bot = self.bots[i]
                if i < 5:
                    print(
                        bot.type, ": ", bot.nb_steps, " / ", bot.g_energy(), end=" | "
                    )
                if bot.alive:
                    bot.step()
                else:
                    bot.dispose_meat_floor()
                    self.current_nb_death += 1
                    self.total_nb_death += 1
                    bot.clear_bot_infos()
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

            if self.current_nb_step % 2 == 0:
                self.map.spawn_tree(130, 30)
            elif self.current_nb_step % 100 == 0:
                self.load_bots(1, reset=False, train=True)

        else:
            # TODO: sauvegarder les meilleurs bots pour les mettre dans la gen d'apres et aussi les sauvegarder sur le disque
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
                bot.x, bot.y = self.g_free_xy()
                self.map.board[bot.x, bot.y, 0] = 1
                bot.incr_energy(10)

            self.load_bots(40000, False)
            self.map.spawn_tree(3000, 30)
            self.reset()

    def spawn_child(self, nb=1, train=False):
        for i in range(nb):
            nb1 = random.randint(0, len(self.bots) - 1)
            nb2 = random.randint(0, len(self.bots) - 1)

            parent1 = self.bots[nb1]  # parent 1
            parent2 = self.bots[nb2]  # parent 2

            # create a child by breeding to random bots
            child_weights = croisement(parent1.model.weights, parent2.model.weights, 1)[
                0
            ]

            mutate(child_weights, 1, 1)

            if self.current_nb_step % 2 == 0:
                x, y = self.g_free_xy(parent1.x, parent1.y, 4)
            else:
                x, y = self.g_free_xy(parent2.x, parent2.y, 4)

            child = Bot(self.map, x, y, self, train=train)
            child.model.weights = child_weights
            self.map.board[x, y, 0] = 1

            self.bots.append(child)

    def g_free_xy(self, x=-1, y=-1, dist=-1):
        """
        return: a random valid position in the board
        if the arguments are given:
        return get a random pos in a certain area around sx and sy
        """
        if x == -1:
            x = random.randint(0, self.map.height - 1)
            y = random.randint(0, self.map.height - 1)

            while self.map.board[x, y, 0] != 0:
                x = random.randint(0, self.map.height - 1)
                y = random.randint(0, self.map.height - 1)

            return x, y

        else:  # get a random pos in a certain area around sx and sy
            i = random.randint(0, dist)
            j = random.randint(0, dist)

            while (
                not self.pos_valid(x + i, y + j) or self.map.board[x + i, y + j, 0] != 0
            ):
                i = random.randint(-dist, dist)
                j = random.randint(-dist, dist)

            return x + i, y + j

    def pos_valid(self, x, y):
        return 0 <= x < self.map.width and 0 <= y < self.map.height

    def play(self):
        print("La Simulation commence")

        for i in range(10000000000000000):
            print("=================")
            print("Total max nb steps: ", self.total_nb_step)
            print("Total elder: ", self.total_max_bot_steps)
            print("Total death: ", self.total_nb_death)
            print("------")
            print("Generation ", self.nb_generation)
            print("Current nb step: ", self.current_nb_step)
            print("Current elder: ", self.current_max_bot_steps)
            print("Current death: ", self.current_nb_death)
            print("Nb bots: ", len(self.bots))
            print("------")
            if len(self.bots) > 0:
                print("Elder: x=", self.bots[0].x, " / y=", self.bots[0].y)
                x1 = max(self.bots[0].x - 20, 0)
                y1 = max(self.bots[0].y - 20, 0)
            else:
                x1 = 0
                y1 = 0

            if self.display:
                self.map.display(style=2, nb_cell_to_display=40, x1=x1, y1=y1)

            self.step()
            self.map.w.update()
            print()
            print()
            # time.sleep(0.5)
            self.current_nb_step += 1

    def reset(self):
        self.current_nb_step = 0
        self.current_max_bot_steps = 0
        self.nb_generation += 1
        self.current_nb_death = 0

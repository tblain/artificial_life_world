import numpy as np
import random
import time

from map import Map
from nn_bot import NN_bot
from herbivore import Herbivore
from genetic import croisement, mutate

from tqdm import tqdm

class Simulation:
    def __init__(self, nb_bots, nb_herbi):
        # cree la map qui va faire 100 blocs de large et de long, et avec 12 infos par cases
        self.map = Map(300, 300, 12, self)

        # cree les murs
        #self.map.spawn_outer_walls()

        # charge x vegetaux avec au max 30 fruits chacun
        self.map.load_trees(18000, 5)

        # la simuation commence sans l'affichage, il peut etre activer par la suite
        self.display = True

        # list des bots
        self.bots = []
        # list des bots de type train (qui vont se faire entrainer)
        self.train_bots = []

        self.nn_bots = []

        # self.load_bots(10, train=True)
        self.load_bots(nb_bots)

        self.load_herbivores(nb_herbi)

        self.total_nb_step = 0
        self.total_max_bot_steps = 0
        self.total_nb_death = 0

        # duree totale de la generation actuelle
        self.current_nb_step = 0
        # duree max de survie qu'a atteint un bot
        self.current_max_bot_steps = 0
        self.current_nb_death = 0

        self.nb_generation = 0

        # list des bots qui vont etre charger a l'etape suivante
        self.next_bots = []

        # self.bots.append(Al_bot(self.map, 3, 3, self))
        # self.map.board[3, 3, 0] = 1

        self.sim_speed = 2

    def load_herbivores(self, nb_herbi):
        for i in tqdm(range(nb_herbi)):
            x, y = self.g_free_xy()

            bot = Herbivore(self.map, x, y, self)
            self.map.board[x, y, 0] = 2
            self.bots.append(bot)

    def load_bots(self, nb_bots, train=False):
        for i in range(nb_bots):
            x, y = self.g_free_xy()

            bot = NN_bot(self.map, x, y, self, train=train)
            if train:
                self.train_bots.append(bot)
            self.map.board[x, y, 0] = 1
            self.bots.append(bot)
            self.nn_bots.append(bot)

    def add_bots(self, bots=[]):
        if len(bots) > 0:
            for bot in bots:
                self.next_bots.append(bot)
        else:
            x, y = self.g_free_xy()
            bot = Bot(self.map, x, y, self)
            if self.map.board[x, y, 0] == 0:
                self.map.board[x, y, 0] = 1
            self.next_bots.append(bot)

    def step(self):
        if True or len(self.bots) > 0:
            cd_repro_board = self.map.board[:, :, 5]
            cd_repro_board[cd_repro_board > 0] -= 1

            if self.current_nb_step % 10 == 1 and len(self.bots) < 100:
                self.spawn_child()
                pass

            for i in range(len(self.bots) - 1, -1, -1):
                bot = self.bots[i]
                if i < 5:
                    # affiche des infos sur les 5 bots en vie les plus vieux
                    print(
                        bot.type, ": ", bot.nb_steps, " / ", bot.g_energy(), end=" | "
                    )
                if bot.alive:
                    bot.step()
                else:
                    bot.dispose_meat_floor()
                    # incremente le nb de bot mort pendant la generation
                    self.current_nb_death += 1
                    # incremente le nb de bot mort toute generation confondue
                    self.total_nb_death += 1

                    # regarde si le bot mort est le plus long survivant
                    self.current_max_bot_steps = max(
                        self.current_max_bot_steps, bot.nb_steps
                    )

                    if bot.type == "B" or bot.type == "T":
                        self.nn_bots.remove(bot)

                    self.bots.remove(bot)
                    bot.nb_steps = 0

                    # supprime le bot et ses infos
                    bot.clear_bot_infos()

            #self.map.supp_trees_deracine()

            # if len(self.bots) < 1000:
            #    for i in range(1000 - len(self.bots)):
            #        self.add_bots()

            if self.current_nb_step % 2 == 0:
                self.map.load_trees(10, 1)
                pass
            if self.current_nb_step % 10 == 0 and len(self.bots) < 5000:
                self.load_bots(1, train=False)
                pass
            if self.current_nb_step % 5 == 0:
                self.map.tree_growth()

            self.map.spawn_trees()

            for bot in self.next_bots:
                self.bots.append(bot)
                if bot.type == "B" or bot.type == "T":
                    self.nn_bots.append(bot)
                    self.map.board[bot.x, bot.y, 0] = 1
                elif bot.type == "H":
                    self.map.board[bot.x, bot.y, 0] = 2

            self.next_bots = []

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
            self.nn_bots = []

            for bot in self.train_bots:
                self.bots.append(bot)
                bot.x, bot.y = self.g_free_xy()
                self.map.board[bot.x, bot.y, 0] = 1
                bot.incr_energy(10)

            self.load_bots(400, False)
            self.map.spawn_tree(3000, 30)
            self.reset()

    def spawn_child(self, nb=1, train=False):
        if len(self.nn_bots) > 0:
            for i in range(nb):
                nb1 = random.randint(0, len(self.nn_bots) - 1)
                nb2 = random.randint(0, len(self.nn_bots) - 1)

                parent1 = self.nn_bots[nb1]  # parent 1
                parent2 = self.nn_bots[nb2]  # parent 2

                # create a child by breeding to random bots
                child_weights = croisement(
                    parent1.model.weights, parent2.model.weights, 1
                )[0]

                mutate(child_weights, 1, 1)

                if self.current_nb_step % 2 == 0:
                    x, y = self.g_free_xy(parent1.x, parent1.y, 4)
                else:
                    x, y = self.g_free_xy(parent2.x, parent2.y, 4)

                child = NN_bot(self.map, x, y, self, train=train)
                child.model.weights = child_weights
                self.map.board[x, y, 0] = 1
                self.bots.append(child)
                self.nn_bots.append(child)

        else:
            self.load_bots(nb, train)

    def g_free_xy(self, x=-1, y=-1, dist=-1):
        """
        return: a random valid position in the board
        if the arguments are given:
        return get a random pos in a certain area around sx and sy
        """
        if x == -1:
            x = random.randint(1, self.map.height - 2)
            y = random.randint(1, self.map.height - 2)

            while self.map.board[x, y, 0] != 0:
                x = random.randint(1, self.map.height - 2)


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

        for i in range(1000000000000000000000000):
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
            if len(self.nn_bots) > 0:
                print("Elder: x=", self.nn_bots[0].x, " / y=", self.nn_bots[0].y)
                x1 = max(self.nn_bots[0].x - 20, 0)
                y1 = max(self.nn_bots[0].y - 20, 0)
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
            time.sleep(1/self.sim_speed)

    def reset(self):
        self.current_nb_step = 0
        self.current_max_bot_steps = 0
        self.nb_generation += 1
        self.current_nb_death = 0

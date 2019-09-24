from bot import Bot
import numpy as np


class Herbivore(Bot):
    def __init__(self, map, x, y, sim):
        Bot.__init__(self, map, x, y, sim)

        # attribue le type au bot
        self.type = "H"  # => bot herbivore

        self.train = False
        self.cellNum = 0

    def predict(self):

        actions = [0, 0, 0, 0, 0, 0, 0, 0]

        if self.g_energy() > 300 and self.can_reproduce(taille_limite=True):
            actions[6] = 1000
            pass

        if self.g_nb_fruit_on_pos() >= 1:
            actions[7] = 10000000000000000000

        actions[1] = self.g_nb_fruit_on_dir([0, -1], 4) - (
            self.g_bot_on_dir([0, -1]) * 1000
        )
        actions[2] = self.g_nb_fruit_on_dir([0, 1], 4) - (
            self.g_bot_on_dir([0, 1]) * 1000
        )
        actions[3] = self.g_nb_fruit_on_dir([-1, 0], 4) - (
            self.g_bot_on_dir([-1, 0]) * 1000
        )
        actions[4] = self.g_nb_fruit_on_dir([1, 0], 4) - (
            self.g_bot_on_dir([1, 0]) * 1000
        )
        # print(actions)
        return np.argmax(actions)

    def can_reproduce(self, taille_limite=False):
        return self.g_cd_repro() == 0 and (
            not taille_limite or len(self.sim.bots) < 750
        )

    def mitose(self):
        if self.g_cd_repro() == 0:

            self.incr_cd_repro(50)  # the bot can't reproduce for 50 tick
            self.incr_energy(-5)  # loose of energy to make the child
            energy_to_child = 5  # energy that will be transfered to the child

            x = -1
            y = -1

            # TODO: faire une fonction pour rendre ca plus propre

            if self.y - 2 > 0:
                if self.map.board[self.x, self.y - 1, 0] == 0:
                    x = self.x
                    y = self.y - 1

            if self.y + 2 < self.map.height - 1:
                if self.map.board[self.x, self.y + 1, 0] == 0:
                    x = self.x
                    y = self.y + 1

            if self.x - 2 > 0:
                if self.map.board[self.x - 1, self.y, 0] == 0:
                    x = self.x - 1
                    y = self.y

            if self.x + 2 < self.map.height - 1:
                if self.map.board[self.x + 1, self.y, 0] == 0:
                    x = self.x + 1
                    y = self.y

            if x == -1:
                # no place to put the child
                self.incr_energy(energy_to_child)
                self.incr_energy(-1)
            else:
                new_bot = Herbivore(self.map, x, y, self.sim)
                new_bot.s_energy(energy_to_child)
                self.sim.add_bots([new_bot])

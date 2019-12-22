from bot import Bot
import numpy as np


class Herbivore(Bot):
    def __init__(self, map, x, y, sim):
        Bot.__init__(self, map, x, y, sim)

        # attribue le type au bot
        self.type = "H"  # => bot herbivore

        self.train = False
        self.cellNum = 1

        # ---------------------------------
        # e => energy when absorbing ...
        self.e_fruit = 6  # energy donne en absorbant un fruit
        self.e_meat = 1  # energy donne en absorbant de la viande

        # ---------------------------------
        # c => cost in energy when ...
        self.c_move = 1  # cout de bouger
        self.c_rien = 1  # cout de rien faire

        # ---------------------------------
        # t => treshold (palier) for ...

        # palier avant lancer une reproduction
        self.t_repro = 300

        self.t_need_to_eat_0 = 0
        self.t_need_to_eat_1_nb_energy = 30

        # besoin de manger mineur / c'est + pour accumuler de l'energie
        self.t_need_to_eat_1 = 300
        # quand le bot a un need_to_eat de 1 quelle quantite d'energie sur pose est ce que le bot mange
        # (le but est d'eviter de trop defoncer les arbres)
        self.t_need_to_eat_1_nb_energy = 10

        # vraiment besoin de manger
        self.t_need_to_eat_2 = 20

        # nombre de fruits dans la zone acceptable
        # Le bot a beaucoup d'energie et cherche une zone avec beaucoup d'energie
        # pour y rester et avoir des arbres qui produisent en grandes quantite
        # A partir de cette quantite il est satisfait de sa zone et donc peux manger
        self.t_fruits_in_zone = 100

    def predict(self):
        if self.g_energy() > self.t_repro and self.can_reproduce(taille_limite=True):
            # actions[6] = 1000
            return 6

        need_to_eat = self.g_need_to_eat()
        if need_to_eat > 0:
            if need_to_eat >= 2 and self.g_nb_fruit_on_pos() > 0:
                return 7
            if need_to_eat >= 1 and self.g_nb_fruit_on_pos() > self.t_need_to_eat_1_nb_energy:
                return 7
            else:
                if self.g_fruits_in_zone(6) > self.t_fruits_in_zone and self.g_nb_fruit_on_pos() > self.t_need_to_eat_0:
                    return 7
                else:
                    return self.predict_move()
        else:
            return self.predict_move()

    def g_fruits_in_zone(self, dist):
        fruits = self.g_nb_fruit_on_pos()

        for i in range(1, dist):
            fruits += self.g_info_sum_on_dir(21, i, [0, 1])
            fruits += self.g_info_sum_on_dir(21, i, [0, -1])
            fruits += self.g_info_sum_on_dir(21, i, [1, 0])
            fruits += self.g_info_sum_on_dir(21, i, [-1, 0])

        return fruits

    def predict_move(self):
        actions = [0, 0, 0, 0, 0, 0, 0, 0]

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

        return np.argmax(actions)

    def g_need_to_eat(self):
        if self.g_energy() < self.t_need_to_eat_2:
            return 2
        elif self.g_energy() <= self.t_need_to_eat_1:
            return 1
        else:
            return 0

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

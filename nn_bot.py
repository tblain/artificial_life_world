from neural_network import NN
import numpy as np
import genetic
import random
from bot import Bot


class NN_bot(Bot):
    def __init__(self, map, x, y, sim, model=None, train=False):
        Bot.__init__(self, map, x, y, sim)

        if model:
            self.model = model
        else:
            self.model = NN(197, [50, 50, 8])

        # attribue le type au bot
        self.type = "B"  # => bot normal

        self.train = train

        if train:  # si le bot est en mode training
            # lui donne de l'energie en plus pour avoir un peux plus de temps pour train
            self.incr_energy(100)
            # lui donne le type training
            self.type = "T"

    def g_inputs(self):
        # TODO mettre en log les energis
        inputs = np.array([])
        inputs = np.append(inputs, np.cbrt(self.g_energy()))
        inputs = np.append(inputs, np.cbrt(self.g_nb_fruit_on_pos()))

        # des inputs qui servent juste a donner des variables qui bouclent pour
        # permettre au bot un peu de changement dans son comportement et lui
        # permettre d'avoir des actions un peu cyclique
        inputs = np.append(inputs, np.cbrt(self.sim.current_nb_step % 2))
        inputs = np.append(inputs, np.cbrt(self.sim.current_nb_step % 10))
        inputs = np.append(inputs, np.cbrt(self.sim.current_nb_step % 50))

        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, 1], 3)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, -1], 3)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([1, 0], 3)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([-1, 0], 3)))

        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, 1], 2)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, -1], 2)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([1, 0], 2)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([-1, 0], 2)))

        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, 1], 1)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, -1], 1)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([1, 0], 1)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([-1, 0], 1)))

        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, 1], 0)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([0, -1], 0)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([1, 0], 0)))
        inputs = np.append(inputs, np.cbrt(self.g_infos_on_dir([-1, 0], 0)))

        # inputs = np.append(inputs, self.g_nb_fruit_on_dir([0, 1], 3))
        # inputs = np.append(inputs, self.g_nb_fruit_on_dir([0, -1], 3))
        # inputs = np.append(inputs, self.g_nb_fruit_on_dir([1, 0], 3))
        # inputs = np.append(inputs, self.g_nb_fruit_on_dir([-1, 0], 3))

        # inputs = np.append(inputs, self.g_bot_on_dir([1, 0]))
        # inputs = np.append(inputs, self.g_bot_on_dir([-1, 0]))
        # inputs = np.append(inputs, self.g_bot_on_dir([0, 1]))
        # inputs = np.append(inputs, self.g_bot_on_dir([0, -1]))

        # inputs = np.append(inputs, self.g_bot_on_dir([1, 0], 3))
        # inputs = np.append(inputs, self.g_bot_on_dir([-1, 0], 3))
        # inputs = np.append(inputs, self.g_bot_on_dir([0, 1]), 3)
        # inputs = np.append(inputs, self.g_bot_on_dir([0, -1], 3))

        return inputs

    def predict(self):
        inputs = self.g_inputs()
        prediction = self.model.predict(inputs)

        action = np.argmax(prediction)

        if self.train:
            albot_actions = self.albot_predict()
            self.model.fit_on_one(self.g_inputs(), albot_actions, 0.001)
            action = albot_actions

        return action

    def albot_predict(self):
        actions = [0, 0, 0, 0, 0, 0, 0, 0]

        if self.g_energy() > 300:
            pass
            # actions[6] = 1000
        if self.g_nb_fruit_on_pos() > 0:
            actions[7] = 10000

        actions[1] = self.g_nb_fruit_on_dir([0, -1], 3) - (
            self.g_bot_on_dir([0, -1]) * 0000
        )
        actions[2] = self.g_nb_fruit_on_dir([0, 1], 3) - (
            self.g_bot_on_dir([0, 1]) * 0000
        )
        actions[3] = self.g_nb_fruit_on_dir([-1, 0], 3) - (
            self.g_bot_on_dir([-1, 0]) * 0000
        )
        actions[4] = self.g_nb_fruit_on_dir([1, 0], 3) - (
            self.g_bot_on_dir([1, 0]) * 0000
        )

        return actions

    def mitose(self):
        if self.g_cd_repro() == 0:

            self.incr_cd_repro(20)
            self.incr_energy(-5)  # loose of energy to make the child
            # energy that will be transfered to the child
            energy_to_child = 5

            x = -1
            y = -1

            # TODO: faire une fonction pour rendre ca plus propre
            if self.y - 2 > 0:
                if self.map.board[self.x, self.y - 1, 0] == 0:
                    x = self.x
                    y = self.y - 1

            elif self.y + 2 < self.map.height - 1:
                if self.map.board[self.x, self.y + 1, 0] == 0:
                    x = self.x
                    y = self.y + 1

            elif self.x - 2 > 0:
                if self.map.board[self.x - 1, self.y, 0] == 0:
                    x = self.x - 1
                    y = self.y

            elif self.x + 2 < self.map.height - 1:
                if self.map.board[self.x + 1, self.y, 0] == 0:
                    x = self.x + 1
                    y = self.y
            else:
                # no place to put the child
                self.incr_energy(energy_to_child)
                self.incr_energy(-1)

            if x == -1:
                pass
            else:
                new_model = genetic.mutate(self.model.weights, 1, 1)
                new_bot = NN_bot(self.map, self.x + 1, self.y, self.sim, new_model)
                new_bot.s_energy(energy_to_child)
                self.sim.add_bots([new_bot])

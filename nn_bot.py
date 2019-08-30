from neural_network import NN
import numpy as np
import genetic
import random
from bot.py import Bot


class NN_bot:
    def __init__(self, map, x, y, sim, model=None, train=False):
        Bot.__init__(self, map, x, y, sim)

        if model:
            self.model = model
        else:
            self.model = NN(198, [200, 150, 100, 50, 8])

        # attribue le type au bot
        self.type = "B"  # => bot normal

        self.train = train

        if train:  # si le bot est en mode training
            # lui donne de l'energie en plus pour avoir un peux plus de temps pour train
            self.incr_energy(100)
            # lui donne le type training
            self.type = "T"

    def g_inputs(self):
        inputs = np.array([])
        inputs = np.append(inputs, self.g_energy())
        inputs = np.append(inputs, self.g_nb_fruit_on_pos())

        # des inputs qui servent juste a donner des variables qui bouclent pour
        # permettre au bot un peu de changement dans son comportement et lui
        # permettre d'avoir des actions un peu cyclique
        inputs = np.append(inputs, self.sim.current_nb_step % 2)
        inputs = np.append(inputs, self.sim.current_nb_step % 10)
        inputs = np.append(inputs, self.sim.current_nb_step % 50)

        inputs = np.append(inputs, self.g_infos_on_dir([0, 1], 3))
        inputs = np.append(inputs, self.g_infos_on_dir([0, -1], 3))
        inputs = np.append(inputs, self.g_infos_on_dir([1, 0], 3))
        inputs = np.append(inputs, self.g_infos_on_dir([-1, 0], 3))

        inputs = np.append(inputs, self.g_infos_on_dir([0, 1], 2))
        inputs = np.append(inputs, self.g_infos_on_dir([0, -1], 2))
        inputs = np.append(inputs, self.g_infos_on_dir([1, 0], 2))
        inputs = np.append(inputs, self.g_infos_on_dir([-1, 0], 2))

        inputs = np.append(inputs, self.g_infos_on_dir([0, 1], 1))
        inputs = np.append(inputs, self.g_infos_on_dir([0, -1], 1))
        inputs = np.append(inputs, self.g_infos_on_dir([1, 0], 1))
        inputs = np.append(inputs, self.g_infos_on_dir([-1, 0], 1))

        inputs = np.append(inputs, self.g_infos_on_dir([0, 1], 0))
        inputs = np.append(inputs, self.g_infos_on_dir([0, -1], 0))
        inputs = np.append(inputs, self.g_infos_on_dir([1, 0], 0))
        inputs = np.append(inputs, self.g_infos_on_dir([-1, 0], 0))

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

        inputs = np.append(inputs, max(self.g_energy() - 15, 0))

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

    def reset(self):
        pass

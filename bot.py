from neural_network import NN
import numpy as np
import genetic
import random


class Bot:
    def __init__(self, map, x, y, sim, model=None, train=False):
        if model:
            self.model = model
        else:
            self.model = NN(198, [200, 150, 100, 50, 8])

        self.map = map
        self.x = x
        self.y = y

        # donne de l'energie au bot
        self.incr_energy(30)

        # donne de la vie au bot
        self.s_health(3)

        # commence le decompte du nb de step du bot
        self.nb_steps = 0

        # donne la simulation au bot
        self.sim = sim

        # attribue le type au bot
        self.type = "B"  # => bot normal

        self.alive = True

        self.train = train

        if train:  # si le bot est en mode training
            # lui donne de l'energie en plus pour avoir un peux plus de temps pour train
            self.incr_energy(100)
            # lui donne le type training
            self.type = "T"

    def step(self):
        if self.g_energy() <= 0:
            self.alive = False
            return False
        else:

            predict = self.predict()
            action = np.argmax(predict)

            if self.train:
                albot_actions = self.albot_predict()
                self.model.fit_on_one(self.g_inputs(), albot_actions, 0.001)

            if action == 0:  # the bot doesn't move
                self.incr_energy(-1)  # but still lose energy

            # TODO: faire une fonction move pour |eviter de se repete
            elif action == 1:  # going up
                if self.y - 1 > 0:
                    if self.map.board[self.x, self.y - 1, 0] == 0:
                        self.move([0, -1])
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 2:  # going down
                if self.y + 1 < self.map.height - 1:
                    if self.map.board[self.x, self.y + 1, 0] == 0:
                        self.move([0, 1])
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 3:  # going left
                if self.x - 1 > 0:
                    if self.map.board[self.x - 1, self.y, 0] == 0:
                        self.move([-1, 0])
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 4:  # going right
                if self.x + 1 < self.map.height - 1:
                    if self.map.board[self.x + 1, self.y, 0] == 0:
                        self.move([1, 0])
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 5:  # TODO
                self.incr_energy(-1)
                # put itself in reproduction mode, will create a child with another nearby bot that is in repromode
                self.s_reproduction(True)
                if self.g_energy() > 5:
                    pass

            elif action == 6:  # duplication / cell mytose
                if self.g_energy() > 15:
                    self.mitose()
                else:
                    self.incr_energy(-1)

            elif action == 7:  # eat on pos
                self.eat()

            else:
                print("pas normal")
            self.nb_steps += 1
            return True

    def g_health(self):
        return self.map.board[self.x, self.y, 4]

    def s_health(self, nb):
        self.map.board[self.x, self.y, 4] = nb

    def incr_health(self, nb):
        self.map.board[self.x, self.y, 4] += nb

    def mitose(self):
        self.incr_energy(-5)  # loose of energy to make the child
        # energy that will be transfered to the child
        energy_to_child = 5
        new_model = genetic.mutate(self.model.weights, 1, 1)

        # TODO: faire une fonction pour rendre ca plus propre
        if self.map.board[self.x + 1, self.y, 0] == 0:
            # TODO: faire une methode pour get un truc dans la map
            new_bot = Bot(self.map, self.x + 1, self.y, self.sim, new_model)
            new_bot.s_energy(energy_to_child)
            self.sim.add_bots([new_bot])
        elif self.map.board[self.x - 1, self.y, 0] == 0:
            new_bot = Bot(self.map, self.x - 1, self.y, self.sim, new_model)
            new_bot.s_energy(energy_to_child)
            self.sim.add_bots([new_bot])
        elif self.map.board[self.x, self.y + 1, 0] == 0:
            new_bot = Bot(self.map, self.x, self.y + 1, self.sim, new_model)
            new_bot.s_energy(energy_to_child)
            self.sim.add_bots([new_bot])
        elif self.map.board[self.x, self.y - 1, 0] == 0:
            new_bot = Bot(self.map, self.x, self.y - 1, self.sim, new_model)
            new_bot.s_energy(energy_to_child)
            self.sim.add_bots([new_bot])
        else:
            # no place to put the child
            self.incr_energy(energy_to_child)
            self.incr_energy(-1)

    def dispose_meat_floor(self):
        """ Put its energy in the form of meat on the floor """
        x = self.x
        y = self.y

        while self.g_energy() > 0:
            meat = random.randint(1, self.g_energy())
            self.incr_energy(-meat)

            if meat % 4 == 0 and self.pos_valid(x + 1, y):
                c_x = x + 1
                c_y = y

            elif meat % 4 == 1 and self.pos_valid(x - 1, y):
                c_x = x - 1
                c_y = y

            elif meat % 4 == 2 and self.pos_valid(x, y + 1):
                c_x = x
                c_y = y + 1

            elif meat % 4 == 3 and self.pos_valid(x, y - 1):
                c_x = x
                c_y = y - 1

            self.map.board[c_x, c_y, 9] = meat

    def eat(self):
        self.incr_energy(-1)  # energy lost by the consume of food
        if self.g_nb_fruit_on_pos() > 0:
            self.incr_energy(4)  # energy given by eating food

            # the tree loose 1 fruit TODO: faire une fonction dans map pour gerer ca
            self.map.board[self.x, self.y, 11] -= 1
            if self.map.board[self.x, self.y, 11] == 0:
                self.map.board[self.x, self.y, 10] = 0

    def clear_bot_infos(self):
        self.map.board[self.x, self.y, :10] = 0

    def move(self, action):
        self.map.board[self.x + action[0], self.y + action[1], :4] = self.map.board[
            self.x, self.y, :4  # change that when the amount of bot infos increase
        ]

        self.clear_bot_infos()

        self.x += action[0]
        self.y += action[1]
        self.incr_energy(-1)  # energy lost by moving

    def g_energy(self):
        """ return bot's energy """
        return self.map.board[self.x, self.y, 1]

    def incr_energy(self, nb):
        """ increase the bot's energy by nb / can be negativ """
        self.map.board[self.x, self.y, 1] += nb

    def s_energy(self, nb):  # TODO comment
        self.map.board[self.x, self.y, 1] - nb

    def s_reproduction(self, repro=True):
        """ set reproduction for the bot to 0 or 1 depending on the repro arg"""
        if repro:
            self.map.board[self.x, self.y, 2] = 1
        else:
            self.map.board[self.x, self.y, 2] = 0

    def g_reproduction(self):
        """ return the reproduction value of the bot """
        return self.map.board[self.x, self.y, 2]

    def g_nb_fruit_on_pos(self, x=-1, y=-1):
        if x == -1:
            return self.map.board[self.x, self.y, 11]
        else:
            if 0 <= x < self.map.width and 0 <= y < self.map.height:
                return self.map.board[x, y, 11]
            else:
                return 0

    def g_nb_fruit_on_dir(self, dir, dist=0):
        # print("Dir: ", dir)
        # print()
        nb_fruits = 0
        c_x = self.x
        c_y = self.y
        for i in reversed(range(dist)):
            c_x += dir[0]
            c_y += dir[1]
            nb_fruits += self.g_nb_fruit_on_pos(c_x, c_y)
            # print("Direct= x: ", c_x, "/ y: ", c_y)

            for k in range(1, i):
                nb_fruits += self.g_nb_fruit_on_pos(c_x + k * dir[1], c_y + k * dir[0])
                nb_fruits += self.g_nb_fruit_on_pos(c_x - k * dir[1], c_y - k * dir[0])
                # print("Cote= x: ", c_x + k * dir[1], "/ y: ", c_y + k * dir[0])
                # print("Cote= x: ", c_x - k * dir[1], "/ y: ", c_y - k * dir[0])

        return nb_fruits

        # x_p_dir = self.x + dir[0]
        # y_p_dir = self.y + dir[1]
        # return (
        #    self.g_nb_fruit_on_pos(x_p_dir + 1, y_p_dir)
        #    + self.g_nb_fruit_on_pos(x_p_dir - 1, y_p_dir)
        #    + self.g_nb_fruit_on_pos(x_p_dir, y_p_dir + 1)
        #    + self.g_nb_fruit_on_pos(x_p_dir, y_p_dir - 1)
        #    + self.g_nb_fruit_on_pos(x_p_dir, y_p_dir)
        #    # substraction of the energy on the bot pos
        #    - self.g_nb_fruit_on_pos()
        # )

    def g_bot_on_dir(self, dir, dist=0):
        nb_bot = 0
        c_x = self.x
        c_y = self.y
        for i in reversed(range(dist)):
            c_x += dir[0]
            c_y += dir[1]
            nb_bot += self.g_nb_bot_on_pos(c_x, c_y)

            for k in range(1, i):
                nb_bot += self.g_nb_bot_on_pos(c_x + k * dir[1], c_y + k * dir[0])
                nb_bot += self.g_nb_bot_on_pos(c_x - k * dir[1], c_y - k * dir[0])

        return nb_bot

    def g_nb_bot_on_pos(self, x=-1, y=-1):
        if x == -1:
            x = self.x
            y = self.y

        if 0 <= x < self.map.width and 0 <= y < self.map.height:
            return self.map.board[x, y, 0]
        else:
            return 0

    def g_nb_kill_on_pos(self, x=-1, y=-1):
        if x == -1:
            x = self.x
            y = self.y

        if self.pos_valid(x, y):
            return self.map.board[x, y, 3]
        else:
            return 0

    def pos_valid(self, x, y):
        return 0 <= x < self.map.width and 0 <= y < self.map.height

    def g_infos_on_pos(self, x=-1, y=-1):
        if x == -1:
            x = self.x
            y = self.y

        if self.pos_valid(x, y):
            return self.map.board[x, y, :12]
        else:
            return 0

    def g_infos_on_dir(self, dir, x=-1, y=-1, dist=0):
        infos = np.zeros((12))
        c_x = self.x
        c_y = self.y
        for i in reversed(range(dist)):
            c_x += dir[0]
            c_y += dir[1]
            infos += self.g_infos_on_pos(c_x, c_y)

            for k in range(1, i):
                infos += self.g_infos_on_pos(c_x + k * dir[1], c_y + k * dir[0])
                infos += self.g_infos_on_pos(c_x - k * dir[1], c_y - k * dir[0])

        return infos

    def g_inputs(self):
        inputs = np.array([])
        inputs = np.append(inputs, self.g_energy())
        inputs = np.append(inputs, self.g_nb_fruit_on_pos())
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
        return self.model.predict(inputs)

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

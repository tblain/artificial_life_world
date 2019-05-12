from neural_network import NN
import numpy as np
import genetic


class Al_bot:
    def __init__(self, map, x, y, sim, model=None):
        self.map = map
        self.x = x
        self.y = y
        self.incr_energy(10)
        self.nb_steps = 0
        self.sim = sim
        self.model = NN(13, [20, 8])
        self.type = "A"

    def step(self):
        if self.g_energy() <= 0:
            return False
        else:
            predict = self.predict()
            action = np.argmax(predict)

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
                    self.incr_energy(-2)  # loose of energy to make the child
                    # energy that will be transfered to the child
                    energy_to_child = self.g_energy() // 2
                    self.incr_energy(-energy_to_child)

                    # TODO: faire une fonction pour rendre ca plus propre
                    if self.map.board[self.x + 1, self.y, 0] == 0:
                        # TODO: faire une methode pour get un truc dans la map
                        new_bot = Al_bot(self.map, self.x + 1, self.y, self.sim)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    elif self.map.board[self.x - 1, self.y, 0] == 0:
                        new_bot = Al_bot(self.map, self.x - 1, self.y, self.sim)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    elif self.map.board[self.x, self.y + 1, 0] == 0:
                        new_bot = Al_bot(self.map, self.x, self.y + 1, self.sim)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    elif self.map.board[self.x, self.y - 1, 0] == 0:
                        new_bot = Al_bot(self.map, self.x, self.y - 1, self.sim)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    else:
                        # no place to put the child
                        self.incr_energy(energy_to_child + 2)
                        self.incr_energy(-1)
                else:
                    self.incr_energy(-1)

            elif action == 7:  # eat on pos
                self.eat()

            else:
                print("pas normal")

            self.nb_steps += 1
            return True

    def eat(self):
        self.incr_energy(-1)  # energy lost by the consume of food
        if self.g_nb_fruit_on_pos() > 0:
            self.incr_energy(4)  # energy given by eating food

            # the tree loose 1 fruit TODO: faire une fonction dans map pour gerer ca
            self.map.board[self.x, self.y, 11] -= 1
            if self.map.board[self.x, self.y, 11] == 0:
                self.map.board[self.x, self.y, 10] = 0

    def move(self, dir):
        self.map.board[self.x + dir[0], self.y + dir[1], :3] = self.map.board[
            self.x, self.y, :3
        ]

        self.map.board[self.x, self.y, 0] = 0
        self.map.board[self.x, self.y, 1] = 0
        self.map.board[self.x, self.y, 2] = 0

        self.x += dir[0]
        self.y += dir[1]
        self.incr_energy(-1)  # energy lost by moving

    def g_energy(self):
        """ return bot's energy """
        return self.map.board[self.x, self.y, 1]

    def incr_energy(self, nb):
        """ increase the bot's energy by nb / can be negativ """
        self.map.board[self.x, self.y, 1] += nb

    def s_energy(self, nb):  # TODO comment
        self.map.board[self.x, self.y, 1] = nb

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

    def g_nb_fruit_on_dir(self, dir):
        x_p_dir = self.x + dir[0]
        y_p_dir = self.y + dir[1]
        return (
            self.g_nb_fruit_on_pos(x_p_dir + 1, y_p_dir)
            + self.g_nb_fruit_on_pos(x_p_dir - 1, y_p_dir)
            + self.g_nb_fruit_on_pos(x_p_dir, y_p_dir + 1)
            + self.g_nb_fruit_on_pos(x_p_dir, y_p_dir - 1)
            + self.g_nb_fruit_on_pos(x_p_dir, y_p_dir)
            # substraction of the energy on the bot pos
            - self.g_nb_fruit_on_pos()
        )

    def g_bot_on_dir(self, dir):
        x_p_dir = self.x + dir[0]
        y_p_dir = self.x + dir[1]
        if 0 <= x_p_dir < self.map.width and 0 <= y_p_dir < self.map.height:
            return self.map.board[x_p_dir, y_p_dir, 0]
        else:
            return 0

    def predict(self):
        actions = [0, 0, 0, 0, 0, 0, 0, 0]

        if self.g_energy() > 300:
            actions[6] = 1
        else:
            if self.g_nb_fruit_on_pos() > 0:
                actions[7] = 1
            else:
                moves_value = np.array(
                    [
                        self.g_nb_fruit_on_dir([0, -1])
                        - (self.g_bot_on_dir([0, -1]) * 1000),
                        self.g_nb_fruit_on_dir([0, 1])
                        - (self.g_bot_on_dir([0, 1]) * 1000),
                        self.g_nb_fruit_on_dir([-1, 0])
                        - (self.g_bot_on_dir([-1, 0]) * 1000),
                        self.g_nb_fruit_on_dir([1, 0])
                        - (self.g_bot_on_dir([1, 0]) * 1000),
                    ]
                )
                actions[np.argmax(moves_value) + 1] = 1

        return actions

    def reset(self):
        pass

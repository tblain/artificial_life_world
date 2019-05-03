from neural_network import NN
import numpy as np
import genetic


class Bot:
    def __init__(self, map, x, y, sim, model=np.array([])):
        if model.shape == (0,):
            self.model = NN((1 + 5 * 2) ** 2 * map.depth + 3, [100, 100, 100, 100, 7])
        else:
            self.model = model

        self.map = map
        self.x = x
        self.y = y
        self.incr_energy(10)
        self.nb_steps = 0
        self.simulation = sim

    def step(self):
        if self.g_energy() <= 0:
            return False
        else:
            print(self.nb_steps, " | ", end="")
            # print(self.g_energy(), " | ", end="")

            predict = self.predict()
            action = np.argmax(predict)

            if action == 1:  # going up
                if self.y - 1 > 0:
                    if self.map.board[self.x, self.y - 1, 0] == 0:
                        self.move([0, -1])
                    elif self.map.board[self.x, self.y - 1, 0] == 2:
                        self.eat(self.x, self.y - 1)
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 2:  # going down
                if self.y + 1 < self.map.height - 1:
                    if self.map.board[self.x, self.y + 1, 0] == 0:
                        self.move([0, 1])
                    elif self.map.board[self.x, self.y + 1, 0] == 2:
                        self.eat(self.x, self.y + 1)
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 3:  # going left
                if self.x - 1 > 0:
                    if self.map.board[self.x - 1, self.y, 0] == 0:
                        self.move([-1, 0])
                    elif self.map.board[self.x - 1, self.y, 0] == 2:
                        self.eat(self.x - 1, self.y)
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 4:  # going right
                if self.x + 1 < self.map.height - 1:
                    if self.map.board[self.x + 1, self.y, 0] == 0:
                        self.move([1, 0])
                    elif self.map.board[self.x + 1, self.y, 0] == 2:
                        self.eat(self.x + 1, self.y)
                    else:  # the bot doesn't move
                        self.incr_energy(-1)
                else:  # the bot doesn't move
                    self.incr_energy(-1)

            elif action == 0:  # the bot doesn't move
                self.incr_energy(-1)  # but still lose energy

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
                    new_model = genetic.mutate(self.model.weights, 1, 1)

                    # TODO: faire une fonction pour rendre ca plus propre
                    if self.map.board[self.x + 1, self.y] == 0:
                        # TODO: faire une methode pour get un truc dans la map
                        new_bot = Bot(self.map, self.x + 1, self.y, self.sim, new_model)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    elif self.map.board[self.x - 1, self.y] == 0:
                        new_bot = Bot(self.map, self.x - 1, self.y, self.sim, new_model)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    elif self.map.board[self.x, self.y + 1] == 0:
                        new_bot = Bot(self.map, self.x, self.y + 1, self.sim, new_model)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    elif self.map.board[self.x, self.y - 1] == 0:
                        new_bot = Bot(self.map, self.x, self.y - 1, self.sim, new_model)
                        new_bot.s_energy(energy_to_child)
                        self.sim.add_bots([new_bot])
                    else:
                        # no place to put the child
                        self.incr_energy(energy_to_child + 2)
                        self.incr_energy(-1)
                else:
                    self.incr_energy(-1)

            else:
                print("pas normal")
            self.nb_steps += 1
            return True

    def eat(self, x, y):
        self.incr_energy(3)  # energy given by eating food
        self.incr_energy(-1)  # energy lost by the consume of food

        # the tree loose 1 fruit TODO: faire une fonction dans map pour gerer ca
        self.map.board[x, y, 1] -= 1
        if self.map.board[x, y, 1] == 0:
            self.map.board[x, y, 0] = 0

    def move(self, action):
        self.map.board[self.x + action[0], self.y + action[1]] = self.map.board[
            self.x, self.y
        ]

        for i in range(self.map.depth):
            # print(self.map.board[self.x, self.y, i])
            self.map.board[self.x, self.y, i] = 0

        self.x += action[0]
        self.y += action[1]
        self.incr_energy(-2)  # energy lost by moving

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

    def predict(self):
        inputs = np.array([])
        # self.map.display(self.map.get_around(self.x, self.y, 5))
        inputs = np.append(inputs, self.map.get_around(self.x, self.y, 5).flatten())
        inputs = np.append(inputs, self.g_energy())
        inputs = np.append(inputs, self.x)
        inputs = np.append(inputs, self.y)
        # print("shape: ", self.map.gets_around(self.x, self.y, 5).shape, " | x: ", self.x, " / y: ", self.y)
        return self.model.predict(inputs)

    def reset(self):
        pass

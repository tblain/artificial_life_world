from neural_network import NN
import numpy as np
import random


class Bot:
    def __init__(self, map, x, y):
        self.model = NN(200 + 3, [10, 10, 6])
        self.map = map
        self.x = x
        self.y = y
        self.energy = 3

    def step(self):
        # print(self.energy)s
        if self.energy <= 0:
            return False
        else:
            # print("energy: ", self.energy)
            predict = self.predict()
            dir = np.argmax(predict)
            # dir = -1

            if dir == 1:  # going up
                if self.y-1 >= 0:
                    if self.map.board[self.x, self.y-1, 0] == 0:
                        self.move([0, -1])
                    elif self.map.board[self.x, self.y-1, 0] == 2:
                        self.eat(self.x, self.y-1)
                    else:  # the bot doesn't move
                        self.energy -= 1
                else:  # the bot doesn't move
                    self.energy -= 1
                        
            elif dir == 2:  # going down
                if self.y+1 < self.map.height:
                    if self.map.board[self.x, self.y+1, 0] == 0:  
                        self.move([0, 1])
                    elif self.map.board[self.x, self.y+1, 0] == 2:
                        self.eat(self.x, self.y+1)
                    else:  # the bot doesn't move
                        self.energy -= 1
                else:  # the bot doesn't move
                    self.energy -= 1

            elif dir == 3:  # going left
                if self.x-1 >= 0:
                    if self.map.board[self.x-1, self.y, 0] == 0:
                        self.move([-1, 0])
                    elif self.map.board[self.x-1, self.y, 0] == 2:
                        self.eat(self.x-1, self.y)
                    else:  # the bot doesn't move
                        self.energy -= 1
                else:  # the bot doesn't move
                    self.energy -= 1

            elif dir == 4:  # going right
                if self.x+1 < self.map.height:
                    if self.map.board[self.x+1, self.y, 0] == 0:
                        self.move([1, 0])
                    elif self.map.board[self.x+1, self.y, 0] == 2:
                        self.eat(self.x+1, self.y)
                    else:  # the bot doesn't move
                        self.energy -= 1
                else:  # the bot doesn't move
                    self.energy -= 1

            elif dir == 0:  # the bot doesn't move
                self.energy -= 1  # but still lose energy
            else:
                print("pas normal")

            return True

    def eat(self, x, y):
        self.energy += 3  # energy given by eating food
        self.energy -= 1  # energy lost by the consume of food
        self.map.board[x, y, 1] -= 1  # the tree loose 1 fruit
        if self.map.board[x, y, 1] == 0:
            self.map.board[x, y, 0] = 0

    def move(self, dir):
        self.map.board[self.x+dir[0], self.y+dir[1]] = self.map.board[self.x, self.y]

        for i in range(self.map.depth):
            # print(self.map.board[self.x, self.y, i])
            self.map.board[self.x, self.y, i] = 0

        self.x += dir[0]
        self.y += dir[1]
        self.energy -= 2  # energy lost by moving

    def predict(self):
        inputs = np.array([])
        inputs = np.append(inputs, self.map.get_around(self.x, self.y, 3).flatten())
        inputs = np.append(inputs, self.energy)
        inputs = np.append(inputs, self.x)
        inputs = np.append(inputs, self.y)
        return self.model.predict(inputs)

    def reset(self):
        pass

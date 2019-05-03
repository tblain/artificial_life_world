import numpy as np
import random


class Map:
    def __init__(self, height, width, depth):
        self.board = np.zeros([height, width, depth])
        self.height = height
        self.width = width
        self.depth = depth

    def get_around(
        self, x_center, y_center, distance
    ):  # TODO: croper le resultat pour avoir que la partie interressante de randu
        height = self.height
        width = self.width

        tboard = np.zeros([height, width, self.depth])

        for x in range(x_center - distance, x_center + 1):
            for y in range(y_center - distance, y_center + 1):
                if (x - x_center) ** 2 + (y - y_center) ** 2 <= distance ** 2:
                    xsym = x_center - (x - x_center)
                    ysym = y_center - (y - y_center)

                    if x >= 0 and x < height and y >= 0 and y < width:
                        tboard[x, y] = self.board[x, y]

                    if xsym >= 0 and xsym < height and y >= 0 and y < width:
                        tboard[xsym, y] = self.board[xsym, y]

                    if x >= 0 and x < height and ysym >= 0 and ysym < width:
                        tboard[x, ysym] = self.board[x, ysym]

                    if xsym >= 0 and xsym < height and ysym >= 0 and ysym < width:
                        tboard[xsym, ysym] = self.board[xsym, ysym]

        rboard = np.zeros([1 + distance * 2, 1 + distance * 2, self.depth])

        xcorner = x_center - distance
        ycorner = y_center - distance

        for i in range(1 + distance * 2):
            for j in range(1 + distance * 2):
                if 0 <= xcorner + i < height and 0 <= ycorner + j < height:
                    rboard[i, j] = tboard[xcorner + i, ycorner + j]
                else:
                    rboard[i, j] = 0

        # self.display(rboard)
        return rboard

    def spawn_tree(self, nb_bush, nb_fruits):
        """
        Spawns trees
        """
        pos = np.random.randint(self.height, size=(nb_bush, 2))
        for i in range(nb_bush):
            x = pos[i, 0]
            y = pos[i, 1]

            while self.board[x, y, 0] != 0:
                x = random.randint(0, self.height - 1)
                y = random.randint(0, self.height - 1)
            self.board[x, y, 0] = 2
            self.board[x, y, 1] = nb_fruits

    def spawn_outer_walls(self):
        for i in range(self.width):
            self.board[i, 0] = 3
            self.board[i, self.height - 1] = 3

        for i in range(self.height):
            self.board[0, i] = 3
            self.board[self.width - 1, i] = 3

    def display(self, board=np.array([]), simple=False):
        if board.shape == (0,):
            board = self.board

        disp_board = board[:, :, 0]

        height = disp_board.shape[0]
        width = disp_board.shape[1]

        if simple:
            print(disp_board)
        else:
            for a in range(-1, width):
                print("_", end="")
            print()

            for i in range(width):
                print("|", end="")
                for j in range(height):
                    if disp_board[j, i] == 1:  # bot
                        print("O", end="")
                    elif disp_board[j, i] == 2:  # tree
                        print("T", end="")
                    elif disp_board[j, i] == 3:  # wall
                        print("=", end="")
                    else:
                        print(" ", end="")
                print("|")

            for a in range(-2, width):
                print("_", end="")

            print()

        # rows = self.map.board.shape[0]
        # cols = self.map.board.shape[1]

        # for x in range(0, rows):
        #     for y in range(0, cols):
        #         if self.map.board[x, y] == 1:
        #             self.w.create_rectangle(
        #                 x * 10, y * 10, (x + 1) * 10, (y + 1) * 10, fill="blue"
        #             )
        #         elif self.map.board[x, y] == -1:
        #             self.w.create_rectangle(
        #                 x * 10, y * 10, (x + 1) * 10, (y + 1) * 10, fill="red"
        #             )

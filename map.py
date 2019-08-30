import numpy as np
import random
from tkinter import (
    Tk,
    Canvas,
    ALL,
    Frame,
    Button,
    IntVar,
    Radiobutton,
    Checkbutton,
    Scale,
    HORIZONTAL,
)


class Map:
    def __init__(self, height, width, depth, sim):
        self.board = np.zeros([height, width, depth])
        self.height = height
        self.width = width
        self.depth = depth
        self.sim = sim

        self.master = Tk()
        self.w = Canvas(self.master, width=800, height=1000)
        # self.w.grid()
        self.board_draw = self.clean_board_draw()

        # Values
        self.v = IntVar()
        self.v.set(1)

        self.v_train_bots = IntVar()
        self.v.set(0)

        # Buttons
        self.btn_spawn_child = Button(
            self.master, text="Spawn child", command=self.spawn_child
        )
        self.btn_spawn_child.grid(row=0, column=0)

        self.btn_toggle_display = Button(
            self.master, text="Toggle display", command=self.toggle_display
        )
        self.btn_toggle_display.grid(row=1, column=0)

        self.btn_load_bot = Button(
            self.master, text="Load bots", command=self.load_bots
        )
        self.btn_load_bot.grid(row=2, column=0)

        self.btn_spawn_tree = Button(
            self.master, text="Spawn tree", command=self.spawn_trees
        )
        self.btn_spawn_tree.grid(row=3, column=0)

        self.btn_spawn_herbi = Button(
            self.master, text="Spawn herbivores", command=self.spawn_spawn_herbivores
        )
        self.btn_spawn_herbi.grid(row=3, column=0)

        # Radiobutton
        # self.radiobutton_train_on = Radiobutton(
        #    self.TK(), text="Train  on", variable=self.v, value=True
        # )
        # self.radiobutton_train_on.grid(row=5, column=0)

        # self.radiobutton_train_off = Radiobutton(
        #    self.TK(), text="Train off", variable=self.v, value=False
        # )
        # self.radiobutton_train_off.grid(row=6, column=0)

        # Checkbutton
        self.checkbutton_train = Checkbutton(
            self.master, text="Train", variable=self.v_train_bots
        )
        self.checkbutton_train.select()
        self.checkbutton_train.grid(row=4, column=0)

        # Scale
        self.scale_nb = Scale(self.master, from_=0, to=1000, orient=HORIZONTAL)
        self.scale_nb.set(25)
        self.scale_nb.grid(row=5, column=0)

    def spawn_child(self):
        self.sim.spawn_child(self.scale_nb.get(), train=(self.v_train_bots == 1))

    def spawn_trees(self):
        self.spawn_tree(self.scale_nb.get(), 30)

    def load_bots(self):
        self.sim.load_bots(self.scale_nb.get(), train=(self.v_train_bots == 1))

    def load_herbivores(self):
        self.sim.load_herbivores(self.scale_nb.get())

    def toggle_display(self):
        self.sim.display = not self.sim.display

    def clean_board_draw(self):
        board_draw = np.empty([40, 40], dtype=object)

        for i in range(40):
            for j in range(40):
                frame = Frame(self.master, width=20, height=20, background="white")
                frame.grid(row=j + 10, column=i + 10)
                board_draw[i, j] = frame

        return board_draw

    def get_around(self, x_center, y_center, distance):
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
        nb_fruits = np.random.randint(nb_fruits, size=(nb_bush,))
        for i in range(nb_bush):
            x = pos[i, 0]
            y = pos[i, 1]

            # while self.board[x, y, 10] != 0:
            # x = random.randint(0, self.height - 1)
            # y = random.randint(0, self.height - 1)
            if self.board[x, y, 0] == 0 and self.board[x, y, 10] == 0:
                self.board[x, y, 10] = 1
                self.board[x, y, 11] = nb_fruits[i]
            # else:
            #    self.board[x, y, 11] += 1

    def spawn_outer_walls(self):
        for i in range(self.width):
            self.board[i, 0] = 2
            self.board[i, self.height - 1] = 3

        for i in range(self.height):
            self.board[0, i] = 2
            self.board[self.width - 1, i] = 3

    def display(self, x1=0, y1=0, nb_cell_to_display=50, board=np.array([]), style=0):
        if board.shape == (0,):
            board = self.board

        disp_board = board[:, :, :]

        height = disp_board.shape[0]
        width = disp_board.shape[1]

        if style == 0:
            print(disp_board)
        elif style == 1:
            for a in range(-1, nb_cell_to_display):
                print("_", end="")
            print()

            for i in range(x1, x1 + nb_cell_to_display):
                print("|", end="")
                for j in range(y1, y1 + nb_cell_to_display):
                    if disp_board[j, i, 0] == 1:  # bot
                        print("O", end="")
                    elif disp_board[j, i, 10] == 1:  # tree
                        print("T", end="")
                    elif disp_board[j, i, 0] == 2:  # wall
                        print("=", end="")
                    else:
                        print(" ", end="")
                print("|")

            for a in range(-1, nb_cell_to_display):
                print("_", end="")

            print()

        elif style == 2:
            self.w.delete(ALL)
            size = 20  # size of a square cell
            if x1 + nb_cell_to_display > self.width:
                x1 -= self.width - x1 + nb_cell_to_display

            if y1 + nb_cell_to_display > self.height:
                y1 -= self.height - y1 + nb_cell_to_display

            for x in range(x1, x1 + nb_cell_to_display):
                for y in range(y1, y1 + nb_cell_to_display):
                    if disp_board[x, y, 0] == 1:
                        self.board_draw[x - x1, y - y1].configure(background="blue")

                    elif disp_board[x, y, 10] == 1:
                        nb_fruits = disp_board[x, y, 11]
                        color = (
                            "#300" + "{:03d}".format(int(nb_fruits * 20 + 400)) + "300"
                        )
                        self.board_draw[x - x1, y - y1].configure(background=color)

                    else:
                        self.board_draw[x - x1, y - y1].configure(background="white")

            # self.w.update()

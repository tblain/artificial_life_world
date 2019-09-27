import numpy as np
import math
import random

from scipy.signal import convolve2d


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
    Spinbox,
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
        self.v_train_bots.set(0)

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

        self.btn_load_trees = Button(
            self.master, text="Load trees", command=self.load_tree_event
        )

        self.btn_load_trees.grid(row=3, column=0)

        self.btn_spawn_herbi = Button(
            self.master, text="Spawn herbivores", command=self.load_herbivores
        )
        self.btn_spawn_herbi.grid(row=6, column=0)

        self.btn_set_sim_speed = Button(
            self.master, text="Set sim speed", command=self.set_sim_speed
        )
        self.btn_set_sim_speed.grid(row=7, column=0)

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

        # Spin box
        self.spin_nb = Spinbox(self.master, from_=0, to_=1000000)
        self.spin_nb.grid(row=5, column=0)
        # Scale
        # self.scale_nb = Scale(self.master, from_=0, to=1000, orient=HORIZONTAL)
        # self.scale_nb.set(1000)
        # self.scale_nb.grid(row=5, column=0)

    # ====================================================================================
    # Handlers

    def get_nb(self):
        # return 100
        return int(self.spin_nb.get())

    def spawn_child(self):
        self.sim.spawn_child(self.get_nb(), train=(self.v_train_bots == 1))

    def load_bots(self):
        self.sim.load_bots(self.get_nb(), train=(self.v_train_bots == 1))

    def set_sim_speed(self):
        self.sim.sim_speed = self.get_nb()

    def load_tree_event(self):
        nb_trees = self.get_nb()
        nb_fruits = 1

        self.load_trees(nb_trees, nb_fruits)

    def load_herbivores(self):
        self.sim.load_herbivores(self.get_nb())

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

    # =========================================================================================
    # gestion du board 

    def load_trees(self, nb_trees, nb_fruits):
        """
        Spawns trees manually
        """

        pos = np.random.randint(self.height, size=(nb_trees, 2))
        nb_fruits = np.random.randint(nb_fruits, size=(nb_trees,))
        for i in range(nb_trees):
            x = pos[i, 0]
            y = pos[i, 1]

            # while self.board[x, y, 10] != 0:
            # x = random.randint(0, self.height - 1)
            # y = random.randint(0, self.height - 1)
            if self.board[x, y, 3] == 0:
                self.board[x, y, 3] = 1
                self.board[x, y, 21] = nb_fruits[i]
            # else:
            #    self.board[x, y, 11] += 1

    def tree_growth(self):
        """
        trees grow fruits
        """
        max_nb_fruits = 40

        tf = self.board[:, :, 21]  # tree_fruits

        # grow polynomiale
        # p1 = 1 / 2
        # p2 = - 1 / 1
        # growth = p1 * tf * tf + p2 * tf * tf * tf

        # growth sinusoidal
        growth = np.sin(tf / 18) * 10

        # on limite la growth des trees en fonction de la growth des arbres voisins

        """
        kernel = np.array(
            [
                [1, 2, 3, 2, 1],
                [2, 5, 9, 5, 2],
                [3, 9, 0, 9, 3],
                [2, 5, 9, 5, 2],
                [1, 2, 3, 2, 1],
            ]
        )  # TODO a renommer

        """
        kernel = np.array(
            [
                [1, 2, 2, 2, 2, 2, 1],
                [2, 2, 3, 3, 3, 2, 2],
                [2, 3, 3, 4, 3, 3, 2],
                [2, 3, 4, 0, 4, 3, 2],
                [2, 3, 3, 4, 3, 3, 2],
                [2, 2, 3, 3, 3, 2, 2],
                [2, 2, 2, 2, 2, 2, 1],
            ]
        )  # TODO a renommer
        growth -= (convolve2d(growth, kernel / 500, "same") + 0.3) + np.random.random((self.height, self.width)) / 10

        growth = np.clip(growth, 0, 1)

        # print(growth)
        self.board[:, :, 21] = np.clip(self.board[:, :, 21] + growth, 0, max_nb_fruits)
        # for l in self.board[:, :, 21]:
            # for a in l:
                # if(0 < a < 1):
                    # print(a)
        # print("fruits:", self.board[10, 10, 11])

    def spawn_trees(self):
        """
        chaque tour les case qui n'ont pas d'arbre genere progressivement
        une graine cette generation est fonction de la taille des arbres
        autour (leur nombre de fruits)
        """
        # TODO renommer les variables pour leurs donnees plus de sens
        # TODO optimiser ce bordel
        tf = self.board[:, :, 21]  # tree_fruits

        kernel = np.array(
            [
                [1, 4, 4, 4, 4, 4, 1],
                [4, 4, 9, 9, 9, 2, 4],
                [4, 9, 9,16, 9, 9, 4],
                [4, 9,16, 0,16, 9, 4],
                [4, 9, 9,16, 9, 9, 4],
                [4, 4, 9, 9, 9, 2, 4],
                [1, 4, 4, 4, 4, 4, 1],
            ]
        )  # TODO a renommer
        growth = convolve2d(tf, kernel / 90000, "same") - np.random.random((self.height, self.width)) / 100
        # TODO ne prendre qu'une partie aleatoire de la growth avec un distribution binomiale ou expo

        # on augmente le niveau de pousse
        self.board[:, :, 22] += growth
        tg = self.board[:, :, 22]

        # on set les graines qui ont eclos a 1
        tg = np.clip(tg, 0, 1)

        # les autres on s'en fout
        tg[tg < 1] = 0

        # on enleve les graines qui sont sur les arbres
        tg -= self.board[:, :, 3]
        tg = np.clip(tg, 0, 1)
        # for l in self.board[:, :, 3]:
            # for a in l:
                # if(0 < a < 1):
                    # print(a)

        self.board[:, :, 3] += tg
        self.board[:, :, 21] += tg

        # on remet le niveau de pousse des graines des arbres qui on pousse a 0
        self.board[:, :, 22] -= tg
        

    def supp_trees_deracine(self): # abandonnee
        print()
        trees = self.board[:, :, 21]
        trees[trees >= 1] = 0
        trees[0 < trees < 1] = 1
        self.board[:, :, 21] = trees

    def spawn_outer_walls(self):
        for i in range(self.width):
            self.board[i, 0] = 3
            self.board[i, self.height - 1] = 3

        for i in range(self.height):
            self.board[0, i] = 3
            self.board[self.width - 1, i] = 3

    def cellLibre(self, x, y):
        return np.count_nonzero(self.board[x, y, [0, 1, 2, 6]]) == 0

    # ==============================================================================================================
    # GUI

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

                    elif disp_board[x, y, 2] == 2:
                        self.board_draw[x - x1, y - y1].configure(background="red")

                    elif disp_board[x, y, 21] > 0:
                        nb_fruits = math.floor(disp_board[x, y, 21]) + random.randint(
                            -1, 1
                        )
                        color = (
                            "#300" + "{:03d}".format(int(nb_fruits * 12 + 300)) + "300"
                        )
                        self.board_draw[x - x1, y - y1].configure(background=color)

                    else:
                        self.board_draw[x - x1, y - y1].configure(background="white")

            # self.w.update()

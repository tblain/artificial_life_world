from bot.py import Bot


class Herbivore(Bot):
    def __init__(self, map, x, y, sim):
        Bot.__init__(map, x, y, sim)

        # attribue le type au bot
        self.type = "H"  # => bot normal

    def predict(self):

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

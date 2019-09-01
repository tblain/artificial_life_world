import numpy as np
from tqdm import tqdm


class NN:
    def __init__(self, input_shape, units):
        """
        units: (10, 11, 12)
            => 3 couches avec 10 neurones pour la premiere
        """
        nb_output = input_shape
        self.weights = []
        for nb_neurones in units:
            self.weights.append(np.random.rand(nb_output, nb_neurones))
            self.weights.append(np.zeros(nb_neurones))
            nb_output = nb_neurones

    def preactiv(self, x):
        res = x
        for i in range(0, len(self.weights), 2):
            res = self.activ(res @ self.weights[i] + self.weights[i + 1])

        return res

    def activ(self, res):
        # leaky ReLU
        res[res < 0] *= 0.01
        return res

    def predict(self, x):
        return self.activ(self.preactiv(x))

    def predict_on_dataset(self, x):
        res = np.zeros(len(x))
        for i in range(len(x)):
            res[i] = self.predict(x.iloc[i])
        return res

    def loss(self, y, res):  # 1 example
        return res - y

    def d_activation(self, res):
        if res > 0:
            return 1
        else:
            return 0

    def cost(self, x, y):  # dataset
        total_cost = 0

        for i in range(len(x)):
            features = x.iloc(i)
            target = y.iloc(i)
            total_cost += (target - self.predict(features)) ** 2

        return total_cost

    def fit_on_one(self, x, y, learning_rate):
        batch_gradient = []
        for k in range(0, len(self.weights), 2):
            batch_gradient.append(np.zeros(self.weights[k].shape))
            batch_gradient.append(np.zeros(self.weights[k + 1].shape))

        res_l = [x]  # store the result after each layer
        res = x

        # calculate the result for the current features
        # print("pre_a")
        for h in range(0, len(self.weights), 2):
            pre_a = res @ self.weights[h] + self.weights[h + 1]
            # print(pre_a)
            res_l.append(pre_a)  # and store the intermediate result before activation
            res = self.activ(pre_a)
        # print()
        # print()

        loss = self.loss(y, res)

        # update of the last neurone
        act_deriv = 1  # self.activation_deriv(post_a)
        batch_gradient[-2] += self.activ(np.expand_dims(res_l[-2], 1)) * loss
        batch_gradient[-1] += loss * act_deriv
        # print("loss:")
        for b in reversed(range(0, len(self.weights) - 2, 2)):  # backpropagation
            l_output = res_l[(b // 2) + 1]  # layer output
            loss = self.activ(l_output) * np.dot(loss, self.weights[b + 2].T)
            # print(loss)
            batch_gradient[b] = l_output * loss
            batch_gradient[b + 1] = l_output
        # print()
        # print()
        # print("batch_gradient")
        for k in range(0, len(self.weights), 2):
            # print(batch_gradient[k])
            self.weights[k] -= learning_rate * batch_gradient[k]
            self.weights[k + 1] -= learning_rate * batch_gradient[k + 1]
        # print()
        # print()

    def fit(self, x, y, step, epochs, batch_size, learning_rate, validation_datas):
        x_val = validation_datas[0]
        y_val = validation_datas[1]
        x = x
        y = y
        i = 0
        epo = 0
        steps_per_epoch = step // epochs

        default_batch_gradient = []
        for k in range(0, len(self.weights), 2):
            default_batch_gradient.append(np.zeros(self.weights[k].shape))
            default_batch_gradient.append(np.zeros(self.weights[k + 1].shape))

        # print("default_batch_gradient shape: ")

        # for q in range(len(default_batch_gradient)):
        #    print(default_batch_gradient[q].shape)

        for etape in tqdm(range(step)):
            i += 1
            bx = x.iloc[batch_size * i : batch_size * (i + 1) - 1]
            by = y.iloc[batch_size * i : batch_size * (i + 1) - 1]

            batch_gradient = (
                default_batch_gradient
            )  # store the gradient calculated on the whole batch

            for k in range(len(bx)):  # iterate over the batch
                res_l = [bx.iloc[k]]  # store the result after each layer
                res = bx.iloc[k]
                for h in range(
                    0, len(self.weights), 2
                ):  # calculate the result for the current features
                    pre_a = res @ self.weights[h] + self.weights[h + 1]
                    res_l.append(
                        pre_a
                    )  # and store the intermediate result before activation
                    res = self.activ(pre_a)

                loss = self.loss(by.iloc[k], res)

                # update of the last neurone
                act_deriv = 1  # self.activation_deriv(post_a)
                batch_gradient[-2] += self.activ(np.expand_dims(res_l[-2], 1)) * loss
                batch_gradient[-1] += loss * act_deriv

                for b in reversed(
                    range(0, len(self.weights) - 2, 2)
                ):  # backpropagation
                    l_output = res_l[(b // 2) + 1]  # layer output
                    loss = self.activ(l_output) * np.dot(loss, self.weights[b + 2].T)
                    batch_gradient[b] = l_output * loss
                    batch_gradient[b + 1] = l_output
                    # print(l_output * loss)

            for k in range(0, len(self.weights), 2):
                self.weights[k] -= learning_rate * (1 / batch_size) * batch_gradient[k]
                self.weights[k + 1] -= (
                    learning_rate * (1 / batch_size) * batch_gradient[k + 1]
                )

            if x.shape[0] < batch_size * nb_bots(i + 1):
                p = np.random.permutation(len(x))
                x = x.iloc[p]
                y = y.iloc[p]
                i = 0

            if etape != 0 and etape % (steps_per_epoch) == 0:
                print("=====================")
                predic_val = self.predict_on_dataset(x_val)
                predic_train = self.predict_on_dataset(x.iloc[i : i + (step // epochs)])
                print("predic_train: ", predic_train)
                print(
                    "Epoch: ",
                    epo,
                    "| loss val: ",
                    ((predic_val - y_val) ** 2).mean(),
                    " | loss train ",
                    ((predic_train - y.iloc[i : i + (step // epochs)]) ** 2).mean() / 2,
                )
                print("mean predic: ", predic_val.mean())
                for l in self.weights:
                    # print(l)
                    pass
                epo += 1


def normalize(x):
    return (x - min(x)) / (max(x) - min(x))

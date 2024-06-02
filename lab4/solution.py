import sys
import numpy as np


def load_data(path):
    data = {}
    with open(path, 'r') as f:
        lines = f.readlines()
        columns = lines[0].strip().split(',')
        lines = lines[1:]

        for c in columns:
            data[c] = []

        for line in lines:
            values = line.strip().split(',')
            for i, v in enumerate(values):
                data[columns[i]].append(float(v))

    return data


def get_weights(rows, columns):
    return np.random.normal(0, 0.01, (rows, columns))


class NeuralNetwork:
    def __init__(self, dimension, data):
        self.dimension = dimension
        self.data = data
        self.columns = list(data.keys())[:-1]
        self.layer_dimension = 5 if self.dimension in ['5s', '5s5s'] else 20
        self.weights = {}
        self.biases = {}
        self.input_dimension = len(self.columns)
        self.err = None
        self.y_hat = []

        self.weights['w1'] = get_weights(self.layer_dimension, self.input_dimension)
        self.biases['b1'] = get_weights(self.layer_dimension, 1)

        if self.dimension == '5s5s':
            self.weights['w2'] = get_weights(self.layer_dimension, self.layer_dimension)
            self.biases['b2'] = get_weights(self.layer_dimension, 1)

        self.weights['w_out'] = get_weights(self.input_dimension, self.layer_dimension)
        self.biases['b_out'] = get_weights(1, 1)


    def forward(self, x):
        x = np.array(x).reshape((2, 1)) if isinstance(x, tuple) else np.array([[x]])

        h = np.dot(self.weights['w1'], x) + self.biases['b1']
        sigmoid = 1 / (1 + np.exp(-h))

        if self.dimension == '5s5s':
            h = np.dot(self.weights['w2'], sigmoid) + self.biases['b2']
            sigmoid = 1 / (1 + np.exp(-h))

        h = np.dot(self.weights['w_out'], sigmoid) + self.biases['b_out']
        return h[0][0]


    def predict(self):
        if self.input_dimension == 1:
            inputs = self.data[self.columns[0]]
        else:
            inputs = zip(self.data[self.columns[0]], self.data[self.columns[1]])

        for x in inputs:
            self.y_hat.append(self.forward(x))

        self.err = (1 / len(self.y_hat)) * sum((y - y_h) ** 2 for y, y_h in zip(self.data[list(self.data.keys())[-1]], self.y_hat))


args = sys.argv[1:]

train_data = load_data('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab4\\files\\' + args[args.index('--train') + 1])
dim = args[args.index('--nn') + 1]

test_data = load_data('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab4\\files\\' + args[args.index('--test') + 1])

population_size = int(args[args.index('--popsize') + 1])
elitism = int(args[args.index('--elitism') + 1])
p = float(args[args.index('--p') + 1])
st_dev = float(args[args.index('--K') + 1])
iterations = int(args[args.index('--iter') + 1])

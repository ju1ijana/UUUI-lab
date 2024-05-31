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
    return np.random.normal(0, 0.1, (rows, columns))


def nn(dimension, data):
    columns = list(data.keys())[:-1]
    layer_dimension = 5 if dimension in ['5s', '5s5s'] else 20
    y_hat = []
    for x in data[columns[0]] if len(columns) == 1 else zip(data[columns[0]], data[columns[1]]):
        weights = get_weights(layer_dimension, len(columns))
        x = np.array(x).reshape((2, 1)) if isinstance(x, tuple) else np.array([[x]])
        h = np.dot(weights, x) + get_weights(layer_dimension, 1)
        sigmoid = 1 / (1 + np.exp(-h))
        if dimension == '5s5s':
            weights = get_weights(layer_dimension, len(columns))
            h = np.dot(weights, x) + get_weights(layer_dimension, 1)
            sigmoid = 1 / (1 + np.exp(-h))
        weights = get_weights(len(columns), layer_dimension)
        y_hat.append((np.dot(weights, sigmoid) + get_weights(1, 1))[0][0])

    err = (1/len(y_hat)) * sum((y - y_h)**2 for y, y_h in zip(data[list(data.keys())[-1]], y_hat))


args = sys.argv[1:]

data = load_data('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab4\\files\\' + args[args.index('--train') + 1])
dim = args[args.index('--nn') + 1]
nn(dim, data)




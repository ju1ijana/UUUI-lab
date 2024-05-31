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


def nn(dimension, data):
    x_data = data['x']
    if dimension == '5s' or dimension == '20s':
        dimension = int(dimension[:-1])
        for x in x_data:
            weights = np.array([np.random.normal(0, 0.1) for _ in range(dimension)])
            h = np.dot(weights, x) + np.array([np.random.normal(0, 0.1) for _ in range(dimension)])
            sigmoid = 1 / (1 + np.exp(-h))
            weights = np.array([np.random.normal(0, 0.1) for _ in range(dimension)])
            y_hat = np.dot(weights, sigmoid) + np.random.normal(0, 0.1)
            y_hat = 1 / (1 + np.exp(-y_hat))


args = sys.argv[1:]

data = load_data('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab4\\files\\' + args[args.index('--train') + 1])
dim = args[args.index('--nn') + 1]
nn(dim, data)




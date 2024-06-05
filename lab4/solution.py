import sys
import copy
import numpy as np


def load_data(path):                                                                        # funkcija za učitavanje podataka u rječnik
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


class NeuralNetwork:
    def __init__(self, dimension, data, set_weights_and_biases, train):
        self.dimension = dimension                                                          # dimenzije slojeva neuronske mreže (argument funkcije)
        self.data = data
        self.columns = list(data.keys())[:-1]
        self.layer_dimension = 5 if self.dimension in ['5s', '5s5s'] else 20                # stvarne dimenzije slojeva
        self.input_dimension = len(self.columns)
        self.weights = {}
        self.biases = {}
        self.y_hat = []
        self.err = None
        self.fitness = None

        if set_weights_and_biases:
            self.weights['w1'] = np.random.normal(0, 0.01, (self.layer_dimension, self.input_dimension))
            self.biases['b1'] = np.random.normal(0, 0.01, (self.layer_dimension, 1))

            if self.dimension == '5s5s':
                self.weights['w2'] = np.random.normal(0, 0.01, (self.layer_dimension, self.layer_dimension))
                self.biases['b2'] = np.random.normal(0, 0.01, (self.layer_dimension, 1))

            self.weights['w_out'] = np.random.normal(0, 0.01, (1, self.layer_dimension))
            self.biases['b_out'] = np.random.normal(0, 0.01, (1, 1))

        if train:
            self.predict()


    def set_weights_and_biases(self, key, w, b):
        self.weights['w' + key] = w
        self.biases['b' + key] = b


    def forward(self, x):                                                       # unaprijedni prolaz svih ulaznih podataka odjednom
        x = np.array(x)

        if x.ndim == 1:
            x = x.reshape(1, -1)

        h = np.dot(self.weights['w1'], x) + self.biases['b1']
        sigmoid = 1 / (1 + np.exp(-h))

        if self.dimension == '5s5s':
            h = np.dot(self.weights['w2'], sigmoid) + self.biases['b2']
            sigmoid = 1 / (1 + np.exp(-h))

        h = np.dot(self.weights['w_out'], sigmoid) + self.biases['b_out']

        return h


    def predict(self):                                                          # priprema podataka za unaprijedni prolaz
        if self.input_dimension == 1:
            inputs = np.array(self.data[self.columns[0]]).T
        else:
            inputs = np.array([self.data[self.columns[0]], self.data[self.columns[1]]])

        self.y_hat = self.forward(inputs)

        self.err = (1 / len(self.y_hat.tolist()[0])) * sum(                     # računanje srednjeg kvadratnog odstupanja (pogreške)
            (y - y_h) ** 2 for y, y_h in zip(self.data[list(self.data.keys())[-1]], self.y_hat.tolist()[0]))
        self.fitness = 1/self.err


    def test_predict(self, data):
        self.data = data
        self.predict()


# ================================================================================================================================


def GenAlg(popsize, elitism, p, K, iter):
    population = [NeuralNetwork(dim, train_data, True, True) for _ in range(popsize)]

    for i in range(iter):
        population = sorted(population, key=lambda nn: nn.fitness, reverse=True)
        fitness = [nn.fitness for nn in population]
        probabilities = [f/sum(fitness) for f in fitness]
        new_population = [population[i] for i in range(elitism)]

        while len(new_population) != popsize:
            pair = np.random.choice(population, size=2, replace=False, p=probabilities).tolist()
            child = NeuralNetwork(dim, train_data, False, False)
            for key in ['1', '2', '_out']:
                if 'w' + key in pair[0].weights:                                # postavljanje weights i biases na srednju vrijednost roditelja
                    child.set_weights_and_biases(key, (pair[0].weights['w' + key] + pair[1].weights['w' + key]) / 2, (pair[0].biases['b' + key] + pair[1].biases['b' + key]) / 2)

            for key, value in child.weights.items():                            # mutiranje weights i biases s vjerojatnosti p i prema normalnoj razdiobi
                child.weights[key] = child.weights[key] + np.where(np.random.rand(*child.weights[key].shape) < p, np.random.normal(0, K, child.weights[key].shape), 0)

            for key, value in child.biases.items():
                child.biases[key] = child.biases[key] + np.where(np.random.rand(*child.biases[key].shape) < p, np.random.normal(0, K, child.biases[key].shape), 0)

            child.predict()
            new_population.append(child)

        population = copy.deepcopy(new_population)

    population = sorted(population, key=lambda nn: nn.fitness, reverse=True)
    print('[Train error @{}]: {:.6f}'.format(iter, population[0].err))
    population[0].test_predict(test_data)
    print('[Test error]: {:.6f}'.format(population[0].err))


args = sys.argv[1:]

train_data = load_data(args[args.index('--train') + 1])
dim = args[args.index('--nn') + 1]

test_data = load_data(args[args.index('--test') + 1])

population_size = int(args[args.index('--popsize') + 1])
elitism = int(args[args.index('--elitism') + 1])
p = float(args[args.index('--p') + 1])
st_dev = float(args[args.index('--K') + 1])
iterations = int(args[args.index('--iter') + 1])

GenAlg(population_size, elitism, p, st_dev, iterations)

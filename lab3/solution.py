import copy
import sys
import pandas as pd
from collections import deque
import math


def entropy_of_dataset_by_values(table, feature, value, outcome_name):                  # najprije pronalaženje broja pojedinih ishoda za sve
    outcomes = {key: 0 for key in sorted(table[outcome_name])}                          # vrijednosti neke značajke pa računanje entropije za tu vrijednost
    outcome_values = table[table[feature] == value][outcome_name].value_counts()
    for key in outcomes.keys():
        outcomes[key] = outcome_values.get(key, 0)
    values = outcomes.values()
    if 0 in values:
        return 0
    ret = 0
    for v in values:
        ret -= (v / sum(values)) * math.log(v / sum(values), 2)
    return ret


def ID3_algrithm(features, values):
    global df, outcome_name
    dataset = copy.deepcopy(df)

    if features and values:
        for f, v in zip(features, values):
            dataset = dataset[dataset[f] == v].drop(f, axis=1)

    E_D = 0                                                                         # entropija početnog skupa primjera (sl. 70)
    outcome_values = dataset[outcome_name].value_counts()
    for i in outcome_values:
        E_D -= (i / sum(outcome_values)) * math.log(i / sum(outcome_values), 2)

    IG = {}                                                                         # računanje informacijske dobiti značajki (sl. 73)
    for k1 in dataset.columns[:-1]:
        IG[k1] = E_D
        for k2 in dataset[k1].unique():
            ED_v = entropy_of_dataset_by_values(dataset, k1, k2, outcome_name)
            IG[k1] -= dataset[k1].value_counts().get(k2, 0) / dataset[k1].count() * ED_v

    if all(value == 0 for value in IG.values()):
        return True, dataset[outcome_name].unique()[0]

    sorted_IG = sorted(IG.items(), key=lambda x: x[1], reverse=True)
    for k, v in sorted_IG:
        print('IG(' + k + ')=' + "{:.4f}".format(round(v, 4)), end=' ')
    print()

    max_key = max(sorted(IG.items()), key=lambda x: x[1])[0]                        # odabir značajke s najvećom IG i abecedno
    return False, max_key


class ID3:
    def __init__(self):
        self.start_node = None
        self.adj_matrix = {}
        self.test_features = {}
        self.paths = []
        self.predictions = []
        self.accuracy = []
        self.confusion_matrix = {}

    def fit(self, train_dataset):
        for c in train_dataset.columns[:-1]:
            self.test_features.setdefault(c, set())
            for v in train_dataset[c].unique():
                self.test_features[c].add(v)

        dataset = train_dataset
        chosen_node = ID3_algrithm([], [])                                          # prvi poziv funkcije
        self.start_node = chosen_node[1]                                            # pronađeni korijen stabla
        queue = deque()
        queue.extend([(chosen_node[1], [], [], chosen_node[0])])
        while queue:
            current = queue.popleft()
            column = current[0]
            for f in sorted(dataset[column].unique()):
                self.adj_matrix.setdefault(column, {})
                self.adj_matrix[column].setdefault(f, '')

                chosen_node = ID3_algrithm(current[1] + [column], current[2] + [f])
                self.adj_matrix[column][f] = chosen_node[1]

                if chosen_node[0]:
                    self.paths.append((current[1] + [column], current[2] + [f], chosen_node[1]))

                if not chosen_node[0]:
                    queue.extend([(chosen_node[1], current[1] + [column], current[2] + [f], chosen_node[0])])

        print('[BRANCHES]:')

        for path in self.paths:
            i = 1
            for j in range(len(path[0])):
                print(i, ':', path[0][j], '=', path[1][j], sep='', end=' ')
                i += 1
            print(path[2])


    def predict(self, test_dataset):
        for el in sorted(list(test_dataset[test_dataset.columns[-1]].unique())):
            self.confusion_matrix.setdefault(el, {str(x): 0 for x in sorted(outcome_values)})

        def test_rule(row, rule):
            extracted = []
            for feature in rule[0]:
                extract = row[feature]
                if extract not in self.test_features[feature]:
                    return True, sorted(test_dataset[test_dataset.columns[-1]].unique())[0]
                extracted.append(extract)
            return set(extracted) == set(rule[1]), rule[2]


        for index, row in test_dataset.iterrows():
            i = 0
            result_status, result = test_rule(row, self.paths[i])
            while not result_status:
                i += 1
                result_status, result = test_rule(row, self.paths[i])

            self.predictions.append(result)
            self.accuracy.append(result == row[outcome_name])
            self.confusion_matrix[row[outcome_name]][result] += 1

        print('[PREDICTIONS]: ', ' '.join(self.predictions), sep='')
        print('[ACCURACY]: ', '{:.5f}'.format(round(sum(self.accuracy)/len(self.accuracy), 5)), sep='')
        print('[CONFUSION_MATRIX]:')

        for key, value in self.confusion_matrix.items():
            for k, v in value.items():
                print(v, end=' ')
            print()


args = sys.argv[1:]
df = pd.read_csv('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab3\\files\\' + args[0], dtype=str)
outcome_name = df.columns[-1]
outcome_values = list(df[df.columns[-1]].unique())

test = pd.read_csv('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab3\\files\\' + args[1], dtype=str)

model = ID3()
model.fit(df)
model.predict(test)

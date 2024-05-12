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

    if all(IG.values()) == 0:
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

    def fit(self, train_dataset):
        dataset = train_dataset
        chosen_node = ID3_algrithm([], [])                                          # prvi poziv funkcije
        self.start_node = chosen_node[1]                                            # pronađeni korijen stabla
        queue = deque()
        queue.extend([(chosen_node[1], [], [], chosen_node[0])])
        while queue:
            current = queue.popleft()
            column = current[0]
            for f in dataset[column].unique():
                self.adj_matrix.setdefault(column, [])
                self.adj_matrix[column].append(f)

                chosen_node = ID3_algrithm(current[1] + [column], current[2] + [f])
                self.adj_matrix.setdefault(f, [])
                self.adj_matrix[f].append(chosen_node[1])

                if not chosen_node[0]:
                    queue.extend([(chosen_node[1], current[1] + [column], current[2] + [f], chosen_node[0])])

        print('[BRANCHES]:')

        def dfs(graph, node, path, paths):
            path.append(node)

            if node not in graph:
                paths.append(path.copy())
            else:
                for neighbor in graph[node]:
                    dfs(graph, neighbor, path, paths)

            path.pop()

        paths = []
        path = []

        dfs(self.adj_matrix, self.start_node, path, paths)

        for p in paths:
            for i in range(0, len(p), 2):
                if i + 1 < len(p):
                    print(int(i / 2) + 1, end=':')
                    print(p[i], '=', p[i + 1], sep='', end=' ')
                else:
                    print(p[i])



    def predict(self, test_dataset):
        a = 2

    def D_xv(self):
        a = 3


args = sys.argv[1:]
df = pd.read_csv('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab3\\files\\' + args[0])
outcome_name = df.columns[-1]


model = ID3()
model.fit(df)

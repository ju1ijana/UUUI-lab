import sys
import math
import copy
from collections import deque
from collections import Counter


def extract_column(dataset, column):                                # u listu se izdvajaju sve vrijednosti neke značajke u trenutnom skupu podataka
    return [row[column] for row in dataset]


def count_values(values):                                                       # vraća listu brojeva različitih vrijednosti
    counts = Counter(values)
    return [count for item, count in counts.items()]


def count_per_value(values):                                                    # vraća broj vrijednosti za svaku vrijednost
    counts = Counter(values)
    return {item: count for item, count in counts.items()}


def extract_rows(dataset, feature, value):                                      # izdvajanje redaka skupa podataka u kojima se nalazi
    return [row for row in dataset if row[feature] == value]                    # željena vrijednost neke značajke


def extract_subset(dataset, feature, value):                                    # izdvajanje podskupa u kojem željena značajka ima određenu vrijednost
    return [{key: value for key, value in row.items() if key != feature} for row in dataset if
            row.get(feature) == value]

def extract_unique_values_of_feature(dataset, feature):                         # za pojedinu značajku vraća koje sve vrijednosti može poprimiti
    return {row[feature] for row in dataset if feature in row}


# najprije pronalaženje broja pojedinih ishoda za sve vrijednosti neke značajke pa računanje entropije za tu vrijednost
def entropy_of_dataset_by_values(table, feature, value, outcome_name):
    outcome_values = count_values(extract_column(extract_rows(table, feature, value), outcome_name))
    if 0 in outcome_values:
        return 0
    ret = 0
    for v in outcome_values:
        ret -= (v / sum(outcome_values)) * math.log(v / sum(outcome_values), 2)
    return ret


def ID3_algrithm(features, values):
    global df, outcome_name
    dataset = copy.deepcopy(df)

    if features and values:
        for f, v in zip(features, values):
            dataset = extract_subset(dataset, f, v)

    E_D = 0                                                                     # entropija početnog skupa primjera (sl. 70)
    outcome_values = count_values(extract_column(dataset, outcome_name))
    for i in outcome_values:
        E_D -= (i / sum(outcome_values)) * math.log(i / sum(outcome_values), 2)
    if dataset:
        IG = {}                                                                     # računanje informacijske dobiti značajki (sl. 73)
        for k1 in list(dataset[0].keys())[:-1]:
            IG[k1] = E_D
            for k2 in extract_unique_values_of_feature(dataset, k1):
                ED_v = entropy_of_dataset_by_values(dataset, k1, k2, outcome_name)
                IG[k1] -= count_per_value(extract_column(dataset, k1))[k2] / len(extract_column(dataset, k1)) * ED_v

        if all(value == 0 for value in IG.values()):
            return True, extract_column(dataset, outcome_name)[0]

        if depth == len(features):
            outcomes = count_per_value(extract_column(dataset, outcome_name))
            return True, min(key for key, value in outcomes.items() if value == max(outcomes.values()))

        sorted_IG = sorted(IG.items(), key=lambda x: x[1], reverse=True)
        for k, v in sorted_IG:
            print('IG(' + k + ')=' + "{:.4f}".format(round(v, 4)), end=' ')
        print()

        max_key = max(sorted(IG.items()), key=lambda x: x[1])[0]                    # odabir značajke s najvećom IG i abecedno
        return False, max_key
    else:
        dataset = copy.deepcopy(df)                                                 # ako je D prazan skup vraća se najčešća oznaka
        for f, v in zip(features[:-1], values[:-1]):                                # primjera u nadčvoru
            dataset = extract_subset(dataset, f, v)
        outcomes = count_per_value(extract_column(dataset, outcome_name))
        return True, min(key for key, value in outcomes.items() if value == max(outcomes.values()))


class ID3:
    def __init__(self):
        self.start_node = None                                                  # korijen stabla odluke
        self.test_features = {}                                                 # lista za moguće vrijednosti značajki početnog skupa podataka
        self.paths = []                                                         # lista za putove u stablu odluke
        self.predictions = []                                                   # lista za dobivene predikcije
        self.accuracy = []                                                      # lista za spremanje informacije o točnosti predikcije (0 ili 1)
        self.confusion_matrix = {}                                              # matrica zabune

    def fit(self, dataset):
        for c in columns[:-1]:                                                  # spremanje mogućih vrijednosti svake od značajki
            self.test_features.setdefault(c, set())                             # ključevi su značajke, vrijednosti setovi mogućih vrijednosti
            for v in set(extract_column(dataset, c)):
                self.test_features[c].add(v)

        if depth == 0:
            outcomes = count_per_value(extract_column(dataset, outcome_name))
            self.paths.append(min(key for key, value in outcomes.items() if value == max(outcomes.values())))

        else:
            chosen_node = ID3_algrithm([], [])                                      # prvi poziv funkcije
            self.start_node = chosen_node[1]                                        # pronađeni korijen stabla
            queue = deque()
            queue.extend([(chosen_node[1], [], [], chosen_node[0])])                # spremanje imena značajke, vektora features i values i statusa

            while queue:                                                            # rekurzivni algoritam ostvaren redom
                current = queue.popleft()
                column = current[0]
                for f in sorted(set(extract_column(dataset, column))):
                    chosen_node = ID3_algrithm(current[1] + [column], current[2] + [f])

                    if chosen_node[0]:                                              # dosegnut list, staza se sprema u self.paths
                        self.paths.append((current[1] + [column], current[2] + [f], chosen_node[1]))

                    if not chosen_node[0]:                                          # u red se dodaje čvor za koji se treba provesti postupak
                        queue.extend([(chosen_node[1], current[1] + [column], current[2] + [f], chosen_node[0])])

        print('[BRANCHES]:')                                                        # ispis grana

        if len(self.paths) == 1:
            print(self.paths[0])
        else:
            for path in self.paths:
                i = 1
                for j in range(len(path[0])):
                    print(i, ':', path[0][j], '=', path[1][j], sep='', end=' ')
                    i += 1
                print(path[2])


    def predict(self, test_dataset):
        outcome_values = extract_unique_values_of_feature(test_dataset, outcome_name)           # priprema matrice zablude
        for el in sorted(outcome_values):
            self.confusion_matrix.setdefault(el, {str(x): 0 for x in sorted(outcome_values)})

        def test_rule(row, rule):                                                               # ispitivanje jednog pravila na jednom test primjeru
            extracted = []
            for feature in rule[0]:
                extract = row[feature]
                if extract not in self.test_features[feature]:
                    return True, sorted(extract_unique_values_of_feature(test_dataset, outcome_name))[0]
                extracted.append(extract)
            return extracted == rule[1], rule[2]

        for index, row in enumerate(test_dataset):                                              # za svaki test primjer ispitivanje naučenih pravila
            if len(self.paths) != 1:
                i = 0
                result_status, result = test_rule(row, self.paths[i])
                while not result_status:
                    i += 1
                    result_status, result = test_rule(row, self.paths[i])
            else:
                result = self.paths[0]

            self.predictions.append(result)
            self.accuracy.append(result == row[outcome_name])
            self.confusion_matrix[row[outcome_name]][result] += 1

        print('[PREDICTIONS]: ', ' '.join(self.predictions), sep='')                        # ispis dobivenih predikcija i mjera točnosti (accuracy, confusion matrix)
        print('[ACCURACY]: ', '{:.5f}'.format(round(sum(self.accuracy) / len(self.accuracy), 5)), sep='')
        print('[CONFUSION_MATRIX]:')

        for key, value in self.confusion_matrix.items():
            for k, v in value.items():
                print(v, end=' ')
            print()


# =====================================================================================================================================================================


args = sys.argv[1:]

df = []                                                                                     # spremanje redaka u listu df u obliku dictionaryja
with open(args[0], 'r') as f:
    lines = f.readlines()
    columns = lines[0].strip().split(',')
    lines = lines[1:]

    for i, line in enumerate(lines):
        df.append({})
        for j, value in enumerate(line.strip().split(',')):
            df[i][columns[j]] = value

outcome_name = columns[-1]

test = []                                                                                   # spremanje test primjera
with open(args[1], 'r') as f:
    lines = f.readlines()
    columns = lines[0].strip().split(',')
    lines = lines[1:]

    for i, line in enumerate(lines):
        test.append({})
        for j, value in enumerate(line.strip().split(',')):
            test[i][columns[j]] = value


depth = int(args[2]) if len(args) == 3 else None

model = ID3()
model.fit(df)
model.predict(test)

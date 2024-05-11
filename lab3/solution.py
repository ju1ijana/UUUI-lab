import sys
import pandas as pd
import math


def entropy_of_dataset_by_values(table, feature, value):
    values = table[feature][value].values()
    if 0 in values:
        return 0
    ret = 0
    for v in values:
        ret -= (v/sum(values))*math.log(v/sum(values), 2)
    return ret



class ID3:

    def fit(self, train_dataset):
        last_column_name = train_dataset.columns[-1]
        outcomes = list(train_dataset[last_column_name].unique())
        count_outcomes = {}                                                 # dict koji služi za zapis tablice na slajdu 69

        # stvaranje tablice značajka - vrijednost - broj pojedinih ishoda
        for column in train_dataset.columns[:-1]:
            count_outcomes[column] = {}
            for value in sorted(train_dataset[column].unique()):
                count_outcomes[column][value] = {key: 0 for key in sorted(outcomes)}
                outcome_values = train_dataset[train_dataset[column] == value][last_column_name].value_counts()
                for key in count_outcomes[column][value].keys():
                    count_outcomes[column][value][key] = outcome_values.get(key, 0)


        E_D = 0                                                             # entropija početnog skupa primjera (sl. 70)
        outcome_values = train_dataset[last_column_name].value_counts()
        for i in outcome_values:
            E_D -= (i/sum(outcome_values))*math.log(i/sum(outcome_values), 2)

        IG = {}                                                             # računanje informacijske dobiti značajki (sl. 73)
        for k1 in count_outcomes.keys():
            IG[k1] = E_D
            for k2 in count_outcomes[k1].keys():
                ED_v = entropy_of_dataset_by_values(count_outcomes, k1, k2)
                IG[k1] -= train_dataset[k1].value_counts().get(k2, 0)/train_dataset[k1].count()*ED_v

        sorted_IG = sorted(IG.items(), key=lambda x: x[1], reverse=True)
        for k, v in sorted_IG:
            print('IG(' + k + ')=' + str(round(v, 4)), end=' ')


    def predict(self, test_dataset):
        a = 2

    def D_xv(self):
        a = 3


args = sys.argv[1:]
df = pd.read_csv('C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab3\\files\\' + args[0])

model = ID3()
model.fit(df)

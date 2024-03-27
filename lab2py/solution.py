import sys
from itertools import combinations

args = sys.argv[1:]

path = 'C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab2\\files\\' + args[1]

with open(path, 'r', encoding='utf-8') as f:
    ss = [line.rstrip() for line in f.readlines()]
ss = [el.lower() for el in ss if '#' not in el]

def Not(c):
    if c[0] == '~':
        return c[1:]
    else:
        return '~' + c


# noinspection PyRedundantParentheses
def resolve(combination):
    global clauses, clause_index
    c1, c2 = combination
    for atom in c1[0].split(' v '):
        if Not(atom) in c2[0].split(' v '):
            new_cl = [a for a in c1[0].split(' v ') if a != atom] + [b for b in c2[0].split(' v ') if b != Not(atom)]
            if ' v '.join(new_cl) not in clauses_set:
                clauses_set.add(' v '.join(new_cl))
                clause_index += 1
                return (' v '.join(new_cl), clause_index, str(c1[1]) + ' + ' + str(c2[1]))
    return None


def resolution():
    global clauses, clause_index, clauses_set
    closed = set()
    for _ in range(3):
        print("clauses:", clauses)
        new = []
        clause_index = clauses[-1][1]
        for combination in combinations(clauses, 2):
            if combination not in closed:
                closed.add(combination)
                res = resolve(combination)
                if res:
                    new.append(res)
                    print(new)
                    if res[0] == '':
                        clauses += new
                        return
        clauses += new
        print()



clauses = ss
clauses[-1] = '~' + clauses[-1]         # negiranje

for index, el in enumerate(clauses):
    print(str(index + 1) + '. ' + el)
    clauses[index] = (clauses[index], index + 1, '')
print('===============')

# definiranje varijabli koje će se koristiti globalno
clause_index = clauses[-1][1]
clauses_set = set(el[0] for el in clauses)
resolution()
print("final clauses:", clauses)











import sys
from itertools import combinations
from collections import deque

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

def find_clause_by_number(number):
    c = [x for x in clauses if x[1] == number]
    if c:
        return c[0]


def resolve(combination):
    global clauses, clause_index, clauses_set
    c1, c2 = combination
    for atom in c1[0].split(' v '):
        if Not(atom) in c2[0].split(' v '):
            new_cl = [a for a in c1[0].split(' v ') if a != atom] + [b for b in c2[0].split(' v ') if b != Not(atom)]
            if ' v '.join(new_cl) not in clauses_set:
                clauses_set.add(' v '.join(new_cl))
                clause_index += 1
                # noinspection PyRedundantParentheses
                return (' v '.join(new_cl), clause_index, str(c1[1]) + ' + ' + str(c2[1]))
    return None


def resolution():
    global clauses, clause_index, clauses_set
    closed = set()
    changed = True
    while changed:
        changed = False
        #print("clauses:", clauses)
        new = []
        clause_index = clauses[-1][1]
        for combination in combinations(clauses, 2):
            if combination not in closed:
                closed.add(combination)
                res = resolve(combination)
                if res:
                    changed = True
                    new.append(res)
                    #print(new)
                    if res[0] == '':
                        clauses += new
                        return
        clauses += new
        #print()



clauses = ss
clauses[-1] = ' v '.join([Not(el) for el in clauses[-1].split(' v ')])

original_clauses_index = len(clauses)
for index, el in enumerate(clauses):
    print(str(index + 1) + '. ' + el)
    clauses[index] = (clauses[index], index + 1, '')
print('===============')

# definiranje varijabli koje će se koristiti globalno
clause_index = clauses[-1][1]
clauses_set = set(el[0] for el in clauses)
resolution()


if clauses[-1][0] == '':
    queue = deque()
    queue.extend([int(x) for x in clauses[-1][2].split(' + ')])
    requirements = [clauses[-1][1]]
    while queue:
        requirements.append(queue.popleft())
        clause = find_clause_by_number(requirements[-1])
        queue.extend([int(x) for x in clause[2].split(' + ') if x != ''])
    requirements = sorted([x for x in requirements if not (x <= original_clauses_index)])
    requirements_dict = {}
    i = original_clauses_index
    for el in requirements:
        i += 1
        requirements_dict[el] = i

    for el in requirements:
        clause = find_clause_by_number(el)
        c = clause[0] if clause[0] != '' else 'NIL'
        a = int(clause[2].split(' + ')[0])
        if a in requirements_dict:
            a = requirements_dict[a]
        b = int(clause[2].split(' + ')[1])
        if b in requirements_dict:
            b = requirements_dict[b]
        print(str(requirements_dict[el]) + '. ' + c + ' (' + str(a) + ', ' + str(b) + ')')
    print('===============')
    print('[CONCLUSION]: ' + str(' v '.join([Not(el) for el in find_clause_by_number(original_clauses_index)[0].split(' v ')])) + ' is true')
else:
    print('[CONCLUSION]: ' + str(' v '.join([Not(el) for el in find_clause_by_number(original_clauses_index)[0].split(' v ')])) + ' is unknown')










import sys
from itertools import combinations
from collections import deque
import copy

args = sys.argv[1:]

path = 'C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab2\\files\\' + args[1]

with open(path, 'r', encoding='utf-8') as f:
    ss = [line.rstrip() for line in f.readlines()]
ss = [el.lower() for el in ss if '#' not in el]


def Not(c):  # funkcija koja vraća negaciju atoma
    if c[0] == '~':
        return c[1:]
    else:
        return '~' + c


def find_clause_by_number(number):
    global clauses
    c = [x for x in clauses if x[1] == number]
    return c[0] if c else None


def resolve(combination):
    global clauses, clause_index, clauses_set
    c1, c2 = combination
    for atom in c1[0].split(' v '):
        if Not(atom) in c2[0].split(' v '):
            new_cl = [a for a in c1[0].split(' v ') if a != atom] + [b for b in c2[0].split(' v ') if b != Not(atom)]
            for c in new_cl:  # uklanjanje valjanih klauzula
                if Not(c) in new_cl:
                    return None
            new_cl = sorted([x for i, x in enumerate(new_cl) if new_cl.index(x) == i], key=lambda x: x.lstrip('~'))
            if ' v '.join(new_cl) not in clauses_set:
                clauses_set.add(' v '.join(new_cl))
                clause_index += 1  # brojač klauzula povećan za 1
                return ' v '.join(new_cl), clause_index, str(c1[1]) + ' + ' + str(c2[1])
    return None


def resolution():
    global clauses, clause_index, clauses_set
    closed = set()
    changed = True
    while changed:
        changed = False
        new = []
        clause_index = clauses[-1][1]
        for combination in combinations(clauses, 2):
            if combination not in closed:
                closed.add(combination)
                res = resolve(combination)
                if res:
                    changed = True
                    new.append(res)
                    if res[0] == '':
                        clauses += new
                        return
        clauses += new


def result(goal_clause, cooking):
    global clauses, original_clauses_index
    if clauses[-1][0] == '':
        queue = deque()
        queue.extend([int(x) for x in clauses[-1][2].split(' + ')])
        requirements = [clauses[-1][1]]
        while queue:
            requirements.append(queue.popleft())
            clause = find_clause_by_number(requirements[-1])
            queue.extend([int(x) for x in clause[2].split(' + ') if x != ''])
        requirements = sorted([x for i, x in enumerate(requirements) if requirements.index(x) == i])
        requirements_dict = {}
        i = 0
        for el in requirements:
            i += 1
            requirements_dict[el] = i

        original_cl = [x for x in requirements if x <= original_clauses_index]
        for num in original_cl:
            print(str(requirements_dict[num]) + '. ' + find_clause_by_number(num)[0])
        print('===============')

        added_cl = [x for x in requirements if x > original_clauses_index]
        for el in added_cl:
            clause = find_clause_by_number(el)
            c = clause[0] if clause[0] != '' else 'NIL'
            a = requirements_dict[int(clause[2].split(' + ')[0])]
            b = requirements_dict[int(clause[2].split(' + ')[1])]
            print(str(requirements_dict[el]) + '. ' + c + ' (' + str(a) + ', ' + str(b) + ')')
        print('===============')
        print('[CONCLUSION]: ' + goal_clause + ' is true')
    else:
        if not cooking:
            for index, el in enumerate(original_clauses):
                print(str(index + 1) + '. ' + el)
            print('===============')
        print('[CONCLUSION]: ' + goal_clause + ' is unknown')


# =============================================== I. DIO - REZOLUCIJA OPOVRGAVANJEM ===============================================

if 'resolution' in args:
    clauses = ss
    goal_clause = clauses.pop()
    clauses += [Not(x) for x in goal_clause.split(' v ')]
    original_clauses = copy.deepcopy(clauses)  # pospremanje za ispis kad je ciljna klauzula unknown

    original_clauses_index = len(clauses)
    for index, el in enumerate(clauses):
        clauses[index] = (clauses[index], index + 1, '')

    clause_index = clauses[-1][1]  # definiranje varijabli koje će se koristiti globalno
    clauses_set = set(el[0] for el in clauses)
    resolution()
    result(goal_clause, False)

# ================================================== II. DIO - KUHARSKI ASISTENT ==================================================

if 'cooking' in args:
    start_clauses = ss
    print('Constructed with knowledge:')
    for c in start_clauses:
        print(c)

    for index, el in enumerate(start_clauses):
        start_clauses[index] = (start_clauses[index], index + 1, '')

    path = 'C:\\Users\\Julijana\\Documents\\uuui\\autograder\\data\\lab2\\files\\' + args[2]

    with open(path, 'r', encoding='utf-8') as f:
        commands = [line.rstrip() for line in f.readlines()]
    commands = [el.lower() for el in commands if '#' not in el]

    for com in commands:
        print("\nUser\'s command:", com)
        if com[-1] == '?':
            clauses = copy.deepcopy(start_clauses)
            for element in [Not(x) for x in com[:-1].strip().split(' v ')]:
                clauses.append((element, clauses[-1][1] + 1, ''))
            original_clauses_index = clauses[-1][1]
            clause_index = clauses[-1][1]
            clauses_set = set(el[0] for el in clauses)
            resolution()
            result(com[:-1].strip(), True)
        if com[-1] == '-':
            start_clauses = [el for el in start_clauses if el[0] != com[:-1].strip()]
            print('Removed', com[:-1].strip())
        if com[-1] == '+':
            if not any(el[0] == com[:-1].strip() for el in start_clauses):
                start_clauses.append((com[:-1].strip(), start_clauses[-1][1] + 1, ''))
                print('Added', com[:-1].strip())

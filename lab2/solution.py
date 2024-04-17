import sys
from itertools import product
from collections import deque
import copy

args = sys.argv[1:]

with open(args[1], 'r', encoding='utf-8') as f:                         # čitanje premisa
    ss = [line.rstrip() for line in f.readlines()]
ss = [el.lower() for el in ss if '#' not in el]


def Not(c):                                                             # funkcija koja vraća negaciju atoma
    if c[0] == '~':
        return c[1:]
    else:
        return '~' + c


def find_clause_by_number(number):                                      # funkcija koja iz liste klauzula vraća tuple klauzulu određenog rednog broja
    global clauses
    c = [x for x in clauses if x[1] == number]
    return c[0] if c else None


def resolve(combination):                                               # funkcija za razrješavanje klauzula
    global clauses, clause_index, clauses_set, removed_clauses, real_start_clauses, combine_with_clauses
    c1, c2 = combination
    for atom in c1[0].split(' v '):
        if Not(atom) in c2[0].split(' v '):
            new_cl = [a for a in c1[0].split(' v ') if a != atom] + [b for b in c2[0].split(' v ') if b != Not(atom)]
            new_cl = set(new_cl)
            for c in new_cl:                                            # uklanjanje valjanih klauzula
                if Not(c) in new_cl:
                    return None
            new_cl = sorted(new_cl, key=lambda x: x.lstrip('~'))
            if ' v '.join(new_cl) != '':                                # uklanjanje redundantnih klauzula (micanje C2 ako je C1 ⊆ C2)
                for cl in clauses:
                    if ' v '.join(list(set(new_cl) & set(cl[0].split(' v ')))) == ' v '.join(new_cl):
                        removed_clauses.add(cl[0])
            if ' v '.join(new_cl) not in clauses_set:
                clauses_set.add(' v '.join(new_cl))
                clause_index += 1                                       # brojač klauzula povećan za 1
                return ' v '.join(new_cl), clause_index, str(c1[1]) + ' + ' + str(c2[1])
    return None


def resolution():                                                       # funkcija rezolucija opovrgavanjem
    global clauses, clause_index, clauses_set, removed_clauses, start_clauses, combine_with_clauses
    closed = set()
    changed = True
    while changed:
        changed = False
        new = []
        clause_index = clauses[-1][1]
        for combination in product(start_clauses, combine_with_clauses):
            if combination not in closed and not (combination[0][0] in removed_clauses or combination[1][0] in removed_clauses):
                closed.add(combination)
                res = resolve(combination)
                if res:
                    changed = True
                    new.append(res)
                    if res[0] == '':
                        clauses += new
                        return
        start_clauses += combine_with_clauses
        combine_with_clauses = copy.deepcopy(new)
        clauses += new


def result(goal_clause, cooking):                                       # funkcija za ispis postupka i rezultata rezolucije
    global clauses, original_clauses_index
    if clauses[-1][0] == '':
        queue = deque()
        queue.extend([int(x) for x in clauses[-1][2].split(' + ')])
        requirements = [clauses[-1][1]]                                 # backtracking i određivanje rednih brojeva "korisnih" klauzula
        while queue:
            requirements.append(queue.popleft())
            clause = find_clause_by_number(requirements[-1])
            queue.extend([int(x) for x in clause[2].split(' + ') if x != ''])
        requirements = sorted([x for i, x in enumerate(requirements) if requirements.index(x) == i])
        requirements_dict = {}                                          # rječnik za mapiranje rednih brojeva korištenih klauzula
        i = 0
        for el in requirements:
            i += 1
            requirements_dict[el] = i

        original_cl = [x for x in requirements if x <= original_clauses_index]      # ispis korištenih početnih klauzula
        for num in original_cl:
            print(str(requirements_dict[num]) + '. ' + find_clause_by_number(num)[0])
        print('===============')

        added_cl = [x for x in requirements if x > original_clauses_index]
        for el in added_cl:                                             # ispis ostalih, izvedenih, klauzula
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

if 'resolution' in args:                                                # zadatak je rezolucija opovrgavanjem
    clauses = ss
    goal_clause = clauses.pop()

    start_clauses = []                                                  # skup početnih premisa (roditeljske klauzule)
    i = 1
    for index, el in enumerate(clauses):
        start_clauses.append((clauses[index], index + 1, ''))
        i += 1

    clauses += [Not(x) for x in goal_clause.split(' v ')]

    combine_with_clauses = []                                           # skup koji je u početku negirani cilj, a kasnije izvedene klauzule
    for x in goal_clause.split(' v '):
        combine_with_clauses.append((Not(x), i, ''))
        i += 1

    original_clauses = copy.deepcopy(clauses)                           # pospremanje za ispis kad je ciljna klauzula unknown

    original_clauses_index = len(clauses)
    for index, el in enumerate(clauses):
        clauses[index] = (clauses[index], index + 1, '')                # klazuzule su spremljene u tuple pa u listu

    clause_index = clauses[-1][1]                                       # definiranje varijabli koje će se koristiti globalno
    clauses_set = set(el[0] for el in clauses)
    removed_clauses = set()
    resolution()
    result(goal_clause, False)


# ================================================== II. DIO - KUHARSKI ASISTENT ==================================================

if 'cooking' in args:                                                   # zadatak je kuharski asistent
    real_start_clauses = ss
    print('Constructed with knowledge:')                                # početni ispis
    for c in real_start_clauses:
        print(c)

    for index, el in enumerate(real_start_clauses):
        real_start_clauses[index] = (real_start_clauses[index], index + 1, '')

    with open(args[2], 'r', encoding='utf-8') as f:
        commands = [line.rstrip() for line in f.readlines()]
    commands = [el.lower() for el in commands if '#' not in el]

    for com in commands:                                                # ispitivanje o kojoj se korisničkoj naredbi radi
        print("\nUser\'s command:", com)
        if com[-1] == '?':                                              # traži se rezolucija opovrgavanjem
            clauses = copy.deepcopy(real_start_clauses)
            start_clauses = copy.deepcopy(real_start_clauses)
            combine_with_clauses = []
            for element in [Not(x) for x in com[:-1].strip().split(' v ')]:
                clauses.append((element, clauses[-1][1] + 1, ''))
                combine_with_clauses.append((element, clauses[-1][1], ''))
            original_clauses_index = clauses[-1][1]
            clause_index = clauses[-1][1]
            clauses_set = set(el[0] for el in clauses)
            removed_clauses = set()
            resolution()
            result(com[:-1].strip(), True)
        if com[-1] == '-':                                              # micanje klauzule iz skupa klauzula
            real_start_clauses = [el for el in real_start_clauses if el[0] != com[:-1].strip()]
            print('Removed', com[:-1].strip())
        if com[-1] == '+':                                              # dodavanje klauzule u skup klauzula
            if not any(el[0] == com[:-1].strip() for el in real_start_clauses):
                real_start_clauses.append((com[:-1].strip(), real_start_clauses[-1][1] + 1, ''))
                print('Added', com[:-1].strip())

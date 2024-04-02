import sys
from collections import deque
from queue import PriorityQueue

args = sys.argv[1:]

path = args[args.index('--ss') + 1]                                     # izdvajanje putanje do opisnika prostora stanja
with open(path, 'r', encoding='utf-8') as f:
    ss = [line.rstrip() for line in f.readlines()]
ss = [el for el in ss if el != '#']                                     # pročitana datoteka s opisnikom stanja (sve osim komentara)


def extract_heuristics(path_heuristics):                                # funkcija za čitanje opisnika heuristike
    with open(path_heuristics, 'r', encoding='utf-8') as f:
        h = [line.rstrip() for line in f.readlines()]
    heuristics = {}
    for el in h:                                                        # zapis heuristike pojedinih stanja u rječnik
        heuristics[el.split(': ')[0]] = float(el.split(': ')[1])
    return heuristics

# funkcija switch preuzeta sa: https://www.javatpoint.com/how-to-swap-two-characters-in-a-string-in-python
def switch(string, i1, i2):                                             # pomoćna funkcija za određivanje sljedećeg stanja za 3x3_puzzle
    char_list = list(string)
    char_list[i1], char_list[i2] = char_list[i2], char_list[i1]
    return "".join(char_list)

def find_neighbours(node):                                              # implicitna funkcija sljedbenika za 3x3_puzzle
    pos = node.index('x')
    neighbours = []
    if pos in [0, 1, 4, 5, 8, 9]:  # desno
        neighbours.append(switch(node, pos, pos + 1))
    if pos in [1, 2, 5, 6, 9, 10]:  # lijevo
        neighbours.append(switch(node, pos, pos - 1))
    if pos in [0, 1, 2, 4, 5, 6]:  # dolje
        neighbours.append(switch(node, pos, pos + 4))
    if pos in [4, 5, 6, 8, 9, 10]:  # gore
        neighbours.append(switch(node, pos, pos - 4))
    return neighbours

# =============================================== I. DIO - ALGORITMI PRETRAŽIVANJA ===============================================

def search_algorithms(alg, start_state, dest_state, heuristic_check):   # zajednička funkcija za sve algoritme pretraživanja
    global graph, heuristics, puzzle

    arr_closed = set()                                                  # definiranje skupova open (queue) i closed
    queue = deque()
    queue.append((start_state, "", 0))
    trail = []                                                          # potrebno za rekonsturiranje puta od početnog do konačnog stanja
    while queue:
        current = queue.popleft()
        node = current[0]
        arr_closed.add(node)
        trail.append(current)
        if node in dest_state:
            if not heuristic_check:
                if alg == 'bfs':
                    print("# BFS\n[FOUND_SOLUTION]: yes")
                if alg == 'ucs':
                    print("# UCS\n[FOUND_SOLUTION]: yes")
                if alg == 'astar':
                    print("# A-STAR " + str(args[args.index('--h') + 1]) + "\n[FOUND_SOLUTION]: yes")
                print('[STATES_VISITED]:', len(arr_closed))
                found_path = [trail[-1][0]]                             # rekonstrukcija puta od početnog do konačnog stanja (backtracking)
                prev = next((t for t in trail if t[0] == found_path[0]), None)[1]
                while prev != "":
                    found_path.insert(0, prev)
                    prev = next((t for t in trail if t[0] == found_path[0]), None)[1]
                print('[PATH_LENGTH]:', len(found_path))
                print("[TOTAL_COST]:", float(trail[-1][2]))
                print("[PATH]: ", end='')
                print(" => ".join(found_path))
                exit(0)
            else:
                return trail[-1][2]                                     # jer funkciju koristimo i u provjeri heuristike (bitna samo udaljenost)
        if alg == 'bfs':                                                # algoritam je BFS
            if puzzle:
                neighbours = find_neighbours(node)
            else:
                neighbours = list(graph[node].keys())
            for n in sorted(neighbours):
                if n not in arr_closed:
                    if not puzzle:
                        queue.append((n, current[0], current[2] + graph[current[0]][n]))
                    else:
                        queue.append((n, current[0], current[2] + 1))
        if alg == 'ucs':                                                # algoritam je UCS
            neighbours = list(graph[node].keys())
            for n in neighbours:
                if n not in arr_closed:
                    queue.append((n, current[0], current[2] + graph[current[0]][n]))
            queue = deque(sorted(queue, key=lambda q: (q[2], q[0])))    # sortiranje prvo po cijeni, a onda abecedno po imenu stanja
        if alg == 'astar':
            neighbours = list(graph[node].keys())
            for n in neighbours:
                if n not in arr_closed:
                    if current[0] == start_state:
                        queue.append((n, current[0], current[2] + graph[current[0]][n] + heuristics[n]))
                    else:
                        to_append = (n, current[0], current[2] + graph[current[0]][n] + heuristics[n] - heuristics[current[0]])
                        dont_add_to_open = [i for i, item in enumerate(queue) if item[0] == n and item[2] < to_append[2]]
                        should_remove_from_open = [i for i, item in enumerate(queue) if item[0] == n and item[2] > to_append[2]]
                        if should_remove_from_open:
                            for i in should_remove_from_open:
                                queue.remove(queue[i])
                        if (not dont_add_to_open) or should_remove_from_open:
                            queue.append(to_append)
                if n in arr_closed:
                    to_append = (n, current[0], current[2] + graph[current[0]][n] + heuristics[n] - heuristics[current[0]])
                    index_remove_closed = [i for i, item in enumerate(trail) if item[0] == n and item[2] > to_append[2]]
                    if index_remove_closed:
                        for i in index_remove_closed:
                            trail.remove(trail[i])
                            arr_closed.remove(trail[i][0])
            queue = deque(sorted(queue, key=lambda q: (q[2], q[0])))


def ucs_3x3(start_state, dest_state):                                   # USC funkcija za 3x3_puzzle (koristi PriorityQueue)
    arr_closed = set()
    queue = PriorityQueue()
    queue.put((0, start_state, ""))
    trail = []
    while queue:
        current = queue.get()
        node = current[1]
        arr_closed.add(node)
        trail.append(current)
        if node in dest_state:
            print("# UCS\n[FOUND_SOLUTION]: yes")
            print('[STATES_VISITED]:', len(arr_closed))
            found_path = [trail[-1][1]]
            prev = next((t for t in trail if t[1] == found_path[0]), None)[2]
            while prev != "":
                found_path.insert(0, prev)
                prev = next((t for t in trail if t[1] == found_path[0]), None)[2]
            print('[PATH_LENGTH]:', len(found_path))
            print("[TOTAL_COST]:", float(trail[-1][0]))
            print("[PATH]: ", end='')
            print(" => ".join(found_path))
            exit(0)
        neighbours = find_neighbours(node)
        for n in neighbours:
            if n not in arr_closed:
                queue.put((1 + current[0], n, node))                    # queue će biti sortiran po cijeni pa abecedno po imenu čvora


if '--alg' in args:                                                     # --alg je u argumentima -> izvođenje nekog algoritma pretraživanja

    start_state = ss[0]                                                 # početno stanje
    dest_state = ss[1].split(' ')                                       # odredišna stanja

    algorithm = args[args.index('--alg') + 1]
    puzzle = args[args.index('--ss') + 1][0:3] == '3x3'                 # bool varijabla koja određuje radi li se o zadatku s 3x3_puzzle

    if algorithm in ['bfs', 'ucs', 'astar']:
        if not puzzle:                                                  # funkciju prijelaza zapisujemo samo ako se ne radi o 3x3_puzzle
            graph = {}                                                  # rječnik za zapis grafa (funkcije prijelaza)
            heuristics = {}
            for el in ss[2:]:
                curr_node = el.split(':')[0]
                graph[curr_node] = {}                                   # ključevi su stanja...
                for e in el.split(':')[1].split(' '):
                    if e != '':
                        graph[curr_node][e.split(',')[0]] = float(e.split(',')[1])      # ..., a vrijednosti susjedi tog stanja

        if '--h' in args:                                               # izdvajanje putanje do opisnika heuristike (ako postoji)
            path_heuristics = args[args.index('--h') + 1]
            heuristics = extract_heuristics(path_heuristics)

        if algorithm != 'ucs' or (algorithm == 'ucs' and not puzzle):   # pozivanje funkcije za algoritme pretraživanja ...
            search_algorithms(algorithm, ss[0].strip() if puzzle else start_state, ss[1].strip() if puzzle else dest_state, False)
        else:
            ucs_3x3(ss[0].strip(), ss[1].strip())                       # ... osim ako se ne radi o UCS i 3x3_puzzle


# =============================================== II. DIO - PROVJERA HEURISTIČKE FUNKCIJE ===============================================

graph = {}                                                              # zapis grafa (stanja i susjeda)
for el in ss[2:]:
    curr_node = el.split(':')[0]
    graph[curr_node] = {}
    for e in el.split(':')[1].split(' '):
        if e != '':
            graph[curr_node][e.split(',')[0]] = float(e.split(',')[1])

if '--h' in args:                                                       # izdvajanje putanje do opisnika heuristike
    path_heuristics = args[args.index('--h') + 1]
    heuristics = extract_heuristics(path_heuristics)

if '--check-consistent' in args:                                        # traži se provjera konzistentnosti
    is_consistent = True

    print('# HEURISTIC-CONSISTENT ' + str(args[args.index('--h') + 1]))

    for state in sorted(heuristics):
        for neighbour in sorted(list(graph[state].keys())):
            if heuristics[state] <= heuristics[neighbour] + graph[state][neighbour]:    # provjera h(s1) ≤ h(s2) + c
                print('[CONDITION]: [OK] ', end='')
            else:
                print('[CONDITION]: [ERR] ', end='')
                is_consistent = False
            print('h(' + state + ') <= h(' + neighbour + ') + c: ' + str(heuristics[state]), end='')
            print(' <= ' + str(heuristics[neighbour]) + ' + ' + str(graph[state][neighbour]))
    print('[CONCLUSION]: Heuristic is ' + ('' if is_consistent else 'not ') + 'consistent.')

if '--check-optimistic' in args:                                        # traži se provjera optimističnosti
    is_optimistic = True

    print('# HEURISTIC-OPTIMISTIC ' + str(args[args.index('--h') + 1]))

    dest_state = ss[1].split(' ')

    for state in sorted(heuristics):
        h_star = search_algorithms('ucs', state, dest_state, True)      # određivanje stvarne udaljenosti od ciljnog stanja
        if heuristics[state] <= h_star:                                 # provjera h(s) ≤ h*(s)
            print('[CONDITION]: [OK] ', end='')
        else:
            print('[CONDITION]: [ERR] ', end='')
            is_optimistic = False
        print('h(' + state + ') <= h*: ' + str(heuristics[state]) + ' <= ' + str(float(h_star)))
    print('[CONCLUSION]: Heuristic is ' + ('' if is_optimistic else 'not ') + 'optimistic.')

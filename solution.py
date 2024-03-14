import sys
from collections import deque

args = sys.argv[1:]

path = 'files/' + args[args.index('--ss') + 1]  # izdvajanje putanje do opisnika prostora stanja
with open(path, 'r', encoding='utf-8') as f:
    ss = [line.rstrip() for line in f.readlines()]
ss = [el for el in ss if el != '#']


def extract_heuristics(path_heuristics):
    with open(path_heuristics, 'r', encoding='utf-8') as f:
        h = [line.rstrip() for line in f.readlines()]
    heuristics = {}
    for el in h:  # zapis heuristike pojedinih stanja u rječnik
        heuristics[el.split(': ')[0]] = float(el.split(': ')[1])
    return heuristics

# funkcija switch preuzeta sa: https://www.javatpoint.com/how-to-swap-two-characters-in-a-string-in-python
def switch(string, i1, i2):
    char_list = list(string)
    char_list[i1], char_list[i2] = char_list[i2], char_list[i1]
    return "".join(char_list)

def find_neighbours(node):
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

def search_algorithms(alg, start_state, dest_state, heuristic_check):
    global graph, heuristics

    arr_closed = set()  # definiranje skupova open i closed
    queue = deque()
    queue.append((start_state, "", 0))
    trail = []
    while queue:
        if len(queue) % 10000 == 0:
            print(len(queue))
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
                found_path = [trail[-1][0]]
                prev = next((t for t in trail if t[0] == found_path[0]), None)[1]
                while prev != "":
                    found_path.insert(0, prev)
                    prev = next((t for t in trail if t[0] == found_path[0]), None)[1]
                print('[PATH_LENGTH]:', len(found_path))
                if algorithm in ['bfs', 'ucs', 'astar']:
                    print("[TOTAL_COST]:", trail[-1][2])
                print("[PATH]: ", end='')
                print(" => ".join(found_path))
                exit(0)
            else:
                return trail[-1][2]
        if alg == 'bfs':
            if path[0:2] == '3x3':
                neighbours = find_neighbours(node)
            else:
                neighbours = list(graph[node].keys())
            for n in sorted(neighbours):
                if n not in arr_closed:
                    queue.append((n, current[0], current[2] + graph[current[0]][n]))
        if alg == 'ucs':
            if path[0:2] == '3x3':
                neighbours = find_neighbours(node)
            else:
                neighbours = list(graph[node].keys())
            for n in neighbours:
                if n not in arr_closed:
                    queue.append((n, current[0], current[2] + graph[current[0]][n]))
            queue = deque(sorted(queue, key=lambda q: (q[2], q[0])))
        if alg == 'astar':
            neighbours = list(graph[node].keys())
            for n in neighbours:
                if n not in arr_closed:
                    if current[0] == start_state:
                        queue.append((n, current[0], current[2] + graph[current[0]][n] + heuristics[n]))
                    else:
                        queue.append(
                            (n, current[0], current[2] + graph[current[0]][n] + heuristics[n] - heuristics[current[0]]))
            queue = deque(sorted(queue, key=lambda q: (q[2], q[0])))
        if len(arr_closed) % 10000 == 0:
            print(len(arr_closed))


if '--alg' in args:

    start_state = ss[0]  # početno stanje
    dest_state = ss[1].split(' ')  # odredišna stanja

    algorithm = args[args.index('--alg') + 1]

    if algorithm in ['bfs', 'ucs', 'astar']:
        graph = {}  # rječnik za zapis grafa
        heuristics = {}
        for el in ss[2:]:
            curr_node = el.split(':')[0]
            graph[curr_node] = {}  # ključevi su stanja...
            for e in el.split(':')[1].split(' '):
                if e != '':
                    graph[curr_node][e.split(',')[0]] = float(e.split(',')[1])  # ..., a vrijednosti susjedi tog stanja

        if '--h' in args:  # izdvajanje putanje do opisnika heuristike
            path_heuristics = 'files/' + args[args.index('--h') + 1]
            heuristics = extract_heuristics(path_heuristics)

        search_algorithms(algorithm, ss[0].strip() if path[0:2] == '3x3' else start_state, ss[1].strip() if path[0:2] == '3x3' else dest_state, False)

# =============================================== II. DIO - PROVJERA HEURISTIČKE FUNKCIJE ===============================================

graph = {}  # zapis grafa (stanja i susjeda)
for el in ss[2:]:
    curr_node = el.split(':')[0]
    graph[curr_node] = {}
    for e in el.split(':')[1].split(' '):
        if e != '':
            graph[curr_node][e.split(',')[0]] = float(e.split(',')[1])

if '--h' in args:  # izdvajanje putanje do opisnika heuristike
    path_heuristics = 'files/' + args[args.index('--h') + 1]
    heuristics = extract_heuristics(path_heuristics)

if '--check-consistent' in args:  # traži se provjera konzistentnosti
    is_consistent = True

    print('# HEURISTIC-CONSISTENT ' + str(args[args.index('--h') + 1]))

    for state in sorted(heuristics):
        for neighbour in sorted(list(graph[state].keys())):
            if heuristics[state] <= heuristics[neighbour] + graph[state][neighbour]:
                print('[CONDITION]: [OK] ', end='')
            else:
                print('[CONDITION]: [ERR] ', end='')
                is_consistent = False
            print('h(' + state + ') <= h(' + neighbour + ') + c: ' + str(heuristics[state]), end='')
            print(' <= ' + str(heuristics[neighbour]) + ' + ' + str(graph[state][neighbour]))
    print('[CONCLUSION]: Heuristic is ' + ('' if is_consistent else 'not ') + 'consistent.')

if '--check-optimistic' in args:
    is_optimistic = True

    print('# HEURISTIC-OPTIMISTIC ' + str(args[args.index('--h') + 1]))

    dest_state = ss[1].split(' ')

    for state in sorted(heuristics):
        h_star = search_algorithms('ucs', state, dest_state, True)
        if heuristics[state] <= h_star:
            print('[CONDITION]: [OK] ', end='')
        else:
            print('[CONDITION]: [ERR] ', end='')
            is_optimistic = False
        print('h(' + state + ') <= h*: ' + str(heuristics[state]) + ' <= ' + str(float(h_star)))
    print('[CONCLUSION]: Heuristic is ' + ('' if is_optimistic else 'not ') + 'optimistic.')

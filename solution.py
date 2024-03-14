import sys
from collections import deque

args = sys.argv[1:]

path = 'files/' + args[args.index('--ss') + 1]  # izdvajanje putanje do opisnika prostora stanja
with open(path, 'r', encoding='utf-8') as f:
    ss = [line.rstrip() for line in f.readlines()]
ss = [el for el in ss if el != '#']

start_state = ss[0]                             # početno stanje
dest_state = ss[1].split(' ')                   # odredišna stanja

algorithm = args[args.index('--alg') + 1]

if algorithm in ['bfs', 'ucs', 'astar']:
    graph = {}      # rječnik za zapis grafa
    for el in ss[2:]:
        curr_node = el.split(':')[0]
        graph[curr_node] = {}
        for e in el.split(':')[1].split(' '):
            if e != '':
                graph[curr_node][e.split(',')[0]] = float(e.split(',')[1])

if '--h' in args:
    path_heuristics = 'files/' + args[args.index('--h') + 1]
    with open(path_heuristics, 'r', encoding='utf-8') as f:
        h = [line.rstrip() for line in f.readlines()]
    heuristics = {}
    for el in h:
        heuristics[el.split(': ')[0]] = float(el.split(': ')[1])

arr_closed = []
queue = deque()
queue.append((start_state, "", 0))
trail = []
while queue:
    current = queue.popleft()
    node = current[0]
    arr_closed.append(node)
    trail.append(current)
    if node in dest_state:
        if algorithm == 'bfs':
            print("# BFS\n[FOUND_SOLUTION]: yes")
        if algorithm == 'ucs':
            print("# UCS\n[FOUND_SOLUTION]: yes")
        if algorithm == 'astar':
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
    if algorithm == 'bfs':
        neighbours = list(graph[node].keys())
        for n in sorted(neighbours):
            if n not in arr_closed:
                queue.append((n, current[0], current[2] + graph[current[0]][n]))
    if algorithm == 'ucs':
        neighbours = list(graph[node].keys())
        for n in neighbours:
            if n not in arr_closed:
                queue.append((n, current[0], current[2] + graph[current[0]][n]))
        queue = deque(sorted(queue, key=lambda q: (q[2], q[0])))
    if algorithm == 'astar':
        neighbours = list(graph[node].keys())
        for n in neighbours:
            if n not in arr_closed:
                #queue.append((n, current[0], current[2] + graph[current[0]][n] + heuristics[n]))
                if current[0] == start_state:
                    queue.append((n, current[0], current[2] + graph[current[0]][n] + heuristics[n]))
                else:
                    queue.append((n, current[0], current[2] + graph[current[0]][n] + heuristics[n] - heuristics[current[0]]))
        queue = deque(sorted(queue, key=lambda q: (q[2], q[0])))


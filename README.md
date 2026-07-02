*This project has been created as part of the 42 curriculum by* **MAGRAM**.

# FLY-IN — Drone Simulation System

---

## Description

FLY-IN is a drone simulation system that models the movement of multiple drones through a weighted zone graph from a start hub to an end hub.

The goal is to route all drones from the start zone to the end zone in the minimum number of turns, respecting zone capacities, connection capacities, and zone type constraints (normal, priority, restricted, blocked).

### Overview

The project is structured as a multi-stage pipeline:

```
Input file
    ↓
Read_file       — reads and validates raw file structure
    ↓
RegEx_line      — parses and validates each line with regex
    ↓
Json_file       — builds the graph + runs reverse Dijkstra
    ↓
Simulation      — runs turn-based drone movement
    ↓
Terminal output — turn-by-turn drone positions
```

### Zone types

| Zone | Movement cost | Effect |
|---|---|---|
| `normal` | 1 | standard movement |
| `priority` | 1 | drones prefer these |
| `restricted` | 2 | costs extra turn to cross |
| `blocked` | 151 | effectively impassable |

---

## Algorithm Choices and Implementation Strategy

### Reverse Dijkstra — Gradient Field

Instead of running Dijkstra per drone per turn, FLY-IN runs **one reverse Dijkstra from the goal** before the simulation starts. This builds a gradient field — every zone knows its cost to reach the goal.

```
goal:  0
A:     1   (priority zone)
B:     3   (restricted zone)
start: 4   (normal + A cost)
```

Drones then follow the gradient downhill each turn — no pathfinding per drone needed. This is O(n log n) once vs O(n log n × drones × turns).

### Priority Queue (Min Heap)

Dijkstra uses Python's `heapq` — a min heap that always pops the lowest cost zone next. This guarantees the shortest path is found first without revisiting zones.

```python
heapq.heappush(heap, (cost, zone))
current_cost, current = heapq.heappop(heap)  # always minimum
```

### Turn-based Simulation

Each turn:
1. Every drone checks its gradient — finds the lowest cost neighbor
2. Skips full zones (`holde >= max_drones`)
3. Skips saturated connections (`holde >= capacity`)
4. Restricted zones add 1 extra wait turn
5. Connection `holde` resets after each turn (flow model)
6. Simulation ends when all drones reach goal

### Parser Pipeline

- `Read_file` — validates file structure (sections, keywords, comments)
- `RegEx_line` — validates each line format with named capture groups
- `Json_file` — assembles adjacency list graph with per-zone and per-edge state

### Visual Representation

The simulation outputs a turn-by-turn terminal trace showing each drone's movement:

```
Turn 1:   D1-d   D2-start-a   D3-d   D4-start-a
Turn 2:   D1-d-f   D2-a   D3-d-f   D4-a   D5-d   D6-d
Turn 3:   D1-f   D2-b   D3-f   D4-b   D5-d-f
Turn 4:   D1-f-e   D2-b-f   D3-f-e   D5-f   D6-d-f
Turn 5:   D1-e   D2-f   D3-e   D6-f
Turn 6:   D1-goal   D2-f-e   D4-b-f
Turn 7:   D2-e   D3-goal   D4-f   D5-f-e
Turn 8:   D2-goal   D4-f-e   D5-e
Turn 9:   D4-e   D5-goal   D6-f-e
Turn 10:   D4-goal   D6-e
Turn 11:   D6-goal

Total turns: 11
```

Each line shows: turn number + drone ID + destination zone. This lets the user trace every drone's path through the graph and verify routing decisions, capacity constraints, and zone interactions at each step.

---

## Instructions

### Requirements

- Python 3.11+
- `flake8`
- `mypy`

### Installation

```bash
# clone the project
git clone <repo_url>
cd FLY-IN

# create and activate virtual environment
python3 -m venv fly_env
source fly_env/bin/activate

# install dependencies
make install
```

### Running

```bash
# run simulation (uses test.txt by default)
make run

# or directly
python3 route_all.py <map.txt>
```

### Debug

```bash
make debug
```

### Lint

```bash
# mandatory flags
make lint

```

### Clean

```bash
make clean
```

### Input file format

Example input 
```
nb_drones: 6

start_hub: start 0 0 [color=green max_drones=6]
hub: a 1 0 [zone=restricted color=orange max_drones=2]
hub: b 2 0 [color=orange max_drones=2]
hub: c 2 1 [color=orange max_drones=1 zone=blocked]
hub: d 1 1 [color=orange max_drones=2]
hub: f 3 0 [zone=restricted color=blue max_drones=3]
hub: e 4 0 [zone=restricted color=Purple  max_drones=2]
end_hub: goal 5 0 [color=red max_drones=3]

connection: start-a [max_link_capacity=2]
connection: start-d [max_link_capacity=3]

connection: a-b [max_link_capacity=2]
connection: a-c [max_link_capacity=2]
connection: d-f [max_link_capacity=2]
connection: e-f [max_link_capacity=2]
connection: b-f [max_link_capacity=1]
connection: c-e [max_link_capacity=2]
connection: c-d [max_link_capacity=2]
connection: e-goal
```

**Sections must appear in this order:**
1. `nb_drones` — first non-comment line
2. `start_hub` — exactly one
3. `end_hub` — exactly one
4. `hub` — zero or more
5. `connection` — one or more

---

## Resources

### Documentation

- [Python `re` module](https://docs.python.org/3/library/re.html) — regex engine used for parsing
- [Python `heapq` module](https://docs.python.org/3/library/heapq.html) — min heap for Dijkstra
- [mypy documentation](https://mypy.readthedocs.io/en/stable/) — static type checking
- [flake8 documentation](https://flake8.pycqa.org/en/latest/) — linting

### Articles

- [Dijkstra's algorithm — Wikipedia](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Adjacency list — Wikipedia](https://en.wikipedia.org/wiki/Adjacency_list)
- [Graph theory — Wikipedia](https://en.wikipedia.org/wiki/Graph_theory)
- [Priority queue — Wikipedia](https://en.wikipedia.org/wiki/Priority_queue)

### AI Usage

ai was used for the following tasks:

| Task | Parts of project |
|---|---|
| Type hint fixes | `Read_file.py`, `RegEx_line.py`, `Json_file.py`, `Simulation.py` |
| mypy and flake8 compliance | all `.py` files |
| Test pipeline setup | `Makefile`, `test_parser.sh`, `tests/` |

AI was used as a learning and debugging tool — all logic, algorithm choices, and architecture decisions were made by the me.
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
| `normal` | 2 | standard movement |
| `priority` | 1 | drones prefer these |
| `restricted` | 3 | costs extra turn to cross |
| `blocked` | 151 | effectively impassable |

---

## Algorithm Choices and Implementation Strategy

### Reverse Dijkstra — Gradient Field

Instead of running Dijkstra per drone per turn, FLY-IN runs **one reverse Dijkstra from the goal** before the simulation starts. This builds a gradient field — every zone knows its cost to reach the goal.

```
goal:  0
A:     1   (priority zone)
B:     3   (restricted zone)
start: 3   (normal + A cost)
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
Turn 1:   D1-junction   D2-junction
Turn 2:   D1-correct_path   D3-junction
Turn 3:   D1-intermediate   D2-correct_path   D4-junction
Turn 4:   D1-goal   D2-intermediate   D3-correct_path   D5-junction
Turn 5:   D2-goal   D3-intermediate   D4-correct_path
Turn 6:   D3-goal   D4-intermediate   D5-correct_path
Turn 7:   D4-goal   D5-intermediate
Turn 8:   D5-goal

Total turns: 8
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
python3 step_one.py
```

### Debug

```bash
make debug
```

### Lint

```bash
# mandatory flags
make lint

# strict mode
make lint-strict
```

### Clean

```bash
make clean
```

### Input file format

```
# comment
nb_drones: 5

start_hub: name x y [color=green max_drones=N]
hub: name x y [zone=priority color=blue max_drones=N]
end_hub: name x y [color=green max_drones=N]

connection: from-to [max_link_capacity=N]
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

Claude (Anthropic) was used for the following tasks:

| Task | Parts of project |
|---|---|
| Type hint fixes | `Read_file.py`, `RegEx_line.py`, `Json_file.py`, `simulation.py` |
| mypy and flake8 compliance | all `.py` files |
| Test pipeline setup | `Makefile`, `test_parser.sh`, `tests/` |
| Concept explanations | Dijkstra, heapq, regex, OOP, namespaces, LEGB |
| Makefile rules | `install`, `run`, `debug`, `lint`, `clean` |

AI was used as a learning and debugging tool — all logic, algorithm choices, and architecture decisions were made by the developer.
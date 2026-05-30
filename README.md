# Maze Generator + Solver Visualizer

A terminal app that generates random mazes and solves them with real-time animation.

```
python3 maze.py
```

## What it does

1. **Generates** a perfect maze (every cell reachable, exactly one path between any two cells) using recursive-backtracker DFS.
2. **Solves** it with your choice of algorithm, animated cell-by-cell so you can watch the search unfold.

## Controls

| Key | Action |
|-----|--------|
| `b` | Solve with **BFS** (breadth-first — shortest path guaranteed) |
| `d` | Solve with **DFS** (depth-first — fast but not shortest) |
| `a` | Solve with **A\*** (heuristic-guided — efficient shortest path) |
| `n` | Generate a **new maze** |
| `q` | Quit |

## Colour legend

| Colour | Meaning |
|--------|---------|
| Green  | Start cell |
| Red    | End cell |
| Blue   | Visited (BFS / A*) |
| Yellow | Frontier (DFS) |
| Magenta | Final solution path |

## Requirements

Python 3.10+ (uses `list[list[int]]` type hints). The `curses` module is part of the standard library — no extra installs needed.

Resize your terminal before starting for a bigger maze. The maze auto-fits to the window size.

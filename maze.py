#!/usr/bin/env python3
"""
Maze Generator + Solver Visualizer
----------------------------------
Generates a random maze using recursive backtracking (DFS), then solves it
with your choice of BFS, DFS, or A* — animated in real-time.

Controls:
  b  — solve with BFS
  d  — solve with DFS
  a  — solve with A*
  n  — generate new maze
  q  — quit
"""

import curses
import random
import time
import heapq
from collections import deque

# ── Maze cell flags ──────────────────────────────────────────────────────────
N, S, E, W = 1, 2, 4, 8
OPPOSITE = {N: S, S: N, E: W, W: E}
DX = {E: 1, W: -1, N: 0, S: 0}
DY = {N: -1, S: 1, E: 0, W: 0}

# ── Curses colour pair IDs ───────────────────────────────────────────────────
C_WALL      = 1
C_PASSAGE   = 2
C_START     = 3
C_END       = 4
C_FRONTIER  = 5
C_VISITED   = 6
C_PATH      = 7
C_TITLE     = 8


def generate_maze(rows: int, cols: int) -> list[list[int]]:
    """Recursive-backtracker DFS; returns a grid of open-wall bitmasks."""
    grid = [[0] * cols for _ in range(rows)]
    visited = [[False] * cols for _ in range(rows)]

    def carve(r: int, c: int) -> None:
        visited[r][c] = True
        directions = [N, S, E, W]
        random.shuffle(directions)
        for d in directions:
            nr, nc = r + DY[d], c + DX[d]
            if 0 <= nr < rows and 0 <= nc < cols and not visited[nr][nc]:
                grid[r][c] |= d
                grid[nr][nc] |= OPPOSITE[d]
                carve(nr, nc)

    carve(0, 0)
    return grid


# ── Rendering helpers ─────────────────────────────────────────────────────────

def draw_maze(win, grid: list[list[int]], rows: int, cols: int,
              cell_w: int = 3, cell_h: int = 1) -> None:
    """Draw the static maze walls (passage tiles) using block characters."""
    win.erase()
    for r in range(rows):
        for c in range(cols):
            # top-left corner of this cell in screen coords
            sy = r * (cell_h + 1) + 1          # +1 for title row
            sx = c * (cell_w + 1)

            # passage interior
            win.addstr(sy, sx + 1, " " * cell_w, curses.color_pair(C_PASSAGE))

            # south wall
            if not (grid[r][c] & S) and r < rows - 1:
                win.addstr(sy + 1, sx, "+" + "─" * cell_w, curses.color_pair(C_WALL))
            else:
                win.addstr(sy + 1, sx, "+" + " " * cell_w, curses.color_pair(C_WALL))

            # east wall
            if not (grid[r][c] & E) and c < cols - 1:
                win.addstr(sy, sx + cell_w + 1, "│", curses.color_pair(C_WALL))
            else:
                win.addstr(sy, sx + cell_w + 1, " ", curses.color_pair(C_WALL))

            # left-most border column
            if c == 0:
                win.addstr(sy, sx, "│", curses.color_pair(C_WALL))

        # top row border
        win.addstr(1, 0,
                   "+" + ("─" * cell_w + "+") * cols,
                   curses.color_pair(C_WALL))

    # mark start & end
    def cell_pos(r: int, c: int):
        return r * (cell_h + 1) + 1, c * (cell_w + 1) + 1

    sr, sc = cell_pos(0, 0)
    er, ec = cell_pos(rows - 1, cols - 1)
    win.addstr(sr, sc, " S ", curses.color_pair(C_START))
    win.addstr(er, ec, " E ", curses.color_pair(C_END))
    win.refresh()


def colour_cell(win, r: int, c: int, label: str, pair: int,
                cell_w: int = 3) -> None:
    sy = r * 2 + 1
    sx = c * (cell_w + 1) + 1
    text = label.center(cell_w)[:cell_w]
    try:
        win.addstr(sy, sx, text, curses.color_pair(pair))
        win.refresh()
    except curses.error:
        pass


# ── Solvers ───────────────────────────────────────────────────────────────────

def bfs(grid, rows, cols, win, speed):
    start, end = (0, 0), (rows - 1, cols - 1)
    queue = deque([(start, [start])])
    visited = {start}
    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path
        for d in [N, S, E, W]:
            if grid[r][c] & d:
                nr, nc = r + DY[d], c + DX[d]
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    colour_cell(win, nr, nc, "·", C_VISITED)
                    time.sleep(speed)
                    queue.append(((nr, nc), path + [(nr, nc)]))
    return []


def dfs(grid, rows, cols, win, speed):
    start, end = (0, 0), (rows - 1, cols - 1)
    stack = [(start, [start])]
    visited = {start}
    while stack:
        (r, c), path = stack.pop()
        if (r, c) == end:
            return path
        for d in [N, S, E, W]:
            if grid[r][c] & d:
                nr, nc = r + DY[d], c + DX[d]
                if (nr, nc) not in visited:
                    visited.add((nr, nc))
                    colour_cell(win, nr, nc, "·", C_FRONTIER)
                    time.sleep(speed)
                    stack.append(((nr, nc), path + [(nr, nc)]))
    return []


def astar(grid, rows, cols, win, speed):
    start, end = (0, 0), (rows - 1, cols - 1)

    def h(r, c):
        return abs(r - end[0]) + abs(c - end[1])

    heap = [(h(*start), 0, start, [start])]
    visited = {}
    while heap:
        _, g, (r, c), path = heapq.heappop(heap)
        if (r, c) in visited:
            continue
        visited[(r, c)] = True
        if (r, c) == end:
            return path
        for d in [N, S, E, W]:
            if grid[r][c] & d:
                nr, nc = r + DY[d], c + DX[d]
                if (nr, nc) not in visited:
                    ng = g + 1
                    colour_cell(win, nr, nc, "·", C_VISITED)
                    time.sleep(speed)
                    heapq.heappush(heap, (ng + h(nr, nc), ng, (nr, nc),
                                         path + [(nr, nc)]))
    return []


# ── Main loop ─────────────────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(C_WALL,     curses.COLOR_CYAN,    -1)
    curses.init_pair(C_PASSAGE,  -1,                   -1)
    curses.init_pair(C_START,    curses.COLOR_BLACK,   curses.COLOR_GREEN)
    curses.init_pair(C_END,      curses.COLOR_BLACK,   curses.COLOR_RED)
    curses.init_pair(C_FRONTIER, curses.COLOR_BLACK,   curses.COLOR_YELLOW)
    curses.init_pair(C_VISITED,  curses.COLOR_BLACK,   curses.COLOR_BLUE)
    curses.init_pair(C_PATH,     curses.COLOR_BLACK,   curses.COLOR_MAGENTA)
    curses.init_pair(C_TITLE,    curses.COLOR_YELLOW,  -1)

    CELL_W = 3

    def fit_maze(rows_hint=None, cols_hint=None):
        sh, sw = stdscr.getmaxyx()
        # each row takes 2 screen rows (+1 top border); each col takes CELL_W+1 cols
        max_rows = (sh - 3) // 2
        max_cols = (sw - 1) // (CELL_W + 1)
        rows = min(rows_hint or max_rows, max_rows)
        cols = min(cols_hint or max_cols, max_cols)
        rows = max(rows, 3)
        cols = max(cols, 3)
        return rows, cols

    SPEED = 0.012          # seconds between animation frames
    SOLVERS = {"b": ("BFS",  bfs),
               "d": ("DFS",  dfs),
               "a": ("A*",   astar)}

    rows, cols = fit_maze()
    grid = generate_maze(rows, cols)
    draw_maze(stdscr, grid, rows, cols)

    def status(msg: str, attr=0):
        sh, sw = stdscr.getmaxyx()
        bar = msg.ljust(sw - 1)[:sw - 1]
        try:
            stdscr.addstr(0, 0, bar, curses.color_pair(C_TITLE) | attr)
            stdscr.refresh()
        except curses.error:
            pass

    status("  MAZE  │ b=BFS  d=DFS  a=A*  n=new maze  q=quit")

    stdscr.nodelay(True)
    stdscr.timeout(50)

    solving = False

    while True:
        key = stdscr.getch()
        if key == ord("q"):
            break

        elif key == ord("n"):
            rows, cols = fit_maze()
            grid = generate_maze(rows, cols)
            draw_maze(stdscr, grid, rows, cols)
            status("  MAZE  │ b=BFS  d=DFS  a=A*  n=new maze  q=quit")

        elif key in (ord("b"), ord("d"), ord("a")) and not solving:
            algo_name, solver_fn = SOLVERS[chr(key)]
            status(f"  Solving with {algo_name}…  (n=new  q=quit)")
            solving = True
            curses.flushinp()

            path = solver_fn(grid, rows, cols, stdscr, SPEED)

            # draw solution path
            for r, c in path:
                if (r, c) not in ((0, 0), (rows - 1, cols - 1)):
                    colour_cell(stdscr, r, c, "★", C_PATH)
                    time.sleep(SPEED * 2)

            steps = len(path) - 1
            colour_cell(stdscr, 0, 0, " S ", C_START)
            colour_cell(stdscr, rows - 1, cols - 1, " E ", C_END)

            status(f"  {algo_name}: {steps} steps │ n=new maze  q=quit")
            solving = False


if __name__ == "__main__":
    curses.wrapper(main)

import random
from typing import List
from mazegenerator import MazeGenerator # type: ignore

EAST = 2
SOUTH = 4

def maze_printer(maze: List[List[int]]):
    for row in maze:
        print(row)

def maze_generator():
    amazing_maze = MazeGenerator()
    rows = len(amazing_maze.maze)
    cols = len(amazing_maze.maze[0])
    
    forty_two = [
        [1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1]
    ]
    
    is_42_cell = set()

    vis_rows = rows * 2 + 1
    vis_cols = cols * 2 + 1

    vis_map: List[List[int]] = [[1 for _ in range(vis_cols)] for _ in range(vis_rows)]

    if len(forty_two) * 2 <= rows and len(forty_two[0]) * 2 <= cols:
        posy = int((rows - len(forty_two)) / 2)
        posx = int((cols - len(forty_two[0])) / 2)
        for y in range(len(forty_two)):
            for x in range(len(forty_two[0])):
                if forty_two[y][x] == 1:
                    is_42_cell.add((posx + x, posy + y))
                    
    valid_paths = []

    for r in range(rows):
        for c in range(cols):
            vr = r * 2 + 1
            vc = c * 2 + 1

            if (c, r) in is_42_cell:
                vis_map[vr][vc] = 5
            else:
                vis_map[vr][vc] = 10
                valid_paths.append((vr, vc))

            if not (amazing_maze.maze[r][c] & EAST):
                vis_map[vr][vc + 1] = 10
                valid_paths.append((vr, vc + 1))

            if not (amazing_maze.maze[r][c] & SOUTH):
                vis_map[vr + 1][vc] = 10
                valid_paths.append((vr + 1, vc))

    power_pellets = random.sample(valid_paths, 4)
    for pr, pc in power_pellets:
        vis_map[pr][pc] = 50

    print("Original Maze")
    maze_printer(amazing_maze.maze)
    print("Maze Wrapper")
    maze_printer(vis_map)
    
    return vis_map
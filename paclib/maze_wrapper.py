from mazegenerator import MazeGenerator # type: ignore
from typing import List


EAST = 2
SOUTH = 4

def maze_generator():
    amazing_maze = MazeGenerator()
    rows = len(amazing_maze.maze)
    cols = len(amazing_maze.maze[0])

    vis_rows = rows * 2 + 1
    vis_cols = cols * 2 + 1

    vis_map: List[List[int]] = [[10 for _ in range(vis_cols)] for _ in range(vis_rows)]

    for r in range(rows):
        for c in range(cols):
            vr = r * 2 + 1
            vc = c * 2 + 1

            vis_map[vr][vc] = 1

            if not (amazing_maze.maze[r][c] & EAST):
                vis_map[vr][vc + 1] = 1
            if not (amazing_maze.maze[r][c] & SOUTH):
                vis_map[vr + 1][vc] = 1
    vis_map[1][1] = 50
    vis_map[1][vis_cols - 2] = 50
    vis_map[vis_rows - 2][1] = 50
    vis_map[vis_rows - 2][vis_cols - 2] = 50
    print("Original Maze")
    print(amazing_maze.maze)
    print("Maze Wrapper")
    print(vis_map)
    return vis_map
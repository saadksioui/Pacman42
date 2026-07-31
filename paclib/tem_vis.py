import pyray as pr
from typing import List, Tuple, Dict

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8

def run_visualizer(grid: List[List[int]],
                   entry_coor: Tuple[int, int],
                   exit_coor: Tuple[int, int],
                   cell_size: int = 20) -> None:
    """
    Renders the bitwise maze grid in a Pyray GUI window.
    Uses double resolution to give walls physical thickness.
    """
    rows = len(grid)
    cols = len(grid[0])

    vis_rows = rows * 2 + 1
    vis_cols = cols * 2 + 1

    # 1. THE ADAPTER PHASE: Translate bitwise logic to a 2D rendering matrix
    # 0 = Wall, 1 = Empty, 2 = Mask, 3 = Path, 4 = Entry, 5 = Exit
    vis_map: List[List[int]] = [[0 for _ in range(vis_cols)] for _ in range(vis_rows)]

    for r in range(rows):
        for c in range(cols):
            vr = r * 2 + 1
            vc = c * 2 + 1

            vis_map[vr][vc] = 1  # Base empty cell

            # Check binary flags to carve out the corridors
            if not (grid[r][c] & EAST):
                vis_map[vr][vc + 1] = 1
            if not (grid[r][c] & SOUTH):
                vis_map[vr + 1][vc] = 1

    # Mark Entry and Exit
    ex, ey = entry_coor
    vis_map[ey * 2 + 1][ex * 2 + 1] = 4
    
    out_x, out_y = exit_coor
    vis_map[out_y * 2 + 1][out_x * 2 + 1] = 5

    # 2. THE RENDER PHASE: Draw the translated matrix to the screen
    screen_width = vis_cols * cell_size
    screen_height = vis_rows * cell_size

    pr.init_window(screen_width, screen_height, "PacMan")
    pr.set_target_fps(60)

    # Map our integer matrix values to Raylib colors
    colors: Dict[int, pr.Color] = {
        0: pr.RAYWHITE,    # Walls
        1: pr.BLACK,       # Empty Corridors
        2: pr.DARKGRAY,    # Masked
        5: pr.RED          # Exit
    }

    while not pr.window_should_close():
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        for r in range(vis_rows):
            for c in range(vis_cols):
                cell_type = vis_map[r][c]
                color = colors.get(cell_type, pr.BLACK)
                
                # Draw the cell
                pr.draw_rectangle(
                    c * cell_size, 
                    r * cell_size, 
                    cell_size, 
                    cell_size,
                    color
                )
                
                # Draw text identifiers for Entry/Exit instead of Emojis
                if cell_type == 4:
                    pr.draw_text("😃", c * cell_size + (cell_size // 3), r * cell_size + (cell_size // 6), cell_size - 4, pr.WHITE)

        pr.end_drawing()

    pr.close_window()
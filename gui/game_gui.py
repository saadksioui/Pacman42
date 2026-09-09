import pyray as rl
from gui import SCREEN_HEIGHT, SCREEN_WIDTH
from mazegenerator import MazeGenerator


WALL_THICKNESS: float = 2.0
MAZE_PADDING: int = 100

class MazeRender:
    maze: list[list[int]]
    maze_height: int
    maze_width: int

    wall_length: int


    def __init__(self, maze: list[list[int]]) -> None:
        self.maze = maze
        self.maze_height = len(self.maze)
        self.maze_width = len(self.maze[0])
        self.wall_length = self._get_wall_length()
        self.start_x: int = SCREEN_WIDTH // 2 - (self.maze_width * self.wall_length) // 2
        self.start_y: int = SCREEN_HEIGHT // 2 - (self.maze_height * self.wall_length) // 2


    def _get_wall_length(self) -> int:
        if self.maze_height > self.maze_width:
            return (SCREEN_HEIGHT - MAZE_PADDING * 2) // self.maze_height
        elif self.maze_width > self.maze_height:
            return (SCREEN_WIDTH - MAZE_PADDING * 2) // self.maze_width
        else:
            return min(SCREEN_HEIGHT - MAZE_PADDING * 2, SCREEN_WIDTH) // self.maze_height


    def draw(self) -> None:
        for i, row in enumerate(self.maze):
            for j, cell in enumerate(row):
                topleft_corner = rl.Vector2(
                    self.start_x + j * self.wall_length,
                    self.start_y + i * self.wall_length
                )
                topright_corner = rl.Vector2(
                    topleft_corner.x + self.wall_length,
                    topleft_corner.y
                )
                bottomleft_corner = rl.Vector2(
                    topleft_corner.x,
                    topleft_corner.y + self.wall_length
                )
                bottomright_corner = rl.Vector2(
                    topleft_corner.x + self.wall_length,
                    topleft_corner.y + self.wall_length
                )
                # north wall
                if cell & 0b1:
                    rl.draw_line_ex(
                        topleft_corner,
                        topright_corner,
                        WALL_THICKNESS, rl.GREEN
                    )
                    rl.draw_circle_v(topleft_corner, WALL_THICKNESS / 2, rl.WHITE)
                    rl.draw_circle_v(topright_corner, WALL_THICKNESS / 2, rl.WHITE)
                # west wall
                if cell & 0b1000:
                    rl.draw_line_ex(
                        topleft_corner,
                        bottomleft_corner,
                        WALL_THICKNESS, rl.BLUE
                    )
                    rl.draw_circle_v(topleft_corner, WALL_THICKNESS / 2, rl.WHITE)
                    rl.draw_circle_v(bottomleft_corner, WALL_THICKNESS / 2, rl.WHITE)
                # south side
                if i == self.maze_height - 1:
                    rl.draw_line_ex(
                        bottomleft_corner,
                        bottomright_corner,
                        WALL_THICKNESS, rl.BLUE
                    )
                    rl.draw_circle_v(bottomright_corner, WALL_THICKNESS / 2, rl.WHITE)
                    rl.draw_circle_v(bottomleft_corner, WALL_THICKNESS / 2, rl.WHITE)
                # east side
                if j == self.maze_width - 1:
                    rl.draw_line_ex(
                        topright_corner,
                        bottomright_corner,
                        WALL_THICKNESS, rl.BLUE
                    )
                    rl.draw_circle_v(bottomright_corner, WALL_THICKNESS / 2, rl.WHITE)
                if cell == 0xf:
                    rl.draw_rectangle(
                        int(topleft_corner.x),
                        int(topleft_corner.y),
                        l := self.wall_length,
                        l,
                        rl.RED
                    )






m = MazeRender(MazeGenerator(size=(40, 40)).maze)
m = MazeRender(MazeGenerator().maze)
while not rl.window_should_close():
    rl.begin_drawing()
    rl.clear_background(rl.BLACK)
    m.draw()
    rl.end_drawing()

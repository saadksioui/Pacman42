import pyray as rl
from gui import SCREEN_HEIGHT, SCREEN_WIDTH
from mazegenerator import MazeGenerator
from .entity import Entity, Ghost


WALL_THICKNESS: float = 2.0
MAZE_PADDING: int = 50


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
            return min(
                (SCREEN_HEIGHT - MAZE_PADDING * 2) // self.maze_height,
                (SCREEN_WIDTH - MAZE_PADDING * 2) // self.maze_width
            )


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


class GhostRender:
    GHOSTS_TEXTURE: rl.Texture = rl.load_texture("assets/ghosts.png")
    GHOSTS_REC_HEIGHT: float = GHOSTS_TEXTURE.height / 12
    GHOSTS_REC_WIDTH: float = GHOSTS_TEXTURE.width / 12
    frame_rec: rl.Rectangle = rl.Rectangle(
       0, 0, GHOSTS_REC_WIDTH, GHOSTS_REC_HEIGHT
    )

    entity: Entity
    frames_counter: int = 0
    current_frame: int = 0
    max_frames_index: int = 1

    def __init__(self, entity: Entity, fps: int) -> None:
        self.entity = entity
        self.fps: int = fps

    def draw(self) -> None:
        frame_speed: int = 7
        self.frames_counter += 1
        if self.frames_counter >= self.fps / frame_speed:
            self.frames_counter = 0
            self.current_frame += 1
            if self.current_frame >  self.max_frames_index:
                self.current_frame = 0
            self.frame_rec.x = self.current_frame * self.GHOSTS_REC_WIDTH


        dst_rect = rl.Rectangle(
            200, 200, 100, 100
        )
        rl.draw_texture_pro(
            self.GHOSTS_TEXTURE,
            self.frame_rec,
            dst_rect,
            (50, 50),
            0.0,
            rl.WHITE
        )




m = MazeRender(MazeGenerator().maze)
ghost = Ghost(rl.Vector2(0,0), 0)
g1 = GhostRender(ghost, 500)
while not rl.window_should_close():
    fps = rl.get_fps()
    # draw framerate
    rl.draw_text(str(fps), 7, 7, 25, rl.WHITE)

    rl.begin_drawing()
    rl.clear_background(rl.BLACK)
    m.draw()
    g1.draw()
    rl.end_drawing()

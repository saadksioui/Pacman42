import pyray as rl
from paclib.config import CONFIG
from ._gui_init import SCREEN_HEIGHT, SCREEN_WIDTH
from enum import Enum, IntEnum
from collections import deque
import random


class _Direction(IntEnum):
    UP = 0b0001
    DOWN = 0b0100
    LEFT = 0b1000
    RIGHT = 0b0010
    NONE = 0


PACMAN_SPEED: float = 4.2
CHASE_GHOST_SPEED: float = 2.0
FRIGHTENED_GHOST_SPEED: float = 2.5
EATEN_GHOST_SPEED: float = 6.2


class _Entity:
    pos: rl.Vector2
    cur_direction: _Direction
    nxt_direction: _Direction
    speed: float

    def __init__(
        self,
        start_pos: rl.Vector2,
        speed: float
    ) -> None:
        self.pos = start_pos
        self.cur_direction = _Direction.NONE
        self.nxt_direction = _Direction.NONE
        self.speed = speed


class _Ghost(_Entity):
    class GhostState(Enum):
        CHASE = "CHASE"
        FRIGHTENED = "FRIGHTENED"
        EATEN = "EATEN"

    class GhostType(IntEnum):
        Blinky = 4
        Pinky = 5
        Inky = 6
        Clyde = 7

    type: GhostType
    state: GhostState

    def __init__(self, start_pos: rl.Vector2, type: GhostType,
                 spawn_pos: tuple[int, int]) -> None:
        super().__init__(start_pos, CHASE_GHOST_SPEED)
        self.type = type
        self.state = _Ghost.GhostState.CHASE
        self.spawn_pos = spawn_pos


class _Pacman(_Entity):
    def __init__(self, start_pos: rl.Vector2) -> None:
        super().__init__(start_pos, PACMAN_SPEED)


class _Pacgum:
    pos: rl.Vector2

    def __init__(self, pos: rl.Vector2) -> None:
        self.pos = pos


class _SuperPacgum(_Pacgum):
    pass


WALL_THICKNESS: float = 4.0
MAZE_PADDING: int = 50


class _MazeRender:
    maze: list[list[int]]
    maze_height: int
    maze_width: int

    wall_length: int

    def __init__(self, maze: list[list[int]]) -> None:
        self.maze = maze
        self.maze_height = len(self.maze)
        self.maze_width = len(self.maze[0])
        self.wall_length = self._get_wall_length()
        self.start_x: int = SCREEN_WIDTH // 2 - \
            (self.maze_width * self.wall_length) // 2
        self.start_y: int = SCREEN_HEIGHT // 2 - \
            (self.maze_height * self.wall_length) // 2

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
                        WALL_THICKNESS, rl.DARKBLUE
                    )
                    rl.draw_circle_v(
                        topleft_corner, WALL_THICKNESS / 2, rl.DARKBLUE)
                    rl.draw_circle_v(
                        topright_corner, WALL_THICKNESS / 2, rl.DARKBLUE)
                # west wall
                if cell & 0b1000:
                    rl.draw_line_ex(
                        topleft_corner,
                        bottomleft_corner,
                        WALL_THICKNESS, rl.DARKBLUE
                    )
                    rl.draw_circle_v(
                        topleft_corner, WALL_THICKNESS / 2, rl.DARKBLUE)
                    rl.draw_circle_v(
                        bottomleft_corner,
                        WALL_THICKNESS / 2,
                        rl.DARKBLUE)
                # south side
                if i == self.maze_height - 1:
                    rl.draw_line_ex(
                        bottomleft_corner,
                        bottomright_corner,
                        WALL_THICKNESS, rl.BLUE
                    )
                    rl.draw_circle_v(
                        bottomright_corner,
                        WALL_THICKNESS / 2,
                        rl.DARKBLUE)
                    rl.draw_circle_v(
                        bottomleft_corner,
                        WALL_THICKNESS / 2,
                        rl.DARKBLUE)
                # east side
                if j == self.maze_width - 1:
                    rl.draw_line_ex(
                        topright_corner,
                        bottomright_corner,
                        WALL_THICKNESS, rl.BLUE
                    )
                    rl.draw_circle_v(
                        bottomright_corner,
                        WALL_THICKNESS / 2,
                        rl.DARKBLUE)
                if cell == 0xf:
                    rl.draw_rectangle(
                        int(topleft_corner.x),
                        int(topleft_corner.y),
                        line := self.wall_length,
                        line,
                        rl.DARKBLUE
                    )

    def get_cell_cord(self, entity: _Entity) -> tuple[int, int]:
        maze_x = round((entity.pos.x - self.start_x) / self.wall_length)
        maze_x = min(maze_x, self.maze_width - 1)
        maze_y = round((entity.pos.y - self.start_y) / self.wall_length)
        maze_y = min(maze_y, self.maze_height - 1)
        return maze_x, maze_y

    def get_cell(self, entity: _Entity) -> int:
        maze_x, maze_y = self.get_cell_cord(entity)
        return self.maze[maze_y][maze_x]

    def can_move_to_direction(self, dirct: _Direction,
                              entity: _Entity) -> bool:
        if dirct is _Direction.NONE:
            return False
        return not (self.get_cell(entity) & dirct.value)

    def is_close_cellcenter(self, entity: _Entity) -> bool:
        return bool(
            ((entity.pos.x - self.start_x) / self.wall_length) % 1 < 0.1
            and ((entity.pos.y - self.start_y) / self.wall_length) % 1 < 0.1
        )

    def move_to_cellcenter(self, entity: _Entity) -> None:
        maze_x, maze_y = self.get_cell_cord(entity)
        entity.pos.x = self.start_x + self.wall_length * maze_x
        entity.pos.y = self.start_y + self.wall_length * maze_y


TEXTURE: rl.Texture = rl.load_texture("assets/everything.png")


class _EntityRender:

    entity: _Entity

    max_frames: int
    cur_frame: int

    src_mask_rec: rl.Rectangle
    dst_mask_rec: rl.Rectangle

    def __init__(
        self,
        entity: _Entity,
        max_frames: int,
        src_mask_rec: rl.Rectangle,
        dst_mask_rec: rl.Rectangle
    ) -> None:
        self.entity = entity
        self.max_frames = max_frames
        self.cur_frame = 0
        self.src_mask_rec = src_mask_rec
        self.dst_mask_rec = dst_mask_rec

        self._frame_count: int = 0

    def draw(self) -> None:
        # to switch between sprite sheet
        frame_speed = 7
        self._frame_count += 1
        if self._frame_count >= rl.get_fps() / frame_speed:
            self._frame_count = 0
            self.cur_frame += 1
            if self.cur_frame > self.max_frames:
                self.cur_frame = 0
                self.src_mask_rec.x -= self.max_frames * 16
            else:
                self.src_mask_rec.x += 16
        self.dst_mask_rec.x = self.entity.pos.x
        self.dst_mask_rec.y = self.entity.pos.y
        rl.draw_texture_pro(
            TEXTURE,
            self.src_mask_rec,
            self.dst_mask_rec,
            (0, 0),
            0.0,
            rl.WHITE
        )


class _PacmanRender(_EntityRender):
    maze_rend: _MazeRender
    lives: int

    def __init__(self, maze_rend: _MazeRender, lives: int) -> None:
        self.maze_rend = maze_rend
        self.lives = lives
        mid_x = maze_rend.maze_width // 2
        mid_y = maze_rend.maze_height // 2
        pixel_x = maze_rend.start_x + (mid_x * maze_rend.wall_length)
        pixel_y = maze_rend.start_y + (mid_y * maze_rend.wall_length)
        super().__init__(
            _Pacman(
                vct := rl.Vector2(pixel_x, pixel_y)
            ),
            2,
            rl.Rectangle(0, 0, 16, 16),
            rl.Rectangle(
                vct.x,
                vct.y,
                maze_rend.wall_length,
                maze_rend.wall_length)
        )

    def draw(self) -> None:
        idx = {
            _Direction.RIGHT: 0, _Direction.NONE: 0,
            _Direction.LEFT: 1,
            _Direction.UP: 2,
            _Direction.DOWN: 3,
        }
        self.src_mask_rec.y = idx[self.entity.cur_direction] * 16
        super().draw()


class _GhostRender(_EntityRender):
    maze_rend: _MazeRender
    ghost: _Ghost

    def __init__(self, maze_rend: _MazeRender, ghost: _Ghost) -> None:
        self.maze_rend = maze_rend
        super().__init__(
            ghost,
            1,
            rl.Rectangle(0, ghost.type.value * 16, 16, 16),
            rl.Rectangle(
                ghost.pos.x,
                ghost.pos.y,
                maze_rend.wall_length,
                maze_rend.wall_length)
        )
        self.ghost = ghost
        self.frightened_timer: float = 0.0
        self.eaten_timer: float = 0.0

    def draw(self, game_paused: bool = False) -> None:
        self._cancel_frightened_state(game_paused)
        self._cancel_eaten_state(game_paused)
        idx = {
            _Direction.RIGHT: 0, _Direction.NONE: 0,
            _Direction.LEFT: 1,
            _Direction.UP: 2,
            _Direction.DOWN: 3,
        }
        if self.ghost.state is _Ghost.GhostState.CHASE:
            self.src_mask_rec.x = (idx[self.entity.cur_direction]) * 16 * 2
            if self.cur_frame:
                self.src_mask_rec.x += 16
        if self.ghost.state is _Ghost.GhostState.EATEN:
            self.src_mask_rec.x = 16 * 8 + \
                (idx[self.entity.cur_direction]) * 16
        super().draw()

    def change_state(self, new_state: _Ghost.GhostState) -> None:
        self.cur_frame = 0
        match new_state:
            case _Ghost.GhostState.FRIGHTENED:
                # avoid changing the state of dead ghosts to frightened.
                if self.ghost.state is _Ghost.GhostState.EATEN:
                    return

                self.frightened_timer = 0.0
                self.src_mask_rec.x = 16 * 8
                self.src_mask_rec.y = 16 * 4
                self.max_frames = 1
                self.ghost.speed = FRIGHTENED_GHOST_SPEED
            case _Ghost.GhostState.CHASE:
                self.max_frames = 1
                self.src_mask_rec.y = self.ghost.type * 16
                self.ghost.speed = CHASE_GHOST_SPEED

            case _Ghost.GhostState.EATEN:
                self.eaten_timer = 0.0
                self.max_frames = 0
                self.src_mask_rec.y = 5 * 16
                self.src_mask_rec.x = 8 * 16
                self.ghost.speed = EATEN_GHOST_SPEED

        self.ghost.state = new_state

    def _cancel_frightened_state(self, game_paused: bool) -> None:
        if self.ghost.state is not _Ghost.GhostState.FRIGHTENED or game_paused:
            return
        self.frightened_timer += rl.get_frame_time()
        if 4 < self.frightened_timer < 7:
            self.max_frames = 3
        if self.frightened_timer > 7:
            self.change_state(_Ghost.GhostState.CHASE)

    def _cancel_eaten_state(self, game_paused: bool) -> None:
        if self.ghost.state is not _Ghost.GhostState.EATEN or game_paused:
            return
        self.eaten_timer += rl.get_frame_time()
        if self.eaten_timer > 5:
            self.change_state(_Ghost.GhostState.CHASE)


class _PacgumRender:
    def __init__(self, maze_rend: _MazeRender) -> None:
        def to_spacgum(x: int, y: int) -> None:
            pg = self.pacgum_map[y][x]
            assert isinstance(pg, _Pacgum)
            self.pacgum_set.remove(pg)
            self.pacgum_map[y][x] = spg = _SuperPacgum(pg.pos)
            self.pacgum_set.add(spg)
        self.pacgum_map: list[list[_Pacgum | None]] = []
        self.pacgum_set: set[_Pacgum] = set()
        self.maze_rend: _MazeRender = maze_rend
        self.PACGUM_RADIUS: float = max(maze_rend.wall_length / 20, 1)
        for i, row in enumerate(maze_rend.maze):
            self.pacgum_map.append([])
            for j, cell in enumerate(row):
                if cell == 0xf:
                    self.pacgum_map[-1].append(None)
                    continue
                self.pacgum_map[-1].append(pg := _Pacgum(rl.Vector2(
                    (maze_rend.start_x
                     + maze_rend.wall_length * j
                     + maze_rend.wall_length / 2),
                    (maze_rend.start_y
                     + maze_rend.wall_length * i
                     + maze_rend.wall_length / 2)
                )))
                self.pacgum_set.add(pg)

        maze_width = maze_rend.maze_width
        maze_height = maze_rend.maze_height
        to_spacgum(2, maze_height - 3)
        to_spacgum(2, 2)
        to_spacgum(maze_width - 3, 2)
        to_spacgum(maze_width - 3, maze_height - 3)

    def draw(self) -> None:
        for pg in self.pacgum_set:
            if isinstance(pg, _SuperPacgum):
                rl.draw_circle(
                    int(pg.pos.x),
                    int(pg.pos.y),
                    self.PACGUM_RADIUS * 3,
                    rl.YELLOW
                )
            else:
                rl.draw_circle(
                    int(pg.pos.x),
                    int(pg.pos.y),
                    self.PACGUM_RADIUS,
                    rl.YELLOW
                )

    def pacman_collect(self, pacman: _Entity) -> tuple[bool, int]:
        maze_x, maze_y = self.maze_rend.get_cell_cord(pacman)
        pg = self.pacgum_map[maze_y][maze_x]
        if pg is None:
            return False, 0
        if self.maze_rend.is_close_cellcenter(pacman):
            self.pacgum_set.remove(pg)
            self.pacgum_map[maze_y][maze_x] = None
            if isinstance(pg, _SuperPacgum):
                return True, CONFIG.points_per_super_pacgum
            return False, CONFIG.points_per_pacgum
        return False, 0


class PauseMenu:
    options: list[str] = [
        "Resume",
        "Main Menu",
        "Exit"
    ]

    cur_op: int
    font_size: int = SCREEN_HEIGHT // 15
    start_x: int = SCREEN_HEIGHT // 2 - \
        (font_size * len(options) - font_size // 5 * (len(options) - 1)) // 2

    def __init__(self) -> None:
        self.cur_op = 0

    def draw(self) -> None:
        half_screen = SCREEN_WIDTH // 2
        for i, op in enumerate(self.options):

            text_width = rl.measure_text(op, self.font_size)
            rl.draw_text(
                op,
                half_screen - text_width // 2,
                self.start_x + (self.font_size + self.font_size // 5) * i,
                self.font_size,
                rl.YELLOW if i == self.cur_op else rl.WHITE
            )

    def handle_keyboard(self) -> str | None:
        if rl.is_key_pressed(rl.KeyboardKey.KEY_DOWN):
            self.cur_op += 1
            if self.cur_op >= len(self.options):
                self.cur_op = 0
        elif rl.is_key_pressed(rl.KeyboardKey.KEY_UP):
            self.cur_op -= 1
            if self.cur_op < 0:
                self.cur_op = len(self.options) - 1

        elif rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            option = self.options[self.cur_op].lower()
            match option:
                case "exit":
                    rl.close_window()
                case _:
                    return option
        return None


class _PacmanLives:

    @staticmethod
    def draw(lives: int) -> None:
        dst = rl.Rectangle(
            10,
            SCREEN_HEIGHT -
            MAZE_PADDING,
            MAZE_PADDING,
            MAZE_PADDING)
        src = rl.Rectangle(16, 0, 16, 16)
        for i in range(lives):
            dst.x = 10 + MAZE_PADDING * i
            rl.draw_texture_pro(
                TEXTURE,
                src,
                dst,
                (0, 0), 0.0, rl.WHITE
            )


class GameLoop:
    class GameState(Enum):
        PLAYING = "PLAYING"
        PAUSED = "PAUSED"

    maze_rend: _MazeRender
    pacman_rend: _PacmanRender
    ghosts_rend: list[_GhostRender]
    pacgum_rend: _PacgumRender
    score: int
    state: GameState
    cheat_mode: bool
    invincible: bool
    ghosts_frozen: bool
    increase_speed: bool
    spawn_tiles: dict[_Ghost.GhostType, tuple[int, int]]

    def __init__(self, maze: list[list[int]], lives: int, score: int) -> None:
        self.maze_rend = _MazeRender(maze)
        self.pacman_rend = _PacmanRender(self.maze_rend, lives)
        max_x = self.maze_rend.maze_width - 1
        max_y = self.maze_rend.maze_height - 1

        self.spawn_tiles = {
            _Ghost.GhostType.Blinky: (1, 1),
            _Ghost.GhostType.Pinky: (max_x, 1),
            _Ghost.GhostType.Inky: (1, max_y),
            _Ghost.GhostType.Clyde: (max_x, max_y)
        }
        self.ghosts_rend = self._create_ghosts()
        self.pacgum_rend = _PacgumRender(self.maze_rend)
        self.score = score
        self.state = self.GameState.PLAYING
        self.cheat_mode = False
        self.invincible = False
        self.ghosts_frozen = False
        self.increase_speed = False

    def _create_ghosts(self) -> list[_GhostRender]:

        ghosttype = [
            _Ghost.GhostType.Blinky, _Ghost.GhostType.Pinky,
            _Ghost.GhostType.Inky, _Ghost.GhostType.Clyde
        ]

        ghosts: list[_GhostRender] = []
        for gt in ghosttype:
            grid_x, grid_y = self.spawn_tiles[gt]

            pixel_x = self.maze_rend.start_x + \
                (grid_x * self.maze_rend.wall_length)
            pixel_y = self.maze_rend.start_y + \
                (grid_y * self.maze_rend.wall_length)
            start_pos = rl.Vector2(pixel_x, pixel_y)
            ghosts.append(
                _GhostRender(
                    self.maze_rend, _Ghost(
                        start_pos, gt, (grid_x, grid_y)))
            )

        return ghosts

    def _run_bfs(self,
                 start: tuple[int, int],
                 target: tuple[int, int]) -> tuple[int, int] | None:
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        if start == target:
            return None
        queue = deque([start])
        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        while queue:
            curr = queue.popleft()
            if curr == target:
                break

            for dx, dy in directions:
                nxt = (curr[0] + dx, curr[1] + dy)
                if (
                    0 <= nxt[0] < self.maze_rend.maze_width
                    and 0 <= nxt[1] < self.maze_rend.maze_height
                ):
                    curr_cell = self.maze_rend.maze[curr[1]][curr[0]]
                    path_is_open = False
                    if dx == 1 and not (curr_cell & _Direction.RIGHT.value):
                        path_is_open = True
                    elif dx == -1 and not (curr_cell & _Direction.LEFT.value):
                        path_is_open = True
                    elif dy == 1 and not (curr_cell & _Direction.DOWN.value):
                        path_is_open = True
                    elif dy == -1 and not (curr_cell & _Direction.UP.value):
                        path_is_open = True
                    if path_is_open and nxt not in parent:
                        parent[nxt] = curr
                        queue.append(nxt)
        else:
            return None

        path = []
        current: tuple[int, int] | None = target
        while current is not None:
            path.append(current)
            current = parent[current]
        path.reverse()

        if len(path) > 1:
            return path[1]
        return None

    def _move_entity(self, entity: _Entity) -> None:
        if self.state is self.GameState.PAUSED:
            return

        if entity.cur_direction is _Direction.NONE:
            entity.cur_direction = entity.nxt_direction
            return

        if (self.maze_rend.can_move_to_direction(entity.nxt_direction, entity)
                and entity.nxt_direction is not entity.cur_direction):
            if self.maze_rend.is_close_cellcenter(entity):
                entity.cur_direction = entity.nxt_direction
                entity.nxt_direction = _Direction.NONE
                self.maze_rend.move_to_cellcenter(entity)
                return
        if (self.maze_rend.can_move_to_direction(entity.cur_direction, entity)
                or not self.maze_rend.is_close_cellcenter(entity)):
            to_move = (self.maze_rend.wall_length
                       * entity.speed * rl.get_frame_time())
            match entity.cur_direction:
                case _Direction.UP:
                    entity.pos.y -= to_move
                case _Direction.DOWN:
                    entity.pos.y += to_move
                case _Direction.LEFT:
                    entity.pos.x -= to_move
                case _Direction.RIGHT:
                    entity.pos.x += to_move
        else:
            self.maze_rend.move_to_cellcenter(entity)

    def _handle_keyboard(self) -> None:
        if self.state is self.GameState.PAUSED:
            return
        if rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
            self.pacman_rend.entity.nxt_direction = _Direction.DOWN
        elif rl.is_key_down(rl.KeyboardKey.KEY_UP):
            self.pacman_rend.entity.nxt_direction = _Direction.UP
        if rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
            self.pacman_rend.entity.nxt_direction = _Direction.LEFT
        elif rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
            self.pacman_rend.entity.nxt_direction = _Direction.RIGHT

    def _set_frightened_direction(self, ghost: _Ghost) -> None:
        if (rl.vector2_distance(ghost.pos, self.pacman_rend.entity.pos)
                >= self.maze_rend.wall_length * 5):
            if self.maze_rend.can_move_to_direction(
                    ghost.cur_direction, ghost):
                return
            ghost.nxt_direction = random.choice(
                [
                    d for d in (_Direction.UP, _Direction.DOWN,
                                _Direction.LEFT, _Direction.RIGHT)
                    if self.maze_rend.can_move_to_direction(d, ghost)
                ]
            )
            return
        directions = {
            _Direction.UP: rl.Vector2(ghost.pos.x, ghost.pos.y
                                      - self.maze_rend.wall_length),
            _Direction.LEFT: rl.Vector2(ghost.pos.x -
                                        self.maze_rend.wall_length,
                                        ghost.pos.y),
            _Direction.DOWN: rl.Vector2(ghost.pos.x, ghost.pos.y +
                                        self.maze_rend.wall_length),
            _Direction.RIGHT: rl.Vector2(
                ghost.pos.x + self.maze_rend.wall_length, ghost.pos.y)
        }
        vectors = {v: k for k, v in directions.items()}
        allowed: list[rl.Vector2] = []
        for drct, vct in directions.items():
            if self.maze_rend.can_move_to_direction(drct, ghost):
                allowed.append(vct)
        allowed = sorted(
            allowed,
            key=lambda vct: rl.vector2_distance(
                vct, self.pacman_rend.entity.pos)
        )
        ghost.nxt_direction = vectors[allowed[-1]]

    def _set_ghost_path(self, ghost: _Ghost) -> None:
        if not self.maze_rend.is_close_cellcenter(ghost):
            return

        curr_x, curr_y = self.maze_rend.get_cell_cord(ghost)
        start = (curr_x, curr_y)

        if ghost.state == ghost.GhostState.FRIGHTENED:
            self._set_frightened_direction(ghost)
            return
        target: tuple[int, int] | None = None
        if ghost.state == ghost.GhostState.CHASE:
            target = self.maze_rend.get_cell_cord(self.pacman_rend.entity)
        elif ghost.state == ghost.GhostState.EATEN:
            target = ghost.spawn_pos

        if target is None:
            return

        next_step = self._run_bfs(start, target)
        if next_step is None:
            return
        dx = next_step[0] - curr_x
        dy = next_step[1] - curr_y
        if dx == 1:
            ghost.nxt_direction = _Direction.RIGHT
        elif dx == -1:
            ghost.nxt_direction = _Direction.LEFT
        elif dy == 1:
            ghost.nxt_direction = _Direction.DOWN
        elif dy == -1:
            ghost.nxt_direction = _Direction.UP

    def _check_entity_collision(self) -> bool:
        for gr in self.ghosts_rend:
            distance = rl.vector2_distance(
                gr.ghost.pos, self.pacman_rend.entity.pos)
            if distance <= self.maze_rend.wall_length * 0.5:
                if gr.ghost.state == gr.ghost.GhostState.CHASE:
                    if not self.invincible:
                        self.pacman_rend.lives -= 1
                        if self.pacman_rend.lives <= 0:
                            return True
                        mid_x = self.maze_rend.maze_width // 2
                        mid_y = self.maze_rend.maze_height // 2
                        respawn_x = self.maze_rend.start_x + \
                            (mid_x * self.maze_rend.wall_length)
                        respawn_y = self.maze_rend.start_y + \
                            (mid_y * self.maze_rend.wall_length)

                        self.pacman_rend.entity.pos = rl.Vector2(
                            respawn_x, respawn_y)
                        self.pacman_rend.entity.cur_direction = _Direction.NONE
                        self.pacman_rend.entity.nxt_direction = _Direction.NONE
                        for g in self.ghosts_rend:
                            pos_x, pos_y = self.spawn_tiles[g.ghost.type]

                            pixel_x = self.maze_rend.start_x + \
                                (pos_x * self.maze_rend.wall_length)
                            pixel_y = self.maze_rend.start_y + \
                                (pos_y * self.maze_rend.wall_length)
                            g.ghost.pos = rl.Vector2(pixel_x, pixel_y)
                            g.ghost.cur_direction = _Direction.NONE
                            g.ghost.nxt_direction = _Direction.NONE
                            g.change_state(_Ghost.GhostState.CHASE)
                elif gr.ghost.state == gr.ghost.GhostState.FRIGHTENED:
                    gr.change_state(gr.ghost.GhostState.EATEN)
                    self.score += CONFIG.points_per_ghost
        return False

    def run(self) -> tuple[int, bool, int] | None:
        pause_menu: PauseMenu = PauseMenu()
        while not rl.window_should_close():
            if rl.is_key_pressed(rl.KeyboardKey.KEY_C):
                self.cheat_mode = not self.cheat_mode
            if rl.is_key_pressed(rl.KeyboardKey.KEY_SPACE):
                if self.state is self.GameState.PLAYING:
                    self.state = self.GameState.PAUSED
                    pause_menu = PauseMenu()
                else:
                    self.state = self.GameState.PLAYING
            if self.state is self.GameState.PAUSED:
                match pause_menu.handle_keyboard():
                    case "main menu":
                        return None
                    case "resume":
                        self.state = self.GameState.PLAYING
            if self.cheat_mode:
                rl.draw_text("Invincible: F1", 7, 217, 25, rl.WHITE)
                rl.draw_text("Level Skip: F2", 7, 257, 25, rl.WHITE)
                rl.draw_text("Ghost Freeze: F3", 7, 307, 25, rl.WHITE)
                rl.draw_text("Extra lives: F4", 7, 347, 25, rl.WHITE)
                rl.draw_text("Increased Speed: F5", 7, 387, 25, rl.WHITE)
                if rl.is_key_pressed(rl.KeyboardKey.KEY_F1):
                    self.invincible = not self.invincible
                if rl.is_key_pressed(rl.KeyboardKey.KEY_F2):
                    self.pacgum_rend.pacgum_set = set()
                if rl.is_key_pressed(rl.KeyboardKey.KEY_F3):
                    self.ghosts_frozen = not self.ghosts_frozen
                if rl.is_key_pressed(rl.KeyboardKey.KEY_F4):
                    self.pacman_rend.lives += 1
                if rl.is_key_pressed(rl.KeyboardKey.KEY_F5):
                    self.increase_speed = not self.increase_speed
                    if self.increase_speed:
                        self.pacman_rend.entity.speed = 10.0
                    else:
                        self.pacman_rend.entity.speed = PACMAN_SPEED
            self._handle_keyboard()
            if not self.ghosts_frozen:
                for g in self.ghosts_rend:
                    self._set_ghost_path(g.ghost)
                    self._move_entity(g.entity)

            self._move_entity(self.pacman_rend.entity)
            if self._check_entity_collision():
                return (self.score, False, self.pacman_rend.lives)

            is_super_pacgum, score = self.pacgum_rend.pacman_collect(
                self.pacman_rend.entity)
            self.score += score
            if is_super_pacgum:
                for gr in self.ghosts_rend:
                    gr.change_state(_Ghost.GhostState.FRIGHTENED)

            if len(self.pacgum_rend.pacgum_set) == 0:
                return (self.score, True, self.pacman_rend.lives)
            rl.begin_drawing()

            rl.clear_background(rl.BLACK)
            _PacmanLives.draw(self.pacman_rend.lives)
            self.maze_rend.draw()
            self.pacgum_rend.draw()
            for g in self.ghosts_rend:
                g.draw(self.state is self.GameState.PAUSED)
            self.pacman_rend.draw()
            rl.draw_text(f"Score: {self.score}", 7, 7, 25, rl.WHITE)
            rl.draw_text(str(rl.get_fps()), 7, 47, 25, rl.WHITE)
            rl.draw_text("Pause: Space", 7, 87, 25, rl.WHITE)
            rl.draw_text("Cheat Mode: C", 7, 127, 25, rl.WHITE)

            if self.state is self.GameState.PAUSED:
                rl.draw_rectangle(
                    0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 0xde))
                pause_menu.draw()

            rl.end_drawing()
        return None

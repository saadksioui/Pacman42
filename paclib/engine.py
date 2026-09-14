import pyray as rl
from typing import override
from ._gui_init import SCREEN_HEIGHT, SCREEN_WIDTH
from enum import IntEnum



class _Direction(IntEnum):
    UP = 0b0001
    DOWN = 0b0100
    LEFT = 0b1000
    RIGHT = 0b0010
    NONE = 0


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
    class GhostType(IntEnum):
        Blinky = 4
        Pinky = 5
        Inky = 6
        Clyde = 7

    type: GhostType

    def __init__(self, start_pos: rl.Vector2, type: GhostType) -> None:
        super().__init__(start_pos, 7)
        self.type = type



class _Pacman(_Entity):
    def __init__(self, start_pos: rl.Vector2) -> None:
        super().__init__(start_pos, 4.2)


class _Pacgum:
    pos: rl.Vector2
    def __init__(self, pos: rl.Vector2) -> None:
        self.pos = pos


WALL_THICKNESS: float = 2.0
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

    def get_cell_cord(self, entity: _Entity) -> tuple[int, int]:
        maze_x = round((entity.pos.x - self.start_x) / self.wall_length)
        maze_y = round((entity.pos.y - self.start_y) / self.wall_length)
        return maze_x, maze_y

    def get_cell(self, entity: _Entity) -> int:
        maze_x, maze_y = self.get_cell_cord(entity)
        return self.maze[maze_y][maze_x]

    def can_move_to_direction(self, dirct: _Direction, entity: _Entity) -> bool:
        if dirct is _Direction.NONE:
            return False
        return not (self.get_cell(entity) & dirct.value)

    def is_close_cellcenter(self, entity: _Entity) -> bool:
        return ((entity.pos.x - self.start_x) / self.wall_length) % 1 < 0.1\
            and ((entity.pos.y - self.start_y) / self.wall_length) % 1 < 0.1

    def move_to_cellcenter(self, entity: _Entity) -> None:
        maze_x, maze_y = self.get_cell_cord(entity)
        entity.pos.x = self.start_x + self.wall_length * maze_x
        entity.pos.y = self.start_y + self.wall_length * maze_y



class _EntityRender:
    TEXTURE: rl.Texture = rl.load_texture("assets/everything.png")
    MASK_REC_DIMENSION: float = 16 # linked to assets (227px // 16 frame)

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
        FRAME_SPEED = 7
        self._frame_count += 1
        if self._frame_count >= rl.get_fps() / FRAME_SPEED:
            self._frame_count = 0
            self.cur_frame += 1
            if self.cur_frame > self.max_frames:
                self.cur_frame = 0
                self.src_mask_rec.x -= self.max_frames * self.MASK_REC_DIMENSION
            else:
                self.src_mask_rec.x += self.MASK_REC_DIMENSION
        self.dst_mask_rec.x = self.entity.pos.x
        self.dst_mask_rec.y = self.entity.pos.y
        rl.draw_texture_pro(
            self.TEXTURE,
            self.src_mask_rec,
            self.dst_mask_rec,
            (0, 0),
            0.0,
            rl.WHITE
        )

class _PacmanRender(_EntityRender):
    maze_rend: _MazeRender

    def __init__(self, maze_rend: _MazeRender) -> None:
        self.maze_rend = maze_rend
        super().__init__(
            _Pacman(
                vct := rl.Vector2(maze_rend.start_x, maze_rend.start_y)
            ),
            2,
            rl.Rectangle(0, 0, self.MASK_REC_DIMENSION, self.MASK_REC_DIMENSION),
            rl.Rectangle(vct.x, vct.y, maze_rend.wall_length, maze_rend.wall_length)
        )

    @override
    def draw(self) -> None:
        idx = {
            _Direction.RIGHT: 0, _Direction.NONE: 0,
            _Direction.LEFT: 1,
            _Direction.UP: 2,
            _Direction.DOWN: 3,
        }
        self.src_mask_rec.y = idx[self.entity.cur_direction] * self.MASK_REC_DIMENSION
        super().draw()


class _GhostRender(_EntityRender):
    maze_rend: _MazeRender

    def __init__(self, maze_rend: _MazeRender, ghost: _Ghost) -> None:
        self.maze_rend = maze_rend
        super().__init__(
            ghost,
            1,
            rl.Rectangle(0, ghost.type.value * self.MASK_REC_DIMENSION, self.MASK_REC_DIMENSION, self.MASK_REC_DIMENSION),
            rl.Rectangle(ghost.pos.x, ghost.pos.y, maze_rend.wall_length, maze_rend.wall_length)
        )

    @override
    def draw(self) -> None:
        idx = {
            _Direction.RIGHT: 0, _Direction.NONE: 0,
            _Direction.LEFT: 1,
            _Direction.UP: 2,
            _Direction.DOWN: 3,
        }
        self.src_mask_rec.x = (idx[self.entity.cur_direction]) * self.MASK_REC_DIMENSION * 2
        if self.cur_frame:
            self.src_mask_rec.x += self.MASK_REC_DIMENSION
        super().draw()


class _PacgumRender:
    def __init__(self, maze_rend: _MazeRender) -> None:
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
                    maze_rend.start_x + maze_rend.wall_length * j + maze_rend.wall_length / 2,
                    maze_rend.start_y + maze_rend.wall_length * i + maze_rend.wall_length / 2
                )))
                self.pacgum_set.add(pg)
    def draw(self) -> None:
        for pg in self.pacgum_set:
            rl.draw_circle(
                int(pg.pos.x),
                int(pg.pos.y),
                self.PACGUM_RADIUS,
                rl.PURPLE
            )


    def pacman_collect(self, pacman: _Entity) -> int:
        maze_x, maze_y = self.maze_rend.get_cell_cord(pacman)
        pg = self.pacgum_map[maze_y][maze_x]
        if pg is None:
            return 0
        if self.maze_rend.is_close_cellcenter(pacman):
            self.pacgum_set.remove(pg)
            self.pacgum_map[maze_y][maze_x] = None
        return 0





class GameLoop:
    maze_rend: _MazeRender
    pacman_rend: _PacmanRender
    ghosts_rend: list[_GhostRender]
    pacgum_rend: _PacgumRender

    def __init__(self, maze: list[list[int]]) -> None:
        self.maze_rend = _MazeRender(maze)
        self.pacman_rend = _PacmanRender(self.maze_rend)
        self.ghosts_rend = self._create_ghosts()
        self.pacgum_rend = _PacgumRender(self.maze_rend)

    def _create_ghosts(self) -> list[_GhostRender]:
        ghosttype = [
            _Ghost.GhostType.Blinky, _Ghost.GhostType.Pinky,
            _Ghost.GhostType.Inky, _Ghost.GhostType.Clyde
        ]
        return [
            _GhostRender(
                self.maze_rend,
                _Ghost(rl.Vector2(self.maze_rend.start_x, self.maze_rend.start_y), gt),
            )
            for gt in ghosttype
        ]


    def _move_entity(self, entity: _Entity) -> None:
        if entity.cur_direction is _Direction.NONE:
            entity.cur_direction = entity.nxt_direction
            return

        if self.maze_rend.can_move_to_direction(entity.nxt_direction, entity) and entity.nxt_direction is not entity.cur_direction:
            if self.maze_rend.is_close_cellcenter(entity):
                entity.cur_direction = entity.nxt_direction
                entity.nxt_direction = _Direction.NONE
                self.maze_rend.move_to_cellcenter(entity)
                return
        if self.maze_rend.can_move_to_direction(entity.cur_direction, entity):
            to_move = self.maze_rend.wall_length * entity.speed * rl.get_frame_time()
            match entity.cur_direction:
                case _Direction.UP:
                    entity.pos.y -= to_move
                case _Direction.DOWN:
                    entity.pos.y += to_move
                case _Direction.LEFT:
                    entity.pos.x -= to_move
                case _Direction.RIGHT:
                    entity.pos.x += to_move
        elif not self.maze_rend.is_close_cellcenter(entity):
            to_move = self.maze_rend.wall_length * entity.speed * rl.get_frame_time()
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
        if rl.is_key_down(rl.KeyboardKey.KEY_DOWN):
            self.pacman_rend.entity.nxt_direction = _Direction.DOWN
        elif rl.is_key_down(rl.KeyboardKey.KEY_UP):
            self.pacman_rend.entity.nxt_direction = _Direction.UP
        if rl.is_key_down(rl.KeyboardKey.KEY_LEFT):
            self.pacman_rend.entity.nxt_direction = _Direction.LEFT
        elif rl.is_key_down(rl.KeyboardKey.KEY_RIGHT):
            self.pacman_rend.entity.nxt_direction = _Direction.RIGHT

    def _set_ghost_path(self, ghost: _Ghost) -> None:
        if self.maze_rend.can_move_to_direction(ghost.cur_direction, ghost):
            return
        import random
        walls = self.maze_rend.get_cell(ghost)
        directions = [_Direction.DOWN, _Direction.UP, _Direction.LEFT, _Direction.RIGHT]
        available = [d for d in directions if not walls & d ]
        ghost.nxt_direction = random.choice(available)


    def run(self) -> None:
        while not rl.window_should_close():
            self._handle_keyboard()
            for g in self.ghosts_rend:
                assert isinstance(g.entity, _Ghost)
                self._set_ghost_path(g.entity)
                self._move_entity(g.entity)
            self._move_entity(self.pacman_rend.entity)
            self.pacgum_rend.pacman_collect(self.pacman_rend.entity)
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            self.maze_rend.draw()
            self.pacgum_rend.draw()
            for g in self.ghosts_rend:
                g.draw()
            self.pacman_rend.draw()
            rl.draw_text(str(rl.get_fps()), 7, 7, 25, rl.WHITE)
            rl.end_drawing()

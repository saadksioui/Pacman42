from abc import abstractmethod, ABC
from enum import IntEnum, auto
import pyray as rl

class Direction(IntEnum):
    UP = 0b0001
    DOWN = 0b0100
    LEFT = 0b1000
    RIGHT = 0b0010
    NONE = 0


class Entity(ABC):
    pos: rl.Vector2
    cur_direction: Direction
    nxt_direction: Direction
    speed: float
    frame_count: int


    def __init__(
        self,
        start_pos: rl.Vector2,
        speed: float
    ) -> None:
        self.pos = start_pos
        self.cur_direction = Direction.NONE
        self.nxt_direction = Direction.NONE
        self.speed = speed


class Ghost(Entity):
    def __init__(self, start_pos: rl.Vector2, speed: float) -> None:
        super().__init__(start_pos, speed)



class Pacman(Entity):
    def __init__(self, start_pos: rl.Vector2) -> None:
        super().__init__(start_pos, 4.2)

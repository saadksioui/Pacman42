from abc import abstractmethod, ABC
from enum import Enum, auto
import pyray as rl

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    NONE = auto()


class Entity(ABC):
    pos: rl.Vector2
    direction: Direction
    speed: float
    frame_count: int


    def __init__(
        self,
        start_pos: rl.Vector2,
        speed: float
    ) -> None:
        self.pos = start_pos
        self.direction = Direction.NONE
        self.speed = speed


class Ghost(Entity):
    frame_count: int = 2
    def __init__(self, start_pos: rl.Vector2, speed: float) -> None:
        super().__init__(start_pos, speed)

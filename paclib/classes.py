from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)


@dataclass
class Position:
    x: int
    y: int

    def distance(self, other: "Position") -> float:
        return abs(self.x - other.x) + abs(self.y - other.y)


class Entity(ABC):
    pos: Position
    curr_direction: Direction
    speed: float

    def __int__(self, init_pos: Position) -> None:
        self.pos = init_pos
        self.curr_direction = Direction.NONE
        self.speed = 1.0

    @abstractmethod
    def update(self) -> None:
        pass



class Pacman(Entity):
    class State(Enum):
        NORMAL = "normal"
        OP = "over powered"

    state: State
    lives: int
    op_timer: float

    def __init__(self, init_pos: Position, lives: int):
        super().__init__(init_pos)
        self.state = self.State.NORMAL
        self.lives = lives
        self.op_timer = 0.0

    def update(self):
        pass


class Ghost(Entity):
    class State(Enum):
        SCATTER = "scatter"
        CHASE = "chase"
        FRIGHTENED = "Frightened"
        EATEN = "Eaten"

    state: State

    def __init__(self, name: str, init_pos: Position):
        super().__init__(init_pos)
        self.state = self.State.SCATTER
        self.name = name

    def update(self):
        pass

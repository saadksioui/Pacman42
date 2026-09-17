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

    def __init__(self, init_pos: Position) -> None:
        self.pos = init_pos
        self.curr_direction = Direction.NONE
        self.speed = 0.5


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


class Ghost(Entity):
    class State(Enum):
        CHASE = "chase"
        FRIGHTENED = "Frightened"
        EATEN = "Eaten"

    state: State

    def __init__(self, init_pos: Position, name: str):
        super().__init__(init_pos)
        self.state = self.State.CHASE
        self.name = name
        self.start_pos = init_pos
        self.prev_pos: tuple[int, int] | None = None

    def get_target(self, pacman: Pacman,
                   blinky_pos: tuple[int, int]
                   | None = None) -> tuple[int, int] | None:
        px, py = pacman.pos.x, pacman.pos.y
        dx, dy = pacman.curr_direction.value

        if self.name == "Blinky":
            return (px, py)

        elif self.name == "Pinky":
            return (px + (dx * 4), py + (dy * 4))

        elif self.name == "Inky":
            pivot_x = px + (dx * 2)
            pivot_y = py + (dy * 2)

            if blinky_pos:
                vec_x = pivot_x - blinky_pos[0]
                vec_y = pivot_y - blinky_pos[1]

                return (blinky_pos[0] + (vec_x * 2),
                        blinky_pos[1] + (vec_y * 2))
            return (px, py)

        elif self.name == "Clyde":
            dist = abs(px - self.pos.x) + abs(py - self.pos.y)
            if dist > 8:
                return (px, py)
            else:
                return (1, 30)

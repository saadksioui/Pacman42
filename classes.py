from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Position:
    x: int
    y: int


class Entity(ABC):
    def __int__(self, curr_pos: Position) -> None:
        self.pos = curr_pos
        self.curr_direction = "up"
        self.speed = 1.0

    @abstractmethod
    def update(self) -> None:
        pass


class Pacman(Entity):
    def __init__(self, pos: Position, lives):
        super().__init__(pos)
        self.lives = lives
        self.score = 0

    def update(self):
        pass


class Ghost(Entity):
    def __init__(self, pos: Position, ghost_type):
        super().__init__(pos)
        self.ghost_type = ghost_type
        self.state = "scatter"

    def update(self):
        pass

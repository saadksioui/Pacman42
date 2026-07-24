from enum import Enum
from paclib.parser import Config
from paclib.classes import Pacman, Ghost, Position
from typing import List

class GameState(Enum):
    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    END = "end"


class Game:
    def __init__(self, maze: List[List[int]], config: Config):
        self.is_running: bool = True
        self.maze: list[list[int]] = maze
        self.state = GameState.MENU
        self.configs = config
        self.pacman = Pacman(Position(10, 10), config.lives)
        self.ghosts = [
            Ghost("Void", Position(5, 5)),
            Ghost("Ubik", Position(5, 5)),
            Ghost("Femto", Position(5, 5)),
            Ghost("Conrad", Position(5, 5)),
        ]
        self.score: int = 0
        self.power_timer: float = 0.0

    def _user_inputs(self):
        # Key input
        pass

    def _update_entities(self):
        pass

    def _collisions(self):
        curr_pos = self.maze[self.pacman.pos.y][self.pacman.pos.x]
        if curr_pos == 10:
            self.score += 10
            self.maze[self.pacman.pos.y][self.pacman.pos.x] = 0
        elif curr_pos == 50:
            self.score += 50
            self._change_pacman_state()

        for ghost in self.ghosts:
            if self.pacman.pos.x == ghost.pos.x and self.pacman.pos.y == ghost.pos.y:
                if ghost.state == ghost.State.FRIGHTENED:
                    ghost.state = ghost.State.EATEN
                    self.score += 200
                else:
                    self._pacman_death()

    def _change_pacman_state(self):
        self.pacman.op_timer = 7.0
        for ghost in self.ghosts:
            if ghost.state != ghost.State.EATEN:
                ghost.state = ghost.State.FRIGHTENED

    def _change_ghosts_state(self):
        for ghost in self.ghosts:
            if ghost.state == ghost.State.FRIGHTENED:
                ghost.state = ghost.State.CHASE
    
    def _pacman_death(self):
        self.pacman.lives -= 1
        if self.pacman.lives == 0:
            self.is_running = False
        else:
            self.pacman.pos.x = 10
            self.pacman.pos.y = 10

    def _rendring(self):
        pass

    def run(self):
        while self.is_running:
            self._user_inputs()
            self._update_entities()
            self._collisions()
            self._rendring()

from enum import Enum
from paclib.parser import Config
from paclib.classes import Pacman, Ghost, Position
from typing import List, Tuple
import pyray as pr  # type: ignore
from collections import deque
import time


class GameState(Enum):
    MENU = "menu"
    PLAY = "play"
    PAUSE = "pause"
    END = "end"


class Game:
    def __init__(self, maze: List[List[int]], config: Config):
        self.is_running: bool = True
        self.maze: list[list[int]] = maze
        self.rows = len(maze)
        self.cols = len(maze[0])
        self.state = GameState.MENU
        self.configs = config
        self.pacman = Pacman(Position(1, 2), config.lives)
        self.ghosts = [
            Ghost(Position(5, 5), "Pinky"),
            Ghost(Position(5, 5), "Inky"),
            Ghost(Position(5, 5), "Blinky"),
            Ghost(Position(5, 5), "Clyde"),
        ]
        self.score: int = 0
        self.power_timer: float = 0.0
        pr.init_window(1080, 1080, "PacMan")
        pr.set_target_fps(60)

    def _user_inputs(self):
        if pr.is_key_down(pr.KEY_UP):
            return pr.KEY_UP
        if pr.is_key_down(pr.KEY_DOWN):
            return pr.KEY_DOWN
        if pr.is_key_down(pr.KEY_LEFT):
            return pr.KEY_LEFT
        if pr.is_key_down(pr.KEY_RIGHT):
            return pr.KEY_RIGHT

        return 0

    def _update_entities(self, key):
        new_x = self.pacman.pos.x
        new_y = self.pacman.pos.y

        if key == pr.KEY_UP:
            new_y -= 1
        elif key == pr.KEY_DOWN:
            new_y += 1
        elif key == pr.KEY_LEFT:
            new_x -= 1
        elif key == pr.KEY_RIGHT:
            new_x += 1
        else:
            return

        if 0 <= new_y < len(self.maze) and 0 <= new_x < len(self.maze[0]):
            target = self.maze[new_y][new_x]
            if target != 10:
                self.pacman.pos.x = new_x
                self.pacman.pos.y = new_y

    def _collisions(self):
        curr_pos = self.maze[self.pacman.pos.y][self.pacman.pos.x]
        if curr_pos == 1:
            self.score += 10
            self.maze[self.pacman.pos.y][self.pacman.pos.x] = 0
        elif curr_pos == 10:
            self.score += 10
            self.maze[self.pacman.pos.y][self.pacman.pos.x] = 0
        elif curr_pos == 50:
            self.score += 50
            self._change_pacman_state()
            self.maze[self.pacman.pos.y][self.pacman.pos.x] = 0

        for ghost in self.ghosts:
            if (self.pacman.pos.x == ghost.pos.x
                    and self.pacman.pos.y == ghost.pos.y):
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
                self._chasing(ghost)

    def _pacman_death(self):
        self.pacman.lives -= 1
        if self.pacman.lives == 0:
            self.state = GameState.END
        else:
            self.pacman.pos.x = 1
            self.pacman.pos.y = 1

    def _chasing(self, ghost: Ghost):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        perfect_dis = float("inf")
        perfect_pos = None
        for dx, dy in directions:
            nx = ghost.pos.x + dx
            ny = ghost.pos.y + dy
            if (0 <= nx < self.rows and 0 <= ny < self.cols):
                if self.maze[ny][nx] != 10:
                    dist = abs(self.pacman.pos.x - nx) + abs(self.pacman.pos.y - ny)
                    if dist < perfect_dis:
                        perfect_dis = dist
                        perfect_pos = (nx, ny)
        if perfect_pos:
            ghost.pos.x = perfect_pos[0]
            ghost.pos.y = perfect_pos[1]
            

    def _rendering(self):
        pr.begin_drawing()
        pr.clear_background(pr.BLACK)

        if self.state == GameState.MENU:
            pr.draw_text("PACMAN", 250, 200, 40, pr.YELLOW)
            pr.draw_text("Press ENTER to Start", 220, 300, 20, pr.WHITE)

            if pr.is_key_pressed(pr.KEY_ENTER):
                self.state = GameState.PLAY

        elif self.state == GameState.PLAY:
            cell_size = 24
            y_offset = 40

            for y, row in enumerate(self.maze):
                for x, cell in enumerate(row):
                    pixel_x = x * cell_size
                    pixel_y = (y * cell_size) + y_offset
                    
                    if cell == 10:
                        pr.draw_rectangle(pixel_x, pixel_y, cell_size, cell_size, pr.DARKBLUE)
                    elif cell == 1:
                        pr.draw_circle(pixel_x + cell_size // 2, pixel_y + cell_size // 2, 3, pr.YELLOW)
                    elif cell == 50:
                        pr.draw_circle(pixel_x + cell_size // 2, pixel_y + cell_size // 2, 5, pr.ORANGE)

            ghost_colors = {
                "Blinky": pr.RED,
                "Pinky": pr.PINK,
                "Inky": pr.SKYBLUE,
                "Clyde": pr.ORANGE
            }

            for ghost in self.ghosts:
                gx = ghost.pos.x * cell_size + cell_size // 2
                gy = ghost.pos.y * cell_size + cell_size // 2 + y_offset

                if ghost.state == ghost.State.FRIGHTENED:
                    g_color = pr.BLUE
                elif ghost.state == ghost.State.EATEN:
                    g_color = pr.DARKGRAY
                else:
                    g_color = ghost_colors.get(ghost.name, pr.PURPLE)

                pr.draw_circle(gx, gy, cell_size // 2 - 2, g_color)

            px = self.pacman.pos.x * cell_size + cell_size // 2
            py = self.pacman.pos.y * cell_size + cell_size // 2 + y_offset

            pr.draw_circle(px, py, cell_size // 2 - 2, pr.YELLOW)

            pr.draw_text(f"Score: {self.score}", 10, 10, 20, pr.WHITE)
            if pr.gui_button(pr.Rectangle(300, 10, 120, 40), "PAUSE"):
                self.state = GameState.PAUSE
            pr.draw_text(f"Lives: {self.pacman.lives}", 200, 10, 20, pr.WHITE)
            
        elif self.state == GameState.PAUSE:
            pr.draw_text("PAUSED", 250, 250, 40, pr.WHITE)
            if pr.gui_button(pr.Rectangle(300, 10, 120, 40), "RESUME"):
                self.state = GameState.PLAY
            
        elif self.state == GameState.END:
            pr.draw_text("GAME OVER", 220, 250, 40, pr.RED)
            pr.draw_text(f"Final Score: {self.score}", 240, 300, 20, pr.WHITE)

        pr.end_drawing()

    def run(self):
        pacman_timer, ghost_timer = 0.0, 0.0
        pacman_delay, ghost_delay = 0.10, 0.10
        while self.is_running and not pr.window_should_close():
            frame_time = pr.get_frame_time()
            if self.state == GameState.PLAY:
                pacman_timer += frame_time
                ghost_timer += frame_time
                if pacman_timer >= pacman_delay:
                    key = self._user_inputs()
                    if key != 0:
                        self._update_entities(key)
                    pacman_timer = 0.0

                if ghost_timer >= ghost_delay:
                    for ghost in self.ghosts:
                        if ghost.state == ghost.State.CHASE:
                            self._chasing(ghost)
                    ghost_timer = 0.0

                self._collisions()

                if self.pacman.op_timer > 0:
                    self.pacman.op_timer -= frame_time
                    if self.pacman.op_timer <= 0:
                        self._change_ghosts_state()
                        self.pacman.op_timer = 0.0
            self._rendering()

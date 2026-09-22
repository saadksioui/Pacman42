from .config import CONFIG
from mazegenerator import MazeGenerator
from .score import Score
from functools import lru_cache
from .engine import GameLoop
from ._gui_init import SCREEN_HEIGHT, SCREEN_WIDTH
import pyray as rl
from pathlib import Path
import json


class LeaderBoardPage:
    @lru_cache
    @staticmethod
    def _load_scores() -> list[Score]:
        results = []
        file_path = Path(CONFIG.highscore_path)
        if file_path.exists():
            with open(file_path, 'r') as file:
                content = json.load(file)
            for item in content:
                results.append(Score(score=item['score'], owner=item['name']))
        return results

    @classmethod
    def _draw_scores(cls) -> None:
        title_size = SCREEN_HEIGHT // 12
        scores = cls._load_scores()
        title_width = rl.measure_text("High Scores", title_size)
        rl.draw_text(
            "High Scores",
            SCREEN_WIDTH // 2 - title_width // 2,
            SCREEN_HEIGHT // 15,
            title_size,
            rl.RED
        )
        scores_y_start = title_size + SCREEN_HEIGHT // 15 + 100
        padding = 20
        score_text_size = (
            SCREEN_HEIGHT - scores_y_start - 100 - 9 * padding) // 10
        text_width = rl.measure_text("G" * 12, score_text_size)
        for i, sc in enumerate(scores, start=1):
            text = str(i) + ". " + sc.owner.ljust(11, " ")
            rl.draw_text(
                text,
                SCREEN_WIDTH // 6,
                scores_y_start + (i - 1) * (score_text_size + padding),
                score_text_size,
                rl.WHITE
            )
            rl.draw_text(
                str(sc.score),
                SCREEN_WIDTH // 6 + 40 + text_width,
                scores_y_start + (i - 1) * (score_text_size + padding),
                score_text_size,
                rl.YELLOW
            )

    @classmethod
    def display(cls) -> None:
        while not rl.window_should_close():
            if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
                break
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            cls._draw_scores()
            rl.end_drawing()


############################################
# SaveScorePage
############################################
class SaveScorePage:
    score: int

    def __init__(self, score: int) -> None:
        self.score = score

    def _save_in_file(self, name: str) -> None:
        file_path = Path(CONFIG.highscore_path)
        scores: list[dict[str, int | str]] = [
            {
                "name": name,
                'score': self.score
            }
        ]
        if file_path.exists():
            with open(CONFIG.highscore_path, 'r') as file:
                content = json.load(file)
            scores.extend(content)
            sorted_scores = sorted(
                scores,
                key=lambda item: int(item['score']),
                reverse=True)[
                :10]
            with open(CONFIG.highscore_path, 'w') as file:
                json.dump(sorted_scores, file)
        else:
            with open(CONFIG.highscore_path, 'w') as file:
                json.dump(scores, file)

    def _should_save(self) -> bool:
        return True

    def _draw_text(self, s: str) -> None:
        title_text_size = SCREEN_HEIGHT // 12
        normal_text_size = title_text_size // 3
        rl.draw_text(
            "New Score",
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 2 - int(title_text_size * 1.5),
            title_text_size,
            rl.GREEN
        )
        rl.draw_text(
            "enter your name:",
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 2 - int(normal_text_size),
            normal_text_size,
            rl.WHITE
        )
        rl.draw_text(
            s.ljust(10, "-"),
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 2,
            SCREEN_HEIGHT // 9,
            rl.WHITE
        )

    def _read_input(self, s: str) -> str:
        key = rl.get_char_pressed()
        if rl.is_key_pressed(rl.KeyboardKey.KEY_BACKSPACE):
            return s[:-1]
        elif rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER) and s:
            return s.ljust(11, ' ')
        elif len(s) < 10:
            key_char = chr(key)
            if key_char.isalnum() or key_char == ' ':
                return s + key_char
        return s

    def draw(self) -> None:
        if not self._should_save():
            return
        name = ""
        while not rl.window_should_close():
            name = self._read_input(name)
            if len(name) == 11:
                break
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            self._draw_text(name)
            rl.end_drawing()
        while rl.is_key_down(
                rl.KeyboardKey.KEY_ENTER) and not rl.window_should_close():
            rl.begin_drawing()
            rl.end_drawing()
        if len(name) == 11:
            self._save_in_file(name)


############################################
# GamePage
############################################
class GamePage:
    @staticmethod
    def draw() -> None:
        levels = CONFIG.levels or []
        curr_lives = CONFIG.lives
        curr_score = 0
        while not rl.window_should_close() and levels:
            lvl = levels[0]
            levels = levels[1:]
            maze = MazeGenerator(
                size=(
                    lvl.height,
                    lvl.width),
                seed=CONFIG.seed).maze
            game = GameLoop(maze, curr_lives, curr_score)
            result = game.run()
            if result is None:
                return
            score, win_or_lose, lives = result
            if not win_or_lose:
                SaveScorePage(score).draw()
                return
            curr_score = score
            curr_lives = lives
            continue
        if not rl.window_should_close():
            SaveScorePage(curr_score).draw()

############################################
# InfoPage
############################################
class InfoPage:
    @staticmethod
    def draw() -> None:
        lines = [
            "Arrow Up = Go Up",
            "Arrow Down = Go Down",
            "Arrow Left = Go Left",
            "Arrow Right = Go Right",
            "C = Cheat Mode",
        ]
        while not rl.window_should_close():
            if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
                return
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            x, y, spacing, font_size = 20, 20, 30, 24
            for i, line in enumerate(lines):
                rl.draw_text(line, x, y + i * spacing, font_size, rl.WHITE)
            rl.draw_text(
                "Created by: nullmaz & saadksioui",
                20,
                SCREEN_HEIGHT - 40,
                20,
                rl.WHITE
            )
            rl.draw_text(
                "Tested by: Gx-Nasr",
                20,
                SCREEN_HEIGHT - 40 * 2,
                20,
                rl.WHITE
            )
            rl.end_drawing()


############################################
# HomePage
############################################
# top consts
TOP_PADDING = SCREEN_HEIGHT * 15 / 100
TOP_SECTION_HEIGHT = (SCREEN_HEIGHT * 30 / 100)
# bottom consts
BOTTOM_SECTION_HEIGHT = (SCREEN_HEIGHT * 50 / 100)
BOTTOM_SECTION_Y_START = TOP_SECTION_HEIGHT
BOTTOM_SECTION_Y_END = BOTTOM_SECTION_Y_START + BOTTOM_SECTION_HEIGHT
BOTTOM_PADDING = SCREEN_HEIGHT * 15 / 100


class _HomeButton:
    rectangle: rl.Rectangle
    text: str
    selected: bool

    def __init__(
        self, text: str, rectangle: rl.Rectangle, selected: bool = False
    ) -> None:
        self.rectangle = rectangle
        self.text = text
        self.selected = selected

    def draw(self) -> None:
        rl.draw_rectangle(
            int(self.rectangle.x),
            int(self.rectangle.y),
            int(self.rectangle.width),
            int(self.rectangle.height),
            rl.WHITE if not self.selected else rl.YELLOW,
        )
        font_size = int((self.rectangle.height) / 2)
        txt_width = rl.measure_text(self.text, font_size)
        rl.draw_text(
            self.text,
            int(SCREEN_WIDTH / 2 - txt_width / 2),
            int(self.rectangle.y + font_size // 2),
            font_size,
            rl.BLACK,
        )

    @classmethod
    def create(cls, options: list[str]) -> list["_HomeButton"]:
        button_spacing = 15
        button_height = (BOTTOM_SECTION_HEIGHT -
                         BOTTOM_PADDING * 2) / len(options)
        button_width = button_height * 5
        buttons = []
        for i, text in enumerate(options):
            buttons.append(
                cls(
                    text,
                    rl.Rectangle(
                        int(SCREEN_WIDTH / 2 - button_width / 2),
                        int(BOTTOM_SECTION_Y_START + BOTTOM_PADDING +
                            i * (button_height + button_spacing)),
                        int(button_width),
                        int(button_height),
                    ),
                    i == 0,
                )
            )
        return buttons


class _Logo:
    texture: rl.Texture = rl.load_texture("assets/logo.png")
    SCALE = (TOP_SECTION_HEIGHT / 2) / texture.height

    @classmethod
    def draw(cls) -> None:
        rl.draw_texture_ex(
            cls.texture,
            rl.Vector2(
                (SCREEN_WIDTH / 2 - cls.texture.width * cls.SCALE / 2),
                TOP_PADDING
            ),
            0.0,  # rotation
            cls.SCALE,
            rl.WHITE
        )


class HomePage:
    @staticmethod
    def buttons(buttons: list[_HomeButton]) -> str | None:
        selected = -1
        for i, b in enumerate(buttons):
            if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER) and b.selected:
                return b.text
            if b.selected:
                selected = i
            b.draw()
        if rl.is_key_pressed(rl.KeyboardKey.KEY_DOWN):
            buttons[selected].selected = False
            selected += 1
            if selected >= len(buttons):
                selected = 0
            buttons[selected].selected = True

        if rl.is_key_pressed(rl.KeyboardKey.KEY_UP):
            buttons[selected].selected = False
            selected -= 1
            if selected < 0:
                selected = len(buttons) - 1
            buttons[selected].selected = True

        return None

    @classmethod
    def start(cls) -> None:
        buttons: list[_HomeButton] = _HomeButton.create(
            ["play", "score", "info", "exit"])
        clicked_button: str | None = None
        skip_click = False
        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            _Logo.draw()
            clicked_button = cls.buttons(buttons)
            rl.end_drawing()

            if skip_click:
                clicked_button = None
            skip_click = False
            if clicked_button is None:
                pass
            elif clicked_button == "score":
                LeaderBoardPage.display()
                skip_click = True
            elif clicked_button == "play":
                GamePage.draw()
                skip_click = True
            elif clicked_button == "info":
                InfoPage.draw()
                skip_click = True
            else:
                return

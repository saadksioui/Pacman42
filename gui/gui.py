from .score import Score
from functools import lru_cache
import pyray as rl
from gui import SCREEN_HEIGHT, SCREEN_WIDTH

class LeaderBoardPage:
    @lru_cache
    @staticmethod
    def _load_scores() -> list[Score]:
        from random import randint
        lst = [
            Score(score=randint(300000, 600000), owner="puckman"),
            Score(score=randint(1,10), owner="hello")
        ]
        for _ in range(8):
            lst.append(Score(score=randint(1,30000), owner="hello"))
        return lst

    @classmethod
    def _draw_scores(cls) -> None:
        TITLE_SIZE = SCREEN_HEIGHT // 12
        scores = cls._load_scores()
        title_width = rl.measure_text("High Scores", TITLE_SIZE)
        rl.draw_text(
            "High Scores",
            SCREEN_WIDTH // 2 - title_width // 2,
            SCREEN_HEIGHT // 15,
            TITLE_SIZE,
            rl.RED
        )
        SCORES_Y_START = TITLE_SIZE + SCREEN_HEIGHT // 15 + 100
        PADDING = 20
        SCORE_TEXT_SIZE = (SCREEN_HEIGHT - SCORES_Y_START - 100 - 9 * PADDING) // 10
        TEXT_WIDTH = rl.measure_text("G"* 12, SCORE_TEXT_SIZE)
        for i, sc in enumerate(scores, start=1):
            text = str(i) + ". " + sc.owner.ljust(11, " ")
            rl.draw_text(
                text,
                SCREEN_WIDTH // 6,
                SCORES_Y_START + (i - 1) * (SCORE_TEXT_SIZE + PADDING),
                SCORE_TEXT_SIZE,
                rl.WHITE
            )
            rl.draw_text(
                str(sc.score),
                SCREEN_WIDTH // 6 + 40 + TEXT_WIDTH,
                SCORES_Y_START + (i - 1) * (SCORE_TEXT_SIZE + PADDING),
                SCORE_TEXT_SIZE,
                rl.YELLOW
            )


    @classmethod
    def draw(cls) -> None:
        while not rl.window_should_close():
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
        raise NotImplementedError

    def _should_save(self) -> bool:
        return True

    def _draw_text(self, s: str) -> None:
        TITLE_TEXT_SIZE = SCREEN_HEIGHT // 12
        NORMAL_TEXT_SIZE = TITLE_TEXT_SIZE // 3
        rl.draw_text(
            "New Score",
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 2 - int(TITLE_TEXT_SIZE * 1.5),
            TITLE_TEXT_SIZE,
            rl.GREEN
        )
        rl.draw_text(
            "enter your name:",
            SCREEN_WIDTH // 4,
            SCREEN_HEIGHT // 2 - int(NORMAL_TEXT_SIZE),
            NORMAL_TEXT_SIZE,
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
        if len(name) == 11:
            self._save_in_file(name)

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

class HomeButton:
    rectangle: rl.Rectangle
    text: str
    selected: bool

    def __init__(
        self, text: str, rectangle: rl.Rectangle, selected: bool = False
    ) -> None:
        self.rectangle = rectangle
        self.text = text
        self.selected = selected

    def draw(self):
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
    def create(cls, options: list[str]) -> list["HomeButton"]:
        BUTTON_SPACING = 15
        BUTTON_HEIGHT = (BOTTOM_SECTION_HEIGHT - BOTTOM_PADDING * 2) / len(options)
        BUTTON_WIDTH = BUTTON_HEIGHT * 5
        buttons = []
        for i, text in enumerate(options):
            buttons.append(
                cls(
                    text,
                    rl.Rectangle(
                        int(SCREEN_WIDTH / 2 - BUTTON_WIDTH / 2),
                        int(BOTTOM_SECTION_Y_START + BOTTOM_PADDING + i * (BUTTON_HEIGHT + BUTTON_SPACING)),
                        int(BUTTON_WIDTH),
                        int(BUTTON_HEIGHT),
                    ),
                    i == 0,
                )
            )
        return buttons


class Logo:
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
    def buttons(
        buttons: list[HomeButton],
        mouse_pressed: bool,
        mouse_position: rl.Vector2
    ) -> str | None:
        for b in buttons:
            b.draw()
            if rl.check_collision_point_rec(mouse_position, b.rectangle):
                if mouse_pressed:
                    return b.text
                rl.draw_rectangle_lines_ex(
                    b.rectangle,
                    10,
                    rl.BLACK,
                )
        return None

    @classmethod
    def run(cls) -> str | None:
        buttons: list[HomeButton] = HomeButton.create(["play", "score", "exit"])
        clicked_button: str | None = None
        while not rl.window_should_close():
            mouse_click = rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)
            mouse_pos = rl.get_mouse_position()
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            Logo.draw()
            clicked_button = cls.buttons(buttons, mouse_click, mouse_pos)
            rl.end_drawing()
            if clicked_button is None:
                continue
            elif clicked_button == "score":
                LeaderBoardPage.draw()
            elif clicked_button == "play":
                raise NotImplementedError
            else:
                return None
        else:
            return None

import pyray as rl

rl.init_window(10, 10, "Pacman")

SCREEN_WIDTH = rl.get_monitor_width(rl.get_current_monitor())
SCREEN_HEIGHT = rl.get_monitor_height(rl.get_current_monitor())
rl.set_window_size(SCREEN_WIDTH, SCREEN_HEIGHT)

# bottom consts
BOTTOM_SECTION_HEIGHT = SCREEN_HEIGHT * 65 / 100
BOTTOM_PADDING = SCREEN_WIDTH * 7 / 100
BUTTON_SPACING = 15


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
        font_size = int((self.rectangle.height - 15) // 2)
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
        BUTTON_HEIGHT = (BOTTOM_SECTION_HEIGHT - BOTTOM_PADDING * 2 + BUTTON_SPACING * len(options)) / len(options)
        BUTTON_WIDTH = BUTTON_HEIGHT * 3
        buttons = []
        for i, text in enumerate(options):
            buttons.append(
                cls(
                    text,
                    rl.Rectangle(
                        int(SCREEN_WIDTH / 2 - BUTTON_WIDTH / 2),
                        int(SCREEN_HEIGHT
                        - BOTTOM_SECTION_HEIGHT
                        + BOTTOM_PADDING
                        + i * (BUTTON_HEIGHT + BUTTON_SPACING)),
                        int(BUTTON_WIDTH),
                        int(BUTTON_HEIGHT),
                    ),
                    i == 0,
                )
            )
        return buttons


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


        

    @classmethod
    def run(cls) -> str | None:
        buttons: list[HomeButton] = HomeButton.create(["play", "score", "exit"])
        clicked_button:str | None = None
        while not rl.window_should_close():
            rl.begin_drawing()
            rl.clear_background(rl.BLACK)
            clicked_button = cls.buttons(
                buttons,
                rl.is_mouse_button_pressed(rl.MOUSE_BUTTON_LEFT),
                rl.get_mouse_position()
            )

            rl.end_drawing()
            if clicked_button is None:
                continue
            elif clicked_button == "score":
                raise NotImplementedError
            else:
                break
        return clicked_button



if __name__ == "__main__":
    HomePage.run()

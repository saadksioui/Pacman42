from mazegenerator import MazeGenerator

from .gui import HomePage, SaveScorePage


if __name__ == "__main__":
    from .game_gui import GameLoop, MazeRender
    mz = MazeRender(MazeGenerator().maze)
    GameLoop(mz).run()

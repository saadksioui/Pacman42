import sys
from pydantic import ValidationError # type: ignore
from paclib.errors import ArgumentError
from paclib.parser import ConfigParser
from paclib.game_loop import Game
from paclib.tem_vis import run_visualizer
from paclib.maze_wrapper import maze_generator

def main():
    try:
        arguments = sys.argv
        if len(arguments) != 2:
            raise ArgumentError("The program must be launched from the command "
                                "line as follows:\n`python3 pac-man.py config.json`")
        config_file_path = arguments[1]
        parser = ConfigParser(config_file_path)
        config = parser.generate()
        print(config)
        """
            maze object attributes:
                - maze: grid
                - (_entryx, _entryy): entry point position
                - (maze._exitx, maze._exity): exit point position
                - (_width, _height): width and height of the maze
                - _perfect: bool attribute that makes the maze perfect
                - _seed: int value to generate the same maze
                - _path: list of positions from entry to exit
        """
        maze = maze_generator()
        game = Game(maze, config)
        game.run()

    except ValidationError as e:
        errors = e.errors()
        for err in errors:
            print(f"Error: {err['loc'][0]} ({err['type']}): {err['msg']}")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()

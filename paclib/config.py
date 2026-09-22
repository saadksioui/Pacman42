from json import JSONDecodeError
from json import loads as check_valid_json
from pydantic import BaseModel, Field, ValidationError
import random
import sys


class Level(BaseModel):
    """Defines the width and height dimensions
    for an individual maze level."""
    width: int = 15
    height: int = 15


class Config(BaseModel):
    """Parses, validates, and stores global game
    configurations from a JSON file."""
    highscore_path: str = "highscores.json"
    levels: list[Level] = Field(
        default=[Level() for _ in range(10)],
        min_length=10
    )
    lives: int = Field(default=3, gt=0)
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = random.randint(0, 10**10)
    level_max_time: int = 90

    @classmethod
    def get_config(cls, file_path: str) -> "Config":
        """Loads and converts configuration data
        from the given JSON file path."""
        try:
            with open(file_path, "r") as file:
                return cls._convert_data(file.read())
        except OSError as e:
            print("OSError:", e)
            exit(1)
        except JSONDecodeError:
            print("JSON: unvalid json")
            exit(1)
        except ValidationError:
            print(f"Warning: using default because {file_path} is broken")
            return Config()

    @classmethod
    def _convert_data(cls, json_data: str) -> "Config":
        """Strips comments from JSON string
        and validates it against the schema."""
        def sanitize_json(json_with_comments: str) -> str:
            """Removes single-line and hash comments
            from the JSON raw content."""
            new_str = ""
            for ln in json_with_comments.split("\n"):
                if ln.lstrip(" \t").startswith(("//", "#")):
                    continue
                new_str += ln + "\n"
            return new_str
        json_data = sanitize_json(json_data)
        check_valid_json(json_data)
        return cls.model_validate_json(json_data)


if len(sys.argv) != 2:
    print("The program must be launched from the command", end=" ")
    print("line as follows:\n`python3 pac-man.py config.json`")
    exit(1)

CONFIG = Config.get_config(sys.argv[1])

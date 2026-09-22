from json import JSONDecodeError
from json import loads as check_valid_json
from pydantic import BaseModel, Field, ValidationError
import random
import sys


class Level(BaseModel):
    width: int = 15
    height: int = 15


class Config(BaseModel):
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
        def sanitize_json(json_with_comments: str) -> str:
            new_str = ""
            for ln in json_with_comments.split("\n"):
                if ln.lstrip(" \t").startswith(("//", "#")):
                    continue
                new_str += ln + "\n"
            return new_str
        json_data = sanitize_json(json_data)
        check_valid_json(json_data)
        return cls.model_validate_json(json_data)


# if len(sys.argv) != 2:
#     print("The program must be launched from the command", end=" ")
#     print("line as follows:\n`python3 pac-man.py config.json`")
#     exit(1)

# CONFIG = Config.get_config(sys.argv[1])
config_path = sys.argv[1] if len(sys.argv) == 2 else "config.json"
CONFIG = Config.get_config(config_path)

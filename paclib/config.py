from json import JSONDecodeError
from json import loads as check_valid_json
from pydantic import BaseModel, Field, ValidationError # type: ignore
import random


class Level(BaseModel):
    width: int = 300
    height: int = 300
    level_max_time: int = 90


class Config(BaseModel):
    highscore_path: str = "scores.json"
    levels: list[Level] = Field(
        default=[Level() for _ in range(10)],
        min_length=10
    )
    lives: int = 3
    pacgum: int = 42
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    seed: int = random.randint(0, 10**10)

    @classmethod
    def get_config(cls, file_path: str) -> "Config" | None:
        try:
            with open(file_path, "r") as file:
                return cls._convert_data(file.read())
        except OSError as e:
            print("OSError:", e)
            return None
        except JSONDecodeError:
            print("JSON: unvalid json")
            return None
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


if __name__ == "__main__":
    if Config.get_config("config.json") is None:
        exit(1)

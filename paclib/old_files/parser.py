import json
import os
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Config:
    seed: int = 42
    lives: int = 3
    level_max_time: int = 90
    points_per_pacgum: int = 10
    points_per_super_pacgum: int = 50
    points_per_ghost: int = 200
    highscore_filename: str = "highscores.json"
    levels: List[Dict[str, int]] = field(default_factory=lambda: [{"width": 15, "height": 15}])

class ConfigParser:
    def __init__(self, file: str):
        self.file = file
        self.default_config = Config()

    def generate(self):
        if not os.path.exists(self.file):
            print(f"Warning: Config file '{self.file}' not found. Using safe defaults.")
            return self.default_config

        with open(self.file, 'r') as f:
            data = f.read()
        data_no_comments = ""
        lines = data.split("\n")
        for line in lines:
            no_space = line.strip()
            if no_space.startswith(('#', '//')):
                continue
            data_no_comments += f"{line}\n"
        data_no_comments = json.loads(data_no_comments)
        config = Config(**data_no_comments)
        return config

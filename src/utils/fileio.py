import json

from json import JSONDecodeError
from pathlib import Path
from typing import Any


def read_json_file(path: Path) -> Any:
    try:
        with open(path, "r") as f:
            return json.load(f)

    except (FileNotFoundError, JSONDecodeError):
        return None

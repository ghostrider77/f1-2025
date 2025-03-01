import tomllib

from pathlib import Path
from typing import Any

from .models import DatabaseConfig, ServiceConfig, WebConfig
from .. import PACKAGE_DIR


def parse_config_file(folder: Path, filename: str) -> dict[str, Any]:
    try:
        with open(folder / filename, "rb") as f:
            return tomllib.load(f)

    except FileNotFoundError:
        return {}


def read_service_config(filename: str) -> ServiceConfig:
    config_folder = Path(PACKAGE_DIR.parent)
    config_dict = parse_config_file(config_folder, filename)

    database_config = config_dict.get("database", {})
    web_config = config_dict.get("web", {})

    return ServiceConfig(
        database=DatabaseConfig(**database_config),
        web=WebConfig.model_validate(web_config),
    )


SERVICE_CONFIG = read_service_config("config.toml")

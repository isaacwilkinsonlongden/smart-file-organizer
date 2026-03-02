import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from .categorizer import EXT_TO_CATEGORY

APP_DIR = "smart-file-organizer"
CONFIG_FILE = "config.toml"

@dataclass
class Config:
    ext_to_category: dict[str, str]
    fallback_category: str | None

def resolve_config() -> Config:
    merge_default_categories = True
    fallback_category = "Other"
    config_path = get_config_path()
    config_extensions = load_user_config_extensions(config_path)
    config_general = load_user_config_general(config_path)
    config = Config(
        ext_to_category=EXT_TO_CATEGORY.copy(),
        fallback_category=fallback_category
        )
    if config_path.exists():
        merge_default_categories = config_general.get(
            "merge_default_categories",
            True,
        )
        fallback_category = config_general.get("fallback_category", "Other")
        if not merge_default_categories:
            config.ext_to_category = {}
        config.ext_to_category.update(config_extensions)
        config.fallback_category = fallback_category
    return config

def get_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        base = Path(xdg)
    else:
        base = Path.home() / ".config"
    return base / APP_DIR / CONFIG_FILE

def load_user_config_extensions(path: Path) -> dict[str, str]:
    extensions = {}
    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        for ext in data["extensions"]:
            if ext[0] != ".":
                new_ext = f".{ext}"
            extensions[new_ext].lower() = data["extensions"][ext]
        return extensions  
    return {}

def load_user_config_general(path: Path) -> dict[str, str]:
    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return data["general"]
    return {}


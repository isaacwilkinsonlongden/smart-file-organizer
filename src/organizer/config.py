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


class ConfigError(Exception):
    pass


def resolve_config() -> Config:
    # Program defaults (current behavior if no config file exists)
    merge_default_categories: bool = True
    fallback_category: str | None = "Other"

    config_path = get_config_path()
    user_config = load_user_config(config_path)

    # Validate top-level TOML structure
    if not isinstance(user_config, dict):
        raise ConfigError(
            f"Config root must be a table/dict, got {type(user_config).__name__}."
        )

    config_general = user_config.get("general", {})
    config_extensions = user_config.get("extensions", {})

    # Validate sections
    if config_general is None:
        config_general = {}
    if not isinstance(config_general, dict):
        raise ConfigError(
            f"Config [general] must be a table/dict, got {type(config_general).__name__}."
        )

    if config_extensions is None:
        config_extensions = {}
    if not isinstance(config_extensions, dict):
        raise ConfigError(
            f"Config [extensions] must be a table/dict, got {type(config_extensions).__name__}."
        )

    # Apply [general]
    if config_general:
        mdc = config_general.get("merge_default_categories", True)
        if not isinstance(mdc, bool):
            raise ConfigError(
                "general.merge_default_categories must be a boolean (true/false). "
                f"Got {mdc!r} ({type(mdc).__name__})."
            )
        merge_default_categories = mdc

        fc = config_general.get("fallback_category", "Other")
        if fc is None:
            fallback_category = None
        elif isinstance(fc, str):
            fc = fc.strip()
            if fc == "":
                raise ConfigError(
                    "general.fallback_category cannot be an empty string. "
                    "Use a non-empty string (e.g. \"Other\") or null."
                )
            if "/" in fc or "\\" in fc:
                raise ConfigError(
                    "general.fallback_category cannot contain path separators ('/' or '\\')."
                )
            fallback_category = fc
        else:
            raise ConfigError(
                "general.fallback_category must be a string or null. "
                f"Got {fc!r} ({type(fc).__name__})."
            )

    # Build base mapping
    ext_to_category: dict[str, str]
    if merge_default_categories:
        ext_to_category = EXT_TO_CATEGORY.copy()
    else:
        ext_to_category = {}

    # Apply [extensions]
    if config_extensions:
        normalized = normalize_extensions(config_extensions)
        ext_to_category.update(normalized)

    return Config(ext_to_category=ext_to_category, fallback_category=fallback_category)


def get_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        base = Path(xdg)
    else:
        base = Path.home() / ".config"
    return base / APP_DIR / CONFIG_FILE


def normalize_extensions(extensions: dict) -> dict[str, str]:
    """
    Normalize user-provided extensions mapping:
    - keys must be strings
    - values must be strings (folder/category names)
    - extension keys are lowercased, stripped, and forced to start with '.'
    """
    if not isinstance(extensions, dict):
        raise ConfigError(
            f"extensions must be a table/dict, got {type(extensions).__name__}."
        )

    new_extensions: dict[str, str] = {}
    for ext, category in extensions.items():
        if not isinstance(ext, str):
            raise ConfigError(
                "extensions keys must be strings like \".mp3\". "
                f"Got key {ext!r} ({type(ext).__name__})."
            )
        if not isinstance(category, str):
            raise ConfigError(
                "extensions values must be strings (folder/category names). "
                f"For key {ext!r}, got {category!r} ({type(category).__name__})."
            )

        ext_norm = ext.strip().lower()
        if ext_norm == "":
            raise ConfigError("extensions contains an empty extension key.")
        if not ext_norm.startswith("."):
            ext_norm = "." + ext_norm

        cat_norm = category.strip()
        if cat_norm == "":
            raise ConfigError(f"extensions[{ext!r}] maps to an empty category name.")
        if "/" in cat_norm or "\\" in cat_norm:
            raise ConfigError(
                f"extensions[{ext!r}] category cannot contain path separators ('/' or '\\')."
            )

        new_extensions[ext_norm] = cat_norm

    return new_extensions


def load_user_config(path: Path) -> dict:
    if not path.exists():
        return {}

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"Invalid TOML in {path}: {e}") from e
    except OSError as e:
        raise ConfigError(f"Unable to read config file {path}: {e}") from e

    if not isinstance(data, dict):
        raise ConfigError(
            f"Config file {path} must contain a TOML table at the top level."
        )
    return data

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
    fallback_category: str
    use_fallback_category: bool


class ConfigError(Exception):
    pass


def resolve_config() -> Config:
    merge_default_categories = True
    fallback_category = "Other"
    use_fallback_category = True

    config_path = get_config_path()
    user_config = load_user_config(config_path)

    if not isinstance(user_config, dict):
        raise ConfigError(
            f"Config root must be a table/dict, got {type(user_config).__name__}."
        )

    config_general = user_config.get("general", {})
    config_extensions = user_config.get("extensions", {})

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

    if config_general:
        merge_default_categories = _validate_merge_default_categories(
            config_general.get("merge_default_categories", True)
        )
        fallback_category = _validate_fallback_category(
            config_general.get("fallback_category", "Other")
        )
        use_fallback_category = _validate_use_fallback_category(
            config_general.get("use_fallback_category", True)
        )

    if merge_default_categories:
        ext_to_category = EXT_TO_CATEGORY.copy()
    else:
        ext_to_category = {}

    if config_extensions:
        ext_to_category.update(normalize_extensions(config_extensions))

    return Config(
        ext_to_category=ext_to_category,
        fallback_category=fallback_category,
        use_fallback_category=use_fallback_category,
    )


def get_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        base = Path(xdg)
    else:
        base = Path.home() / ".config"
    return base / APP_DIR / CONFIG_FILE


def normalize_extensions(extensions: dict) -> dict[str, str]:
    if not isinstance(extensions, dict):
        raise ConfigError(
            f"extensions must be a table/dict, got {type(extensions).__name__}."
        )

    new_extensions: dict[str, str] = {}
    for ext, category in extensions.items():
        ext_norm = _normalize_ext(ext)
        cat_norm = _normalize_category(category, ext)
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


def init_config() -> Path:
    path = get_config_path()
    if path.exists():
        raise ConfigError(
            f"Config file already exists at {path}. "
            "Use organize config reset to overwrite"
        )

    return _write_text_config(path, _default_user_config_text())


def reset_config_default() -> Path:
    path = get_config_path()
    return _write_text_config(path, _default_user_config_text())


def reset_config_blank() -> Path:
    path = get_config_path()
    return _write_text_config(path, _blank_user_config_text())


def show_config() -> str:
    path = get_config_path()
    if not path.exists():
        return "No config file exists yet. Run 'organize config init' to create one\n"

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise ConfigError(f"Unable to read config file {path}: {e}") from e

    if not text.endswith("\n"):
        text += "\n"
    return text


def set_extension(ext: str, category: str) -> Path:
    path = get_config_path()
    if not path.exists():
        init_config()

    data = load_user_config(path)
    general = _get_general_with_defaults(data)
    extensions = _get_extensions_table(data)

    ext_norm = _normalize_ext(ext)
    cat_norm = _normalize_category(category, ext_norm)
    extensions[ext_norm] = cat_norm

    _write_user_config(path, general, extensions)
    return path


def unset_extension(ext: str) -> Path:
    path = get_config_path()
    if not path.exists():
        raise ConfigError("No config file exists. Run 'organize config init' first")

    data = load_user_config(path)
    general = _get_general_with_defaults(data)
    extensions = _get_extensions_table(data)

    ext_norm = _normalize_ext(ext)
    if ext_norm not in extensions:
        return path

    extensions.pop(ext_norm)
    _write_user_config(path, general, extensions)
    return path


def _get_general_with_defaults(data: dict) -> dict:
    general = data.get("general", {})
    if not isinstance(general, dict):
        raise ConfigError("[general] must be a table")

    general = general.copy()
    general.setdefault("merge_default_categories", True)
    general.setdefault("use_fallback_category", True)
    general.setdefault("fallback_category", "Other")
    return general


def _get_extensions_table(data: dict) -> dict:
    extensions = data.get("extensions", {})
    if not isinstance(extensions, dict):
        raise ConfigError("[extensions] must be a table")
    return extensions.copy()


def _write_user_config(path: Path, general: dict, extensions: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    general_lines = ["[general]"]
    for key in sorted(general):
        general_lines.append(f"{key} = {_toml_value(general[key])}")

    extensions_lines = ["[extensions]"]
    for key in sorted(extensions):
        extensions_lines.append(f'"{key}" = {_toml_value(extensions[key])}')

    content = "\n".join(general_lines + [""] + extensions_lines) + "\n"

    try:
        path.write_text(content, encoding="utf-8")
    except OSError as e:
        raise ConfigError(f"Unable to write config file {path}: {e}") from e


def _write_text_config(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text(content, encoding="utf-8")
    except OSError as e:
        raise ConfigError(f"Unable to write config file {path}: {e}") from e
    return path


def _default_user_config_text() -> str:
    return """[general]
merge_default_categories = true
use_fallback_category = true
fallback_category = "Other"

[extensions]
# Add overrides like:
# ".mp3" = "MP3"
"""


def _blank_user_config_text() -> str:
    return """[general]
merge_default_categories = false
use_fallback_category = false
fallback_category = "Other"

[extensions]
# Add overrides like:
# ".mp3" = "MP3"
"""


def _validate_merge_default_categories(value) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(
            "general.merge_default_categories must be a boolean (true/false). "
            f"Got {value!r} ({type(value).__name__})."
        )
    return value


def _validate_use_fallback_category(value) -> bool:
    if not isinstance(value, bool):
        raise ConfigError(
            "general.use_fallback_category must be a bool. "
            f"got {value!r} ({type(value).__name__})"
        )
    return value


def _validate_fallback_category(value) -> str:
    if not isinstance(value, str):
        raise ConfigError(
            "general.fallback_category must be a string. "
            f"Got {value!r} ({type(value).__name__})."
        )

    value = value.strip()
    if value == "":
        raise ConfigError(
            "general.fallback_category cannot be an empty string. "
            'Use a non-empty string (e.g. "Other").'
        )
    if "/" in value or "\\" in value:
        raise ConfigError(
            "general.fallback_category cannot contain path separators ('/' or '\\')."
        )
    return value


def _toml_value(v):
    if v is True:
        return "true"
    if v is False:
        return "false"
    if v is None:
        return "null"
    if isinstance(v, str):
        escaped = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'

    raise ConfigError(
        "Unsupported value type in config. Expected bool, null, or string; "
        f"Got {type(v).__name__}: {v!r}"
    )


def _normalize_ext(ext: str) -> str:
    if not isinstance(ext, str):
        raise ConfigError(
            'extensions keys must be strings like ".mp3". '
            f"Got key {ext!r} ({type(ext).__name__})."
        )

    ext_norm = ext.strip().lower()
    if ext_norm == "":
        raise ConfigError("extensions contains an empty extension key.")
    if not ext_norm.startswith("."):
        ext_norm = "." + ext_norm
    return ext_norm


def _normalize_category(category: str, ext: str) -> str:
    if not isinstance(category, str):
        raise ConfigError(
            "extensions values must be strings (folder/category names). "
            f"For key {ext!r}, got {category!r} ({type(category).__name__})."
        )

    cat_norm = category.strip()
    if cat_norm == "":
        raise ConfigError(f"extensions[{ext!r}] maps to an empty category name.")
    if "/" in cat_norm or "\\" in cat_norm:
        raise ConfigError(
            f"extensions[{ext!r}] category cannot contain path separators ('/' or '\\')."
        )
    return cat_norm


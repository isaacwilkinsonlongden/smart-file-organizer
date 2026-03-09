from pathlib import Path

import pytest

from organizer.config import (
    resolve_config,
    get_config_path,
    init_config,
    reset_config_default,
    reset_config_blank,
    set_extension,
    unset_extension,
    show_config,
)


def test_resolve_config_without_file_uses_defaults(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    config = resolve_config()

    assert config.use_fallback_category is True
    assert config.fallback_category == "Other"
    assert ".jpg" in config.ext_to_category


def test_init_config_creates_file(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    path = init_config()

    assert path.exists()
    assert path.read_text()


def test_set_extension_adds_mapping(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()
    set_extension(".mp3", "Music")

    config = resolve_config()

    assert config.ext_to_category[".mp3"] == "Music"


def test_set_extension_normalizes_extension(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()
    set_extension("MP3", "Music")

    config = resolve_config()

    assert config.ext_to_category[".mp3"] == "Music"


def test_unset_extension_removes_mapping(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()
    set_extension(".mp3", "Music")

    unset_extension(".mp3")

    config = resolve_config()

    assert config.ext_to_category[".mp3"] == "Audio"


def test_unset_extension_removes_mapping_from_user_config(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()
    set_extension(".mp3", "Music")
    unset_extension(".mp3")

    text = show_config()

    assert '".mp3" = "Music"' not in text


def test_unset_extension_missing_key_is_noop(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()

    # should not raise
    unset_extension(".doesnotexist")


def test_show_config_returns_text(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()

    text = show_config()

    assert "[general]" in text
    assert "[extensions]" in text


def test_show_config_when_missing(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    text = show_config()

    assert "No config file exists yet" in text


def test_reset_default(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    reset_config_default()

    config = resolve_config()

    assert config.use_fallback_category is True
    assert config.fallback_category == "Other"


def test_reset_blank(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    reset_config_blank()

    config = resolve_config()

    assert config.use_fallback_category is False


def test_invalid_extension_key(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    init_config()

    with pytest.raises(Exception):
        set_extension("", "Music")
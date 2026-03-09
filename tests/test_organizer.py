from pathlib import Path

from organizer.organizer import plan_moves
from organizer.config import resolve_config


def test_plan_moves_creates_correct_destination(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    files = [file_path]

    config = resolve_config()
    moves = plan_moves(tmp_path, files, config)

    assert len(moves) == 1

    move = moves[0]

    assert move.destination == tmp_path / "Images" / "photo.jpg"
    assert move.category == "Images"


def test_plan_moves_skips_unmapped_when_no_fallback(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "unknown.xyz"
    file_path.touch()

    config = resolve_config()
    config.use_fallback_category = False

    moves = plan_moves(tmp_path, [file_path], config)

    assert moves == []


def test_plan_moves_multiple_files(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    img = tmp_path / "photo.jpg"
    doc = tmp_path / "file.pdf"

    img.touch()
    doc.touch()

    config = resolve_config()

    moves = plan_moves(tmp_path, [img, doc], config)

    destinations = {m.destination for m in moves}

    assert tmp_path / "Images" / "photo.jpg" in destinations
    assert tmp_path / "Documents" / "file.pdf" in destinations
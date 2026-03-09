import pytest
from organizer.executor import execute_moves
from organizer.organizer import plan_moves
from organizer.config import resolve_config


def test_execute_moves_dry_run_does_not_move(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config)

    result = execute_moves(moves, dry_run=True)

    assert len(result.moved) == 1
    assert file_path.exists()
    assert not (tmp_path / "Images" / "photo.jpg").exists()


def test_execute_moves_moves_file(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config)

    result = execute_moves(moves, dry_run=False)

    assert len(result.moved) == 1
    assert not file_path.exists()
    assert (tmp_path / "Images" / "photo.jpg").exists()


def test_execute_moves_skips_existing_destination(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    dest_dir = tmp_path / "Images"
    dest_dir.mkdir()
    (dest_dir / "photo.jpg").touch()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config)

    result = execute_moves(
        moves,
        dry_run=False,
        collision_policy="skip",
    )

    assert len(result.moved) == 0
    assert len(result.skipped) == 1
    assert file_path.exists()


def test_execute_moves_renames_on_collision(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    dest_dir = tmp_path / "Images"
    dest_dir.mkdir()
    (dest_dir / "photo.jpg").touch()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config)

    result = execute_moves(
        moves,
        dry_run=False,
        collision_policy="rename",
    )

    assert len(result.moved) == 1
    assert not file_path.exists()

    assert (dest_dir / "photo.jpg").exists()
    assert (dest_dir / "photo (1).jpg").exists()


def test_execute_moves_fail_on_collision(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    dest_dir = tmp_path / "Images"
    dest_dir.mkdir()
    (dest_dir / "photo.jpg").touch()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config)

    with pytest.raises(FileExistsError):
        execute_moves(
            moves,
            dry_run=False,
            collision_policy="fail",
        )
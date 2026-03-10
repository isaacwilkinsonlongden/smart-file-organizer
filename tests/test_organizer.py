from organizer.config import resolve_config
from organizer.organizer import plan_moves


def test_plan_moves_creates_correct_destination(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config)

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


def test_plan_moves_recursive_includes_nested_files(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    subdir = tmp_path / "subdir"
    subdir.mkdir()

    nested_file = subdir / "photo.jpg"
    nested_file.touch()

    config = resolve_config()

    moves = plan_moves(tmp_path, [nested_file], config, recursive=True)

    assert len(moves) == 1
    assert moves[0].destination == tmp_path / "Images" / "photo.jpg"


def test_plan_moves_recursive_skips_files_already_in_category(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    images_dir = tmp_path / "Images"
    images_dir.mkdir()

    file_path = images_dir / "photo.jpg"
    file_path.touch()

    config = resolve_config()

    moves = plan_moves(tmp_path, [file_path], config, recursive=True)

    assert moves == []


def test_plan_moves_recursive_skips_nested_category_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    subdir = tmp_path / "subdir"
    subdir.mkdir()

    images_dir = subdir / "Images"
    images_dir.mkdir()

    file_path = images_dir / "photo.jpg"
    file_path.touch()

    config = resolve_config()

    moves = plan_moves(tmp_path, [file_path], config, recursive=True)

    assert moves == []


def test_plan_moves_uses_custom_output_root(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    output_root = tmp_path / "organized"
    output_root.mkdir()

    config = resolve_config()
    moves = plan_moves(tmp_path, [file_path], config, output_root=output_root)

    assert len(moves) == 1
    assert moves[0].destination == output_root / "Images" / "photo.jpg"


def test_plan_moves_recursive_uses_custom_output_root(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    subdir = tmp_path / "subdir"
    subdir.mkdir()

    nested_file = subdir / "photo.jpg"
    nested_file.touch()

    output_root = tmp_path / "organized"
    output_root.mkdir()

    config = resolve_config()
    moves = plan_moves(
        tmp_path,
        [nested_file],
        config,
        output_root=output_root,
        recursive=True,
    )

    assert len(moves) == 1
    assert moves[0].destination == output_root / "Images" / "photo.jpg"
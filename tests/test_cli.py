from organizer.cli import main


def test_main_returns_zero_on_dry_run(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    (tmp_path / "photo.jpg").touch()

    exit_code = main(["run", str(tmp_path), "--dry-run"])

    assert exit_code == 0


def test_main_returns_zero_on_execution(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    (tmp_path / "photo.jpg").touch()

    exit_code = main(["run", str(tmp_path)])

    assert exit_code == 0


def test_main_returns_non_zero_on_fail_collision(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    (tmp_path / "photo.jpg").touch()

    dest_dir = tmp_path / "Images"
    dest_dir.mkdir()
    (dest_dir / "photo.jpg").touch()

    exit_code = main(["run", str(tmp_path), "--collision", "fail"])

    assert exit_code == 1


def test_main_returns_error_for_missing_directory(tmp_path):
    bad_path = tmp_path / "missing"

    exit_code = main(["run", str(bad_path)])

    assert exit_code == 1


def test_main_recursive_moves_nested_file(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    subdir = tmp_path / "subdir"
    subdir.mkdir()

    nested_file = subdir / "photo.jpg"
    nested_file.touch()

    exit_code = main(["run", str(tmp_path), "--recursive"])

    assert exit_code == 0
    assert not nested_file.exists()
    assert (tmp_path / "Images" / "photo.jpg").exists()


def test_main_recursive_skips_file_already_in_category(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    images_dir = tmp_path / "Images"
    images_dir.mkdir()

    file_path = images_dir / "photo.jpg"
    file_path.touch()

    exit_code = main(["run", str(tmp_path), "--recursive"])

    assert exit_code == 0
    assert file_path.exists()


def test_main_moves_to_custom_output_root(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    output_root = tmp_path / "organized"
    output_root.mkdir()

    exit_code = main(["run", str(tmp_path), "--output", str(output_root)])

    assert exit_code == 0
    assert not file_path.exists()
    assert (output_root / "Images" / "photo.jpg").exists()


def test_main_recursive_moves_nested_file_to_custom_output_root(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    subdir = tmp_path / "subdir"
    subdir.mkdir()

    nested_file = subdir / "photo.jpg"
    nested_file.touch()

    output_root = tmp_path / "organized"
    output_root.mkdir()

    exit_code = main(
        ["run", str(tmp_path), "--recursive", "--output", str(output_root)]
    )

    assert exit_code == 0
    assert not nested_file.exists()
    assert (output_root / "Images" / "photo.jpg").exists()


def test_main_returns_error_for_missing_output_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))

    (tmp_path / "photo.jpg").touch()
    missing_output = tmp_path / "missing_output"

    exit_code = main(["run", str(tmp_path), "--output", str(missing_output)])

    assert exit_code == 1
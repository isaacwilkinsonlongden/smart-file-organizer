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
from organizer.cli import main


def test_main_returns_zero_on_dry_run(tmp_path):
    (tmp_path / "photo.jpg").touch()

    exit_code = main([str(tmp_path), "--dry-run"])

    assert exit_code == 0


def test_main_returns_zero_on_execution(tmp_path):
    (tmp_path / "photo.jpg").touch()

    exit_code = main([str(tmp_path)])

    assert exit_code == 0
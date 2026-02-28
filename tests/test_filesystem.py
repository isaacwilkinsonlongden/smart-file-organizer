from organizer.filesystem import list_files


def test_list_files_returns_only_files(tmp_path):
    # Create files
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.jpg").touch()

    # Create directory
    (tmp_path / "subdir").mkdir()

    files = list_files(tmp_path)

    names = {f.name for f in files}

    assert names == {"a.txt", "b.jpg"}
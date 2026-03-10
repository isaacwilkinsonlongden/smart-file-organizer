from organizer.filesystem import list_files


def test_list_files_returns_only_files_non_recursive(tmp_path):
    # Create files
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.jpg"
    file_a.touch()
    file_b.touch()

    # Create directory
    (tmp_path / "subdir").mkdir()

    files = list_files(tmp_path)

    assert all(f.is_file() for f in files)
    names = {f.name for f in files}

    assert names == {"a.txt", "b.jpg"}


def test_list_files_skips_hidden_files_non_recursive(tmp_path):
    (tmp_path / "visible.txt").touch()
    (tmp_path / ".hidden.txt").touch()

    files = list_files(tmp_path)

    names = {f.name for f in files}

    assert names == {"visible.txt"}


def test_list_files_recursive_includes_child_files(tmp_path):
    (tmp_path / "top.txt").touch()

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.jpg").touch()

    files = list_files(tmp_path, recursive=True)

    rel_paths = {f.relative_to(tmp_path) for f in files}

    assert rel_paths == {
        (tmp_path / "top.txt").relative_to(tmp_path),
        (tmp_path / "subdir" / "nested.jpg").relative_to(tmp_path),
    }


def test_list_files_recursive_skips_hidden_files(tmp_path):
    (tmp_path / "visible.txt").touch()
    (tmp_path / ".hidden.txt").touch()

    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "nested.txt").touch()
    (subdir / ".hidden_nested.txt").touch()

    files = list_files(tmp_path, recursive=True)

    rel_paths = {f.relative_to(tmp_path) for f in files}

    assert rel_paths == {
        (tmp_path / "visible.txt").relative_to(tmp_path),
        (tmp_path / "subdir" / "nested.txt").relative_to(tmp_path),
    }


def test_list_files_recursive_skips_hidden_directories(tmp_path):
    (tmp_path / "visible.txt").touch()

    hidden_dir = tmp_path / ".hidden_dir"
    hidden_dir.mkdir()
    (hidden_dir / "secret.txt").touch()

    normal_dir = tmp_path / "subdir"
    normal_dir.mkdir()
    (normal_dir / "nested.txt").touch()

    files = list_files(tmp_path, recursive=True)

    rel_paths = {f.relative_to(tmp_path) for f in files}

    assert rel_paths == {
        (tmp_path / "visible.txt").relative_to(tmp_path),
        (tmp_path / "subdir" / "nested.txt").relative_to(tmp_path),
    }


def test_list_files_returns_sorted_paths(tmp_path):
    (tmp_path / "b.txt").touch()
    (tmp_path / "a.txt").touch()

    files = list_files(tmp_path)

    names = [f.name for f in files]

    assert names == ["a.txt", "b.txt"]
from pathlib import Path
from organizer.filesystem import list_files


def test_list_files_returns_only_files(tmp_path):
    # Create files
    file_a = tmp_path / "a.txt"
    file_b = tmp_path / "b.jpg"
    file_a.touch()
    file_b.touch()

    # Create directory
    (tmp_path / "subdir").mkdir()

    files = list_files(tmp_path)

    # All returned items should be files
    assert all(f.is_file() for f in files)

    names = {f.name for f in files}

    assert names == {"a.txt", "b.jpg"}
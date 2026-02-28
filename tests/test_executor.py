from organizer.executor import execute_moves
from organizer.organizer import plan_moves


def test_execute_moves_dry_run_does_not_move(tmp_path):
    # Arrange
    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    moves = plan_moves(tmp_path, [file_path])

    # Act
    result = execute_moves(moves, dry_run=True)

    # Assert
    assert len(result.moved) == 1
    assert file_path.exists()  # file should still exist
    assert not (tmp_path / "Images" / "photo.jpg").exists()


def test_execute_moves_moves_file(tmp_path):
    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    moves = plan_moves(tmp_path, [file_path])

    result = execute_moves(moves, dry_run=False)

    assert len(result.moved) == 1
    assert not file_path.exists()
    assert (tmp_path / "Images" / "photo.jpg").exists()


def test_execute_moves_skips_existing_destination(tmp_path):
    # Create original file
    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    # Create destination file to force collision
    dest_dir = tmp_path / "Images"
    dest_dir.mkdir()
    (dest_dir / "photo.jpg").touch()

    moves = plan_moves(tmp_path, [file_path])

    result = execute_moves(moves, dry_run=False)

    assert len(result.skipped) == 1
    assert file_path.exists()  # original should remain
from pathlib import Path
from organizer.organizer import plan_moves


def test_plan_moves_creates_correct_destination(tmp_path):
    # Create file
    file_path = tmp_path / "photo.jpg"
    file_path.touch()

    files = [file_path]

    moves = plan_moves(tmp_path, files)

    assert len(moves) == 1

    move = moves[0]

    assert move.destination == tmp_path / "Images" / "photo.jpg"
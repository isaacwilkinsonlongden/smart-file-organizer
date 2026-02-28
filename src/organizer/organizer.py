from dataclasses import dataclass
from pathlib import Path

from .categorizer import get_category

@dataclass
class PlannedMove:
    source: Path
    destination: Path
    category: str

def plan_moves(directory: Path, files: list[Path]) -> list[PlannedMove]:
    planned_moves = []
    for file in files:
        category = get_category(file)
        destination = directory / category / file.name
        planned_moves.append(PlannedMove(
            source=file,
            destination=destination,
            category=category
        ))
    return planned_moves

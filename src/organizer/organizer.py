from dataclasses import dataclass
from pathlib import Path

from .categorizer import get_category
from .config import Config

@dataclass
class PlannedMove:
    source: Path
    destination: Path
    category: str

def plan_moves(
        directory: Path, 
        files: list[Path],
        config: Config
    ) -> list[PlannedMove]:
    planned_moves = []
    for file in files:
        category = get_category(file, config)
        destination = directory / category / file.name
        planned_moves.append(PlannedMove(
            source=file,
            destination=destination,
            category=category
        ))
    return planned_moves

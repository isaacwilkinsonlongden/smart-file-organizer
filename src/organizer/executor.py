from dataclasses import dataclass
from pathlib import Path
import shutil

from .organizer import PlannedMove

@dataclass
class ExecutionResult:
    moved: list[PlannedMove]
    skipped: list[PlannedMove]

def execute_moves(
        moves: list[PlannedMove],
        dry_run: bool = False
    ) -> ExecutionResult:
    result = ExecutionResult(moved=[], skipped=[])
    for move in moves:
        if move.destination.exists():
            result.skipped.append(move)
            continue
        if not dry_run:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(move.source, move.destination)
        result.moved.append(move)
    return result

        
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
        dry_run: bool = False,
        collision_policy: str = "rename",
    ) -> ExecutionResult:
    result = ExecutionResult(moved=[], skipped=[])
    for move in moves:
        if move.destination.exists():
            if collision_policy == "rename":
                move.destination = generate_renamed_path(move.destination)
            elif collision_policy == "skip":
                result.skipped.append(move)
                continue
            elif collision_policy == "fail":
                raise FileExistsError (
                    f"Collision detected at {move.destination}"
                )       
        if not dry_run:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(move.source, move.destination)
        result.moved.append(move)
    return result

def generate_renamed_path(destination: Path) -> Path:
    n = 1
    stem = destination.stem
    suffix = destination.suffix
    while True:
        candidate = destination.with_name(f"{stem} ({n}){suffix}")
        if not candidate.exists():
            return candidate
        n += 1


        
import argparse
import sys

from pathlib import Path

from .filesystem import list_files
from .organizer import plan_moves, PlannedMove

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    directory = Path(args.directory).expanduser().resolve()
    if not validate_directory(directory):
        return 1
    files = list_files(directory)
    planned_moves = plan_moves(directory, files)
    if not planned_moves:
        print("Nothing to organize.")
        return 0
    grouped = group_moves(planned_moves)
    if args.dry_run:
        print_dry_run(files, planned_moves, grouped, directory)
    return 0

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser()
    return parser.parse_args(argv)

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Organize files in a directory by category"
    ) 
    parser.add_argument("directory", help="Target directory to organize")
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Preview changes without moving files"
    )
    return parser 

def validate_directory(directory: Path) -> bool:
    if not directory.exists():
        print(f"Error: path does not exist: {directory}", file=sys.stderr)
        return False
    if not directory.is_dir():
        print(f"Error: path is not a directory: {directory}", file=sys.stderr)
        return False
    return True

def group_moves(planned_moves: list[PlannedMove]) -> dict[str, list[PlannedMove]]:
    grouped = {}
    for move in planned_moves:
        grouped.setdefault(move.category, []).append(move)
    return grouped

def print_dry_run(
        files: list[Path],
        planned_moves: list[PlannedMove],
        grouped: dict[str, list[PlannedMove]],
        directory: Path,
) -> None:
    print()
    print(f"Scanned {len(files)} files.")
    print(f"Found {len(planned_moves)} files to move.")
    for category in sorted(
        grouped,
        key=lambda c: (c == "Other", c)
    ):
        moves = grouped[category]
        print()
        for move in moves:
            print(
                f"{directory.name}/{move.source.relative_to(directory)} "
                f"-> {directory.name}/{move.destination.relative_to(directory)}"
            )
        
if __name__ == "__main__":
    sys.exit(main())


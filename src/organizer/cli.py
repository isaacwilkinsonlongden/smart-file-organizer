import argparse
import sys

from pathlib import Path

from .filesystem import list_files
from .organizer import plan_moves, PlannedMove

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    directory = Path(args.directory).expanduser().resolve()
    if not directory.exists():
        print(f"Error: path does not exist: {directory}", file=sys.stderr)
        return 1
    if not directory.is_dir():
        print(f"Error: path is not a directory: {directory}", file=sys.stderr)
        return 1
    files = list_files(directory)
    planned_moves = plan_moves(directory, files)
    if not planned_moves:
        print("Nothing to organize.")
        return 0
    grouped = group_moves(planned_moves)
    if args.dry_run:
        print()
        print(f"Scanned {len(files)} files.")
        print(f"Found {len(planned_moves)} files to move.")
        for category in sorted(
            grouped,
            key=lambda category: (category == "Other", category)
        ):
            moves = grouped[category]
            print()
            for move in moves:
                print(
                    f"{directory.name}/{move.source.relative_to(directory)} "
                    f"-> {directory.name}/{move.destination.relative_to(directory)}"
                )
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

def group_moves(planned_moves: list[PlannedMove]) -> dict[str, list[PlannedMove]]:
    grouped = {}
    for move in planned_moves:
        grouped.setdefault(move.category, []).append(move)
    return grouped

if __name__ == "__main__":
    sys.exit(main())


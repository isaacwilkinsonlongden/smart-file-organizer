import argparse
import sys

from pathlib import Path

from .filesystem import list_files
from .organizer import plan_moves, PlannedMove
from .executor import execute_moves, ExecutionResult
from .config import resolve_config, get_config_path

def run() -> None:
    raise SystemExit(main())

def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        print("Usage: organize <directory> or organize config <command>")
        return 1
    if argv[0] == "config":
        args = parse_args_config(argv[1:])
        if args.command == "path":
            print(get_config_path())
            return 0
        
    args = parse_args(argv)
    directory = Path(args.directory).expanduser().resolve()
    if not validate_directory(directory):
        return 1
    files = list_files(directory)
    config = resolve_config()
    planned_moves = plan_moves(directory, files, config)
    if not planned_moves:
        print("Nothing to organize.")
        return 0
    try:
        result = execute_moves(
            planned_moves, 
            dry_run=args.dry_run,
            collision_policy=args.collision,
            )
    except FileExistsError as e:
        print(f"Error: {e}")
        return 1
    print_execution(result, directory, files, args.dry_run)
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
        "-d", "--dry-run",
        action="store_true",
        help="Preview changes without moving files"
    )
    parser.add_argument(
        "-c", "--collision",
        choices=("rename", "skip", "fail"),
        default="rename",
        help="What to do if the destination file already exists: rename (default), skip, or fail"
    )
    return parser 

def parse_args_config(argv: list[str] | None = None) -> argparse.Namespace:
    parser = build_parser_config()
    return parser.parse_args(argv)

def build_parser_config() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="config commands"
    )
    parser.add_argument(
        "command",
        choices=["path"],
        default="path",
        help="config command"
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

def group_moves(
        planned_moves: list[PlannedMove]
    ) -> dict[str, list[PlannedMove]]:
    grouped = {}
    for move in planned_moves:
        grouped.setdefault(move.category, []).append(move)
    return grouped

def print_execution(
        result: ExecutionResult,
        directory: Path,
        files: list[Path],
        dry_run: bool = False
    ) -> None:
    print()
    print(f"Scanned {len(files)} files")
    print(f"Found {len(result.moved)} files to move")
    print(f"Skipped {len(result.skipped)} files")
    print()
    if dry_run:
        print("Dry run (no changes made)")
    else:
        print("Executing moves:")
    grouped = group_moves(result.moved)
    for category in sorted(
        grouped,
        key=lambda c: (c == "Other", c)
    ):
        moves = grouped[category]
        print()
        print(f"{category} ({len(moves)})")
        for move in moves:
            print(
                f"   {directory.name}/{move.source.relative_to(directory)} "
                f"-> {directory.name}/{move.destination.relative_to(directory)}"
            )
    if result.skipped:
        print()
        print("Skipped:")
        for skipped_file in result.skipped:
            print(
                f"{directory.name}/"
                f"{skipped_file.source.relative_to(directory)}"
            )
    if not dry_run:
        print()
        print(f"Execution complete. "
              f"Moved {len(result.moved)}, skipped {len(result.skipped)}"
        )
     
if __name__ == "__main__":
    run()


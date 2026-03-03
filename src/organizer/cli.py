import argparse
import sys
from pathlib import Path

from .filesystem import list_files
from .organizer import plan_moves, PlannedMove
from .executor import execute_moves, ExecutionResult
from .config import ConfigError, resolve_config, get_config_path, init_config


def run() -> None:
    raise SystemExit(main())


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    # Dispatch
    if args.top_command == "config":
        if args.config_command == "path":
            print(get_config_path())
            return 0

        if args.config_command == "init":
            try:
                path = init_config()
            except ConfigError as e:
                print(f"Error: {e}", file=sys.stderr)
                return 1
            print(f"Created config at {path}")
            return 0

        # Should be unreachable due to argparse choices
        print("Unknown config command", file=sys.stderr)
        return 1

    if args.top_command == "run":
        directory = Path(args.directory).expanduser().resolve()
        if not validate_directory(directory):
            return 1

        files = list_files(directory)

        try:
            config = resolve_config()
        except ConfigError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

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
            print(f"Error: {e}", file=sys.stderr)
            return 1

        print_execution(result, directory, files, args.dry_run)
        return 0

    # Should be unreachable due to argparse required subparsers
    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="organize",
        description="Organize files in a directory by category",
    )

    subparsers = parser.add_subparsers(dest="top_command", required=True)

    # ---- run ----
    run_parser = subparsers.add_parser(
        "run",
        help="Organize files in a directory",
        description="Organize files in a directory by category",
    )
    run_parser.add_argument("directory", help="Target directory to organize")
    run_parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Preview changes without moving files",
    )
    run_parser.add_argument(
        "-c",
        "--collision",
        choices=("rename", "skip", "fail"),
        default="rename",
        help="What to do if the destination file already exists: rename (default), skip, or fail",
    )

    # ---- config ----
    config_parser = subparsers.add_parser(
        "config",
        help="Manage configuration",
        description="Manage Smart File Organizer configuration",
    )
    config_sub = config_parser.add_subparsers(dest="config_command", required=True)

    config_sub.add_parser(
        "path",
        help="Print the config file path",
        description="Print the location of the config file.",
    )

    config_sub.add_parser(
        "init",
        help="Create a minimal default config file (if missing)",
        description="Create a minimal default config file if one does not already exist.",
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
    grouped: dict[str, list[PlannedMove]] = {}
    for move in planned_moves:
        grouped.setdefault(move.category, []).append(move)
    return grouped


def print_execution(
    result: ExecutionResult,
    directory: Path,
    files: list[Path],
    dry_run: bool = False,
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
    for category in sorted(grouped, key=lambda c: (c == "Other", c)):
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
            print(f"{directory.name}/{skipped_file.source.relative_to(directory)}")

    if not dry_run:
        print()
        print(
            f"Execution complete. Moved {len(result.moved)}, skipped {len(result.skipped)}"
        )


if __name__ == "__main__":
    run()


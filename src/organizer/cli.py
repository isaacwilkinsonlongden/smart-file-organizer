import argparse
import sys
from pathlib import Path

from .config import (
    ConfigError,
    get_config_path,
    init_config,
    reset_config_blank,
    reset_config_default,
    resolve_config,
    set_extension,
    show_config,
    unset_extension,
)
from .executor import ExecutionResult, execute_moves
from .filesystem import list_files
from .organizer import PlannedMove, plan_moves


def run() -> None:
    raise SystemExit(main())


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    if args.top_command == "config":
        return handle_config_command(args)

    if args.top_command == "run":
        return handle_run_command(args)

    parser.print_help()
    return 1


def handle_config_command(args: argparse.Namespace) -> int:
    if args.config_command == "path":
        return handle_config_path()

    if args.config_command == "init":
        return handle_config_init()

    if args.config_command == "set":
        return handle_config_set(args)

    if args.config_command == "unset":
        return handle_config_unset(args)

    if args.config_command == "show":
        return handle_config_show()

    if args.config_command == "reset":
        return handle_config_reset(args)

    print("Unknown config command", file=sys.stderr)
    return 1


def handle_config_path() -> int:
    print(get_config_path())
    return 0


def handle_config_init() -> int:
    try:
        path = init_config()
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Created config at {path}")
    return 0


def handle_config_set(args: argparse.Namespace) -> int:
    try:
        path = set_extension(args.extension, args.category)
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Updated config at {path}")
    return 0


def handle_config_unset(args: argparse.Namespace) -> int:
    try:
        path = unset_extension(args.extension)
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print(f"Updated config at {path}")
    return 0


def handle_config_show() -> int:
    try:
        print(show_config(), end="")
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def handle_config_reset(args: argparse.Namespace) -> int:
    try:
        if args.default:
            path = reset_config_default()
            print(f"Reset to default config at {path}")
            return 0

        if args.blank:
            path = reset_config_blank()
            print(f"Reset to blank config at {path}")
            return 0
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print("Error: reset mode not specified", file=sys.stderr)
    return 1


def handle_run_command(args: argparse.Namespace) -> int:
    directory = Path(args.directory).expanduser().resolve()
    if not validate_directory(directory):
        return 1

    files = list_files(directory, recursive=args.recursive)

    try:
        config = resolve_config()
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    planned_moves = plan_moves(
        directory,
        files,
        config,
        recursive=args.recursive,
    )

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
    run_parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recursively organize files in child directories",
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

    set_parser = config_sub.add_parser(
        "set",
        help="Add or update an extension mapping",
        description="Add or update an extension mapping in the config file.",
    )
    set_parser.add_argument(
        "extension",
        help="File extension to map (e.g. .mp3)",
    )
    set_parser.add_argument(
        "category",
        help="Category folder name (e.g. Music)",
    )

    unset_parser = config_sub.add_parser(
        "unset",
        help="Remove an extension mapping",
        description="Remove an extension mapping in the config file",
    )
    unset_parser.add_argument(
        "extension",
        help="File extension to remove (e.g. .mp3)",
    )

    config_sub.add_parser(
        "show",
        help="Show the current config file",
        description="Print the contents of the current config file",
    )

    reset_parser = config_sub.add_parser(
        "reset",
        help="Reset the config to default or blank",
        description="Reset the config file to the default config or a blank config",
    )
    mode_group = reset_parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--default",
        action="store_true",
        help="Reset the config to the default minimal config",
    )
    mode_group.add_argument(
        "--blank",
        action="store_true",
        help="Reset the config to a blank config (no merged defaults, no fallback category)",
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


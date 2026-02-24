import argparse
import sys

from pathlib import Path

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    directory = Path(args.directory).expanduser().resolve()
    if not directory.exists():
        print(f"Error: path does not exist: {directory}", file=sys.stderr)
        return 1
    if not directory.is_dir():
        print(f"Error: path is not a directory: {directory}", file=sys.stderr)
        return 1
    print(f"Target directory: {directory}")
    print(f"Dry run: {args.dry_run}")
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

if __name__ == "__main__":
    sys.exit(main())


import os
from pathlib import Path


def list_files(directory: Path, recursive: bool = False) -> list[Path]:
    files_out: list[Path] = []

    if recursive:
        for root, dirs, files in os.walk(directory):
            dirs[:] = [d for d in dirs if not d.startswith(".")]

            for file in files:
                file_path = Path(root) / file

                if not is_hidden(file_path):
                    files_out.append(file_path)

    else:
        for item in directory.iterdir():
            if item.is_file() and not is_hidden(item):
                files_out.append(item)

    return sorted(files_out)


def is_hidden(path: Path) -> bool:
    return path.name.startswith(".")
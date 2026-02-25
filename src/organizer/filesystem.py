from pathlib import Path

def list_files(directory: Path) -> list[Path]:
    files: list[Path] = []
    for item in directory.iterdir():
        if item.is_file():
            files.append(item)
    return files
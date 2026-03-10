from pathlib import Path

EXT_TO_CATEGORY = {
    # ========================
    # Images
    # ========================
    ".png": "Images",
    ".jpg": "Images",
    ".jpeg": "Images",
    ".gif": "Images",
    ".bmp": "Images",
    ".tiff": "Images",
    ".tif": "Images",
    ".webp": "Images",
    ".svg": "Images",
    ".ico": "Images",
    ".heic": "Images",
    ".heif": "Images",
    ".raw": "Images",
    ".cr2": "Images",
    ".nef": "Images",
    # ========================
    # Videos
    # ========================
    ".mp4": "Videos",
    ".mkv": "Videos",
    ".mov": "Videos",
    ".avi": "Videos",
    ".wmv": "Videos",
    ".flv": "Videos",
    ".webm": "Videos",
    ".m4v": "Videos",
    ".mpeg": "Videos",
    ".mpg": "Videos",
    ".3gp": "Videos",
    # ========================
    # Documents
    # ========================
    ".pdf": "Documents",
    ".doc": "Documents",
    ".docx": "Documents",
    ".xls": "Documents",
    ".xlsx": "Documents",
    ".ppt": "Documents",
    ".pptx": "Documents",
    ".txt": "Documents",
    ".rtf": "Documents",
    ".md": "Documents",
    ".csv": "Documents",
    ".odt": "Documents",
    ".ods": "Documents",
    ".odp": "Documents",
    ".pages": "Documents",
    ".numbers": "Documents",
    ".key": "Documents",
    # ========================
    # Audio
    # ========================
    ".mp3": "Audio",
    ".wav": "Audio",
    ".flac": "Audio",
    ".aac": "Audio",
    ".ogg": "Audio",
    ".m4a": "Audio",
    ".wma": "Audio",
    ".aiff": "Audio",
    ".alac": "Audio",
    # ========================
    # Code
    # ========================
    ".py": "Code",
    ".pyw": "Code",
    ".js": "Code",
    ".ts": "Code",
    ".jsx": "Code",
    ".tsx": "Code",
    ".java": "Code",
    ".c": "Code",
    ".cpp": "Code",
    ".cc": "Code",
    ".h": "Code",
    ".hpp": "Code",
    ".cs": "Code",
    ".go": "Code",
    ".rs": "Code",
    ".rb": "Code",
    ".php": "Code",
    ".swift": "Code",
    ".kt": "Code",
    ".kts": "Code",
    ".html": "Code",
    ".css": "Code",
    ".scss": "Code",
    ".json": "Code",
    ".yaml": "Code",
    ".yml": "Code",
    ".xml": "Code",
    ".sh": "Code",
    ".bash": "Code",
    ".ps1": "Code",
    ".sql": "Code",
    ".r": "Code",
    ".dart": "Code",
    # ========================
    # Archives
    # ========================
    ".zip": "Archives",
    ".rar": "Archives",
    ".7z": "Archives",
    ".tar": "Archives",
    ".gz": "Archives",
    ".tgz": "Archives",
    ".bz2": "Archives",
    ".xz": "Archives",
    ".iso": "Archives",
}


def get_category(
    path: Path,
    ext_to_category: dict[str, str],
    fallback_category: str,
    use_fallback_category: bool,
) -> str | None:
    ext = path.suffix.lower()

    if not use_fallback_category:
        fallback_category = None

    return ext_to_category.get(ext, fallback_category)
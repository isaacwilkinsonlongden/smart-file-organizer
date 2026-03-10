from dataclasses import dataclass
from pathlib import Path

from .categorizer import get_category
from .config import Config

@dataclass
class PlannedMove:
    source: Path
    destination: Path
    category: str

def plan_moves(
        directory: Path, 
        files: list[Path],
        config: Config,
        output_root: Path | None = None,
        recursive: bool = False
    ) -> list[PlannedMove]:
    if output_root is None:
        output_root = directory
        
    planned_moves = []
    if recursive:
        active_categories = set(config.ext_to_category.values())
        if config.use_fallback_category:
            active_categories.add(config.fallback_category)
    for file in files:
        if recursive:
            if _is_in_active_category_folder(file, directory, active_categories):
                continue
        category = get_category(
            file,
            config.ext_to_category,
            config.fallback_category,
            config.use_fallback_category
        )
        if category is not None:
            destination = output_root / category / file.name
            if file == destination:
                continue
            planned_moves.append(PlannedMove(
                source=file,
                destination=destination,
                category=category
            ))
    return planned_moves


def _is_in_active_category_folder(
    file: Path,
    root: Path,
    active_categories: set[str],
) -> bool:
    rel_path = file.relative_to(root)
    return any(part in active_categories for part in rel_path.parent.parts)

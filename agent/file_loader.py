"""
File loading and filtering utilities for the Code Review Assistant.
"""

from collections.abc import Iterator
from pathlib import Path
from typing import TypeAlias

from config import (
    IGNORED_DIRECTORIES,
    MAX_DEPTH,
    MAX_FILE_SIZE,
    MAX_FILES,
    SUPPORTED_EXTENSIONS,
)

RelativeFilePath: TypeAlias = str  # Path relative to codebase root
FileContent: TypeAlias = str
FileExtension: TypeAlias = str


def load_codebase(
    root_path: str, filter_pattern: str | None = None
) -> dict[RelativeFilePath, FileContent]:
    """
    Load all source code files from the given directory.

    Args:
        root_path: Path to the codebase directory
        filter_pattern: Optional pattern to filter files (e.g., "auth", "test")

    Returns:
        Dictionary mapping file paths (relative to root) to file contents
    """
    root = Path(root_path).resolve()
    files: dict[RelativeFilePath, FileContent] = {}
    file_count = 0

    for file_path in _walk_directory(root):
        if file_count >= MAX_FILES:
            break

        relative_path = str(file_path.relative_to(root))

        if filter_pattern and not _matches_filter(relative_path, filter_pattern):
            continue

        content = _read_file(file_path)
        if content is not None:
            files[relative_path] = content
            file_count += 1

    return files


def format_files_for_prompt(files: dict[RelativeFilePath, FileContent]) -> str:
    """Format loaded files into a string for the LLM prompt."""
    if not files:
        return "(No files found)"

    sections: list[str] = []
    for filepath, content in files.items():
        sections.append(f"=== {filepath} ===\n{content}")

    return "\n\n".join(sections)


def get_codebase_summary(root_path: str) -> str:
    """Get a quick summary of the codebase structure."""
    root = Path(root_path).resolve()
    files: list[Path] = list(_walk_directory(root))

    by_extension: dict[FileExtension, list[RelativeFilePath]] = {}
    for f in files:
        ext = f.suffix
        if ext not in by_extension:
            by_extension[ext] = []
        by_extension[ext].append(str(f.relative_to(root)))

    lines: list[str] = [f"Found {len(files)} source files:"]
    for ext, file_list in sorted(by_extension.items()):
        lines.append(f"  {ext}: {len(file_list)} files")

    return "\n".join(lines)


def _walk_directory(root: Path, depth: int = 0) -> Iterator[Path]:
    """
    Recursively walk directory, yielding source code files.

    Safety guards:
    - Skips symlinks to prevent infinite loops
    - Limits recursion depth to prevent stack overflow
    - Caller should limit total file count
    """
    if depth > MAX_DEPTH:
        return

    try:
        for item in root.iterdir():
            # Skip symlinks entirely to prevent loops
            if item.is_symlink():
                continue

            if item.is_dir():
                if item.name not in IGNORED_DIRECTORIES:
                    yield from _walk_directory(item, depth + 1)
            elif item.is_file() and item.suffix in SUPPORTED_EXTENSIONS:
                yield item
    except PermissionError:
        return


def _matches_filter(relative_path: RelativeFilePath, pattern: str) -> bool:
    """Check if file path matches the filter pattern (case-insensitive)."""
    return pattern.lower() in relative_path.lower()


def _read_file(file_path: Path) -> FileContent | None:
    """Read file content, returning None if file should be skipped."""
    try:
        if file_path.stat().st_size > MAX_FILE_SIZE:
            return None

        return file_path.read_text(encoding="utf-8", errors="ignore")
    except (IOError, OSError):
        return None

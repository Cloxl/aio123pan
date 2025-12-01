"""Validators for 123Pan API parameters."""

import re
from pathlib import Path

from aio123pan.exceptions import ValidationError

MAX_FILENAME_LENGTH = 255
INVALID_FILENAME_CHARS = r'"\/:*?|><'
INVALID_FILENAME_PATTERN = re.compile(f"[{re.escape(INVALID_FILENAME_CHARS)}]")

MAX_FILE_SIZE = 10 * 1024 * 1024 * 1024
MAX_BATCH_SIZE = 100
MAX_PAGE_LIMIT = 100


def validate_filename(filename: str) -> None:
    r"""Validate filename according to 123Pan rules.

    Rules:
    - Must be less than 256 characters (255 max)
    - Cannot contain: "\/:*?|><
    - Cannot be all spaces

    Args:
        filename: Filename to validate

    Raises:
        ValidationError: If validation fails
    """
    if not filename:
        raise ValidationError("Filename cannot be empty")

    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValidationError(f"Filename must be less than {MAX_FILENAME_LENGTH + 1} characters")

    if not filename.strip():
        raise ValidationError("Filename cannot be all spaces")

    if INVALID_FILENAME_PATTERN.search(filename):
        raise ValidationError(f"Filename cannot contain any of these characters: {INVALID_FILENAME_CHARS}")


def validate_file_size(file_path: str | Path) -> None:
    """Validate file size according to 123Pan rules.

    Rules:
    - Developer upload limit: 10GB per file

    Args:
        file_path: Path to the file

    Raises:
        ValidationError: If validation fails
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise ValidationError(f"File not found: {file_path}")

    if not file_path.is_file():
        raise ValidationError(f"Not a file: {file_path}")

    file_size = file_path.stat().st_size

    if file_size > MAX_FILE_SIZE:
        max_gb = MAX_FILE_SIZE / (1024**3)
        actual_gb = file_size / (1024**3)
        raise ValidationError(f"File size exceeds {max_gb}GB limit (actual: {actual_gb:.2f}GB)")

    if file_size == 0:
        raise ValidationError("File is empty (0 bytes)")


def validate_batch_size(item_count: int, operation: str = "operation") -> None:
    """Validate batch operation size.

    Rules:
    - Maximum 100 items per batch operation

    Args:
        item_count: Number of items in the batch
        operation: Name of the operation (for error message)

    Raises:
        ValidationError: If validation fails
    """
    if item_count <= 0:
        raise ValidationError(f"Batch {operation} requires at least 1 item")

    if item_count > MAX_BATCH_SIZE:
        raise ValidationError(f"Batch {operation} limited to {MAX_BATCH_SIZE} items (requested: {item_count})")


def validate_page_limit(limit: int) -> None:
    """Validate pagination limit.

    Rules:
    - Maximum 100 items per page

    Args:
        limit: Number of items per page

    Raises:
        ValidationError: If validation fails
    """
    if limit <= 0:
        raise ValidationError("Limit must be greater than 0")

    if limit > MAX_PAGE_LIMIT:
        raise ValidationError(f"Limit cannot exceed {MAX_PAGE_LIMIT}")

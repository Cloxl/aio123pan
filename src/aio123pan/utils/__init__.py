"""Utility functions for aio123pan."""

import hashlib
from collections.abc import AsyncIterator
from pathlib import Path


def calculate_md5(file_path: str | Path) -> str:
    """Calculate MD5 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        MD5 hash string in hexadecimal
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def calculate_md5_from_bytes(data: bytes) -> str:
    """Calculate MD5 hash from bytes.

    Args:
        data: Bytes data

    Returns:
        MD5 hash string in hexadecimal
    """
    return hashlib.md5(data).hexdigest()


async def read_file_chunks(
    file_path: str | Path, chunk_size: int = 1024 * 1024 * 4
) -> AsyncIterator[bytes]:
    """Read file in chunks asynchronously.

    Args:
        file_path: Path to the file
        chunk_size: Size of each chunk in bytes (default 4MB)

    Yields:
        Chunks of file data
    """
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk


def split_file_into_slices(file_path: str | Path, slice_size: int) -> list[tuple[int, int, bytes]]:
    """Split file into slices for multipart upload.

    Args:
        file_path: Path to the file
        slice_size: Size of each slice in bytes

    Returns:
        List of tuples (slice_index, slice_size, slice_data)
    """
    slices = []
    with open(file_path, "rb") as f:
        slice_index = 0
        while True:
            chunk = f.read(slice_size)
            if not chunk:
                break
            slices.append((slice_index, len(chunk), chunk))
            slice_index += 1
    return slices

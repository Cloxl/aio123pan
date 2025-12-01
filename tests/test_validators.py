"""Tests for validators module."""

import tempfile
from pathlib import Path

import pytest

from aio123pan.validators import (
    MAX_BATCH_SIZE,
    MAX_FILE_SIZE,
    MAX_FILENAME_LENGTH,
    ValidationError,
    validate_batch_size,
    validate_file_size,
    validate_filename,
    validate_page_limit,
)


class TestValidateFilename:
    """Tests for validate_filename function."""

    def test_valid_filename(self):
        """Test valid filenames pass validation."""
        valid_names = [
            "test.txt",
            "my_file.pdf",
            "文件名.docx",
            "file-123.jpg",
            "a" * 255,
        ]
        for name in valid_names:
            validate_filename(name)

    def test_empty_filename(self):
        """Test empty filename raises error."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_filename("")

    def test_filename_too_long(self):
        """Test filename exceeding 255 characters raises error."""
        long_name = "a" * 256
        with pytest.raises(ValidationError, match="less than 256 characters"):
            validate_filename(long_name)

    def test_filename_all_spaces(self):
        """Test filename with only spaces raises error."""
        with pytest.raises(ValidationError, match="cannot be all spaces"):
            validate_filename("   ")

    def test_filename_invalid_characters(self):
        """Test filename with invalid characters raises error."""
        invalid_chars = r'"\/:*?|><'
        for char in invalid_chars:
            filename = f"test{char}file.txt"
            with pytest.raises(ValidationError, match="cannot contain"):
                validate_filename(filename)

    def test_filename_boundary_length(self):
        """Test filename at exact boundary (255 chars)."""
        boundary_name = "a" * 255
        validate_filename(boundary_name)

        too_long_name = "a" * 256
        with pytest.raises(ValidationError):
            validate_filename(too_long_name)


class TestValidateFileSize:
    """Tests for validate_file_size function."""

    def test_valid_file_size(self):
        """Test valid file size passes validation."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"test content" * 1000)
            temp_path = f.name

        try:
            validate_file_size(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_file_not_found(self):
        """Test non-existent file raises error."""
        with pytest.raises(ValidationError, match="File not found"):
            validate_file_size("nonexistent_file.txt")

    def test_not_a_file(self):
        """Test directory path raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(ValidationError, match="Not a file"):
                validate_file_size(tmpdir)

    def test_empty_file(self):
        """Test empty file (0 bytes) raises error."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name

        try:
            with pytest.raises(ValidationError, match="File is empty"):
                validate_file_size(temp_path)
        finally:
            Path(temp_path).unlink()


class TestValidateBatchSize:
    """Tests for validate_batch_size function."""

    def test_valid_batch_size(self):
        """Test valid batch sizes pass validation."""
        for size in [1, 50, 100]:
            validate_batch_size(size)

    def test_batch_size_zero(self):
        """Test batch size of 0 raises error."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_batch_size(0)

    def test_batch_size_negative(self):
        """Test negative batch size raises error."""
        with pytest.raises(ValidationError, match="at least 1"):
            validate_batch_size(-1)

    def test_batch_size_exceeds_max(self):
        """Test batch size exceeding 100 raises error."""
        with pytest.raises(ValidationError, match="limited to 100"):
            validate_batch_size(101)

    def test_batch_size_boundary(self):
        """Test batch size at exact boundary (100)."""
        validate_batch_size(100)

        with pytest.raises(ValidationError):
            validate_batch_size(101)

    def test_custom_operation_name(self):
        """Test custom operation name appears in error message."""
        with pytest.raises(ValidationError, match="delete"):
            validate_batch_size(101, operation="delete")


class TestValidatePageLimit:
    """Tests for validate_page_limit function."""

    def test_valid_page_limit(self):
        """Test valid page limits pass validation."""
        for limit in [1, 50, 100]:
            validate_page_limit(limit)

    def test_page_limit_zero(self):
        """Test page limit of 0 raises error."""
        with pytest.raises(ValidationError, match="greater than 0"):
            validate_page_limit(0)

    def test_page_limit_negative(self):
        """Test negative page limit raises error."""
        with pytest.raises(ValidationError, match="greater than 0"):
            validate_page_limit(-1)

    def test_page_limit_exceeds_max(self):
        """Test page limit exceeding 100 raises error."""
        with pytest.raises(ValidationError, match="cannot exceed 100"):
            validate_page_limit(101)

    def test_page_limit_boundary(self):
        """Test page limit at exact boundary (100)."""
        validate_page_limit(100)

        with pytest.raises(ValidationError):
            validate_page_limit(101)


class TestConstants:
    """Tests for validator constants."""

    def test_max_filename_length(self):
        """Test MAX_FILENAME_LENGTH constant."""
        assert MAX_FILENAME_LENGTH == 255

    def test_max_file_size(self):
        """Test MAX_FILE_SIZE constant."""
        assert MAX_FILE_SIZE == 10 * 1024 * 1024 * 1024

    def test_max_batch_size(self):
        """Test MAX_BATCH_SIZE constant."""
        assert MAX_BATCH_SIZE == 100

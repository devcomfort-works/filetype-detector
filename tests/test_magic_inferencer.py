"""Tests for MagicInferencer."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from loguru import logger

from filetype_detector.magic_inferencer import MagicInferencer


class TestMagicInferencer:
    """Test suite for MagicInferencer."""

    def test_infer_with_string_path(self, sample_text_file):
        """Test inferring extension from string path."""
        logger.debug(f"Testing string path inference with file: {sample_text_file}")
        inferencer = MagicInferencer()
        file_type = inferencer.infer(str(sample_text_file))
        logger.success(
            f"String path test - File: {sample_text_file.name}, Type: {file_type}"
        )
        assert ".txt" in file_type.extensions
        assert any(ext.startswith(".") for ext in file_type.extensions)

    def test_infer_with_path_object(self, sample_text_file):
        """Test inferring extension from Path object."""
        logger.debug(f"Testing Path object inference with file: {sample_text_file}")
        inferencer = MagicInferencer()
        file_type = inferencer.infer(sample_text_file)
        logger.success(
            f"Path object test - File: {sample_text_file.name}, Type: {file_type}"
        )
        assert ".txt" in file_type.extensions

    def test_infer_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        logger.warning("Testing FileNotFoundError for non-existent file")
        inferencer = MagicInferencer()
        with pytest.raises(FileNotFoundError, match="File not found") as exc_info:
            inferencer.infer("nonexistent_file.pdf")
        logger.success(f"FileNotFoundError correctly raised: {exc_info.value}")

    def test_infer_value_error_for_directory(self, temp_dir_path):
        """Test that ValueError is raised for directories."""
        logger.warning(f"Testing ValueError for directory: {temp_dir_path}")
        inferencer = MagicInferencer()
        with pytest.raises(ValueError, match="Path is not a file") as exc_info:
            inferencer.infer(str(temp_dir_path))
        logger.success(f"ValueError correctly raised: {exc_info.value}")

    @patch("filetype_detector.magic_inferencer.magic.from_file")
    def test_infer_runtime_error_no_mime_type(self, mock_magic, sample_text_file):
        """Test that RuntimeError is raised when MIME type cannot be determined."""
        logger.debug("Testing RuntimeError when MIME type cannot be determined")
        mock_magic.return_value = None
        inferencer = MagicInferencer()
        with pytest.raises(
            RuntimeError, match="Cannot determine MIME type"
        ) as exc_info:
            inferencer.infer(sample_text_file)
        logger.success(f"RuntimeError correctly raised: {exc_info.value}")

    def test_infer_with_pdf_file(self, sample_pdf_file):
        """Test inferring extension from PDF file."""
        logger.info(f"Testing PDF file inference: {sample_pdf_file.name}")
        inferencer = MagicInferencer()
        file_type = inferencer.infer(sample_pdf_file)
        logger.success(f"PDF file test - Type: {file_type}")
        assert any(ext.startswith(".") for ext in file_type.extensions)
        # May vary by system, but should be a valid extension
        assert any(len(ext) > 1 for ext in file_type.extensions)

    def test_infer_with_python_file(self, sample_python_file):
        """Test inferring extension from Python file."""
        logger.info(f"Testing Python file inference: {sample_python_file.name}")
        inferencer = MagicInferencer()
        file_type = inferencer.infer(sample_python_file)
        logger.info(f"Python file test - Type: {file_type} (may vary by system)")
        # May vary by system (could be .py, .txt, or other)
        assert any(ext.startswith(".") for ext in file_type.extensions)
        assert any(len(ext) > 1 for ext in file_type.extensions)

    def test_infer_with_json_file(self, sample_json_file):
        """Test inferring extension from JSON file."""
        logger.info(f"Testing JSON file inference: {sample_json_file.name}")
        inferencer = MagicInferencer()
        file_type = inferencer.infer(sample_json_file)
        logger.info(f"JSON file test - Type: {file_type} (may vary by system)")
        # May be .json or .txt depending on system
        assert any(ext.startswith(".") for ext in file_type.extensions)

    @patch("filetype_detector.magic_inferencer.magic.from_file")
    def test_infer_successful_flow(self, mock_magic, sample_text_file):
        """Test successful inference flow."""
        logger.debug("Testing successful inference flow with mocked magic")
        mock_magic.return_value = "text/plain"
        inferencer = MagicInferencer()
        file_type = inferencer.infer(sample_text_file)
        logger.success(f"Successful flow test - Type: {file_type}")
        assert ".txt" in file_type.extensions
        mock_magic.assert_called_once_with(str(sample_text_file), mime=True)
        logger.debug("Mock verification passed")

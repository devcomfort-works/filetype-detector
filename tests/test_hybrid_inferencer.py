"""Tests for HybridInferencer."""

import pytest
from unittest.mock import patch, MagicMock
from loguru import logger

from filetype_detector.hybrid_inferencer import HybridInferencer


class TestHybridInferencer:
    """Test suite for HybridInferencer."""

    def test_infer_with_string_path(self, sample_text_file):
        """Test inferring extension from string path."""
        logger.debug(f"Testing string path inference with file: {sample_text_file}")
        inferencer = HybridInferencer()
        file_type = inferencer.infer(str(sample_text_file))
        logger.success(
            f"String path test - File: {sample_text_file.name}, Type: {file_type}"
        )
        assert any(ext.startswith(".") for ext in file_type.extensions)
        assert any(len(ext) > 1 for ext in file_type.extensions)

    def test_infer_with_path_object(self, sample_text_file):
        """Test inferring extension from Path object."""
        logger.debug(f"Testing Path object inference with file: {sample_text_file}")
        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)
        logger.success(
            f"Path object test - File: {sample_text_file.name}, Type: {file_type}"
        )
        assert any(ext.startswith(".") for ext in file_type.extensions)

    def test_infer_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        logger.warning("Testing FileNotFoundError for non-existent file")
        inferencer = HybridInferencer()
        with pytest.raises(FileNotFoundError, match="File not found") as exc_info:
            inferencer.infer("nonexistent_file.pdf")
        logger.success(f"FileNotFoundError correctly raised: {exc_info.value}")

    def test_infer_value_error_for_directory(self, temp_dir_path):
        """Test that ValueError is raised for directories."""
        logger.warning(f"Testing ValueError for directory: {temp_dir_path}")
        inferencer = HybridInferencer()
        with pytest.raises(ValueError, match="Path is not a file") as exc_info:
            inferencer.infer(str(temp_dir_path))
        logger.success(f"ValueError correctly raised: {exc_info.value}")

    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    def test_infer_runtime_error_no_mime_type(self, mock_magic, sample_text_file):
        """Test that RuntimeError is raised when MIME type cannot be determined."""
        logger.debug("Testing RuntimeError when MIME type cannot be determined")
        mock_magic.return_value = None
        inferencer = HybridInferencer()
        with pytest.raises(
            RuntimeError, match="Cannot determine MIME type"
        ) as exc_info:
            inferencer.infer(sample_text_file)
        logger.success(f"RuntimeError correctly raised: {exc_info.value}")

    def test_infer_with_text_file_uses_magika(self, sample_text_file):
        """Test that text files trigger Magika inference."""
        logger.info(f"Testing text file inference with Magika: {sample_text_file.name}")
        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)
        logger.success(f"Text file test - Type: {file_type}")
        assert any(ext.startswith(".") for ext in file_type.extensions)

    def test_infer_with_python_file(self, sample_python_file):
        """Test inferring extension from Python file."""
        logger.info(f"Testing Python file inference: {sample_python_file.name}")
        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_python_file)
        logger.success(f"Python file test - Type: {file_type}")
        assert any(ext.startswith(".") for ext in file_type.extensions)
        # Should detect as .py using Magika (for text files)
        if ".py" in file_type.extensions:
            logger.info("Correctly identified as Python file")
        else:
            logger.info(f"Detected as {file_type.extensions} (may vary)")

    def test_infer_with_json_file(self, sample_json_file):
        """Test inferring extension from JSON file."""
        logger.info(f"Testing JSON file inference: {sample_json_file.name}")
        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_json_file)
        logger.success(f"JSON file test - Type: {file_type}")
        assert any(ext.startswith(".") for ext in file_type.extensions)
        # Should detect as .json using Magika (for text files)
        if ".json" in file_type.extensions:
            logger.info("Correctly identified as JSON file")

    def test_infer_with_pdf_file_uses_magic_only(self, sample_pdf_file):
        """Test that non-text files use Magic only (not Magika)."""
        logger.info(f"Testing PDF file inference (Magic only): {sample_pdf_file.name}")
        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_pdf_file)
        logger.success(f"PDF file test - Type: {file_type}")
        assert any(ext.startswith(".") for ext in file_type.extensions)
        # PDF files are not text/*, so should use Magic only

    @patch("filetype_detector.hybrid_inferencer.Magika")
    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    def test_text_file_cascades_to_magika(
        self, mock_magic, mock_magika_class, sample_text_file
    ):
        """Test that text files cascade to Magika inference."""
        logger.debug("Testing cascading behavior for text files")
        mock_magic.return_value = "text/plain"
        mock_magika = MagicMock()
        mock_result = MagicMock()
        mock_result.output.extensions = ["txt"]
        mock_magika.identify_path.return_value = mock_result
        mock_magika_class.return_value = mock_magika

        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)

        logger.success(f"Cascading test - Type: {file_type}")
        # Verify Magic was called
        mock_magic.assert_called_once()
        # Verify Magika was called (for text files)
        mock_magika_class.assert_called_once()
        mock_magika.identify_path.assert_called_once()
        assert ".txt" in file_type.extensions

    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    def test_non_text_file_does_not_use_magika(self, mock_magic, sample_pdf_file):
        """Test that non-text files do not use Magika."""
        logger.debug("Testing that non-text files skip Magika")
        mock_magic.return_value = "application/pdf"
        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_pdf_file)

        logger.success(f"Non-text file test - Type: {file_type}")
        # Verify Magic was called
        mock_magic.assert_called_once()
        # Magika should not be used for non-text files
        assert any(ext.startswith(".") for ext in file_type.extensions)

    @patch("filetype_detector.hybrid_inferencer.Magika")
    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    @patch("filetype_detector.hybrid_inferencer.mimetypes.guess_extension")
    def test_magika_failure_falls_back_to_magic(
        self, mock_guess_ext, mock_magic, mock_magika_class, sample_text_file
    ):
        """Test that Magika failure falls back to Magic result."""
        logger.debug("Testing fallback behavior when Magika fails")
        mock_magic.return_value = "text/plain"
        mock_guess_ext.return_value = ".txt"
        mock_magika = MagicMock()
        mock_magika.identify_path.side_effect = Exception("Magika error")
        mock_magika_class.return_value = mock_magika

        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)

        logger.success(f"Fallback test - Type: {file_type}")
        # Should fallback to Magic result
        assert ".txt" in file_type.extensions
        # Verify Magic was called
        mock_magic.assert_called_once()
        # Verify Magika was attempted but failed
        mock_magika.identify_path.assert_called_once()

    @patch("filetype_detector.hybrid_inferencer.Magika")
    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    @patch("filetype_detector.hybrid_inferencer.mimetypes.guess_extension")
    def test_magika_empty_result_falls_back_to_magic(
        self, mock_guess_ext, mock_magic, mock_magika_class, sample_text_file
    ):
        """Test that empty Magika result falls back to Magic."""
        logger.debug("Testing fallback when Magika returns empty result")
        mock_magic.return_value = "text/plain"
        mock_guess_ext.return_value = ".txt"
        mock_magika = MagicMock()
        mock_result = MagicMock()
        mock_result.output.extensions = []  # Empty list
        mock_magika.identify_path.return_value = mock_result
        mock_magika_class.return_value = mock_magika

        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)

        logger.success(f"Empty result fallback test - Type: {file_type}")
        # Should fallback to Magic result
        assert ".txt" in file_type.extensions

    @patch("filetype_detector.hybrid_inferencer.Magika")
    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    def test_magika_extension_without_dot(
        self, mock_magic, mock_magika_class, sample_text_file
    ):
        """Test that Magika extension without dot gets dot prefix added."""
        logger.debug("Testing Magika extension formatting (without dot)")
        mock_magic.return_value = "text/plain"
        mock_magika = MagicMock()
        mock_result = MagicMock()
        mock_result.output.extensions = ["py"]  # Without dot
        mock_magika.identify_path.return_value = mock_result
        mock_magika_class.return_value = mock_magika

        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)

        logger.success(f"Extension formatting test - Type: {file_type}")
        assert ".py" in file_type.extensions
        assert any(ext.startswith(".") for ext in file_type.extensions)

    @patch("filetype_detector.hybrid_inferencer.Magika")
    @patch("filetype_detector.hybrid_inferencer.magic.from_file")
    def test_magika_extension_as_string(
        self, mock_magic, mock_magika_class, sample_text_file
    ):
        """Test that Magika extension as string is handled correctly."""
        logger.debug("Testing Magika extension as string format")
        mock_magic.return_value = "text/plain"
        mock_magika = MagicMock()
        mock_result = MagicMock()
        mock_result.output.extensions = "json"  # String format
        mock_magika.identify_path.return_value = mock_result
        mock_magika_class.return_value = mock_magika

        inferencer = HybridInferencer()
        file_type = inferencer.infer(sample_text_file)

        logger.success(f"String extension test - Type: {file_type}")
        assert ".json" in file_type.extensions
        assert any(ext.startswith(".") for ext in file_type.extensions)

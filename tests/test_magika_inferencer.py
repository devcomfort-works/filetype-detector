"""Tests for MagikaInferencer with FileType return type."""

import pytest
from unittest.mock import patch, MagicMock
from magika import PredictionMode
from loguru import logger

from filetype_detector.magika_inferencer import MagikaInferencer
from filetype_detector.file_type import FileType


class TestMagikaInferencer:
    """Test suite for MagikaInferencer."""

    def test_infer_with_string_path(self, sample_txt):
        """Test inferring FileType from string path."""
        logger.debug(f"Testing string path inference with file: {sample_txt}")
        inferencer = MagikaInferencer()
        ft = inferencer.infer(str(sample_txt))
        logger.success(
            f"String path test - File: {sample_txt.name}, FileType: {ft}"
        )
        assert isinstance(ft, FileType)
        assert isinstance(ft.extensions, tuple)
        assert len(ft.extensions) > 0

    def test_infer_with_path_object(self, sample_txt):
        """Test inferring FileType from Path object."""
        logger.debug(f"Testing Path object inference with file: {sample_txt}")
        inferencer = MagikaInferencer()
        ft = inferencer.infer(sample_txt)
        logger.success(
            f"Path object test - File: {sample_txt.name}, FileType: {ft}"
        )
        assert isinstance(ft, FileType)
        assert isinstance(ft.extensions, tuple)
        assert len(ft.extensions) > 0

    def test_infer_with_score_returns_tuple(self, sample_txt):
        """Test that infer_with_score returns a tuple of (extension, score)."""
        logger.debug(
            f"Testing infer_with_score returns tuple for file: {sample_txt}"
        )
        inferencer = MagikaInferencer()
        extension, score = inferencer.infer_with_score(sample_txt)
        logger.success(
            f"infer_with_score test - Extension: {extension}, Score: {score:.4f}"
        )
        assert isinstance(extension, str)
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

    def test_infer_returns_filetype(self, sample_txt):
        """Test that infer returns FileType object."""
        logger.debug("Testing that infer returns FileType object")
        inferencer = MagikaInferencer()
        ft = inferencer.infer(sample_txt)
        logger.success(f"FileType returned: {ft}")
        assert isinstance(ft, FileType)
        assert hasattr(ft, 'extensions')
        assert hasattr(ft, 'mime_types')

    def test_infer_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        logger.warning("Testing FileNotFoundError for non-existent file (infer method)")
        inferencer = MagikaInferencer()
        with pytest.raises(FileNotFoundError, match="File not found") as exc_info:
            inferencer.infer("nonexistent_file.pdf")
        logger.success(f"FileNotFoundError correctly raised: {exc_info.value}")

    def test_infer_with_score_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        logger.warning(
            "Testing FileNotFoundError for non-existent file (infer_with_score method)"
        )
        inferencer = MagikaInferencer()
        with pytest.raises(FileNotFoundError, match="File not found") as exc_info:
            inferencer.infer_with_score("nonexistent_file.pdf")
        logger.success(f"FileNotFoundError correctly raised: {exc_info.value}")

    def test_infer_value_error_for_directory(self, temp_dir_path):
        """Test that ValueError is raised for directories."""
        logger.warning(
            f"Testing ValueError for directory: {temp_dir_path} (infer method)"
        )
        inferencer = MagikaInferencer()
        with pytest.raises(ValueError, match="Path is not a file") as exc_info:
            inferencer.infer(str(temp_dir_path))
        logger.success(f"ValueError correctly raised: {exc_info.value}")

    def test_infer_with_score_value_error_for_directory(self, temp_dir_path):
        """Test that ValueError is raised for directories."""
        logger.warning(
            f"Testing ValueError for directory: {temp_dir_path} (infer_with_score method)"
        )
        inferencer = MagikaInferencer()
        with pytest.raises(ValueError, match="Path is not a file") as exc_info:
            inferencer.infer_with_score(str(temp_dir_path))
        logger.success(f"ValueError correctly raised: {exc_info.value}")

    @patch("filetype_detector.magika_inferencer.Magika")
    def test_infer_with_score_runtime_error(self, mock_magika_class, sample_txt):
        """Test that RuntimeError is raised when Magika fails."""
        logger.debug("Testing RuntimeError when Magika fails (infer_with_score method)")
        mock_magika = MagicMock()
        mock_magika.identify_path.side_effect = Exception("Magika error")
        mock_magika_class.return_value = mock_magika

        inferencer = MagikaInferencer()
        with pytest.raises(RuntimeError, match="Failed to analyze file") as exc_info:
            inferencer.infer_with_score(sample_txt)
        logger.success(f"RuntimeError correctly raised: {exc_info.value}")

    @patch("filetype_detector.magika_inferencer.Magika")
    def test_infer_runtime_error_propagates(self, mock_magika_class, sample_txt):
        """Test that RuntimeError from infer_with_score propagates through infer."""
        logger.debug("Testing RuntimeError propagation through infer method")
        mock_magika = MagicMock()
        mock_magika.identify_path.side_effect = Exception("Magika error")
        mock_magika_class.return_value = mock_magika

        inferencer = MagikaInferencer()
        with pytest.raises(RuntimeError, match="Failed to analyze file") as exc_info:
            inferencer.infer(sample_txt)
        logger.success(f"RuntimeError correctly propagated: {exc_info.value}")

    def test_infer_with_score_prediction_mode(self, sample_txt):
        """Test that prediction_mode parameter is respected."""
        logger.info("Testing different prediction modes")
        inferencer = MagikaInferencer()
        logger.debug("Testing MEDIUM_CONFIDENCE mode")
        extension1, score1 = inferencer.infer_with_score(
            sample_txt, prediction_mode=PredictionMode.MEDIUM_CONFIDENCE
        )
        logger.debug("Testing HIGH_CONFIDENCE mode")
        extension2, score2 = inferencer.infer_with_score(
            sample_txt, prediction_mode=PredictionMode.HIGH_CONFIDENCE
        )
        logger.success(
            f"Prediction mode test - MEDIUM: ext={extension1}, score={score1:.4f} | HIGH: ext={extension2}, score={score2:.4f}"
        )
        assert isinstance(extension1, str)
        assert isinstance(extension2, str)
        assert isinstance(score1, float)
        assert isinstance(score2, float)

    @patch("filetype_detector.magika_inferencer.Magika")
    def test_infer_with_score_successful_flow(
        self, mock_magika_class, sample_txt
    ):
        """Test successful inference flow with mocked Magika."""
        logger.debug("Testing successful inference flow with mocked Magika")
        mock_magika = MagicMock()
        mock_result = MagicMock()
        mock_result.output.extensions = [".txt"]
        mock_result.prediction.score = 0.95
        mock_magika.identify_path.return_value = mock_result
        mock_magika_class.return_value = mock_magika

        inferencer = MagikaInferencer()
        extension, score = inferencer.infer_with_score(sample_txt)

        logger.success(
            f"Successful flow test - Extension: {extension}, Score: {score:.4f}"
        )
        assert extension == ".txt"
        assert score == 0.95
        mock_magika_class.assert_called_once_with(
            prediction_mode=PredictionMode.MEDIUM_CONFIDENCE
        )
        mock_magika.identify_path.assert_called_once()
        logger.debug("Mock verification passed")

    def test_infer_with_pdf_file(self, sample_pdf):
        """Test inferring FileType from PDF file."""
        logger.info(f"Testing PDF file inference: {sample_pdf.name}")
        inferencer = MagikaInferencer()
        ft = inferencer.infer(sample_pdf)
        logger.success(f"PDF file test - FileType: {ft}")
        assert isinstance(ft, FileType)
        assert ".pdf" in ft.extensions

    def test_infer_with_json_file(self, sample_json):
        """Test inferring FileType from JSON file."""
        logger.info(f"Testing JSON file inference: {sample_json.name}")
        inferencer = MagikaInferencer()
        ft = inferencer.infer(sample_json)
        logger.success(f"JSON file test - FileType: {ft}")
        assert isinstance(ft, FileType)
        assert ".json" in ft.extensions or ".jsonl" in ft.extensions or ".jsonld" in ft.extensions

    def test_filetype_has_multiple_extensions(self, sample_json):
        """Test that FileType can contain multiple extensions."""
        logger.info("Testing FileType with multiple extensions")
        inferencer = MagikaInferencer()
        ft = inferencer.infer(sample_json)
        logger.success(f"Multiple extensions test - Extensions: {ft.extensions}")
        assert isinstance(ft.extensions, tuple)
        assert all(isinstance(ext, str) for ext in ft.extensions)

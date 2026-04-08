"""Magika 기반 추론기 구현체를 제공한다."""

from .base_inferencer import BaseInferencer
from typing import Union, Tuple
from pathlib import Path
from magika import Magika, PredictionMode


class MagikaInferencer(BaseInferencer):
    """Magika 모델로 파일 형식을 추론한다.

    Notes
    -----
    파일 내용을 딥러닝 모델에 입력해 파일 타입과 신뢰도 점수를 함께 예측한다.
    고정된 규칙 대신 학습된 특징을 바탕으로 판단하므로 텍스트 기반 파일의
    세부 타입 구분에 특히 강하다.
    `infer`는 확장자만 반환하고, `infer_with_score`는 확장자와 신뢰도 점수를 함께 반환한다.
    """

    def infer_with_score(
        self,
        file_path: Union[Path, str],
        prediction_mode: PredictionMode = PredictionMode.MEDIUM_CONFIDENCE,
    ) -> Tuple[str, float]:
        """확장자와 신뢰도 점수를 함께 반환한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            분석할 파일 경로이다.
        prediction_mode : PredictionMode, optional
            Magika의 예측 모드이다.

        Returns
        -------
        Tuple[str, float]
            추론된 확장자와 신뢰도 점수를 함께 반환한다.

        Raises
        ------
        FileNotFoundError
            파일이 존재하지 않을 때 발생한다.
        ValueError
            경로가 파일이 아닐 때 발생한다.
        RuntimeError
            Magika 분석에 실패했을 때 발생한다.

        Examples
        --------
        >>> inferencer = MagikaInferencer()
        >>> extension, score = inferencer.infer_with_score('document.pdf')
        >>> print(extension, score)
        .pdf 0.99
        >>> extension, score = inferencer.infer_with_score(Path('notes.txt'))
        >>> print(extension, score)
        .txt 0.97
        """
        file_path_str = str(file_path)
        path_obj = Path(file_path_str)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path_str}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path_str}")

        magika = Magika(prediction_mode=prediction_mode)

        try:
            result = magika.identify_path(path=file_path_str)
            extension = result.output.extensions
            score = result.prediction.score
            return (extension, score)
        except Exception as e:
            raise RuntimeError(
                f"Failed to analyze file {file_path_str}: {str(e)}"
            ) from e

    def infer(self, file_path: Union[Path, str]) -> str:
        """확장자만 반환하는 간단한 추론 인터페이스다.

        Parameters
        ----------
        file_path : Union[Path, str]
            분석할 파일 경로이다.

        Returns
        -------
        str
            앞에 점이 붙은 확장자 문자열이다.

        Raises
        ------
        FileNotFoundError
            파일이 존재하지 않을 때 발생한다.
        ValueError
            경로가 파일이 아닐 때 발생한다.
        RuntimeError
            Magika 분석에 실패했을 때 발생한다.

        Examples
        --------
        >>> inferencer = MagikaInferencer()
        >>> inferencer.infer('document.pdf')
        '.pdf'
        >>> inferencer.infer(Path('notes.txt'))
        '.txt'
        """
        extension, _ = self.infer_with_score(
            file_path, prediction_mode=PredictionMode.MEDIUM_CONFIDENCE
        )
        return extension

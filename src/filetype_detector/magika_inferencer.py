"""Magika 기반 추론기 구현체를 제공한다."""

from .base_inferencer import BaseInferencer
from .file_type import FileType
from typing import Union, Tuple
from pathlib import Path
import mimetypes
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
        path_obj = Path(file_path)

        # 파일 존재 여부와 타입을 미리 검증해서 Magika 분석 전에 실패시킨다.
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {path_obj}")

        # Magika는 매번 새로운 인스턴스를 생성한다.
        # 모델 로딩은 비용이 크지만 스레드 안전성을 보장한다.
        magika = Magika(prediction_mode=prediction_mode)

        try:
            result = magika.identify_path(path=str(path_obj))
            # Magika는 여러 가능한 확장자를 리스트로 반환하므로 첫 번째를 선택한다.
            extensions = result.output.extensions
            extension = extensions[0] if extensions else ""
            score = result.prediction.score
            return (extension, score)
        except Exception as e:
            raise RuntimeError(
                f"Failed to analyze file {path_obj}: {str(e)}"
            ) from e

    def infer(self, file_path: Union[Path, str]) -> FileType:
        """Magika 모델로 파일 타입을 추론하여 FileType을 반환한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            분석할 파일 경로이다.

        Returns
        -------
        FileType
            추론된 확장자들과 MIME 타입을 포함하는 FileType 인스턴스이다.

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
        >>> ft = inferencer.infer('document.pdf')
        >>> '.pdf' in ft.extensions
        True
        """
        path_obj = Path(file_path)

        # 파일 존재 여부와 타입을 미리 검증해서 Magika 분석 전에 실패시킨다.
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {path_obj}")

        # Magika는 매번 새로운 인스턴스를 생성한다.
        # 모델 로딩은 비용이 크지만 스레드 안전성을 보장한다.
        magika = Magika(prediction_mode=PredictionMode.MEDIUM_CONFIDENCE)

        try:
            result = magika.identify_path(path=str(path_obj))
            # Magika는 여러 가능한 확장자를 리스트로 반환한다.
            # FileType이 여러 확장자를 수용할 수 있으므로 모두 보존한다.
            extensions = result.output.extensions

            # 확장자들을 정규화한다 (dot prefix 추가).
            normalized_exts = []
            for ext in extensions:
                if not ext.startswith("."):
                    ext = "." + ext
                normalized_exts.append(ext)

            # 첫 번째 확장자로부터 MIME 타입을 조회한다.
            mime, _ = (
                mimetypes.guess_type(f"file{normalized_exts[0]}", strict=False)
                if normalized_exts
                else (None, None)
            )
            mime_types = (mime,) if mime else ()

            return FileType(extensions=tuple(normalized_exts), mime_types=mime_types)
        except Exception as e:
            raise RuntimeError(
                f"Failed to analyze file {path_obj}: {str(e)}"
            ) from e


if __name__ == "__main__":
    from pathlib import Path

    print("=== MagikaInferencer Demo ===\n")

    # fixtures 디렉토리 경로
    fixtures_dir = Path(__file__).parent.parent.parent / "tests" / "fixtures"

    # 사용 가능한 샘플 파일들
    sample_files = sorted(fixtures_dir.glob("sample.*"))

    if not sample_files:
        print(f"Error: No sample files found in {fixtures_dir}")
        exit(1)

    inferencer = MagikaInferencer()

    print("--- infer() 메서드: FileType 반환 ---")
    for file_path in sample_files:
        try:
            ft = inferencer.infer(file_path)
            print(f"{file_path.name}")
            print(f"  extensions: {ft.extensions}")
            print(f"  mime_types: {ft.mime_types}\n")
        except Exception as e:
            print(f"{file_path.name}: Error - {e}\n")

    print("--- infer_with_score() 메서드: 신뢰도 점수 포함 ---")
    for file_path in sample_files[:3]:  # 처음 3개만 표시
        try:
            ext, score = inferencer.infer_with_score(file_path)
            print(f"{file_path.name}: ext={ext!r}, score={score:.3f}\n")
        except Exception as e:
            print(f"{file_path.name}: Error - {e}\n")

"""Magic과 Magika를 결합한 하이브리드 추론기를 제공한다.

이 모듈의 구현체는 모든 파일에 Magic을 먼저 적용하고, 텍스트 파일로 판별된 경우에만
Magika를 추가로 사용한다. 바이너리 파일에서는 처리 비용을 낮추고,
텍스트 파일에서는 더 세밀한 확장자 분류를 얻기 위한 설계다.
"""

from .base_inferencer import BaseInferencer
from .file_type import FileType
from typing import Union
from pathlib import Path
import magic
from magika import Magika, PredictionMode


class HybridInferencer(BaseInferencer):
    """Magic과 Magika를 단계적으로 조합하는 추론기.

    Notes
    -----
    먼저 Magic으로 MIME 타입을 판별하고, 결과가 텍스트 계열이면 Magika로
    한 번 더 분석한다. 따라서 바이너리 파일에는 빠르고, 텍스트 파일에는 더 정밀하다.
    """

    def infer(self, file_path: Union[Path, str]) -> FileType:
        """하이브리드 전략으로 파일 확장자를 추론한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            분석할 파일 경로이다.

        Returns
        -------
        FileType
            추론된 확장자와 MIME 타입을 포함하는 FileType 인스턴스이다.
            텍스트 파일은 Magika로 더 세밀하게 분류된 결과를 반영한다.

        Raises
        ------
        FileNotFoundError
            파일이 존재하지 않을 때 발생한다.
        ValueError
            경로가 파일이 아닐 때 발생한다.
        RuntimeError
            MIME 타입을 구하지 못했을 때 발생한다.

        Examples
        --------
        >>> inferencer = HybridInferencer()
        >>> ft = inferencer.infer('document.pdf')
        >>> '.pdf' in ft.extensions
        True
        """
        path_obj = Path(file_path)

        # 파일 존재 여부와 타입을 미리 검증한다.
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {path_obj}")

        # Magic으로 먼저 MIME 타입을 분석한다.
        mime_type = magic.from_file(str(path_obj), mime=True)
        if mime_type is None:
            raise RuntimeError(f"Cannot determine MIME type for file: {path_obj}")

        # 텍스트 파일일 경우 Magika로 추가 분석하여 더 세밀한 분류를 얻는다.
        if mime_type.startswith("text/"):
            try:
                magika = Magika(prediction_mode=PredictionMode.MEDIUM_CONFIDENCE)
                result = magika.identify_path(path=str(path_obj))

                extensions = result.output.extensions
                if isinstance(extensions, list) and len(extensions) > 0:
                    extension = extensions[0]
                    if not extension.startswith("."):
                        extension = "." + extension
                    return FileType.from_extension(extension)
                elif isinstance(extensions, str) and extensions:
                    extension = extensions
                    if not extension.startswith("."):
                        extension = "." + extension
                    return FileType.from_extension(extension)
            except Exception:
                pass

        return FileType.from_mimetype(mime_type)

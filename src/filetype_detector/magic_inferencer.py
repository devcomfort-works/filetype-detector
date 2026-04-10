"""libmagic 기반 추론기 구현체를 제공한다."""

from .base_inferencer import BaseInferencer
from .file_type import FileType
from typing import Union
from pathlib import Path
import magic
import mimetypes


class MagicInferencer(BaseInferencer):
    """python-magic로 파일 형식을 추론한다.

    Notes
    -----
    파일 앞부분의 매직 넘버와 바이트 패턴을 libmagic 데이터베이스와 대조해
    MIME 타입을 결정한 뒤, `mimetypes`로 확장자로 변환한다.
    파일 이름이나 확장자에 의존하지 않아 확장자가 없거나 잘못된 파일에도 유용하다.
    """

    def infer(self, file_path: Union[Path, str]) -> FileType:
        """파일 내용으로부터 FileType을 추론한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            분석할 파일 경로이다.

        Returns
        -------
        FileType
            MIME 타입으로부터 추론된 확장자들을 포함하는 FileType 인스턴스이다.

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
        >>> inferencer = MagicInferencer()
        >>> ft = inferencer.infer('document.pdf')
        >>> '.pdf' in ft.extensions
        True
        """
        path_obj = Path(file_path)

        # 파일 존재 여부와 타입을 미리 검증하여 libmagic 호출 전에 실패시킨다.
        # 이렇게 하면 디렉토리 읽기 시도 등의 불필요한 연산을 피할 수 있다.
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {path_obj}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {path_obj}")

        # libmagic은 파일의 매직 넘버를 분석하여 MIME 타입을 반환한다.
        # 일부 파일은 매직 넘버가 불명확하여 None을 반환할 수 있다.
        mime_type = magic.from_file(str(path_obj), mime=True)
        if mime_type is None:
            raise RuntimeError(f"Cannot determine MIME type for file: {path_obj}")

        # MIME 타입으로부터 표준 확장자들을 조회한다.
        return FileType.from_mimetype(mime_type)

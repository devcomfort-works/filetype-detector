"""libmagic 기반 추론기 구현체를 제공한다."""

from .base_inferencer import BaseInferencer
from typing import Union
from pathlib import Path
import mimetypes
import magic


class MagicInferencer(BaseInferencer):
    """python-magic로 파일 형식을 추론한다.

    Notes
    -----
    파일 앞부분의 매직 넘버와 바이트 패턴을 libmagic 데이터베이스와 대조해
    MIME 타입을 결정한 뒤, `mimetypes`로 확장자로 변환한다.
    파일 이름이나 확장자에 의존하지 않아 확장자가 없거나 잘못된 파일에도 유용하다.
    """

    def infer(self, file_path: Union[Path, str]) -> str:
        """파일 내용으로부터 확장자를 추론한다.

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
            MIME 타입을 구하지 못했거나 확장자로 변환하지 못했을 때 발생한다.

        Examples
        --------
        >>> inferencer = MagicInferencer()
        >>> inferencer.infer('document.pdf')
        '.pdf'
        >>> inferencer.infer(Path('notes.txt'))
        '.txt'
        """
        file_path_str = str(file_path)
        path_obj = Path(file_path_str)
        if not path_obj.exists():
            raise FileNotFoundError(f"File not found: {file_path_str}")
        if not path_obj.is_file():
            raise ValueError(f"Path is not a file: {file_path_str}")
        mime_type = magic.from_file(file_path_str, mime=True)
        if mime_type is None:
            raise RuntimeError(f"Cannot determine MIME type for file: {file_path_str}")
        extension = mimetypes.guess_extension(mime_type, strict=True)
        if extension is None:
            raise RuntimeError(
                f"Cannot convert MIME type '{mime_type}' to extension for file: {file_path_str}"
            )
        return extension

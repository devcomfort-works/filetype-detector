"""경로 문자열만으로 확장자를 추론하는 추론기 구현체를 제공한다."""

from .base_inferencer import BaseInferencer
from .file_type import FileType
from typing import Union
from pathlib import Path


class LexicalInferencer(BaseInferencer):
    """파일 경로만 보고 확장자를 반환하는 추론기.

    Notes
    -----
    파일 내용을 읽지 않으므로 가장 빠르지만, 잘못된 확장자를 교정하지는 못한다.
    """

    def infer(self, file_path: Union[Path, str]) -> FileType:
        """파일 경로에서 확장자를 추출하여 FileType을 반환한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            확장자를 읽을 파일 경로이다.

        Returns
        -------
        FileType
            확장자와 대응하는 MIME 타입을 포함한 FileType 인스턴스이다.

        Raises
        ------
        ValueError
            파일 경로에 확장자가 없을 때 발생한다.

        Examples
        --------
        >>> inferencer = LexicalInferencer()
        >>> ft = inferencer.infer('document.pdf')
        >>> ft.extensions
        ('.pdf',)
        >>> ft.mime_types
        ('application/pdf',)
        >>> inferencer.infer('no_extension')
        Traceback (most recent call last):
            ...
        ValueError: ...
        """
        ext = Path(file_path).suffix.lower()
        if not ext:
            raise ValueError(f"파일 경로에 확장자가 없습니다: {file_path!r}")
        return FileType.from_extension(ext)

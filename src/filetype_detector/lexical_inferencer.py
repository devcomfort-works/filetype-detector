"""경로 문자열만으로 확장자를 추론하는 추론기 구현체를 제공한다."""

from .base_inferencer import BaseInferencer
from typing import Union
from pathlib import Path


class LexicalInferencer(BaseInferencer):
    """파일 경로만 보고 확장자를 반환하는 추론기.

    Notes
    -----
    파일 내용을 읽지 않으므로 가장 빠르지만, 잘못된 확장자를 교정하지는 못한다.
    """

    def infer(self, file_path: Union[Path, str]) -> str:
        """파일 경로에서 확장자를 추출한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            확장자를 읽을 파일 경로이다.

        Returns
        -------
        str
            소문자로 정규화된 확장자 문자열이다.
            확장자가 없으면 빈 문자열을 반환한다.

        Examples
        --------
        >>> inferencer = LexicalInferencer()
        >>> inferencer.infer('document.pdf')
        '.pdf'
        >>> inferencer.infer(Path('data.txt'))
        '.txt'
        >>> inferencer.infer('no_extension')
        ''
        """
        return Path(file_path).suffix.lower()

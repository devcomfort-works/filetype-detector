"""여러 추론기를 하나의 인터페이스로 감싸는 모듈.

`AutoInferencer`는 문자열 backend 키를 받아 적절한 추론기 구현체를 선택한다.
경로 기반 추론, Magic 기반 추론, Magika 기반 추론, 그리고 두 방식을 결합한
Hybrid 추론을 동일한 방식으로 사용할 수 있다.
"""

from typing import Literal, Union
from pathlib import Path

from .base_inferencer import BaseInferencer
from .lexical_inferencer import LexicalInferencer
from .magic_inferencer import MagicInferencer
from .magika_inferencer import MagikaInferencer
from .hybrid_inferencer import HybridInferencer


BackendType = Literal["lexical", "magic", "magika", "hybrid"]
"""`AutoInferencer`가 지원하는 공개 backend 키 타입이다."""

_BACKEND_MAP: dict[str, type[BaseInferencer]] = {
    "lexical": LexicalInferencer,
    "magic": MagicInferencer,
    "magika": MagikaInferencer,
    "hybrid": HybridInferencer,
    "both": HybridInferencer,
}


class AutoInferencer(BaseInferencer):
    """선택한 backend 구현체에 위임하는 추론기.

    Parameters
    ----------
    backend : BackendType
        사용할 backend 이름이다.

        - ``"lexical"``: 경로에서 확장자를 바로 읽는다.
        - ``"magic"``: 파일 내용을 기반으로 MIME 타입을 판별한다.
        - ``"magika"``: Magika 모델로 내용을 분석한다.
        - ``"hybrid"``: Magic으로 1차 분류한 뒤 텍스트 파일만 Magika로 재분석한다.

    Examples
    --------
    >>> inferencer = AutoInferencer(backend="lexical")
    >>> inferencer.infer("document.pdf")
    '.pdf'

    >>> inferencer = AutoInferencer(backend="magic")
    >>> inferencer.infer("archive.dat")
    '.zip'

    >>> inferencer = AutoInferencer(backend="magika")
    >>> inferencer.infer("data.txt")
    '.json'

    >>> inferencer = AutoInferencer(backend="hybrid")
    >>> inferencer.infer("script.py")
    '.py'
    """

    def __init__(self, backend: BackendType = "lexical") -> None:
        self._inferencer: BaseInferencer = _BACKEND_MAP[backend]()

    def infer(self, file_path: Union[Path, str]) -> str:
        """설정된 backend를 사용해 파일 확장자를 추론한다.

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
            backend가 파일 형식을 판별하지 못했을 때 발생한다.
        """
        return self._inferencer.infer(file_path)

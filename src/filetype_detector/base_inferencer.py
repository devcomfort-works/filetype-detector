"""파일 형식 추론기의 공통 인터페이스를 정의한다.

이 모듈은 모든 추론기가 따라야 하는 기본 추상 클래스를 제공한다.
구현체는 입력으로 받은 파일 경로로부터 FileType을 추론하는 `infer` 메서드를
반드시 구현해야 한다.
"""

from abc import ABC, abstractmethod
from typing import Union
from pathlib import Path
from .file_type import FileType


class BaseInferencer(ABC):
    """파일 형식 추론기의 추상 기반 클래스.

    Notes
    -----
    모든 하위 클래스는 `infer` 메서드를 구현해야 하며, 반환값은 FileType 인스턴스여야 한다.
    """

    @abstractmethod
    def infer(self, file_path: Union[Path, str]) -> FileType:
        """파일 경로로부터 파일 형식을 추론한다.

        Parameters
        ----------
        file_path : Union[Path, str]
            파일 형식을 추론할 대상 경로이다.

        Returns
        -------
        FileType
            추론된 확장자와 MIME 타입을 포함하는 FileType 인스턴스이다.

        Raises
        ------
        NotImplementedError
            하위 클래스가 이 메서드를 구현하지 않았을 때 발생한다.
        """
        raise NotImplementedError

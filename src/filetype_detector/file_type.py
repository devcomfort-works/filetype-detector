"""파일 확장자와 MIME 타입을 보관하는 데이터 스키마"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass


@dataclass(frozen=True)
class FileType:
    """파일 확장자와 MIME 타입을 보관한다.

    Parameters
    ----------
    extensions : tuple[str, ...]
        파일 확장자 튜플 (예: ``('.pdf',)``, ``('.jpg', '.jpeg')``)
    mime_types : tuple[str, ...]
        MIME 타입 튜플 (예: ``('application/pdf',)``, ``('image/jpeg',)``)

    Examples
    --------
    >>> ft = FileType(('.pdf',), ('application/pdf',))
    >>> ft.extensions
    ('.pdf',)
    >>> ft.mime_types
    ('application/pdf',)
    """

    extensions: tuple[str, ...] = ()
    mime_types: tuple[str, ...] = ()

    def __repr__(self) -> str:
        return (
            f"FileType(extensions={self.extensions!r}, mime_types={self.mime_types!r})"
        )

    @classmethod
    def from_extension(cls, ext: str) -> FileType:
        """확장자로부터 FileType을 생성한다.

        Parameters
        ----------
        ext : str
            파일 확장자 (점 포함, 예: ``.pdf``, ``.jpg``)

        Returns
        -------
        FileType
            확장자와 MIME 타입을 보관한 FileType 인스턴스

        Examples
        --------
        >>> ft = FileType.from_extension('.pdf')
        >>> '.pdf' in ft.extensions
        True
        >>> 'application/pdf' in ft.mime_types
        True
        """
        # strict=False는 OS별 MIME 매핑 차이를 무시하고 표준 타입 사용.
        # guess_type은 알려진 확장자만 MIME을 반환하므로 None 가능.
        mime, _ = mimetypes.guess_type(f"file{ext}", strict=False)
        mime_types_set = {mime} if mime else set()

        return cls(
            extensions=(ext,),
            mime_types=tuple(mime_types_set),
        )

    @classmethod
    def from_mimetype(cls, mime: str) -> FileType:
        """MIME 타입으로부터 FileType을 생성한다.

        Parameters
        ----------
        mime : str
            MIME 타입 문자열 (예: ``application/pdf``, ``image/jpeg``)

        Returns
        -------
        FileType
            확장자와 MIME 타입을 보관한 FileType 인스턴스

        Examples
        --------
        >>> ft = FileType.from_mimetype('application/pdf')
        >>> '.pdf' in ft.extensions
        True
        >>> 'application/pdf' in ft.mime_types
        True

        >>> ft = FileType.from_mimetype('image/jpeg')
        >>> len(ft.extensions) > 1  # .jpg, .jpeg 등 여러 확장자
        True
        """
        # 한 MIME 타입에 여러 확장자 가능 (예: image/jpeg는 .jpg, .jpeg).
        extensions = mimetypes.guess_all_extensions(mime, strict=False)
        if not extensions:
            extensions = []

        # 정렬하여 결과 재현성 보장.
        return cls(
            extensions=tuple(sorted(extensions)),
            mime_types=(mime,),
        )


if __name__ == "__main__":
    print("=== FileType.from_extension ===")
    ext_cases = [".pdf", ".jpg", ".mp4", ".json"]
    for case in ext_cases:
        ft = FileType.from_extension(case)
        print(f"  {case!r:<10} → mime_types={ft.mime_types}")

    print("\n=== FileType.from_mimetype ===")
    mime_cases = [
        "application/pdf",
        "image/jpeg",
        "application/json",
    ]
    for case in mime_cases:
        ft = FileType.from_mimetype(case)
        print(f"  {case!r:<25} → extensions={ft.extensions}")

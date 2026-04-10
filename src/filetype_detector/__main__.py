"""Main entry point for filetype_detector comparison tests."""

from pathlib import Path
from tabulate import tabulate

from .lexical_inferencer import LexicalInferencer
from .magic_inferencer import MagicInferencer
from .magika_inferencer import MagikaInferencer
from .hybrid_inferencer import HybridInferencer


def main():
    """Compare all inferencer implementations on fixture files."""
    print("=== FileType Detector Comparison ===\n")

    # fixtures 디렉토리 경로
    fixtures_dir = Path(__file__).parent.parent.parent / "tests" / "fixtures"

    # 사용 가능한 샘플 파일들
    sample_files = sorted(fixtures_dir.glob("sample.*"))

    if not sample_files:
        print(f"Error: No sample files found in {fixtures_dir}")
        return

    # Inferencer 인스턴스 생성
    inferencers = {
        "Lexical": LexicalInferencer(),
        "Magic": MagicInferencer(),
        "Magika": MagikaInferencer(),
        "Hybrid": HybridInferencer(),
    }

    # 테이블 데이터 수집
    table_data = []

    for file_path in sample_files:
        row = [file_path.name]

        for inferencer_name, inferencer in inferencers.items():
            try:
                ft = inferencer.infer(file_path)
                # 확장자들을 간단히 표시
                ext_str = ", ".join(ft.extensions) if ft.extensions else "—"
                # MIME 타입도 함께 표시
                mime_str = ft.mime_types[0] if ft.mime_types else "—"
                result = f"{ext_str}\n({mime_str})"
                row.append(result)
            except Exception as e:
                row.append(f"❌ {type(e).__name__}")

        table_data.append(row)

    # 테이블 출력
    headers = ["File"] + list(inferencers.keys())
    print(tabulate(table_data, headers=headers, tablefmt="grid"))
    print()


if __name__ == "__main__":
    main()

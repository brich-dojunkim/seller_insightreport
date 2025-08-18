# config.py
from pathlib import Path

CONFIG = {
    # 입력 엑셀 경로
    "INPUT_XLSX": str(Path("/Users/brich/Desktop/seller_insightreport/order_list_20250818120157_497.xlsx")),
    # 출력 폴더
    "OUTPUT_DIR": str(Path("./reports")),
    # 기간 필터(결제일 기준). None이면 전체
    "START_DATE": None,   # 예: "2025-08-11"
    "END_DATE":   None,   # 예: "2025-08-18"
    # 리포트 대상 셀러명 리스트(정확 일치). []면 전체 자동
    "SELLERS": ["포레스트핏"],
    # 전체 합산 리포트 생성 여부
    "BUILD_OVERALL_REPORT": True,
    # 셀러 리포트 링크 모음 인덱스 생성 여부
    "BUILD_INDEX": True,
    # 인덱스 타이틀
    "INDEX_TITLE": "셀러 리포트 인덱스",
}

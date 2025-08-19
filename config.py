# config.py
"""설정 파일"""

CONFIG = {
    # 입력 엑셀 경로
    "INPUT_XLSX": "/Users/brich/Desktop/seller_insightreport/files/order_list_20250818120157_497.xlsx",
    # 출력 폴더 (없으면 생성)
    "OUTPUT_DIR": "./reports",
    # 기간 필터 (결제일 기준). None이면 전체 사용
    "START_DATE": None,          # 예: "2025-08-11"
    "END_DATE":   None,          # 예: "2025-08-18"
    # 리포트 생성 대상 셀러명 리스트 (정확히 일치). 빈 리스트면 파일의 모든 셀러 자동 생성
    "SELLERS": ["포레스트핏"],     # 예: ["포레스트핏", "ABC몰"]  / []면 전체
    # 모든 셀러 합산 리포트도 생성할지
    "BUILD_OVERALL_REPORT": True,
    # 인덱스 페이지(셀러별 리포트 링크 모음) 생성할지
    "BUILD_INDEX": True,
}
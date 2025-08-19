#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
비플로우 주문리스트 → 지정한 셀러별 리포트(HTML, 결제일 기준) - 모듈화 버전
- 3페이지 A4 컴팩트 레이아웃
- 질문 기반 페이지 구성
"""

from pathlib import Path
from typing import List, Tuple

from config import CONFIG
from fonts import setup_korean_font
from constants import COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_SELLER
from utils import sanitize_filename
from file_manager import load_excel_data, determine_sellers, build_index_html
from report_generator import generate_report_html

def main():
    """메인 실행 함수"""
    # 폰트 설정
    setup_korean_font()
    
    # 설정 값 로드
    in_path = CONFIG["INPUT_XLSX"]
    out_dir = Path(CONFIG["OUTPUT_DIR"])
    out_dir.mkdir(parents=True, exist_ok=True)
    start = CONFIG.get("START_DATE")
    end = CONFIG.get("END_DATE")
    wanted = CONFIG.get("SELLERS") or []

    # 데이터 로드
    df = load_excel_data(in_path)
    
    # 필수 컬럼 확인
    if COL_PAYMENT_DATE not in df.columns or COL_ORDER_AMOUNT not in df.columns:
        raise KeyError(f"필수 칼럼 부족: '{COL_PAYMENT_DATE}', '{COL_ORDER_AMOUNT}'")

    # 생성 대상 셀러 결정
    sellers = determine_sellers(df, wanted)
    
    index_items: List[Tuple[str, str]] = []

    # 전체(합산) 리포트
    if CONFIG.get("BUILD_OVERALL_REPORT", True):
        html, dmin, dmax = generate_report_html(df, seller_name=None, start=start, end=end)
        fname = f"seller_report_전체_{dmin}_{dmax}.html"
        (out_dir / fname).write_text(html, encoding="utf-8")
        index_items.insert(0, ("전체", fname))
        print(f"✔ Saved: {out_dir / fname}")

    # 지정 셀러들 생성
    for s in sellers:
        if COL_SELLER in df.columns and s not in df[COL_SELLER].astype(str).unique():
            print(f"⚠️  스킵: '{s}'는 데이터에 없음")
            continue
        
        html, dmin, dmax = generate_report_html(df, seller_name=s, start=start, end=end)
        fname = f"seller_report_{sanitize_filename(s)}_{dmin}_{dmax}.html"
        (out_dir / fname).write_text(html, encoding="utf-8")
        index_items.append((s, fname))
        print(f"✔ Saved: {out_dir / fname}")

    # 인덱스 페이지
    if CONFIG.get("BUILD_INDEX", True) and index_items:
        idx_html = build_index_html("셀러 리포트 인덱스", index_items)
        (out_dir / "index.html").write_text(idx_html, encoding="utf-8")
        print(f"✔ Saved: {out_dir / 'index.html'}")

if __name__ == "__main__":
    main()
# utils.py
"""통합 유틸리티 모듈 - 순수 유틸리티만 포함"""

import math
import pandas as pd
from typing import Optional

# ================================
# 포맷팅 함수들
# ================================

def format_currency(v):
    """통화 포맷"""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"₩{int(round(float(v))):,}"

def pct(v):
    """퍼센트 포맷"""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{float(v)*100:.1f}%"

def df_to_html_table(d: Optional[pd.DataFrame], max_rows: int = 8) -> str:
    """DataFrame을 HTML 테이블로 변환"""
    if d is None or d.empty:
        return "<div>-</div>"
    return d.head(max_rows).to_html(index=False, border=1, justify="center", table_id="", classes="")

def sanitize_filename(s: str) -> str:
    """파일명에서 특수문자 제거"""
    return (
        s.replace("/", "_")
         .replace("\\", "_")
         .replace(" ", "_")
         .replace(":", "_")
         .replace("*", "_")
         .replace("?", "_")
         .replace('"', "_")
         .replace("<", "_")
         .replace(">", "_")
         .replace("|", "_")
    )
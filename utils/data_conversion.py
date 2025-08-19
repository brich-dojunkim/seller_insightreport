# utils/data_conversion.py
"""데이터 변환 유틸리티 함수들"""

import pandas as pd

def to_datetime_safe(s: pd.Series) -> pd.Series:
    """안전한 날짜 변환"""
    return pd.to_datetime(s, errors="coerce")

def to_number_safe(s: pd.Series) -> pd.Series:
    """안전한 숫자 변환"""
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9\.-]", "", regex=True), errors="coerce")
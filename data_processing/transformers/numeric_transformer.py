# data_processing/transformers/numeric_transformer.py
"""숫자 변환기"""

import pandas as pd

def to_number_safe(s: pd.Series) -> pd.Series:
    """안전한 숫자 변환"""
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9\.-]", "", regex=True), errors="coerce")
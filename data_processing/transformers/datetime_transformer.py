# data_processing/transformers/datetime_transformer.py
"""날짜/시간 변환기"""

import pandas as pd

def to_datetime_safe(s: pd.Series) -> pd.Series:
    """안전한 날짜 변환"""
    return pd.to_datetime(s, errors="coerce")
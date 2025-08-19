# data_processing/analyzers/operational_analyzer.py
"""운영 효율성 분석기"""

import pandas as pd
from constants import COL_STATUS

def get_status_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """상태 분석 (기존 호환성)"""
    if COL_STATUS not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    st = sdf[COL_STATUS].astype(str).value_counts().reset_index()
    st.columns = ["status", "count"]
    return st
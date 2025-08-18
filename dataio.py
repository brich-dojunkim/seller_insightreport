# dataio.py
from pathlib import Path
import pandas as pd

from .constants import COL_SELLER

def load_main_sheet(xlsx_path: str) -> pd.DataFrame:
    p = Path(xlsx_path)
    if not p.exists():
        raise FileNotFoundError(f"Input not found: {p}")
    xls = pd.ExcelFile(p)
    sheets = {name: xls.parse(name) for name in xls.sheet_names}
    _, df = max(sheets.items(), key=lambda kv: len(kv[1]))
    df.columns = [str(c).strip() for c in df.columns]
    return df

def resolve_sellers(df: pd.DataFrame, wanted: list[str]) -> list[str]:
    if wanted:
        return wanted
    if COL_SELLER not in df.columns:
        raise KeyError(f"모든 셀러 자동 생성에는 '{COL_SELLER}' 칼럼이 필요합니다.")
    return df[COL_SELLER].dropna().astype(str).unique().tolist()

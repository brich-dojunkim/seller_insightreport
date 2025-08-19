# file_manager.py
"""파일 입출력 관리"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple
from constants import COL_SELLER

def load_excel_data(xlsx_path: str) -> pd.DataFrame:
    """엑셀 파일에서 가장 큰 시트 로드"""
    path = Path(xlsx_path)
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}")
    
    xls = pd.ExcelFile(path)
    sheets = {name: xls.parse(name) for name in xls.sheet_names}
    main_name, df = max(sheets.items(), key=lambda kv: len(kv[1]))
    df.columns = [str(c).strip() for c in df.columns]
    return df

def determine_sellers(df: pd.DataFrame, wanted_sellers: List[str]) -> List[str]:
    """생성 대상 셀러 목록 결정"""
    if wanted_sellers:
        return wanted_sellers
    
    if COL_SELLER not in df.columns:
        raise KeyError(f"모든 셀러 생성에는 '{COL_SELLER}' 칼럼이 필요합니다.")
    
    return df[COL_SELLER].dropna().astype(str).unique().tolist()

def build_index_html(title: str, items: List[Tuple[str, str]]) -> str:
    """인덱스 HTML 페이지 생성"""
    links = "\n".join([f'<li><a href="{fname}" target="_blank">{name}</a></li>' for name, fname in items])
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, sans-serif; padding: 24px; }}
    h1 {{ margin-top: 0; }}
    ul {{ line-height: 1.8; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <ul>
    {links}
  </ul>
</body>
</html>
"""
# file_manager.py
"""파일 입출력 관리"""

import pandas as pd
from pathlib import Path
from typing import List, Tuple
from constants import COL_SELLER

def load_excel_data(xlsx_path: str) -> pd.DataFrame:
    """엑셀 파일에서 가장 큰 시트 로드 (개선된 에러 처리)"""
    path = Path(xlsx_path)
    if not path.exists():
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {path}")
    
    try:
        xls = pd.ExcelFile(path)
        if not xls.sheet_names:
            raise ValueError("엑셀 파일에 시트가 없습니다.")
        
        sheets = {}
        for name in xls.sheet_names:
            try:
                sheet_df = xls.parse(name)
                if not sheet_df.empty:
                    sheets[name] = sheet_df
            except Exception as e:
                print(f"시트 '{name}' 로드 실패: {e}")
                continue
        
        if not sheets:
            raise ValueError("읽을 수 있는 시트가 없습니다.")
        
        main_name, df = max(sheets.items(), key=lambda kv: len(kv[1]))
        df.columns = [str(c).strip() for c in df.columns]
        
        if df.empty:
            raise ValueError("선택된 시트가 비어있습니다.")
        
        return df
        
    except Exception as e:
        raise ValueError(f"엑셀 파일 읽기 실패: {e}")

def determine_sellers(df: pd.DataFrame, wanted_sellers: List[str]) -> List[str]:
    """생성 대상 셀러 목록 결정"""
    if wanted_sellers:
        # 요청된 셀러들이 실제 데이터에 있는지 확인
        if COL_SELLER in df.columns:
            available_sellers = df[COL_SELLER].dropna().astype(str).unique().tolist()
            missing_sellers = [s for s in wanted_sellers if s not in available_sellers]
            if missing_sellers:
                print(f"경고: 다음 셀러들이 데이터에 없습니다: {missing_sellers}")
        return wanted_sellers
    
    if COL_SELLER not in df.columns:
        raise KeyError(f"모든 셀러 생성에는 '{COL_SELLER}' 칼럼이 필요합니다.")
    
    sellers = df[COL_SELLER].dropna().astype(str).unique().tolist()
    if not sellers:
        raise ValueError("데이터에 셀러 정보가 없습니다.")
    
    return sellers

def build_index_html(title: str, items: List[Tuple[str, str]]) -> str:
    """인덱스 HTML 페이지 생성"""
    if not items:
        links = "<li>생성된 리포트가 없습니다.</li>"
    else:
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
# utils/category_mapping.py
"""카테고리 매핑 유틸리티 함수들"""

import pandas as pd
from typing import Optional, Dict
from pathlib import Path

# 전역 카테고리 매핑 캐시
_category_mapping_cache = None

def load_category_mapping(csv_path: str = "/Users/brich/Desktop/seller_insightreport/files/brich_category_250407.csv") -> Dict[str, str]:
    """카테고리 매핑 파일 로드 및 캐시"""
    global _category_mapping_cache
    
    if _category_mapping_cache is not None:
        return _category_mapping_cache
    
    try:
        # CSV 파일 로드
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # Code -> Name 매핑 딕셔너리 생성
        mapping = {}
        for _, row in df.iterrows():
            code = str(row['Code']).strip()
            name = str(row['Name']).strip()
            if code and name and code != 'nan' and name != 'nan':
                mapping[code] = name
        
        _category_mapping_cache = mapping
        print(f"✅ 카테고리 매핑 로드 완료: {len(mapping):,}개")
        return mapping
        
    except Exception as e:
        print(f"⚠️ 카테고리 매핑 파일 로드 실패: {e}")
        return {}

def map_category_code_to_name(category_code, mapping: Optional[Dict[str, str]] = None) -> str:
    """카테고리 코드를 한글명으로 변환"""
    
    if pd.isna(category_code) or category_code is None:
        return None
    
    # 매핑이 제공되지 않으면 자동 로드
    if mapping is None:
        mapping = load_category_mapping()
    
    # 코드를 문자열로 변환 (소수점 제거)
    if isinstance(category_code, float):
        code_str = str(int(category_code))
    else:
        code_str = str(category_code).strip()
    
    # 매핑에서 찾기
    if code_str in mapping:
        return mapping[code_str]
    
    # 매핑에서 찾지 못한 경우 원본 반환
    return f"미분류_{code_str}"
# data_processing/transformers/category_transformer.py
"""카테고리 매핑 변환기"""

import pandas as pd
from typing import Optional, Dict
from pathlib import Path

# 전역 카테고리 매핑 캐시
_category_mapping_cache = None

def load_category_mapping(csv_path: Optional[str] = None) -> Dict[str, str]:
    """카테고리 매핑 파일 로드 및 캐시"""
    global _category_mapping_cache
    
    if _category_mapping_cache is not None:
        return _category_mapping_cache
    
    # 경로 우선순위: 1) 파라미터 2) 설정파일
    if csv_path is None:
        try:
            from config import CONFIG
            csv_path = CONFIG.get('CATEGORY_MAPPING_PATH')
        except:
            pass
    
    if csv_path is None or not Path(csv_path).exists():
        print(f"⚠️ 카테고리 매핑 파일을 찾을 수 없음: {csv_path}")
        print(f"    config.py에서 CATEGORY_MAPPING_PATH를 확인하세요.")
        _category_mapping_cache = {}
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
        _category_mapping_cache = {}
        return _category_mapping_cache

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

def apply_category_mapping(category_series: pd.Series) -> pd.Series:
    """카테고리 Series에 매핑 적용"""
    mapping = load_category_mapping()
    if not mapping:
        return category_series
    
    return category_series.apply(lambda x: map_category_code_to_name(x, mapping))
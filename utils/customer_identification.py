# utils/customer_identification.py
"""고객 식별 유틸리티 함수들"""

import pandas as pd
import hashlib

def create_customer_id(name_series: pd.Series, phone_series: pd.Series) -> pd.Series:
    """구매자명 + 전화번호로 고유 고객 ID 생성"""
    def make_customer_id(name, phone):
        if pd.isna(name) or pd.isna(phone):
            return None
        
        # 전화번호 정규화 (하이픈, 공백 제거)
        clean_phone = str(phone).replace('-', '').replace(' ', '').replace('(', '').replace(')', '')
        clean_name = str(name).strip()
        
        if not clean_name or not clean_phone:
            return None
            
        # 이름+전화번호 조합으로 해시 생성
        combined = f"{clean_name}_{clean_phone}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()[:12]
    
    return pd.Series([make_customer_id(name, phone) for name, phone in zip(name_series, phone_series)])
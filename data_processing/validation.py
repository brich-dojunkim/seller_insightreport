# data_processing/validation.py
"""데이터 검증 및 전처리 모듈"""

import pandas as pd
from typing import Optional
from constants import *
from utils import to_datetime_safe, to_number_safe, create_customer_id, extract_region_from_address

def validate_dataframe(df: pd.DataFrame) -> None:
    """데이터프레임 유효성 검사"""
    if df.empty:
        raise ValueError("입력 데이터가 비어있습니다.")
    
    required_cols = [COL_PAYMENT_DATE, COL_ORDER_AMOUNT]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"필수 컬럼이 없습니다: {missing_cols}")

def prepare_dataframe(df: pd.DataFrame, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    """데이터프레임 전처리 (고객 식별 로직 포함)"""
    validate_dataframe(df)
    
    # 필요한 컬럼만 선택
    needed_cols = [COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_SELLER, COL_CHANNEL, 
                   COL_QTY, COL_STATUS, COL_REFUND_FIELD, COL_SHIP_DATE, 
                   COL_DELIVERED_DATE, COL_CUSTOMER, COL_ITEM_NAME, COL_ORDER_ID,
                   COL_BUYER_NAME, COL_BUYER_PHONE, COL_ADDRESS, COL_POSTAL_CODE,
                   COL_CATEGORY, COL_SETTLEMENT, COL_PRODUCT_PRICE]
    available_cols = [col for col in needed_cols if col in df.columns]
    
    dfp = df[available_cols].copy()
    dfp["__dt__"] = to_datetime_safe(dfp[COL_PAYMENT_DATE])
    dfp["__amount__"] = to_number_safe(dfp[COL_ORDER_AMOUNT])
    dfp["__qty__"] = to_number_safe(dfp[COL_QTY]) if COL_QTY in dfp.columns else 1

    # 고객 식별 ID 생성
    if COL_BUYER_NAME in dfp.columns and COL_BUYER_PHONE in dfp.columns:
        dfp["__customer_id__"] = create_customer_id(dfp[COL_BUYER_NAME], dfp[COL_BUYER_PHONE])
    elif COL_CUSTOMER in dfp.columns:
        dfp["__customer_id__"] = dfp[COL_CUSTOMER].astype(str)
    else:
        dfp["__customer_id__"] = None

    # 지역 정보 추출
    if COL_ADDRESS in dfp.columns:
        dfp["__region__"] = extract_region_from_address(dfp[COL_ADDRESS])

    # 유효 데이터만
    dfp = dfp[dfp["__dt__"].notna() & dfp["__amount__"].notna()]
    if dfp.empty:
        raise ValueError("유효한 데이터가 없습니다.")

    # 기간 필터
    if start: dfp = dfp[dfp["__dt__"] >= pd.to_datetime(start)]
    if end:   dfp = dfp[dfp["__dt__"] < pd.to_datetime(end) + pd.to_timedelta(1, "D")]

    return dfp

def slice_by_seller(df: pd.DataFrame, seller_name: Optional[str]) -> pd.DataFrame:
    """셀러별 데이터 슬라이싱"""
    if seller_name and COL_SELLER in df.columns:
        filtered = df[df[COL_SELLER].astype(str) == str(seller_name)].copy()
        if filtered.empty:
            raise ValueError(f"셀러 '{seller_name}'의 데이터가 없습니다.")
        return filtered
    return df.copy()

def safe_divide(a, b):
    """안전한 나누기"""
    if b == 0 or pd.isna(b):
        return float("nan")
    return a / b

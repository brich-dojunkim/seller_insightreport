# data_processing/pipeline.py
"""메인 데이터 처리 파이프라인"""

import pandas as pd
from typing import Optional, Dict, Any
from constants import *

# 변환기들
from .transformers import (
    to_datetime_safe, to_number_safe, create_customer_id, 
    extract_region_from_address, apply_category_mapping
)

# 분석기들
from .analyzers import (
    get_channel_analysis, get_product_analysis, get_category_analysis,
    get_region_analysis, get_time_analysis, get_heatmap_data, 
    get_status_analysis, get_comprehensive_analysis, get_daily_trend
)

# 지표 계산기들
from .metrics import calculate_comprehensive_kpis, calculate_kpis

def apply_all_transformations(df: pd.DataFrame) -> pd.DataFrame:
    """모든 변환을 한 번에 적용하는 통합 함수"""
    result_df = df.copy()
    
    # 1. 기본 데이터 변환
    if COL_PAYMENT_DATE in result_df.columns:
        result_df["__dt__"] = to_datetime_safe(result_df[COL_PAYMENT_DATE])
    
    if COL_ORDER_AMOUNT in result_df.columns:
        result_df["__amount__"] = to_number_safe(result_df[COL_ORDER_AMOUNT])
    
    if COL_QTY in result_df.columns:
        result_df["__qty__"] = to_number_safe(result_df[COL_QTY])
    else:
        result_df["__qty__"] = 1
    
    # 2. 고객 식별 ID 생성
    if COL_BUYER_NAME in result_df.columns and COL_BUYER_PHONE in result_df.columns:
        result_df["__customer_id__"] = create_customer_id(
            result_df[COL_BUYER_NAME], 
            result_df[COL_BUYER_PHONE]
        )
    elif COL_CUSTOMER in result_df.columns:
        result_df["__customer_id__"] = result_df[COL_CUSTOMER].astype(str)
    else:
        result_df["__customer_id__"] = None
    
    # 3. 지역 정보 추출
    if COL_ADDRESS in result_df.columns:
        result_df["__region__"] = extract_region_from_address(result_df[COL_ADDRESS])
    
    # 4. 카테고리 매핑 적용 (기존에 누락되었던 부분!)
    if COL_CATEGORY in result_df.columns:
        result_df["__category_mapped__"] = apply_category_mapping(result_df[COL_CATEGORY])
    
    return result_df

class DataPipeline:
    """데이터 처리 파이프라인 클래스"""
    
    def __init__(self):
        self.processed_data = None
        self.analysis_cache = {}
        self.metrics_cache = {}
    
    def process(self, df: pd.DataFrame, start: Optional[str] = None, end: Optional[str] = None) -> pd.DataFrame:
        """전체 데이터 처리 파이프라인 실행"""
        
        # 1. 데이터 변환
        processed = apply_all_transformations(df)
        
        # 2. 유효성 검증
        processed = processed[processed["__dt__"].notna() & processed["__amount__"].notna()]
        if processed.empty:
            raise ValueError("유효한 데이터가 없습니다.")
        
        # 3. 기간 필터
        if start: 
            processed = processed[processed["__dt__"] >= pd.to_datetime(start)]
        if end:   
            processed = processed[processed["__dt__"] < pd.to_datetime(end) + pd.to_timedelta(1, "D")]
        
        self.processed_data = processed
        return processed
    
    def get_seller_data(self, seller_name: Optional[str] = None) -> pd.DataFrame:
        """셀러별 데이터 추출"""
        if self.processed_data is None:
            raise ValueError("데이터를 먼저 처리해야 합니다.")
        
        if seller_name and COL_SELLER in self.processed_data.columns:
            filtered = self.processed_data[self.processed_data[COL_SELLER].astype(str) == str(seller_name)].copy()
            if filtered.empty:
                raise ValueError(f"셀러 '{seller_name}'의 데이터가 없습니다.")
            return filtered
        
        return self.processed_data.copy()
    
    def analyze(self, seller_data: pd.DataFrame) -> Dict[str, Any]:
        """종합 분석 실행 (캐싱으로 중복 계산 방지)"""
        data_hash = str(hash(str(seller_data.shape) + str(seller_data.columns.tolist())))
        
        if data_hash not in self.analysis_cache:
            self.analysis_cache[data_hash] = get_comprehensive_analysis(seller_data)
        
        return self.analysis_cache[data_hash]
    
    def calculate_metrics(self, seller_data: pd.DataFrame, overall_data: pd.DataFrame) -> Dict[str, Any]:
        """KPI 계산 (캐싱으로 중복 계산 방지)"""
        seller_hash = str(hash(str(seller_data.shape)))
        overall_hash = str(hash(str(overall_data.shape)))
        cache_key = f"{seller_hash}_{overall_hash}"
        
        if cache_key not in self.metrics_cache:
            self.metrics_cache[cache_key] = calculate_comprehensive_kpis(seller_data, overall_data)
        
        return self.metrics_cache[cache_key]
    
    def clear_cache(self):
        """캐시 초기화"""
        self.analysis_cache.clear()
        self.metrics_cache.clear()

# 전역 파이프라인 인스턴스 (싱글톤 패턴)
_global_pipeline = DataPipeline()

def get_pipeline() -> DataPipeline:
    """전역 파이프라인 인스턴스 반환"""
    return _global_pipeline
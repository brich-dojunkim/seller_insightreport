# data_processing/__init__.py
"""데이터 처리 패키지 - 새로운 모듈 구조"""

# 기존 호환성을 위한 validation 함수들
from .validation import (
    validate_dataframe, 
    prepare_dataframe, 
    slice_by_seller, 
    safe_divide
)

# 새로운 구조의 모듈들
from .transformers import *
from .analyzers import *
from .metrics import *
from .pipeline import DataPipeline, get_pipeline, apply_all_transformations

# 기존 코드 호환성을 위한 전체 함수 리스트
__all__ = [
    # 기존 호환성 (validation)
    'validate_dataframe',
    'prepare_dataframe', 
    'slice_by_seller',
    'safe_divide',
    
    # 변환기들 (transformers)
    'to_datetime_safe',
    'to_number_safe',
    'create_customer_id',
    'extract_region_from_address',
    'load_category_mapping',
    'map_category_code_to_name',
    'apply_category_mapping',
    
    # 분석기들 (analyzers)
    'get_channel_analysis',
    'get_product_analysis', 
    'get_category_analysis',
    'get_region_analysis',
    'get_time_analysis',
    'get_heatmap_data',
    'get_status_analysis',
    'get_comprehensive_analysis',
    'get_daily_trend',
    
    # 지표 계산기들 (metrics)
    'calculate_comprehensive_kpis',
    'calculate_kpis',
    'calculate_sales_metrics',
    'calculate_customer_metrics',
    'calculate_operational_metrics', 
    'calculate_benchmark_metrics',
    
    # 파이프라인
    'DataPipeline',
    'get_pipeline',
    'apply_all_transformations'
]
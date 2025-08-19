# data_processing/__init__.py
"""데이터 처리 패키지 - 모든 함수들을 패키지 레벨에서 직접 import 가능"""

from .validation import (
    validate_dataframe, 
    prepare_dataframe, 
    slice_by_seller, 
    safe_divide
)

from .kpi_metrics import (
    calculate_comprehensive_kpis,
    calculate_kpis
)

from .business_analysis import (
    get_channel_analysis,
    get_product_analysis,
    get_category_analysis,
    get_region_analysis,
    get_time_analysis,
    get_heatmap_data,
    get_status_analysis,
    get_comprehensive_analysis,
    get_daily_trend
)

# 기존 코드 호환성을 위한 전체 함수 리스트
__all__ = [
    # 데이터 검증 및 전처리
    'validate_dataframe',
    'prepare_dataframe', 
    'slice_by_seller',
    'safe_divide',
    
    # KPI 계산
    'calculate_comprehensive_kpis',
    'calculate_kpis',
    
    # 비즈니스 분석
    'get_channel_analysis',
    'get_product_analysis', 
    'get_category_analysis',
    'get_region_analysis',
    'get_time_analysis',
    'get_heatmap_data',
    'get_status_analysis',
    'get_comprehensive_analysis',
    'get_daily_trend'
]

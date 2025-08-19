# data_processing/analyzers/__init__.py
"""분석기 패키지"""

import pandas as pd
from .channel_analyzer import get_channel_analysis
from .product_analyzer import get_product_analysis, get_category_analysis
from .customer_analyzer import get_region_analysis
from .temporal_analyzer import get_time_analysis, get_daily_trend, get_heatmap_data
from .operational_analyzer import get_status_analysis
from .relative_analyzer import (
    get_relative_channel_analysis,
    get_relative_region_analysis, 
    get_relative_time_analysis,
    get_comprehensive_relative_analysis
)

def get_comprehensive_analysis(sdf: pd.DataFrame):
    """종합 분석 결과 반환"""
    return {
        'channel_analysis': get_channel_analysis(sdf),
        'product_analysis': get_product_analysis(sdf),
        'category_analysis': get_category_analysis(sdf),
        'region_analysis': get_region_analysis(sdf),
        'time_analysis': get_time_analysis(sdf)
    }

def get_comprehensive_analysis_with_benchmarks(sdf: pd.DataFrame, overall: pd.DataFrame):
    """벤치마킹이 포함된 종합 분석"""
    return {
        # 기본 분석
        'channel_analysis': get_channel_analysis(sdf),
        'product_analysis': get_product_analysis(sdf),
        'category_analysis': get_category_analysis(sdf),
        'region_analysis': get_region_analysis(sdf),
        'time_analysis': get_time_analysis(sdf),
        
        # 상대적 분석 (카테고리 평균 대비)
        'relative_channel_analysis': get_relative_channel_analysis(sdf, overall),
        'relative_region_analysis': get_relative_region_analysis(sdf, overall),
        'relative_time_analysis': get_relative_time_analysis(sdf, overall)
    }

__all__ = [
    'get_channel_analysis',
    'get_product_analysis',
    'get_category_analysis',
    'get_region_analysis',
    'get_time_analysis',
    'get_heatmap_data',
    'get_status_analysis',
    'get_comprehensive_analysis',
    'get_daily_trend',
    
    # 상대 분석 추가
    'get_relative_channel_analysis',
    'get_relative_region_analysis',
    'get_relative_time_analysis', 
    'get_comprehensive_relative_analysis',
    'get_comprehensive_analysis_with_benchmarks'
]
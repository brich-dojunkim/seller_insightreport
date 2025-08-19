# data_processing/metrics/benchmark_metrics.py
"""확장된 벤치마킹 지표 계산"""

import pandas as pd
from typing import Dict
from constants import COL_STATUS, COL_SELLER

def calculate_benchmark_metrics(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict[str, float]:
    """확장된 벤치마킹 지표 계산 - 모든 지표를 상대적 비교로"""
    if overall.empty:
        return {}
    
    from .benchmark_calculator import get_benchmark_calculator
    calculator = get_benchmark_calculator()
    
    # 내 주요 카테고리 찾기
    my_category = calculator.get_my_category(sdf)
    
    if my_category is None:
        # 카테고리를 찾을 수 없으면 기존 방식 (전체 평균)
        return _calculate_legacy_benchmarks(sdf, overall)
    
    # 카테고리별 벤치마크 계산
    category_benchmarks = calculator.calculate_category_benchmarks(overall, my_category)
    
    if not category_benchmarks:
        return _calculate_legacy_benchmarks(sdf, overall)
    
    # 내 성과 계산
    from .sales_metrics import calculate_sales_metrics
    from .customer_metrics import calculate_customer_metrics  
    from .operational_metrics import calculate_operational_metrics
    
    my_metrics = {}
    my_metrics.update(calculate_sales_metrics(sdf))
    my_metrics.update(calculate_customer_metrics(sdf))
    my_metrics.update(calculate_operational_metrics(sdf))
    
    # 상대적 성과 계산
    relative_metrics = calculator.calculate_relative_performance(my_metrics, category_benchmarks)
    
    # 기본 벤치마크 정보 추가
    relative_metrics['benchmark_category'] = my_category
    
    # 카테고리 내 셀러 수 계산 (수정됨)
    try:
        if '__category_mapped__' in overall.columns:
            category_data = overall[overall['__category_mapped__'] == my_category]
        elif 'COL_CATEGORY' in overall.columns:
            category_data = overall[overall['COL_CATEGORY'] == my_category]
        else:
            category_data = overall
        
        if COL_SELLER in category_data.columns:
            unique_sellers = category_data[COL_SELLER].nunique()
        else:
            unique_sellers = 1
            
        relative_metrics['benchmark_sellers_count'] = unique_sellers
    except Exception as e:
        print(f"⚠️ 벤치마크 셀러 수 계산 실패: {e}")
        relative_metrics['benchmark_sellers_count'] = 0
    
    return relative_metrics

def _calculate_legacy_benchmarks(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict[str, float]:
    """기존 벤치마킹 방식 (전체 평균 대비)"""
    metrics = {}
    
    # 전체 평균 AOV
    overall_aov = overall["__amount__"].sum() / len(overall) if len(overall) > 0 else 0
    metrics['benchmark_aov'] = overall_aov
    
    # 전체 평균 취소율
    if COL_STATUS in overall.columns:
        overall_cancel = (overall[COL_STATUS] == '결제취소').sum() / len(overall) if len(overall) > 0 else 0
        metrics['benchmark_cancel_rate'] = overall_cancel
    else:
        metrics['benchmark_cancel_rate'] = float('nan')
    
    return metrics
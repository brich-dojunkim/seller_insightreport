# data_processing/metrics/__init__.py
"""지표 계산 패키지 - 확장된 벤치마킹 포함"""

import pandas as pd
import math
from typing import Dict, Any

from .sales_metrics import calculate_sales_metrics
from .customer_metrics import calculate_customer_metrics
from .operational_metrics import calculate_operational_metrics
from .benchmark_metrics import calculate_benchmark_metrics

def calculate_comprehensive_kpis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict[str, Any]:
    """종합 KPI 계산 - 확장된 벤치마킹 포함"""
    if sdf.empty:
        raise ValueError("분석할 데이터가 없습니다.")
    
    kpis = {}
    
    # 기본 지표들 계산
    kpis.update(calculate_sales_metrics(sdf))
    kpis.update(calculate_customer_metrics(sdf))
    kpis.update(calculate_operational_metrics(sdf))
    
    # 확장된 벤치마킹 지표 (모든 지표의 상대적 비교)
    benchmark_metrics = calculate_benchmark_metrics(sdf, overall)
    kpis.update(benchmark_metrics)
    
    return kpis

def calculate_kpis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict:
    """기존 KPI 계산 (기존 코드 호환성) - comprehensive를 사용하여 중복 제거"""
    comprehensive = calculate_comprehensive_kpis(sdf, overall)
    
    # 기존 형식으로 매핑 (상대적 지표 추가)
    legacy_format = {
        'orders': comprehensive.get('total_orders', 0),
        'revenue': comprehensive.get('total_revenue', 0),
        'aov': comprehensive.get('avg_order_value', float('nan')),
        'refund_rate_any': comprehensive.get('cancel_rate', float('nan')),
        'unique_customers': comprehensive.get('unique_customers', float('nan')),
        'repurchase_rate': comprehensive.get('repeat_rate', float('nan')),
        'lead_ship': comprehensive.get('avg_ship_leadtime', float('nan')),
        'lead_deliv': comprehensive.get('avg_delivery_time', float('nan')),
        'overall_aov': comprehensive.get('benchmark_aov', float('nan')),
        'overall_refund_rate_any': comprehensive.get('benchmark_cancel_rate', float('nan')),
    }
    
    # 상대적 성과 정보 추가
    category = comprehensive.get('benchmark_category', '전체')
    relative_aov = comprehensive.get('avg_order_value_vs_category', float('nan'))
    relative_cancel = comprehensive.get('cancel_rate_vs_category', float('nan'))
    
    if not math.isnan(relative_aov):
        legacy_format['aov_vs_category'] = relative_aov
        legacy_format['aov_performance'] = '우수' if relative_aov >= 1.1 else '보통' if relative_aov >= 0.9 else '개선필요'
    
    if not math.isnan(relative_cancel):
        legacy_format['cancel_vs_category'] = relative_cancel  
        legacy_format['cancel_performance'] = '우수' if relative_cancel <= 0.9 else '보통' if relative_cancel <= 1.1 else '개선필요'
    
    # 개선된 추천사항
    recommendations = [f"{category} 카테고리 평균 대비 성과 분석을 바탕으로 최적화 방안을 검토하세요."]
    
    if not math.isnan(relative_aov) and relative_aov < 0.9:
        recommendations.append("AOV가 카테고리 평균보다 낮습니다. 상품 구성 및 마케팅 전략을 점검해보세요.")
    
    if not math.isnan(relative_cancel) and relative_cancel > 1.1:
        recommendations.append("취소율이 카테고리 평균보다 높습니다. 주문 프로세스와 상품 정보를 개선해보세요.")
    
    legacy_format['recos'] = recommendations
    
    return legacy_format

__all__ = [
    'calculate_comprehensive_kpis',
    'calculate_kpis',
    'calculate_sales_metrics',
    'calculate_customer_metrics', 
    'calculate_operational_metrics',
    'calculate_benchmark_metrics'
]
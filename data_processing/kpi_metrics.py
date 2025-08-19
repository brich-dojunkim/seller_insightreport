# data_processing/kpi_metrics.py
"""KPI 계산 모듈"""

import math
import pandas as pd
from typing import Dict, Any
from constants import *
from utils import to_datetime_safe, to_number_safe
from .validation import safe_divide

def calculate_comprehensive_kpis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict[str, Any]:
    """종합 KPI 계산 (45개 지표)"""
    if sdf.empty:
        raise ValueError("분석할 데이터가 없습니다.")
    
    kpis = {}
    
    # === 1. 기본 매출 지표 ===
    kpis['total_orders'] = int(len(sdf))
    kpis['total_revenue'] = float(sdf["__amount__"].sum())
    kpis['avg_order_value'] = safe_divide(kpis['total_revenue'], kpis['total_orders'])
    kpis['total_quantity'] = int(sdf["__qty__"].sum())
    
    if COL_PRODUCT_PRICE in sdf.columns:
        kpis['avg_product_price'] = float(to_number_safe(sdf[COL_PRODUCT_PRICE]).mean())
    
    # === 2. 고객 행동 지표 ===
    if "__customer_id__" in sdf.columns and sdf["__customer_id__"].notna().any():
        customer_counts = sdf["__customer_id__"].value_counts()
        kpis['unique_customers'] = int(len(customer_counts))
        kpis['repeat_customers'] = int((customer_counts >= 2).sum())
        kpis['repeat_rate'] = safe_divide(kpis['repeat_customers'], kpis['unique_customers'])
        kpis['avg_orders_per_customer'] = safe_divide(kpis['total_orders'], kpis['unique_customers'])
        kpis['customer_ltv'] = safe_divide(kpis['total_revenue'], kpis['unique_customers'])
    
    # === 3. 주문 상태 지표 ===
    if COL_STATUS in sdf.columns:
        status_counts = sdf[COL_STATUS].value_counts()
        total = len(sdf)
        kpis['completion_rate'] = safe_divide(status_counts.get('배송완료', 0), total)
        kpis['cancel_rate'] = safe_divide(status_counts.get('결제취소', 0), total)
        kpis['delay_rate'] = safe_divide(status_counts.get('배송지연', 0), total)
        kpis['return_rate'] = safe_divide(status_counts.get('반품', 0), total)
        kpis['exchange_rate'] = safe_divide(status_counts.get('교환', 0), total)
    
    # === 4. 운영 효율성 지표 ===
    if COL_SHIP_DATE in sdf.columns:
        ship_data = sdf[sdf[COL_SHIP_DATE].notna()].copy()
        if not ship_data.empty:
            ship_data['ship_dt'] = to_datetime_safe(ship_data[COL_SHIP_DATE])
            lead_times = (ship_data['ship_dt'] - ship_data["__dt__"]).dt.total_seconds() / 86400.0
            kpis['avg_ship_leadtime'] = float(lead_times.mean())
            kpis['same_day_ship_rate'] = safe_divide((lead_times <= 1).sum(), len(lead_times))
    
    if COL_DELIVERED_DATE in sdf.columns and COL_SHIP_DATE in sdf.columns:
        delivery_data = sdf[sdf[COL_DELIVERED_DATE].notna() & sdf[COL_SHIP_DATE].notna()].copy()
        if not delivery_data.empty:
            delivery_data['delivery_dt'] = to_datetime_safe(delivery_data[COL_DELIVERED_DATE])
            delivery_data['ship_dt'] = to_datetime_safe(delivery_data[COL_SHIP_DATE])
            delivery_times = (delivery_data['delivery_dt'] - delivery_data['ship_dt']).dt.total_seconds() / 86400.0
            kpis['avg_delivery_time'] = float(delivery_times.mean())
    
    # === 5. 벤치마킹 지표 ===
    if not overall.empty:
        overall_aov = safe_divide(overall["__amount__"].sum(), len(overall))
        kpis['benchmark_aov'] = overall_aov
        
        if COL_STATUS in overall.columns:
            overall_cancel = safe_divide(
                (overall[COL_STATUS] == '결제취소').sum(), 
                len(overall)
            )
            kpis['benchmark_cancel_rate'] = overall_cancel
    
    return kpis

def calculate_kpis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict:
    """기존 KPI 계산 (기존 코드 호환성)"""
    comprehensive = calculate_comprehensive_kpis(sdf, overall)
    
    # 기존 형식으로 매핑
    return {
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
        'recos': ["종합 분석 결과를 바탕으로 최적화 방안을 검토하세요."]
    }
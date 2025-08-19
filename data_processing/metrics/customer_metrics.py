# data_processing/metrics/customer_metrics.py
"""고객 관련 지표 계산"""

import pandas as pd
import math
from typing import Dict

def calculate_customer_metrics(sdf: pd.DataFrame) -> Dict[str, float]:
    """고객 관련 지표 계산"""
    if sdf.empty:
        return {}
    
    metrics = {}
    
    # 고객 행동 지표 (6개)
    if "__customer_id__" in sdf.columns and sdf["__customer_id__"].notna().any():
        customer_counts = sdf["__customer_id__"].value_counts()
        metrics['unique_customers'] = int(len(customer_counts))
        metrics['repeat_customers'] = int((customer_counts >= 2).sum())
        metrics['repeat_rate'] = metrics['repeat_customers'] / metrics['unique_customers'] if metrics['unique_customers'] > 0 else 0
        metrics['avg_orders_per_customer'] = len(sdf) / metrics['unique_customers'] if metrics['unique_customers'] > 0 else 0
        metrics['customer_ltv'] = sdf["__amount__"].sum() / metrics['unique_customers'] if metrics['unique_customers'] > 0 else 0
    else:
        # 고객 식별이 안되는 경우 NaN으로 설정
        metrics['unique_customers'] = float('nan')
        metrics['repeat_customers'] = float('nan')
        metrics['repeat_rate'] = float('nan')
        metrics['avg_orders_per_customer'] = float('nan')
        metrics['customer_ltv'] = float('nan')
    
    return metrics
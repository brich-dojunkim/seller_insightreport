# data_processing/metrics/sales_metrics.py
"""매출 관련 지표 계산"""

import pandas as pd
from typing import Dict
from constants import COL_PRODUCT_PRICE
from ..transformers.numeric_transformer import to_number_safe

def calculate_sales_metrics(sdf: pd.DataFrame) -> Dict[str, float]:
    """매출 관련 지표 계산"""
    if sdf.empty:
        return {}
    
    metrics = {}
    
    # 기본 매출 지표 (5개)
    metrics['total_orders'] = int(len(sdf))
    metrics['total_revenue'] = float(sdf["__amount__"].sum())
    metrics['avg_order_value'] = metrics['total_revenue'] / metrics['total_orders'] if metrics['total_orders'] > 0 else 0
    metrics['total_quantity'] = int(sdf["__qty__"].sum())
    
    if COL_PRODUCT_PRICE in sdf.columns:
        metrics['avg_product_price'] = float(to_number_safe(sdf[COL_PRODUCT_PRICE]).mean())
    
    return metrics
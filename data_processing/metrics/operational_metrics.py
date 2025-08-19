# data_processing/metrics/operational_metrics.py
"""운영 효율성 지표 계산"""

import pandas as pd
import math
from typing import Dict
from constants import COL_STATUS, COL_SHIP_DATE, COL_DELIVERED_DATE
from ..transformers.datetime_transformer import to_datetime_safe

def calculate_operational_metrics(sdf: pd.DataFrame) -> Dict[str, float]:
    """운영 효율성 지표 계산"""
    if sdf.empty:
        return {}
    
    metrics = {}
    
    # 주문 상태 지표 (5개)
    if COL_STATUS in sdf.columns:
        status_counts = sdf[COL_STATUS].value_counts()
        total = len(sdf)
        metrics['completion_rate'] = status_counts.get('배송완료', 0) / total if total > 0 else 0
        metrics['cancel_rate'] = status_counts.get('결제취소', 0) / total if total > 0 else 0
        metrics['delay_rate'] = status_counts.get('배송지연', 0) / total if total > 0 else 0
        metrics['return_rate'] = status_counts.get('반품', 0) / total if total > 0 else 0
        metrics['exchange_rate'] = status_counts.get('교환', 0) / total if total > 0 else 0
    else:
        metrics['completion_rate'] = float('nan')
        metrics['cancel_rate'] = float('nan')
        metrics['delay_rate'] = float('nan')
        metrics['return_rate'] = float('nan')
        metrics['exchange_rate'] = float('nan')
    
    # 배송 효율성 지표 (3개)
    if COL_SHIP_DATE in sdf.columns:
        ship_data = sdf[sdf[COL_SHIP_DATE].notna()].copy()
        if not ship_data.empty:
            ship_data['ship_dt'] = to_datetime_safe(ship_data[COL_SHIP_DATE])
            lead_times = (ship_data['ship_dt'] - ship_data["__dt__"]).dt.total_seconds() / 86400.0
            metrics['avg_ship_leadtime'] = float(lead_times.mean())
            metrics['same_day_ship_rate'] = (lead_times <= 1).sum() / len(lead_times) if len(lead_times) > 0 else 0
        else:
            metrics['avg_ship_leadtime'] = float('nan')
            metrics['same_day_ship_rate'] = float('nan')
    else:
        metrics['avg_ship_leadtime'] = float('nan')
        metrics['same_day_ship_rate'] = float('nan')
    
    if COL_DELIVERED_DATE in sdf.columns and COL_SHIP_DATE in sdf.columns:
        delivery_data = sdf[sdf[COL_DELIVERED_DATE].notna() & sdf[COL_SHIP_DATE].notna()].copy()
        if not delivery_data.empty:
            delivery_data['delivery_dt'] = to_datetime_safe(delivery_data[COL_DELIVERED_DATE])
            delivery_data['ship_dt'] = to_datetime_safe(delivery_data[COL_SHIP_DATE])
            delivery_times = (delivery_data['delivery_dt'] - delivery_data['ship_dt']).dt.total_seconds() / 86400.0
            metrics['avg_delivery_time'] = float(delivery_times.mean())
        else:
            metrics['avg_delivery_time'] = float('nan')
    else:
        metrics['avg_delivery_time'] = float('nan')
    
    return metrics
# data_processing/analyzers/customer_analyzer.py
"""고객 행동 분석기"""

import pandas as pd

def get_region_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """지역별 분석"""
    if "__region__" not in sdf.columns:
        return pd.DataFrame()
    
    region_data = sdf[sdf["__region__"].notna()]
    if region_data.empty:
        return pd.DataFrame()
    
    region_stats = region_data.groupby("__region__").agg({
        '__amount__': ['count', 'sum', 'mean']
    }).round(2)
    
    region_stats.columns = ['orders', 'revenue', 'aov']
    region_stats['revenue_share'] = region_stats['revenue'] / region_stats['revenue'].sum()
    
    return region_stats.sort_values('revenue', ascending=False)
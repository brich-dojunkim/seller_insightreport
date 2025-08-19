# data_processing/analyzers/channel_analyzer.py
"""채널 분석기"""

import pandas as pd
from constants import COL_CHANNEL, COL_STATUS

def get_channel_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """채널별 분석 (상세)"""
    if COL_CHANNEL not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    
    channel_stats = sdf.groupby(COL_CHANNEL).agg({
        '__amount__': ['count', 'sum', 'mean'],
        COL_STATUS: lambda x: (x == '결제취소').mean() if COL_STATUS in sdf.columns else 0
    }).round(2)
    
    channel_stats.columns = ['orders', 'revenue', 'aov', 'cancel_rate']
    channel_stats['revenue_share'] = channel_stats['revenue'] / channel_stats['revenue'].sum()
    
    return channel_stats.sort_values('revenue', ascending=False)
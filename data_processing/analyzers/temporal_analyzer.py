# data_processing/analyzers/temporal_analyzer.py
"""시간 패턴 분석기"""

import pandas as pd
from typing import Dict, Tuple

def get_time_analysis(sdf: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """시간 분석 (시간대별, 요일별, 일별)"""
    if sdf.empty:
        return {}
    
    result = {}
    
    # 일별 트렌드
    daily = sdf.groupby(sdf["__dt__"].dt.date).agg({
        '__amount__': ['sum', 'count', 'mean']
    }).round(2)
    daily.columns = ['revenue', 'orders', 'aov']
    result['daily'] = daily.reset_index()
    
    # 시간대별 분포
    hourly = sdf.groupby(sdf["__dt__"].dt.hour).agg({
        '__amount__': ['sum', 'count']
    }).round(2)
    hourly.columns = ['revenue', 'orders']
    result['hourly'] = hourly.reset_index()
    
    # 요일별 분포
    weekly = sdf.groupby(sdf["__dt__"].dt.day_name()).agg({
        '__amount__': ['sum', 'count']
    }).round(2)
    weekly.columns = ['revenue', 'orders']
    result['weekly'] = weekly.reset_index()
    
    return result

def get_daily_trend(sdf: pd.DataFrame) -> pd.DataFrame:
    """일자별 추이 (기존 호환성)"""
    time_analysis = get_time_analysis(sdf)
    return time_analysis.get('daily', pd.DataFrame())

def get_heatmap_data(sdf: pd.DataFrame) -> Tuple:
    """히트맵 데이터 (기존 호환성)"""
    if sdf.empty:
        return None, None, None
    
    try:
        sdf_copy = sdf.copy()
        sdf_copy["__hour__"] = sdf_copy["__dt__"].dt.hour
        sdf_copy["__dow__"] = sdf_copy["__dt__"].dt.weekday
        
        heat = sdf_copy.pivot_table(
            index="__dow__", columns="__hour__", 
            values="__amount__", aggfunc="sum", fill_value=0.0
        )
        
        for h in range(24):
            if h not in heat.columns:
                heat[h] = 0.0
        
        heat = heat[sorted(heat.columns)]
        heat_arr = heat.reindex(range(0,7)).fillna(0.0).values
        xlabels = [str(h) for h in sorted(heat.columns)]
        ylabels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        
        return heat_arr, xlabels, ylabels
    except Exception:
        return None, None, None
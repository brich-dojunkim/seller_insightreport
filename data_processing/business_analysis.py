# data_processing/business_analysis.py
"""비즈니스 분석 모듈 - 채널, 상품, 카테고리, 지역, 시간 분석"""

import pandas as pd
from typing import Dict, Any, Tuple
from constants import *

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

def get_product_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """상품 분석 (상세)"""
    if COL_ITEM_NAME not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    
    product_stats = sdf.groupby(COL_ITEM_NAME).agg({
        '__amount__': ['count', 'sum', 'mean'],
        '__qty__': 'sum',
        COL_STATUS: lambda x: (x == '결제취소').mean() if COL_STATUS in sdf.columns else 0
    }).round(2)
    
    product_stats.columns = ['orders', 'revenue', 'aov', 'quantity', 'cancel_rate']
    product_stats = product_stats.sort_values('revenue', ascending=False)
    
    return product_stats.reset_index().head(20)

def get_category_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """카테고리별 분석"""
    if COL_CATEGORY not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    
    category_data = sdf[sdf[COL_CATEGORY].notna()]
    if category_data.empty:
        return pd.DataFrame()
    
    category_stats = category_data.groupby(COL_CATEGORY).agg({
        '__amount__': ['count', 'sum', 'mean']
    }).round(2)
    
    category_stats.columns = ['orders', 'revenue', 'aov']
    category_stats['revenue_share'] = category_stats['revenue'] / category_stats['revenue'].sum()
    
    return category_stats.sort_values('revenue', ascending=False)

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

def get_status_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """상태 분석 (기존 호환성)"""
    if COL_STATUS not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    st = sdf[COL_STATUS].astype(str).value_counts().reset_index()
    st.columns = ["status", "count"]
    return st

def get_comprehensive_analysis(sdf: pd.DataFrame) -> Dict[str, Any]:
    """종합 분석 결과 반환"""
    return {
        'channel_analysis': get_channel_analysis(sdf),
        'product_analysis': get_product_analysis(sdf),
        'category_analysis': get_category_analysis(sdf),
        'region_analysis': get_region_analysis(sdf),
        'time_analysis': get_time_analysis(sdf)
    }

# 기존 함수들 (호환성 유지)
def get_daily_trend(sdf: pd.DataFrame) -> pd.DataFrame:
    """일자별 추이 (기존 호환성)"""
    time_analysis = get_time_analysis(sdf)
    return time_analysis.get('daily', pd.DataFrame())
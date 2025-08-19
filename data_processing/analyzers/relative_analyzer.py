# data_processing/analyzers/relative_analyzer.py
"""상대적 분석기 - 카테고리 평균 대비 성과"""

import pandas as pd
from typing import Dict
from ..metrics.benchmark_calculator import get_benchmark_calculator
from .channel_analyzer import get_channel_analysis
from .product_analyzer import get_category_analysis
from .customer_analyzer import get_region_analysis
from .temporal_analyzer import get_time_analysis

def get_relative_channel_analysis(sdf: pd.DataFrame, overall: pd.DataFrame) -> pd.DataFrame:
    """채널별 성과를 카테고리 평균 대비로 분석"""
    calculator = get_benchmark_calculator()
    my_category = calculator.get_my_category(sdf)
    
    if my_category is None:
        return get_channel_analysis(sdf)  # 기존 분석 반환
    
    # 내 채널 성과
    my_channels = get_channel_analysis(sdf)
    if my_channels.empty:
        return my_channels
    
    # 카테고리 평균 채널 성과 계산
    try:
        if '__category_mapped__' in overall.columns:
            category_data = overall[overall['__category_mapped__'] == my_category]
        else:
            category_data = overall
        
        category_channels = get_channel_analysis(category_data) if not category_data.empty else pd.DataFrame()
    except Exception as e:
        print(f"⚠️ 카테고리 채널 분석 실패: {e}")
        return my_channels
    
    if category_channels.empty:
        return my_channels
    
    # 상대적 성과 계산
    relative_channels = my_channels.copy()
    
    for channel in relative_channels.index:
        if channel in category_channels.index:
            cat_avg = category_channels.loc[channel]
            
            # 각 지표별 상대 비율 계산
            for metric in ['orders', 'revenue', 'aov']:
                if cat_avg[metric] > 0:
                    relative_channels.loc[channel, f'{metric}_vs_category'] = \
                        relative_channels.loc[channel, metric] / cat_avg[metric]
                else:
                    relative_channels.loc[channel, f'{metric}_vs_category'] = float('nan')
    
    return relative_channels

def get_relative_region_analysis(sdf: pd.DataFrame, overall: pd.DataFrame) -> pd.DataFrame:
    """지역별 성과를 카테고리 평균 대비로 분석"""
    calculator = get_benchmark_calculator()
    my_category = calculator.get_my_category(sdf)
    
    if my_category is None:
        return get_region_analysis(sdf)
    
    # 내 지역 성과
    my_regions = get_region_analysis(sdf)
    if my_regions.empty:
        return my_regions
    
    # 카테고리 평균 지역 성과
    try:
        if '__category_mapped__' in overall.columns:
            category_data = overall[overall['__category_mapped__'] == my_category]
        else:
            category_data = overall
            
        category_regions = get_region_analysis(category_data) if not category_data.empty else pd.DataFrame()
    except Exception as e:
        print(f"⚠️ 카테고리 지역 분석 실패: {e}")
        return my_regions
    
    if category_regions.empty:
        return my_regions
    
    # 상대적 성과 계산
    relative_regions = my_regions.copy()
    
    for region in relative_regions.index:
        if region in category_regions.index:
            cat_avg = category_regions.loc[region]
            
            for metric in ['orders', 'revenue', 'aov']:
                if cat_avg[metric] > 0:
                    relative_regions.loc[region, f'{metric}_vs_category'] = \
                        relative_regions.loc[region, metric] / cat_avg[metric]
                else:
                    relative_regions.loc[region, f'{metric}_vs_category'] = float('nan')
    
    return relative_regions

def get_relative_time_analysis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """시간 패턴을 카테고리 평균 대비로 분석"""
    calculator = get_benchmark_calculator()
    my_category = calculator.get_my_category(sdf)
    
    if my_category is None:
        return get_time_analysis(sdf)
    
    # 내 시간 패턴
    my_time = get_time_analysis(sdf)
    if not my_time:
        return my_time
    
    # 카테고리 평균 시간 패턴
    try:
        if '__category_mapped__' in overall.columns:
            category_data = overall[overall['__category_mapped__'] == my_category]
        else:
            category_data = overall
            
        category_time = get_time_analysis(category_data) if not category_data.empty else {}
    except Exception as e:
        print(f"⚠️ 카테고리 시간 분석 실패: {e}")
        return my_time
    
    if not category_time:
        return my_time
    
    relative_time = {}
    
    # 시간대별 상대 성과
    for time_type in ['daily', 'hourly', 'weekly']:
        if time_type in my_time and time_type in category_time:
            my_df = my_time[time_type]
            cat_df = category_time[time_type]
            
            if not my_df.empty and not cat_df.empty:
                relative_df = my_df.copy()
                
                # 평균 대비 비율 계산
                my_avg_revenue = my_df['revenue'].mean()
                cat_avg_revenue = cat_df['revenue'].mean()
                
                if cat_avg_revenue > 0:
                    relative_df['revenue_vs_category'] = relative_df['revenue'] / cat_avg_revenue
                    relative_df['performance_level'] = relative_df['revenue_vs_category'].apply(
                        lambda x: 'excellent' if x >= 1.2 else 
                                 'good' if x >= 1.1 else
                                 'average' if x >= 0.9 else 'below_average'
                    )
                
                relative_time[time_type] = relative_df
            else:
                relative_time[time_type] = my_time[time_type]
        else:
            relative_time[time_type] = my_time.get(time_type, pd.DataFrame())
    
    return relative_time

def get_comprehensive_relative_analysis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """종합적인 상대 분석"""
    return {
        'relative_channel_analysis': get_relative_channel_analysis(sdf, overall),
        'relative_region_analysis': get_relative_region_analysis(sdf, overall),
        'relative_time_analysis': get_relative_time_analysis(sdf, overall)
    }
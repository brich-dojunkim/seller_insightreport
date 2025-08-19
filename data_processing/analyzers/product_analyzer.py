# data_processing/analyzers/product_analyzer.py
"""상품 분석기"""

import pandas as pd
from constants import COL_ITEM_NAME, COL_STATUS, COL_CATEGORY

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
    """카테고리별 분석 - 매핑된 카테고리 사용"""
    # 매핑된 카테고리 컬럼 우선 사용
    category_col = None
    
    if '__category_mapped__' in sdf.columns:
        category_col = '__category_mapped__'
    elif COL_CATEGORY in sdf.columns:
        category_col = COL_CATEGORY
    else:
        return pd.DataFrame()
    
    category_data = sdf[sdf[category_col].notna()]
    if category_data.empty:
        return pd.DataFrame()
    
    category_stats = category_data.groupby(category_col).agg({
        '__amount__': ['count', 'sum', 'mean']
    }).round(2)
    
    category_stats.columns = ['orders', 'revenue', 'aov']
    category_stats['revenue_share'] = category_stats['revenue'] / category_stats['revenue'].sum()
    
    return category_stats.sort_values('revenue', ascending=False)
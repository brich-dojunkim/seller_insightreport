"""트렌드 분석기"""

import pandas as pd
from datetime import timedelta
from .base_analyzer import BaseAnalyzer

class TrendsAnalyzer(BaseAnalyzer):
    """트렌드 분석"""
    
    def analyze(self) -> dict:
        """트렌드 분석"""
        trends = {}
        
        # A. 월별 트렌드 (데이터 기간이 충분한 경우)
        monthly_trend = self.seller_data.groupby(self.seller_data['__dt__'].dt.to_period('M')).agg({
            '__amount__': ['sum', 'count', 'mean'],
            '__customer_id__': 'nunique' if '__customer_id__' in self.seller_data.columns else lambda x: None
        }).round(2)
        
        monthly_trend.columns = ['매출액', '주문수', 'AOV', '고객수']
        monthly_trend.index = monthly_trend.index.astype(str)
        
        # 성장률 계산
        if len(monthly_trend) > 1:
            monthly_trend['매출성장률'] = monthly_trend['매출액'].pct_change() * 100
            monthly_trend['주문성장률'] = monthly_trend['주문수'].pct_change() * 100
        
        trends['monthly_trend'] = monthly_trend
        
        # B. 주별 트렌드
        weekly_trend = self.seller_data.groupby(self.seller_data['__dt__'].dt.to_period('W')).agg({
            '__amount__': ['sum', 'count'],
        }).round(2)
        
        weekly_trend.columns = ['매출액', '주문수']
        weekly_trend.index = weekly_trend.index.astype(str)
        
        trends['weekly_trend'] = weekly_trend
        
        # C. 일별 트렌드 (최근 30일)
        recent_30days = self.seller_data[
            self.seller_data['__dt__'] >= (self.seller_data['__dt__'].max() - timedelta(days=30))
        ]
        
        daily_trend = recent_30days.groupby(recent_30days['__dt__'].dt.date).agg({
            '__amount__': ['sum', 'count'],
        }).round(2)
        
        daily_trend.columns = ['매출액', '주문수']
        daily_trend.index = daily_trend.index.astype(str)
        
        trends['daily_trend'] = daily_trend
        
        return trends
"""매출 분석기"""

import pandas as pd
from .base_analyzer import BaseAnalyzer
from constants import COL_CHANNEL, COL_ITEM_NAME, COL_PRODUCT_PRICE

class SalesAnalyzer(BaseAnalyzer):
    """매출 분석"""
    
    def analyze(self) -> dict:
        """매출 분석"""
        sales = {}
        
        # A. 기본 매출 지표
        basic_metrics = {
            '총_매출액': self.seller_data['__amount__'].sum(),
            '총_주문수': len(self.seller_data),
            '평균주문금액': self.seller_data['__amount__'].mean(),
            '총_판매수량': self.seller_data['__qty__'].sum(),
            '일평균_매출액': self.seller_data['__amount__'].sum() / ((self.seller_data['__dt__'].max() - self.seller_data['__dt__'].min()).days + 1)
        }
        
        if COL_PRODUCT_PRICE in self.seller_data.columns:
            basic_metrics['평균상품가격'] = pd.to_numeric(self.seller_data[COL_PRODUCT_PRICE], errors='coerce').mean()
        
        sales['basic_metrics'] = basic_metrics
        
        # B. 채널별 매출 분석
        if COL_CHANNEL in self.seller_data.columns:
            channel_analysis = self.seller_data.groupby(COL_CHANNEL).agg({
                '__amount__': ['sum', 'count', 'mean'],
                '__qty__': 'sum'
            }).round(2)
            
            channel_analysis.columns = ['매출액', '주문수', 'AOV', '판매수량']
            channel_analysis['매출비중'] = (channel_analysis['매출액'] / channel_analysis['매출액'].sum()) * 100
            channel_analysis = channel_analysis.sort_values('매출액', ascending=False)
            
            sales['channel_analysis'] = channel_analysis
        
        # C. 상품별 매출 TOP 20
        if COL_ITEM_NAME in self.seller_data.columns:
            product_analysis = self.seller_data.groupby(COL_ITEM_NAME).agg({
                '__amount__': ['sum', 'count', 'mean'],
                '__qty__': 'sum'
            }).round(2)
            
            product_analysis.columns = ['매출액', '주문수', 'AOV', '판매수량']
            product_analysis['매출기여도'] = (product_analysis['매출액'] / product_analysis['매출액'].sum()) * 100
            product_analysis = product_analysis.sort_values('매출액', ascending=False).head(20)
            
            sales['product_analysis'] = product_analysis
        
        # D. 시간대별 매출 패턴
        hourly_pattern = self.seller_data.groupby(self.seller_data['__dt__'].dt.hour).agg({
            '__amount__': ['sum', 'count', 'mean']
        }).round(2)
        hourly_pattern.columns = ['매출액', '주문수', 'AOV']
        hourly_pattern['시간대'] = hourly_pattern.index.map(lambda x: f"{x:02d}-{x+1:02d}시")
        
        sales['hourly_pattern'] = hourly_pattern
        
        # E. 요일별 매출 패턴
        daily_pattern = self.seller_data.groupby(self.seller_data['__dt__'].dt.day_name()).agg({
            '__amount__': ['sum', 'count', 'mean']
        }).round(2)
        daily_pattern.columns = ['매출액', '주문수', 'AOV']
        
        # 요일 순서 정렬
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_pattern = daily_pattern.reindex([day for day in day_order if day in daily_pattern.index])
        
        sales['daily_pattern'] = daily_pattern
        
        return sales
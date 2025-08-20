"""고객 분석기"""

import pandas as pd
from .base_analyzer import BaseAnalyzer

class CustomerAnalyzer(BaseAnalyzer):
    """고객 분석"""
    
    def analyze(self) -> dict:
        """고객 분석"""
        customers = {}
        
        if '__customer_id__' not in self.seller_data.columns or self.seller_data['__customer_id__'].isna().all():
            customers['error'] = "고객 식별 정보가 없어 고객 분석을 수행할 수 없습니다."
            return customers
        
        # 고객별 구매 데이터 집계
        customer_data = self.seller_data[self.seller_data['__customer_id__'].notna()].copy()
        customer_summary = customer_data.groupby('__customer_id__').agg({
            '__amount__': ['sum', 'count', 'mean'],
            '__dt__': ['min', 'max']
        }).round(2)
        
        customer_summary.columns = ['총구매금액', '구매횟수', '평균구매금액', '첫구매일', '최근구매일']
        
        # A. 고객 기본 지표
        total_customers = len(customer_summary)
        new_customers = (customer_summary['구매횟수'] == 1).sum()
        repeat_customers = (customer_summary['구매횟수'] >= 2).sum()
        
        basic_metrics = {
            '총_고객수': total_customers,
            '신규_고객수': new_customers,
            '기존_고객수': repeat_customers,
            '재구매율': (repeat_customers / total_customers * 100) if total_customers > 0 else 0,
            '평균_구매횟수': customer_summary['구매횟수'].mean(),
            '평균_고객생애가치': customer_summary['총구매금액'].mean()
        }
        
        customers['basic_metrics'] = basic_metrics
        
        # B. 퍼센타일 기반 고객 세그먼트 분석
        segments = self._create_customer_segments(customer_summary)
        customers['segment_analysis'] = segments
        
        # C. 지역별 고객 분석
        if '__region__' in customer_data.columns:
            region_analysis = customer_data.groupby('__region__').agg({
                '__customer_id__': 'nunique',
                '__amount__': ['sum', 'mean'],
                '__dt__': 'count'
            }).round(2)
            
            region_analysis.columns = ['고객수', '매출액', 'AOV', '주문수']
            region_analysis['고객당_매출'] = region_analysis['매출액'] / region_analysis['고객수']
            region_analysis = region_analysis.sort_values('매출액', ascending=False).head(10)
            
            customers['region_analysis'] = region_analysis
        
        # D. 고객 생애주기 분석 (구매 차수별)
        lifecycle_analysis = customer_summary['구매횟수'].value_counts().sort_index()
        lifecycle_df = pd.DataFrame({
            '구매차수': lifecycle_analysis.index,
            '고객수': lifecycle_analysis.values
        })
        lifecycle_df['누적고객수'] = lifecycle_df['고객수'].cumsum()
        lifecycle_df['잔존율'] = (lifecycle_df['누적고객수'] / total_customers * 100)
        
        # 각 차수별 평균 구매금액
        for purchase_count in lifecycle_df['구매차수']:
            customers_at_count = customer_summary[customer_summary['구매횟수'] >= purchase_count]
            if len(customers_at_count) > 0:
                avg_amount = customers_at_count['총구매금액'].mean()
                lifecycle_df.loc[lifecycle_df['구매차수'] == purchase_count, '평균누적구매금액'] = avg_amount
        
        customers['lifecycle_analysis'] = lifecycle_df.head(10)  # 상위 10차수까지
        
        return customers
    
    def _create_customer_segments(self, customer_summary: pd.DataFrame) -> pd.DataFrame:
        """퍼센타일 기반 고객 세그먼트 생성"""
        
        # 총구매금액 기준으로 퍼센타일 계산
        customer_summary['percentile'] = customer_summary['총구매금액'].rank(pct=True) * 100
        
        # 세그먼트 정의
        def assign_segment(percentile):
            if percentile >= 90:
                return 'VIP (상위 10%)'
            elif percentile >= 70:
                return '골드 (상위 11-30%)'
            elif percentile >= 30:
                return '실버 (상위 31-70%)'
            else:
                return '브론즈 (하위 30%)'
        
        customer_summary['세그먼트'] = customer_summary['percentile'].apply(assign_segment)
        
        # 세그먼트별 집계
        segment_analysis = customer_summary.groupby('세그먼트').agg({
            '총구매금액': ['count', 'sum', 'mean'],
            '구매횟수': 'mean',
            '평균구매금액': 'mean'
        }).round(2)
        
        segment_analysis.columns = ['고객수', '총매출기여', '평균구매금액', '평균구매횟수', '평균AOV']
        
        # 비율 계산
        total_customers = customer_summary.shape[0]
        total_revenue = customer_summary['총구매금액'].sum()
        
        segment_analysis['고객비율'] = (segment_analysis['고객수'] / total_customers * 100)
        segment_analysis['매출기여도'] = (segment_analysis['총매출기여'] / total_revenue * 100)
        segment_analysis['고객생애가치'] = segment_analysis['총매출기여'] / segment_analysis['고객수']
        
        # 세그먼트 순서 정렬
        segment_order = ['VIP (상위 10%)', '골드 (상위 11-30%)', '실버 (상위 31-70%)', '브론즈 (하위 30%)']
        segment_analysis = segment_analysis.reindex([seg for seg in segment_order if seg in segment_analysis.index])
        
        return segment_analysis
"""운영 분석기"""

import pandas as pd
from .base_analyzer import BaseAnalyzer
from constants import COL_STATUS, COL_SHIP_DATE, COL_DELIVERED_DATE, COL_REFUND_FIELD

class OperationsAnalyzer(BaseAnalyzer):
    """운영 분석"""
    
    def analyze(self) -> dict:
        """운영 분석"""
        operations = {}
        
        # A. 주문 처리 현황
        if COL_STATUS in self.seller_data.columns:
            status_analysis = self.seller_data[COL_STATUS].value_counts()
            status_df = pd.DataFrame({
                '상태': status_analysis.index,
                '건수': status_analysis.values,
                '비율': (status_analysis.values / len(self.seller_data) * 100).round(2)
            })
            
            operations['status_analysis'] = status_df
            
            # 주요 지표 계산
            total_orders = len(self.seller_data)
            operations['key_metrics'] = {
                '전체주문수': total_orders,
                '배송완료율': (status_analysis.get('배송완료', 0) / total_orders * 100),
                '취소율': (status_analysis.get('결제취소', 0) / total_orders * 100),
                '지연율': (status_analysis.get('배송지연', 0) / total_orders * 100),
                '반품률': (status_analysis.get('반품', 0) / total_orders * 100)
            }
        
        # B. 배송 성과 분석
        shipping_metrics = {}
        
        if COL_SHIP_DATE in self.seller_data.columns:
            ship_data = self.seller_data[self.seller_data[COL_SHIP_DATE].notna()].copy()
            if not ship_data.empty:
                ship_data['ship_dt'] = pd.to_datetime(ship_data[COL_SHIP_DATE], errors='coerce')
                ship_data['출고소요시간'] = (ship_data['ship_dt'] - ship_data['__dt__']).dt.total_seconds() / 86400.0
                
                shipping_metrics['평균출고시간'] = ship_data['출고소요시간'].mean()
                shipping_metrics['당일발송률'] = (ship_data['출고소요시간'] <= 1).mean() * 100
                
        if COL_DELIVERED_DATE in self.seller_data.columns and COL_SHIP_DATE in self.seller_data.columns:
            delivery_data = self.seller_data[
                self.seller_data[COL_DELIVERED_DATE].notna() & 
                self.seller_data[COL_SHIP_DATE].notna()
            ].copy()
            
            if not delivery_data.empty:
                delivery_data['delivery_dt'] = pd.to_datetime(delivery_data[COL_DELIVERED_DATE], errors='coerce')
                delivery_data['ship_dt'] = pd.to_datetime(delivery_data[COL_SHIP_DATE], errors='coerce')
                delivery_data['배송소요시간'] = (delivery_data['delivery_dt'] - delivery_data['ship_dt']).dt.total_seconds() / 86400.0
                
                shipping_metrics['평균배송시간'] = delivery_data['배송소요시간'].mean()
                shipping_metrics['빠른배송률'] = (delivery_data['배송소요시간'] <= 2).mean() * 100
        
        operations['shipping_metrics'] = shipping_metrics
        
        # C. 클레임 분석 (환불 필드 기준)
        if COL_REFUND_FIELD in self.seller_data.columns:
            refund_data = self.seller_data[self.seller_data[COL_REFUND_FIELD].notna()]
            if not refund_data.empty:
                claim_analysis = refund_data[COL_REFUND_FIELD].value_counts()
                claim_df = pd.DataFrame({
                    '클레임유형': claim_analysis.index,
                    '건수': claim_analysis.values,
                    '발생률': (claim_analysis.values / len(self.seller_data) * 100).round(3)
                })
                operations['claim_analysis'] = claim_df
        
        return operations
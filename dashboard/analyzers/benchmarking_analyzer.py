"""벤치마킹 분석기"""

import math
import numpy as np
import pandas as pd
from .base_analyzer import BaseAnalyzer
from constants import COL_SELLER

class BenchmarkingAnalyzer(BaseAnalyzer):
    """벤치마킹 분석"""
    
    def __init__(self, seller_data, overall_data, seller_name, kpis):
        super().__init__(seller_data, overall_data, seller_name)
        self.kpis = kpis
    
    def analyze(self) -> dict:
        """벤치마킹 분석"""
        benchmarking = {}
        
        # A. 카테고리 내 포지션
        main_category = self._get_main_category()
        
        if main_category and '__category_mapped__' in self.overall_data.columns and COL_SELLER in self.overall_data.columns:
            category_data = self.overall_data[self.overall_data['__category_mapped__'] == main_category]
            
            # 셀러별 성과 집계
            seller_performance = category_data.groupby(COL_SELLER).agg({
                '__amount__': ['sum', 'count', 'mean'],
                '__customer_id__': 'nunique' if '__customer_id__' in category_data.columns else lambda x: np.nan
            }).round(2)
            
            seller_performance.columns = ['총매출', '주문수', 'AOV', '고객수']
            seller_performance = seller_performance.sort_values('총매출', ascending=False)
            
            # 내 순위 정보
            if self.seller_name in seller_performance.index:
                my_rank = seller_performance.index.get_loc(self.seller_name) + 1
                total_sellers = len(seller_performance)
                
                position_metrics = {
                    '매출순위': f"{my_rank}/{total_sellers}",
                    '상위퍼센트': f"{((total_sellers - my_rank) / total_sellers * 100):.1f}%"
                }
                
                # 각 지표별 순위
                for metric in ['총매출', '주문수', 'AOV', '고객수']:
                    if not seller_performance[metric].isna().all():
                        metric_rank = seller_performance[metric].rank(ascending=False)[self.seller_name]
                        position_metrics[f'{metric}_순위'] = f"{int(metric_rank)}/{total_sellers}"
                
                benchmarking['position_metrics'] = position_metrics
                
                # 경쟁사 TOP 5 (나를 포함)
                top_competitors = seller_performance.head(10)
                benchmarking['top_competitors'] = top_competitors
        
        # B. 상대적 성과 분석
        relative_performance = {}
        
        for key, value in self.kpis.items():
            if '_vs_category' in key and not (isinstance(value, float) and math.isnan(value)):
                metric_name = key.replace('_vs_category', '')
                relative_performance[metric_name] = {
                    '상대성과': value,
                    '성과등급': self._get_performance_grade(value, metric_name),
                    '개선여지': self._get_improvement_potential(value, metric_name)
                }
        
        benchmarking['relative_performance'] = relative_performance
        
        return benchmarking
    
    def _get_main_category(self):
        """주력 카테고리 조회"""
        if '__category_mapped__' in self.seller_data.columns:
            cat_revenue = self.seller_data.groupby('__category_mapped__')['__amount__'].sum()
            if not cat_revenue.empty:
                return cat_revenue.idxmax()
        return None
    
    def _get_performance_grade(self, value: float, metric_name: str) -> str:
        """성과 등급 계산"""
        # 낮을수록 좋은 지표들
        if any(bad_word in metric_name for bad_word in ['cancel', 'delay', 'return']):
            if value <= 0.7: return 'A+'
            elif value <= 0.8: return 'A'
            elif value <= 0.9: return 'B+'
            elif value <= 1.1: return 'B'
            else: return 'C'
        else:
            # 높을수록 좋은 지표들
            if value >= 1.3: return 'A+'
            elif value >= 1.2: return 'A'
            elif value >= 1.1: return 'B+'
            elif value >= 0.9: return 'B'
            else: return 'C'
    
    def _get_improvement_potential(self, value: float, metric_name: str) -> str:
        """개선 여지 평가"""
        # 낮을수록 좋은 지표들
        if any(bad_word in metric_name for bad_word in ['cancel', 'delay', 'return']):
            if value <= 0.8: return '유지'
            elif value <= 1.1: return '중간'
            else: return '높음'
        else:
            # 높을수록 좋은 지표들
            if value >= 1.2: return '유지'
            elif value >= 0.9: return '중간'
            else: return '높음'
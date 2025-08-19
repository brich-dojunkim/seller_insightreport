# data_processing/metrics/benchmark_calculator.py
"""카테고리별 벤치마크 계산기"""

import pandas as pd
from typing import Dict, Optional
from constants import COL_SELLER, COL_CATEGORY
from .sales_metrics import calculate_sales_metrics
from .customer_metrics import calculate_customer_metrics
from .operational_metrics import calculate_operational_metrics

class CategoryBenchmarkCalculator:
    """카테고리별 벤치마크 계산기"""
    
    def __init__(self):
        self.benchmark_cache = {}
    
    def calculate_category_benchmarks(self, overall_data: pd.DataFrame, target_category: str) -> Dict[str, float]:
        """특정 카테고리의 평균 벤치마크 계산"""
        
        # 캐시 확인
        cache_key = f"{target_category}_{len(overall_data)}"
        if cache_key in self.benchmark_cache:
            return self.benchmark_cache[cache_key]
        
        # 해당 카테고리 데이터만 필터링
        if '__category_mapped__' in overall_data.columns:
            category_data = overall_data[overall_data['__category_mapped__'] == target_category]
        elif COL_CATEGORY in overall_data.columns:
            category_data = overall_data[overall_data[COL_CATEGORY] == target_category]
        else:
            # 카테고리 정보가 없으면 전체 데이터 사용
            category_data = overall_data.copy()
        
        if category_data.empty:
            return {}
        
        # 카테고리 내 셀러들의 평균 성과 계산
        seller_performances = []
        
        if COL_SELLER in category_data.columns:
            for seller in category_data[COL_SELLER].unique():
                seller_data = category_data[category_data[COL_SELLER] == seller]
                if len(seller_data) >= 10:  # 최소 10건 이상인 셀러만
                    seller_metrics = self._calculate_seller_metrics(seller_data)
                    seller_performances.append(seller_metrics)
        
        if not seller_performances:
            # 셀러별 분리가 안되면 전체 카테고리 데이터로 계산
            benchmarks = self._calculate_seller_metrics(category_data)
        else:
            # 여러 셀러의 평균값 계산
            benchmarks = self._average_seller_performances(seller_performances)
        
        # 캐시에 저장
        self.benchmark_cache[cache_key] = benchmarks
        return benchmarks
    
    def _calculate_seller_metrics(self, seller_data: pd.DataFrame) -> Dict[str, float]:
        """개별 셀러의 모든 지표 계산"""
        metrics = {}
        
        # Sales Metrics
        sales = calculate_sales_metrics(seller_data)
        metrics.update(sales)
        
        # Customer Metrics  
        customer = calculate_customer_metrics(seller_data)
        metrics.update(customer)
        
        # Operational Metrics
        operational = calculate_operational_metrics(seller_data)
        metrics.update(operational)
        
        return metrics
    
    def _average_seller_performances(self, performances: list) -> Dict[str, float]:
        """여러 셀러 성과의 평균 계산"""
        if not performances:
            return {}
        
        # 모든 지표의 평균값 계산
        avg_metrics = {}
        all_keys = set()
        for perf in performances:
            all_keys.update(perf.keys())
        
        for key in all_keys:
            values = [perf.get(key) for perf in performances if perf.get(key) is not None]
            values = [v for v in values if not (isinstance(v, float) and pd.isna(v))]
            
            if values:
                avg_metrics[key] = sum(values) / len(values)
            else:
                avg_metrics[key] = float('nan')
        
        return avg_metrics
    
    def calculate_relative_performance(self, my_metrics: Dict[str, float], benchmarks: Dict[str, float]) -> Dict[str, float]:
        """내 성과 vs 카테고리 평균 상대적 비교"""
        relative = {}
        
        for metric_name, my_value in my_metrics.items():
            if metric_name in benchmarks:
                benchmark_value = benchmarks[metric_name]
                
                # 유효한 값들만 비교
                if (my_value is not None and benchmark_value is not None and 
                    not pd.isna(my_value) and not pd.isna(benchmark_value) and 
                    benchmark_value != 0):
                    
                    relative_ratio = my_value / benchmark_value
                    relative[f'{metric_name}_vs_category'] = relative_ratio
                    
                    # 성과 레벨 추가
                    if relative_ratio >= 1.2:
                        relative[f'{metric_name}_performance_level'] = 'excellent'
                    elif relative_ratio >= 1.1:
                        relative[f'{metric_name}_performance_level'] = 'good'
                    elif relative_ratio >= 0.9:
                        relative[f'{metric_name}_performance_level'] = 'average'
                    else:
                        relative[f'{metric_name}_performance_level'] = 'below_average'
        
        return relative
    
    def get_my_category(self, my_data: pd.DataFrame) -> Optional[str]:
        """내 데이터에서 주요 카테고리 추출"""
        if '__category_mapped__' in my_data.columns:
            category_col = '__category_mapped__'
        elif COL_CATEGORY in my_data.columns:
            category_col = COL_CATEGORY
        else:
            return None
        
        # 가장 많은 매출을 차지하는 카테고리 반환
        category_revenue = my_data.groupby(category_col)['__amount__'].sum()
        if not category_revenue.empty:
            return category_revenue.idxmax()
        
        return None

# 전역 인스턴스
_benchmark_calculator = CategoryBenchmarkCalculator()

def get_benchmark_calculator():
    """벤치마크 계산기 인스턴스 반환"""
    return _benchmark_calculator
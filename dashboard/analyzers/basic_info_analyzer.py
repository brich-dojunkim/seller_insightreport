"""기본 정보 분석기"""

from datetime import datetime
from .base_analyzer import BaseAnalyzer
from constants import COL_SELLER

class BasicInfoAnalyzer(BaseAnalyzer):
    """기본 정보 분석"""
    
    def analyze(self) -> dict:
        """기본 정보 분석"""
        info = {}
        
        # 기본 통계
        info['seller_name'] = self.seller_name
        info['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        info['period_start'] = self.seller_data['__dt__'].min().strftime('%Y-%m-%d')
        info['period_end'] = self.seller_data['__dt__'].max().strftime('%Y-%m-%d')
        info['total_days'] = (self.seller_data['__dt__'].max() - self.seller_data['__dt__'].min()).days + 1
        
        # 주력 카테고리
        if '__category_mapped__' in self.seller_data.columns:
            cat_revenue = self.seller_data.groupby('__category_mapped__')['__amount__'].sum()
            if not cat_revenue.empty:
                info['main_category'] = cat_revenue.idxmax()
                info['main_category_share'] = (cat_revenue.max() / self.seller_data['__amount__'].sum()) * 100
                
                # 카테고리 내 순위 계산
                if '__category_mapped__' in self.overall_data.columns and COL_SELLER in self.overall_data.columns:
                    category_data = self.overall_data[self.overall_data['__category_mapped__'] == info['main_category']]
                    seller_perf = category_data.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
                    
                    if self.seller_name in seller_perf.index:
                        rank = seller_perf.index.get_loc(self.seller_name) + 1
                        total_sellers = len(seller_perf)
                        market_share = (seller_perf[self.seller_name] / seller_perf.sum()) * 100
                        
                        info['category_rank'] = rank
                        info['category_total_sellers'] = total_sellers
                        info['category_percentile'] = ((total_sellers - rank) / total_sellers) * 100
                        info['market_share'] = market_share
        
        return info
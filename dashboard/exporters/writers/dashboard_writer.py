"""대시보드 요약 시트 작성기"""

import pandas as pd
import numpy as np
from dashboard.utils.excel_formatter import ExcelFormatter, format_basic_metrics

class DashboardWriter:
    """대시보드 요약 시트 작성"""
    
    def __init__(self, analysis_data: dict, kpis: dict):
        self.analysis_data = analysis_data
        self.kpis = kpis
    
    def write(self, writer):
        """대시보드 요약 시트 작성"""
        
        basic_info = self.analysis_data['basic_info']
        current_row = 0
        
        # A. 셀러 기본 정보
        title_df = pd.DataFrame([['A. 셀러 기본 정보']], columns=[''])
        title_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False, header=False)
        current_row += 2
        
        seller_info_data = [
            ['셀러명', basic_info['seller_name']],
            ['분석기간', f"{basic_info['period_start']} ~ {basic_info['period_end']}"],
            ['분석일시', basic_info['analysis_date']],
            ['총 분석일수', basic_info['total_days']],
            ['주력카테고리', basic_info.get('main_category', 'N/A')],
            ['카테고리 점유율', basic_info.get('main_category_share', 0)],
            ['카테고리 순위', f"{basic_info.get('category_rank', 'N/A')}/{basic_info.get('category_total_sellers', 'N/A')}"],
            ['시장점유율', basic_info.get('market_share', 0)]
        ]
        
        seller_info = pd.DataFrame(seller_info_data, columns=['구분', '값'])
        
        # 자동 포맷팅 적용
        format_basic_metrics(seller_info, '대시보드요약', writer, current_row)
        current_row += len(seller_info) + 3
        
        # B. KPI 스코어카드
        title_df = pd.DataFrame([['B. KPI 스코어카드 (카테고리 평균 대비)']], columns=[''])
        title_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False, header=False)
        current_row += 2
        
        kpi_scorecard = self._create_kpi_scorecard()
        kpi_df = pd.DataFrame(kpi_scorecard, columns=['지표', '현재값', '카테고리대비', '등급'])
        
        # KPI에 대한 커스텀 포맷
        kpi_formats = {
            '현재값': 'auto',  # 자동 감지
            '카테고리대비': 'float2'
        }
        
        formatter = ExcelFormatter(writer.book)
        formatter.detect_and_format_dataframe(kpi_df, '대시보드요약', writer, current_row)
        current_row += len(kpi_df) + 3
        
        # C. 성과 점수
        title_df = pd.DataFrame([['C. 영역별 성과 점수 (0-100점)']], columns=[''])
        title_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False, header=False)
        current_row += 2
        
        performance_scores = {
            '매출성과': self._calculate_sales_score(),
            '고객성과': self._calculate_customer_score(),
            '운영성과': self._calculate_operations_score(),
            '시장성과': self._calculate_market_score()
        }
        
        scores_df = pd.DataFrame(list(performance_scores.items()), columns=['영역', '점수'])
        
        # 점수 포맷
        score_formats = {'점수': 'float1'}
        formatter.apply_formats_to_dataframe_by_columns(scores_df, score_formats, '대시보드요약', writer, current_row)
    
    
    def _create_kpi_scorecard(self):
        """KPI 스코어카드 생성 - 숫자 값 유지"""
        kpi_scorecard = []
        
        kpi_mapping = {
            '총매출액': ('total_revenue', 'total_revenue_vs_category'),
            '평균주문금액': ('avg_order_value', 'avg_order_value_vs_category'),
            '재구매율': ('repeat_rate', 'repeat_rate_vs_category'),
            '취소율': ('cancel_rate', 'cancel_rate_vs_category'),
            '배송완료시간': ('avg_delivery_time', 'avg_delivery_time_vs_category'),
            '고객수': ('unique_customers', 'unique_customers_vs_category')
        }
        
        for kpi_name, (base_key, vs_key) in kpi_mapping.items():
            current_value = self.kpis.get(base_key, np.nan)
            vs_category = self.kpis.get(vs_key, np.nan)
            
            if not pd.isna(current_value):
                # 값 그대로 유지 (숫자)
                formatted_value = float(current_value)
                
                # 상대 성과
                if not pd.isna(vs_category):
                    is_inverse = any(word in kpi_name for word in ['취소', '시간', '지연'])
                    if is_inverse:
                        relative_perf = float(1 - vs_category)
                        grade = self._get_performance_grade(vs_category, 'cancel')
                    else:
                        relative_perf = float(vs_category - 1)
                        grade = self._get_performance_grade(vs_category, 'normal')
                else:
                    relative_perf = np.nan
                    grade = "N/A"
                
                kpi_scorecard.append([kpi_name, formatted_value, relative_perf, grade])
        
        return kpi_scorecard
    
    def _get_performance_grade(self, value: float, metric_type: str) -> str:
        """성과 등급 계산"""
        if metric_type == 'cancel':
            if value <= 0.7: return 'A+'
            elif value <= 0.8: return 'A'
            elif value <= 0.9: return 'B+'
            elif value <= 1.1: return 'B'
            else: return 'C'
        else:
            if value >= 1.3: return 'A+'
            elif value >= 1.2: return 'A'
            elif value >= 1.1: return 'B+'
            elif value >= 0.9: return 'B'
            else: return 'C'
    
    def _calculate_sales_score(self) -> float:
        """매출 성과 점수 계산"""
        scores = []
        aov_vs = self.kpis.get('avg_order_value_vs_category', 1.0)
        revenue_vs = self.kpis.get('total_revenue_vs_category', 1.0)
        
        if not pd.isna(aov_vs):
            scores.append(min(100, max(0, (aov_vs - 0.5) * 100)))
        if not pd.isna(revenue_vs):
            scores.append(min(100, max(0, (revenue_vs - 0.5) * 100)))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _calculate_customer_score(self) -> float:
        """고객 성과 점수 계산"""
        scores = []
        repeat_vs = self.kpis.get('repeat_rate_vs_category', 1.0)
        ltv_vs = self.kpis.get('customer_ltv_vs_category', 1.0)
        
        if not pd.isna(repeat_vs):
            scores.append(min(100, max(0, (repeat_vs - 0.5) * 100)))
        if not pd.isna(ltv_vs):
            scores.append(min(100, max(0, (ltv_vs - 0.5) * 100)))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _calculate_operations_score(self) -> float:
        """운영 성과 점수 계산"""
        scores = []
        cancel_vs = self.kpis.get('cancel_rate_vs_category', 1.0)
        delivery_vs = self.kpis.get('avg_delivery_time_vs_category', 1.0)
        
        if not pd.isna(cancel_vs):
            scores.append(min(100, max(0, (2 - cancel_vs - 0.5) * 100)))
        if not pd.isna(delivery_vs):
            scores.append(min(100, max(0, (2 - delivery_vs - 0.5) * 100)))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _calculate_market_score(self) -> float:
        """시장 성과 점수 계산"""
        basic_info = self.analysis_data['basic_info']
        if 'category_percentile' in basic_info:
            return basic_info['category_percentile']
        return 50
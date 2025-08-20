"""벤치마킹 분석 시트 작성기"""

import pandas as pd
from dashboard.utils.excel_formatter import smart_format_dataframe

class BenchmarkingWriter:
    """벤치마킹 분석 시트 작성"""
    
    def __init__(self, benchmarking_data: dict):
        self.benchmarking_data = benchmarking_data
    
    def write(self, writer):
        """벤치마킹 분석 시트 작성"""
        
        current_row = 0
        
        # A. 카테고리 내 포지션
        if 'position_metrics' in self.benchmarking_data:
            title_df = pd.DataFrame([['A. 카테고리 내 포지션']], columns=[''])
            title_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False, header=False)
            current_row += 2
            
            position_df = pd.DataFrame(list(self.benchmarking_data['position_metrics'].items()), columns=['지표', '값'])
            smart_format_dataframe(position_df, '벤치마킹', writer, current_row)
            current_row += len(position_df) + 3
        
        # B. 경쟁사 비교 (TOP 10)
        if 'top_competitors' in self.benchmarking_data:
            title_df = pd.DataFrame([['B. 카테고리 내 경쟁사 비교 TOP 10']], columns=[''])
            title_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False, header=False)
            current_row += 2
            
            competitors_df = self.benchmarking_data['top_competitors'].reset_index()
            smart_format_dataframe(competitors_df, '벤치마킹', writer, current_row)
            current_row += len(competitors_df) + 3
        
        # C. 상대적 성과 분석
        if 'relative_performance' in self.benchmarking_data:
            title_df = pd.DataFrame([['C. 상대적 성과 분석 (카테고리 평균 대비)']], columns=[''])
            title_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False, header=False)
            current_row += 2
            
            relative_data = []
            for metric, data in self.benchmarking_data['relative_performance'].items():
                relative_data.append([
                    metric,
                    data['상대성과'],
                    data['성과등급'],
                    data['개선여지']
                ])
            
            relative_df = pd.DataFrame(relative_data, columns=['지표', '상대성과', '등급', '개선여지'])
            smart_format_dataframe(relative_df, '벤치마킹', writer, current_row)
"""고객 분석 시트 작성기"""

import pandas as pd
from dashboard.utils.excel_formatter import format_basic_metrics, smart_format_dataframe

class CustomerWriter:
    """고객 분석 시트 작성"""
    
    def __init__(self, customers_data: dict):
        self.customers_data = customers_data
    
    def write(self, writer):
        """고객 분석 시트 작성"""
        
        current_row = 0
        
        if 'error' in self.customers_data:
            error_df = pd.DataFrame([['오류', self.customers_data['error']]], columns=['구분', '내용'])
            error_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False)
            return
        
        # A. 고객 기본 지표
        if 'basic_metrics' in self.customers_data:
            title_df = pd.DataFrame([['A. 고객 기본 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            basic_df = pd.DataFrame(list(self.customers_data['basic_metrics'].items()), columns=['지표', '값'])
            format_basic_metrics(basic_df, '고객분석', writer, current_row)
            current_row += len(basic_df) + 3
        
        # B. 고객 세그먼트 분석 (퍼센타일 기반)
        if 'segment_analysis' in self.customers_data:
            title_df = pd.DataFrame([['B. 고객 세그먼트 분석 (퍼센타일 기반)']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            segment_df = self.customers_data['segment_analysis'].reset_index()
            smart_format_dataframe(segment_df, '고객분석', writer, current_row)
            current_row += len(segment_df) + 3
        
        # C. 지역별 고객 분석
        if 'region_analysis' in self.customers_data:
            title_df = pd.DataFrame([['C. 지역별 고객 분석 TOP 10']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            region_df = self.customers_data['region_analysis'].reset_index()
            smart_format_dataframe(region_df, '고객분석', writer, current_row)
            current_row += len(region_df) + 3
        
        # D. 고객 생애주기 분석
        if 'lifecycle_analysis' in self.customers_data:
            title_df = pd.DataFrame([['D. 고객 생애주기 분석 (구매 차수별)']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            lifecycle_df = self.customers_data['lifecycle_analysis']
            smart_format_dataframe(lifecycle_df, '고객분석', writer, current_row)
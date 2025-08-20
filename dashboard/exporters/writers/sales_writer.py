"""매출 분석 시트 작성기"""

import pandas as pd
from dashboard.utils.excel_formatter import format_basic_metrics, smart_format_dataframe

class SalesWriter:
    """매출 분석 시트 작성"""
    
    def __init__(self, sales_data: dict):
        self.sales_data = sales_data
    
    def write(self, writer):
        """매출 분석 시트 작성"""
        
        current_row = 0
        
        # A. 기본 매출 지표
        if 'basic_metrics' in self.sales_data:
            title_df = pd.DataFrame([['A. 기본 매출 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            basic_df = pd.DataFrame(list(self.sales_data['basic_metrics'].items()), columns=['지표', '값'])
            format_basic_metrics(basic_df, '매출분석', writer, current_row)
            current_row += len(basic_df) + 3
        
        # B. 채널별 매출 분석
        if 'channel_analysis' in self.sales_data:
            title_df = pd.DataFrame([['B. 채널별 매출 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            channel_df = self.sales_data['channel_analysis'].reset_index()
            smart_format_dataframe(channel_df, '매출분석', writer, current_row)
            current_row += len(channel_df) + 3
        
        # C. 상품별 매출 TOP 20
        if 'product_analysis' in self.sales_data:
            title_df = pd.DataFrame([['C. 상품별 매출 TOP 20']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            product_df = self.sales_data['product_analysis'].reset_index()
            smart_format_dataframe(product_df, '매출분석', writer, current_row)
            current_row += len(product_df) + 3
        
        # D. 시간대별 매출 패턴
        if 'hourly_pattern' in self.sales_data:
            title_df = pd.DataFrame([['D. 시간대별 매출 패턴']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            hourly_df = self.sales_data['hourly_pattern'].reset_index()
            smart_format_dataframe(hourly_df, '매출분석', writer, current_row)
            current_row += len(hourly_df) + 3
        
        # E. 요일별 매출 패턴
        if 'daily_pattern' in self.sales_data:
            title_df = pd.DataFrame([['E. 요일별 매출 패턴']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            daily_df = self.sales_data['daily_pattern'].reset_index()
            smart_format_dataframe(daily_df, '매출분석', writer, current_row)
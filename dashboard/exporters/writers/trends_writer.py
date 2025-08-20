"""트렌드 분석 시트 작성기"""

import pandas as pd

class TrendsWriter:
    """트렌드 분석 시트 작성"""
    
    def __init__(self, trends_data: dict):
        self.trends_data = trends_data
    
    def write(self, writer):
        """트렌드 분석 시트 작성"""
        
        current_row = 0
        
        # A. 월별 트렌드
        if 'monthly_trend' in self.trends_data:
            title_df = pd.DataFrame([['A. 월별 트렌드 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            monthly_df = self.trends_data['monthly_trend'].reset_index()
            monthly_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False)
            current_row += len(monthly_df) + 3
        
        # B. 주별 트렌드
        if 'weekly_trend' in self.trends_data:
            title_df = pd.DataFrame([['B. 주별 트렌드 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            weekly_df = self.trends_data['weekly_trend'].reset_index()
            weekly_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False)
            current_row += len(weekly_df) + 3
        
        # C. 일별 트렌드 (최근 30일)
        if 'daily_trend' in self.trends_data:
            title_df = pd.DataFrame([['C. 일별 트렌드 분석 (최근 30일)']], columns=[''])
            title_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            daily_df = self.trends_data['daily_trend'].reset_index()
            daily_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False)
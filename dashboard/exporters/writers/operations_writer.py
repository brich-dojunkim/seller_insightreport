"""운영 분석 시트 작성기"""

import pandas as pd

class OperationsWriter:
    """운영 분석 시트 작성"""
    
    def __init__(self, operations_data: dict):
        self.operations_data = operations_data
    
    def write(self, writer):
        """운영 분석 시트 작성"""
        
        current_row = 0
        
        # A. 주요 운영 지표
        if 'key_metrics' in self.operations_data:
            title_df = pd.DataFrame([['A. 주요 운영 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            key_df = pd.DataFrame(list(self.operations_data['key_metrics'].items()), columns=['지표', '값'])
            # 값 포맷팅
            for idx, row in key_df.iterrows():
                if '율' in row['지표'] or '률' in row['지표']:
                    key_df.loc[idx, '값'] = f"{row['값']:.2f}%"
                else:
                    key_df.loc[idx, '값'] = f"{row['값']:,.0f}"
            
            key_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
            current_row += len(key_df) + 3
        
        # B. 주문 상태 분석
        if 'status_analysis' in self.operations_data:
            title_df = pd.DataFrame([['B. 주문 상태 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            status_df = self.operations_data['status_analysis']
            status_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
            current_row += len(status_df) + 3
        
        # C. 배송 성과 지표
        if 'shipping_metrics' in self.operations_data:
            title_df = pd.DataFrame([['C. 배송 성과 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            shipping_df = pd.DataFrame(list(self.operations_data['shipping_metrics'].items()), columns=['지표', '값'])
            # 값 포맷팅
            for idx, row in shipping_df.iterrows():
                if '시간' in row['지표']:
                    shipping_df.loc[idx, '값'] = f"{row['값']:.1f}일"
                elif '률' in row['지표'] or '율' in row['지표']:
                    shipping_df.loc[idx, '값'] = f"{row['값']:.1f}%"
            
            shipping_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
            current_row += len(shipping_df) + 3
        
        # D. 클레임 분석
        if 'claim_analysis' in self.operations_data:
            title_df = pd.DataFrame([['D. 클레임 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            claim_df = self.operations_data['claim_analysis']
            claim_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
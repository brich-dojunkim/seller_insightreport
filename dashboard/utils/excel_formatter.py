"""엑셀 포맷팅 유틸리티"""

import pandas as pd
import numpy as np

class ExcelFormatter:
    """엑셀 셀 포맷팅 유틸리티"""
    
    def __init__(self, workbook):
        self.workbook = workbook
        self._create_formats()
    
    def _create_formats(self):
        """엑셀 포맷 정의"""
        self.formats = {
            'money': self.workbook.add_format({'num_format': '₩#,##0'}),
            'percent': self.workbook.add_format({'num_format': '0.0%'}),
            'number': self.workbook.add_format({'num_format': '#,##0'}),
            'float1': self.workbook.add_format({'num_format': '0.0'}),
            'float2': self.workbook.add_format({'num_format': '0.00'}),
            'days': self.workbook.add_format({'num_format': '0.0"일"'}),
            'days_number': self.workbook.add_format({'num_format': '#,##0"일"'}),
            'times': self.workbook.add_format({'num_format': '0.0"시간"'}),
        }
    
    def detect_and_format_dataframe(self, df: pd.DataFrame, sheet_name: str, writer, startrow=0):
        """DataFrame의 컬럼을 분석해서 자동으로 적절한 포맷 적용"""
        
        # DataFrame을 일단 쓰기
        df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        worksheet = writer.sheets[sheet_name]
        
        # 시트별 특수 포맷 매핑 먼저 적용
        custom_mappings = self._get_custom_format_mapping(sheet_name, df.columns)
        
        # 각 컬럼 분석 및 포맷 적용
        for col_idx, column in enumerate(df.columns):
            # 커스텀 매핑이 있으면 우선 사용
            if column in custom_mappings:
                column_format = custom_mappings[column]
            else:
                column_format = self._detect_column_format(column, df[column])
            
            if column_format and column_format in self.formats:
                # 데이터 행에만 포맷 적용 (헤더 제외)
                for row_idx in range(len(df)):
                    cell_row = startrow + 1 + row_idx  # 헤더 다음부터
                    value = df.iloc[row_idx, col_idx]
                    
                    if pd.notna(value) and isinstance(value, (int, float)):
                        formatted_value = self._convert_value_for_format(value, column, column_format)
                        worksheet.write(cell_row, col_idx, formatted_value, self.formats[column_format])
    
    def _detect_column_format(self, column_name: str, column_data: pd.Series) -> str:
        """컬럼명과 데이터를 기반으로 포맷 유형 감지"""
        
        column_lower = column_name.lower()
        
        # 특수 케이스 먼저 처리
        if '총 분석일수' in column_name:
            return 'days_number'
        
        # 통화 관련 (한글 키워드 확장)
        money_keywords = [
            '매출', '금액', '가격', '수익', '총매출기여', '고객생애가치', 'ltv', 'aov',
            'revenue', 'amount', 'price', '총매출', '매출액', '구매금액', '평균구매금액',
            '평균주문금액', '총구매금액', '고객당_매출'
        ]
        if any(keyword in column_lower for keyword in money_keywords):
            return 'money'
        
        # 퍼센트 관련 (한글 키워드 확장)
        percent_keywords = [
            '율', '률', '비율', '비중', '점유', '기여도', '성장률', '잔존율',
            'rate', 'ratio', 'share', 'percent', '매출비중', '매출기여도', 
            '고객비율', '매출기여', '상위퍼센트'
        ]
        if any(keyword in column_lower for keyword in percent_keywords):
            return 'percent'
        
        # 시간 관련
        if any(keyword in column_lower for keyword in ['일', 'day', '시간', 'hour', 'time']) and any(keyword in column_lower for keyword in ['평균', '소요', '리드', 'avg', 'lead']):
            if '일' in column_lower or 'day' in column_lower:
                return 'days'
            else:
                return 'times'
        
        # 개수 관련 (정수)
        count_keywords = ['수', '건', '개', 'count', 'number', '주문', 'orders', '고객수', '셀러']
        if any(keyword in column_lower for keyword in count_keywords):
            return 'number'
        
        # 점수나 지수 (소수점 1자리)
        if any(keyword in column_lower for keyword in ['점수', '지수', 'score', 'index']):
            return 'float1'
        
        # 기본적으로 숫자이면 float1
        if column_data.dtype in ['float64', 'int64'] and not column_data.isna().all():
            return 'float1'
        
        return None
    
    def _convert_value_for_format(self, value, column_name: str, format_type: str):
        """포맷 타입에 따라 값 변환"""
        
        if format_type == 'percent':
            # 퍼센트 변환 로직 개선
            if isinstance(value, (int, float)):
                # 이미 0~1 범위인 경우 (예: 0.305)
                if 0 <= value <= 1:
                    return value
                # 1 이상인 경우 100으로 나누기 (예: 30.5 → 0.305)
                else:
                    return value / 100
        
        return value
    
    def apply_formats_to_dataframe_by_columns(self, df: pd.DataFrame, format_mapping: dict, 
                                             sheet_name: str, writer, startrow=0):
        """특정 컬럼에 직접 포맷 지정"""
        
        # DataFrame 쓰기
        df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        worksheet = writer.sheets[sheet_name]
        
        # 시트별 특수 포맷 매핑 적용
        custom_mappings = self._get_custom_format_mapping(sheet_name, df.columns)
        format_mapping.update(custom_mappings)
        
        # 지정된 포맷 적용
        for column, format_type in format_mapping.items():
            if column in df.columns:
                col_idx = df.columns.get_loc(column)
                
                for row_idx in range(len(df)):
                    cell_row = startrow + 1 + row_idx
                    value = df.iloc[row_idx, col_idx]
                    
                    if pd.notna(value) and isinstance(value, (int, float)):
                        formatted_value = self._convert_value_for_format(value, column, format_type)
                        worksheet.write(cell_row, col_idx, formatted_value, self.formats[format_type])
    
    def _get_custom_format_mapping(self, sheet_name: str, columns) -> dict:
        """시트별 특수 포맷 매핑"""
        mappings = {
            '대시보드요약': {
                '총 분석일수': 'days_number'
            },
            '매출분석': {
                '매출액': 'money',
                '매출비중': 'percent',
                '매출기여도': 'percent'
            },
            '고객분석': {
                '매출기여도': 'percent',
                '고객비율': 'percent'
            },
            '벤치마킹': {
                '총매출': 'money'
            },
            '트렌드분석': {
                '매출액': 'money'
            }
        }
        return mappings.get(sheet_name, {})

def smart_format_dataframe(df: pd.DataFrame, sheet_name: str, writer, startrow=0, custom_formats=None):
    """DataFrame을 자동으로 포맷팅하는 편의 함수"""
    
    if df.empty:
        return
    
    workbook = writer.book
    formatter = ExcelFormatter(workbook)
    
    if custom_formats:
        # 사용자 지정 포맷 사용
        formatter.apply_formats_to_dataframe_by_columns(df, custom_formats, sheet_name, writer, startrow)
    else:
        # 자동 감지 포맷 사용
        formatter.detect_and_format_dataframe(df, sheet_name, writer, startrow)

# 기존 writer들이 쉽게 사용할 수 있는 헬퍼 함수들
def format_basic_metrics(metrics_df: pd.DataFrame, sheet_name: str, writer, startrow=0):
    """기본 지표 DataFrame 포맷팅"""
    custom_formats = {}
    
    for idx, row in metrics_df.iterrows():
        metric_name = row.iloc[0]  # 첫 번째 컬럼이 지표명
        
        if any(keyword in metric_name for keyword in ['매출', '금액', '가격', 'AOV', 'LTV']):
            custom_formats[metrics_df.columns[1]] = 'money'  # 값 컬럼
        elif any(keyword in metric_name for keyword in ['율', '률', '비율']):
            custom_formats[metrics_df.columns[1]] = 'percent'
        elif any(keyword in metric_name for keyword in ['시간', '일']):
            custom_formats[metrics_df.columns[1]] = 'days'
        elif any(keyword in metric_name for keyword in ['수', '건', '개']):
            custom_formats[metrics_df.columns[1]] = 'number'
    
    smart_format_dataframe(metrics_df, sheet_name, writer, startrow, custom_formats)
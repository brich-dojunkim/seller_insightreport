"""최종 수정된 엑셀 포맷팅 유틸리티"""

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
            'money_decimal': self.workbook.add_format({'num_format': '₩#,##0.0'}),
            'percent': self.workbook.add_format({'num_format': '0.0%'}),
            'percent_int': self.workbook.add_format({'num_format': '0%'}),
            'number': self.workbook.add_format({'num_format': '#,##0'}),
            'float1': self.workbook.add_format({'num_format': '0.0'}),
            'float2': self.workbook.add_format({'num_format': '0.00'}),
            'days': self.workbook.add_format({'num_format': '0.0"일"'}),
            'days_number': self.workbook.add_format({'num_format': '#,##0"일"'}),
            'times': self.workbook.add_format({'num_format': '0.0"시간"'}),
            'rank': self.workbook.add_format({'num_format': '0"위"'}),
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
                column_format = self._detect_column_format(column, df[column], sheet_name)
            
            if column_format and column_format in self.formats:
                # 데이터 행에만 포맷 적용 (헤더 제외)
                for row_idx in range(len(df)):
                    cell_row = startrow + 1 + row_idx  # 헤더 다음부터
                    value = df.iloc[row_idx, col_idx]
                    
                    if pd.notna(value) and isinstance(value, (int, float)):
                        formatted_value = self._convert_value_for_format(value, column, column_format)
                        worksheet.write(cell_row, col_idx, formatted_value, self.formats[column_format])
    
    def _detect_column_format(self, column_name: str, column_data: pd.Series, sheet_name: str = '') -> str:
        """개선된 컬럼명과 데이터를 기반으로 포맷 유형 감지"""
        
        column_lower = column_name.lower()
        
        # 1. 특수 케이스 먼저 처리 (정확한 매칭)
        special_cases = {
            '총 분석일수': 'days_number',
            '총분석일수': 'days_number',
            '분석일수': 'days_number'
        }
        
        for case, format_type in special_cases.items():
            if case in column_name:
                return format_type
        
        # 2. 순위나 텍스트 형태는 포맷하지 않음
        if any(keyword in column_name for keyword in ['순위', '등급']) and '/' in str(column_data.iloc[0] if len(column_data) > 0 else ''):
            return None
        
        # 3. 대시보드요약 시트의 특별 처리
        if sheet_name == '대시보드요약':
            if column_name == '값':
                # 행별로 다른 포맷이 필요한 경우는 커스텀 매핑에 의존
                return None
        
        # 4. 퍼센트 관련 키워드를 먼저 체크 (구체적인 것부터)
        percent_keywords = [
            '점유율', '비율', '비중', '기여도', '성장률', '잔존율', '완료율', 
            '취소율', '반품률', '재구매율', '발송률', '배송완료율', '지연율',
            '율', '률', 'rate', 'ratio', 'share', 'percent', '상위퍼센트'
        ]
        if any(keyword in column_lower for keyword in percent_keywords):
            return 'percent'
        
        # 5. 통화 관련 키워드 (구체적인 것부터)
        money_keywords = [
            '매출액', '총매출', '총_매출액', '일평균_매출액',
            '금액', '가격', '수익', '구매금액', '주문금액', '평균구매금액', '평균주문금액',
            '총구매금액', '고객생애가치', '고객당_매출', '총매출기여',
            'aov', 'ltv', 'revenue', 'amount', 'price'
        ]
        if any(keyword in column_lower for keyword in money_keywords):
            # 소수점이 있는 값들은 money_decimal 사용
            if hasattr(column_data, 'dtype') and column_data.dtype == 'float64':
                return 'money_decimal'
            return 'money'
        
        # 6. 개수/수량 관련 키워드
        count_keywords = [
            '고객수', '주문수', '건수', '판매수량', '구매횟수', '총_주문수', '총_판매수량',
            'count', 'number', '주문', 'orders', '고객', '셀러'
        ]
        if any(keyword in column_lower for keyword in count_keywords):
            return 'number'
        
        # 7. 시간 관련
        if any(keyword in column_lower for keyword in ['일', 'day']) and any(keyword in column_lower for keyword in ['평균', '소요', '리드', 'avg', 'lead']):
            return 'days'
        
        if any(keyword in column_lower for keyword in ['시간', 'hour', 'time']) and any(keyword in column_lower for keyword in ['평균', '소요', '배송', 'delivery']):
            return 'times'
        
        # 8. 점수나 지수
        if any(keyword in column_lower for keyword in ['점수', '지수', 'score', 'index']):
            return 'float1'
        
        # 9. 기본적으로 숫자이면 적절한 소수점 포맷
        if hasattr(column_data, 'dtype') and column_data.dtype in ['float64', 'int64'] and not column_data.isna().all():
            # 정수형 데이터면 number, 실수형이면 float1
            if column_data.dtype == 'int64':
                return 'number'
            else:
                return 'float1'
        
        return None
    
    def _convert_value_for_format(self, value, column_name: str, format_type: str):
        """포맷 타입에 따라 값 변환"""
        
        if format_type == 'percent':
            # 퍼센트 변환 로직 개선
            if isinstance(value, (int, float)):
                # 이미 0~1 범위에 있다면 그대로 사용
                if 0 <= value <= 1:
                    return value
                # 1보다 크다면 100으로 나누기
                elif value > 1:
                    return value / 100
                else:
                    return value
        
        elif format_type == 'days_number':
            # 일수는 정수로 변환
            return int(value) if isinstance(value, (int, float)) else value
        
        return value
    
    def apply_formats_to_dataframe_by_columns(self, df: pd.DataFrame, format_mapping: dict, 
                                             sheet_name: str, writer, startrow=0):
        """특정 컬럼에 직접 포맷 지정"""
        
        # DataFrame 쓰기
        df.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=False)
        worksheet = writer.sheets[sheet_name]
        
        # 시트별 특수 포맷 매핑 적용
        custom_mappings = self._get_custom_format_mapping(sheet_name, df.columns)
        
        # 행별 특별 처리가 필요한 경우
        if sheet_name == '대시보드요약' and '값' in df.columns:
            self._apply_dashboard_special_formatting(df, worksheet, startrow, custom_mappings)
            return
        
        # 일반적인 컬럼별 포맷 적용
        format_mapping.update(custom_mappings)
        
        for column, format_type in format_mapping.items():
            if column in df.columns and format_type in self.formats:
                col_idx = df.columns.get_loc(column)
                
                for row_idx in range(len(df)):
                    cell_row = startrow + 1 + row_idx
                    value = df.iloc[row_idx, col_idx]
                    
                    if pd.notna(value) and isinstance(value, (int, float)):
                        formatted_value = self._convert_value_for_format(value, column, format_type)
                        worksheet.write(cell_row, col_idx, formatted_value, self.formats[format_type])
    
    def _apply_dashboard_special_formatting(self, df: pd.DataFrame, worksheet, startrow: int, custom_mappings: dict):
        """대시보드요약 시트의 특별한 행별 포맷팅"""
        
        value_col_idx = df.columns.get_loc('값')
        
        for row_idx in range(len(df)):
            cell_row = startrow + 1 + row_idx
            label = df.iloc[row_idx, 0]  # 구분 컬럼
            value = df.iloc[row_idx, value_col_idx]
            
            if pd.notna(value) and isinstance(value, (int, float)):
                # 라벨에 따라 포맷 결정
                format_type = None
                
                if '총 분석일수' in str(label):
                    format_type = 'days_number'
                elif any(keyword in str(label) for keyword in ['점유율', '비율']):
                    format_type = 'percent'
                elif any(keyword in str(label) for keyword in ['매출액', '금액']):
                    format_type = 'money'
                elif any(keyword in str(label) for keyword in ['고객수', '주문수']):
                    format_type = 'number'
                
                if format_type and format_type in self.formats:
                    formatted_value = self._convert_value_for_format(value, str(label), format_type)
                    worksheet.write(cell_row, value_col_idx, formatted_value, self.formats[format_type])
    
    def _get_custom_format_mapping(self, sheet_name: str, columns) -> dict:
        """시트별 특수 포맷 매핑"""
        mappings = {
            '대시보드요약': {
                '총매출액': 'money',
                '평균주문금액': 'money_decimal',
                '재구매율': 'percent',
                '취소율': 'percent',
                '배송완료시간': 'days',
                '고객수': 'number',
                '카테고리대비': 'float2',
                '점수': 'float1'
            },
            '매출분석': {
                '총_매출액': 'money',
                '총_주문수': 'number',
                '평균주문금액': 'money_decimal',
                '총_판매수량': 'number',
                '일평균_매출액': 'money',
                '평균상품가격': 'money_decimal',
                '매출액': 'money',
                '매출비중': 'percent',
                '매출기여도': 'percent',
                'AOV': 'money_decimal'
            },
            '고객분석': {
                '총_고객수': 'number',
                '신규_고객수': 'number',
                '기존_고객수': 'number',
                '재구매율': 'percent',
                '평균_구매횟수': 'float1',
                '평균_고객생애가치': 'money',
                '고객수': 'number',
                '총매출기여': 'money',
                '평균구매금액': 'money',
                '고객비율': 'percent',
                '매출기여도': 'percent',
                '고객생애가치': 'money'
            },
            '운영분석': {
                '전체주문수': 'number',
                '배송완료율': 'percent',
                '취소율': 'percent',
                '지연율': 'percent',
                '반품률': 'percent',
                '평균출고시간': 'days',
                '당일발송률': 'percent',
                '평균배송시간': 'days',
                '빠른배송률': 'percent'
            },
            '벤치마킹': {
                '총매출': 'money',
                'AOV': 'money_decimal',
                '고객수': 'number',
                '상대성과': 'float2'
            },
            '트렌드분석': {
                '매출액': 'money',
                '주문수': 'number',
                'AOV': 'money_decimal',
                '고객수': 'number',
                '매출성장률': 'percent',
                '주문성장률': 'percent'
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

def format_basic_metrics(metrics_df: pd.DataFrame, sheet_name: str, writer, startrow=0):
    """기본 지표 DataFrame 포맷팅 - smart_format_dataframe 사용하도록 변경"""
    
    if metrics_df.empty:
        return
    
    # format_basic_metrics 대신 smart_format_dataframe 사용
    smart_format_dataframe(metrics_df, sheet_name, writer, startrow)

# 통화 포맷팅 유틸리티 함수
def format_currency(value):
    """통화 포맷팅 유틸리티"""
    if pd.isna(value) or not isinstance(value, (int, float)):
        return value
    return f"₩{value:,.0f}"
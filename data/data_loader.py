# data/data_loader.py - 엑셀 데이터 로드 및 검증

import pandas as pd
import os
from datetime import datetime
import sys
sys.path.append('..')
from config import DATA_VALIDATION, ERROR_MESSAGES, SUCCESS_MESSAGES

class DataLoader:
    """엑셀 데이터 로드 및 기본 검증을 담당하는 클래스"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.raw_data = None
        self.validated_data = None
        
    def load_excel(self):
        """엑셀 파일 로드"""
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(ERROR_MESSAGES['file_not_found'].format(self.file_path))
            
            # 엑셀 파일 읽기
            self.raw_data = pd.read_excel(self.file_path)
            print(SUCCESS_MESSAGES['data_loaded'].format(len(self.raw_data)))
            
            return self.raw_data
            
        except Exception as e:
            print(f"❌ 파일 로드 실패: {str(e)}")
            return None
    
    def validate_data_structure(self):
        """데이터 구조 검증"""
        if self.raw_data is None:
            print("❌ 데이터가 로드되지 않았습니다")
            return False
        
        # 필수 컬럼 확인
        missing_columns = []
        for col in DATA_VALIDATION['required_columns']:
            if col not in self.raw_data.columns:
                missing_columns.append(col)
        
        if missing_columns:
            print(ERROR_MESSAGES['missing_columns'].format(', '.join(missing_columns)))
            return False
        
        # 최소 레코드 수 확인
        if len(self.raw_data) < DATA_VALIDATION['min_records_for_analysis']:
            print(ERROR_MESSAGES['insufficient_data'].format(
                DATA_VALIDATION['min_records_for_analysis']))
            return False
        
        print("✅ 데이터 구조 검증 완료")
        return True
    
    def clean_data(self):
        """데이터 정리 및 전처리"""
        if self.raw_data is None:
            return None
        
        try:
            # 데이터 복사
            cleaned_data = self.raw_data.copy()
            
            # 결제일 데이터 타입 확인 및 변환
            if '결제일' in cleaned_data.columns:
                # 문자열로 되어 있는 경우 datetime 변환 시도
                try:
                    cleaned_data['결제일'] = pd.to_datetime(cleaned_data['결제일'])
                except:
                    print("⚠️ 결제일 형식 변환 실패, 원본 형태 유지")
            
            # 숫자형 컬럼 정리
            numeric_columns = ['상품가격', '수량', '상품별 총 주문금액']
            for col in numeric_columns:
                if col in cleaned_data.columns:
                    # 문자열에서 숫자 추출 (쉼표 제거 등)
                    if cleaned_data[col].dtype == 'object':
                        cleaned_data[col] = pd.to_numeric(
                            cleaned_data[col].astype(str).str.replace(',', ''), 
                            errors='coerce'
                        )
                    
                    # 결측값을 0으로 처리
                    cleaned_data[col] = cleaned_data[col].fillna(0)
            
            # 문자열 컬럼 정리 (앞뒤 공백 제거)
            string_columns = ['판매채널', '입점사명', '상품명', '주문상태']
            for col in string_columns:
                if col in cleaned_data.columns:
                    cleaned_data[col] = cleaned_data[col].astype(str).str.strip()
            
            # 중복 제거
            initial_count = len(cleaned_data)
            cleaned_data = cleaned_data.drop_duplicates(subset=['상품주문번호'])
            final_count = len(cleaned_data)
            
            if initial_count != final_count:
                print(f"✅ 중복 제거: {initial_count - final_count}건")
            
            self.validated_data = cleaned_data
            print("✅ 데이터 정리 완료")
            
            return self.validated_data
            
        except Exception as e:
            print(f"❌ 데이터 정리 실패: {str(e)}")
            return None
    
    def get_data_summary(self):
        """데이터 요약 정보 반환"""
        if self.validated_data is None:
            return None
        
        summary = {
            'total_records': len(self.validated_data),
            'date_range': {
                'start': self.validated_data['결제일'].min(),
                'end': self.validated_data['결제일'].max()
            },
            'companies': self.validated_data['입점사명'].unique().tolist(),
            'channels': self.validated_data['판매채널'].unique().tolist(),
            'total_revenue': self.validated_data['상품별 총 주문금액'].sum(),
            'columns': self.validated_data.columns.tolist()
        }
        
        return summary
    
    def filter_by_company(self, company_name):
        """특정 입점사 데이터만 필터링"""
        if self.validated_data is None:
            print("❌ 검증된 데이터가 없습니다")
            return None
        
        company_data = self.validated_data[
            self.validated_data['입점사명'] == company_name
        ].copy()
        
        if len(company_data) == 0:
            print(ERROR_MESSAGES['no_company_data'].format(company_name))
            return None
        
        print(SUCCESS_MESSAGES['company_filtered'].format(company_name, len(company_data)))
        return company_data
    
    def get_available_companies(self):
        """사용 가능한 입점사 목록 반환"""
        if self.validated_data is None:
            return []
        
        companies = self.validated_data.groupby('입점사명').size().sort_values(ascending=False)
        return companies.to_dict()

# 테스트 함수
def test_data_loader(file_path="order_list_20250818120157_497.xlsx"):
    """데이터 로더 테스트"""
    print("🧪 데이터 로더 테스트 시작...")
    
    # 데이터 로더 초기화
    loader = DataLoader(file_path)
    
    # 1. 엑셀 파일 로드
    data = loader.load_excel()
    if data is None:
        return False
    
    # 2. 데이터 구조 검증
    if not loader.validate_data_structure():
        return False
    
    # 3. 데이터 정리
    cleaned_data = loader.clean_data()
    if cleaned_data is None:
        return False
    
    # 4. 데이터 요약
    summary = loader.get_data_summary()
    print("\n📊 데이터 요약:")
    print(f"   • 총 레코드: {summary['total_records']:,}건")
    print(f"   • 기간: {summary['date_range']['start']} ~ {summary['date_range']['end']}")
    print(f"   • 입점사 수: {len(summary['companies'])}개")
    print(f"   • 판매채널 수: {len(summary['channels'])}개")
    print(f"   • 총 매출: ₩{summary['total_revenue']:,.0f}")
    
    # 5. 입점사별 데이터 확인
    companies = loader.get_available_companies()
    print("\n🏢 입점사별 주문 건수:")
    for company, count in list(companies.items())[:5]:
        print(f"   • {company}: {count:,}건")
    
    # 6. 포레스트핏 데이터 필터링 테스트
    forestfit_data = loader.filter_by_company("포레스트핏")
    if forestfit_data is not None:
        print(f"\n✅ 포레스트핏 데이터: {len(forestfit_data)}건")
    
    print("\n🎉 데이터 로더 테스트 완료!")
    return True

if __name__ == "__main__":
    test_data_loader()
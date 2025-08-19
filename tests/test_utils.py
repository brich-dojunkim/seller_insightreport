#!/usr/bin/env python3
"""모듈화된 utils 테스트"""
# 경로 문제 해결
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

# 모듈별 import 테스트
from utils import (
    # 데이터 변환
    to_datetime_safe, to_number_safe,
    
    # 고객 식별  
    create_customer_id,
    
    # 카테고리 매핑
    load_category_mapping, map_category_code_to_name,
    
    # 지역 추출
    extract_region_from_address,
    
    # 포맷팅
    format_currency, pct, df_to_html_table, sanitize_filename
)

def test_region_extraction_combined():
    """지역 추출 결합 방식 테스트"""
    
    print("=== 지역 추출 결합 방식 테스트 ===")
    
    # 테스트 주소들 - 다양한 시/도 표현 방식
    test_addresses = [
        "서울 성북구 하월곡동 90-16301층",
        "서울특별시 강남구 대치동 543", 
        "서울시 종로구 청와대로",
        "경기도 성남시 분당구 정자동",
        "경기 화성시 새솔동",
        "부산광역시 해운대구 중동",
        "부산시 사하구 다대동",
        "부산 진구 부전동",
        "대구 달서구 성서동",
        "대구광역시 수성구",
        "인천 남동구",
        "인천광역시 연수구",
        "제주특별자치도 제주시",
        "제주도 서귀포시",
        "제주 애월읍",
        "강원도 춘천시 교동",
        "강원 원주시",
        "충남 천안시 서북구",
        "충청남도 아산시",
        "전북 전주시 완산구",
        "전라북도 익산시",
        "경남 창원시 마산",
        "경상남도 진주시",
        "부산",  # 단어 하나만
        "서울",  # 단어 하나만
        "",      # 빈 문자열
        None     # None 값
    ]
    
    # pandas Series로 변환
    address_series = pd.Series(test_addresses)
    
    # 지역 추출 (결합 방식)
    regions = extract_region_from_address(address_series)
    
    print("주소 → 추출된 지역 (두 단어 + 시/도 표준화):")
    for original, extracted in zip(test_addresses, regions):
        print(f"  {original} → {extracted}")
    
    # 표준화 효과 확인
    print(f"\n🔍 표준화 효과:")
    unique_regions = regions.dropna().unique()
    print(f"총 {len(unique_regions)}개 고유 지역:")
    for region in sorted(unique_regions):
        print(f"  - {region}")

def test_category_mapping():
    """카테고리 매핑 테스트"""
    
    print("\n=== 카테고리 매핑 테스트 ===")
    
    # 카테고리 매핑 로드
    mapping = load_category_mapping()
    print(f"매핑 딕셔너리 크기: {len(mapping):,}개")
    
    # 샘플 코드들 테스트
    test_codes = [
        "1100010001",      # 실제 데이터에서 자주 나오는 코드
        "11000700020001",  # 또 다른 코드
        "1000100020001",   # 또 다른 코드
        "0001000100010001", # 매핑 파일에서 확인한 코드
        "999999",          # 존재하지 않는 코드
        1100010001.0,      # float 형태
        None               # None 값
    ]
    
    print("\n카테고리 코드 → 한글명 변환 테스트:")
    for code in test_codes:
        korean_name = map_category_code_to_name(code, mapping)
        print(f"  {code} → {korean_name}")

def test_other_modules():
    """다른 모듈들 테스트"""
    
    print("\n=== 기타 모듈 테스트 ===")
    
    # 데이터 변환 테스트
    test_dates = pd.Series(['2025-08-11', '2025-08-12', 'invalid', None])
    converted_dates = to_datetime_safe(test_dates)
    print("날짜 변환 테스트:")
    for orig, conv in zip(test_dates, converted_dates):
        print(f"  {orig} → {conv}")
    
    # 숫자 변환 테스트
    test_numbers = pd.Series(['1,234', '₩5,678', 'abc', None])
    converted_numbers = to_number_safe(test_numbers)
    print("\n숫자 변환 테스트:")
    for orig, conv in zip(test_numbers, converted_numbers):
        print(f"  {orig} → {conv}")
    
    # 고객 ID 생성 테스트
    names = pd.Series(['김철수', '이영희', '김철수'])
    phones = pd.Series(['010-1234-5678', '010-2345-6789', '010-1234-5678'])
    customer_ids = create_customer_id(names, phones)
    print("\n고객 ID 생성 테스트:")
    for name, phone, cid in zip(names, phones, customer_ids):
        print(f"  {name} + {phone} → {cid}")
    
    # 포맷팅 테스트
    print("\n포맷팅 테스트:")
    print(f"  통화: {format_currency(123456)}")
    print(f"  퍼센트: {pct(0.1234)}")
    print(f"  파일명: {sanitize_filename('test/file:name*.txt')}")

def test_integration_with_real_data():
    """실제 데이터와 통합 테스트"""
    
    print("\n=== 실제 데이터 통합 테스트 ===")
    
    try:
        from config import CONFIG
        from file_manager import load_excel_data
        
        # 실제 데이터 로드
        df = load_excel_data(CONFIG["INPUT_XLSX"])
        print(f"실제 데이터: {len(df):,}건")
        
        # 지역 추출 테스트
        address_columns = [col for col in df.columns if '배송지' in col or '주소' in col]
        if address_columns:
            address_col = address_columns[0]
            sample_addresses = df[address_col].dropna().head(10)
            
            print(f"\n실제 주소 → 지역 추출 (결합 방식):")
            regions = extract_region_from_address(sample_addresses)
            for addr, region in zip(sample_addresses, regions):
                print(f"  {addr[:50]}... → {region}")
        
    except Exception as e:
        print(f"실제 데이터 테스트 중 오류: {e}")

if __name__ == "__main__":
    test_region_extraction_combined()
    test_category_mapping()
    test_other_modules()
    test_integration_with_real_data()
    print("\n✅ 모든 모듈 테스트 완료!")
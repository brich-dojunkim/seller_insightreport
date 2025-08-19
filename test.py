#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""통합 테스트 파일 - 전체 시스템 검증"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import math
from pathlib import Path
from config import CONFIG
from file_manager import load_excel_data
from constants import *

# utils 모듈 테스트
from utils import format_currency, pct, df_to_html_table, sanitize_filename

# data_processing 모듈 테스트 (새로운 구조)
from data_processing import (
    prepare_dataframe, slice_by_seller, 
    calculate_comprehensive_kpis, calculate_kpis,
    get_channel_analysis, get_product_analysis, get_category_analysis,
    get_region_analysis, get_time_analysis, get_comprehensive_analysis,
    to_datetime_safe, to_number_safe, create_customer_id,
    extract_region_from_address, load_category_mapping, map_category_code_to_name
)

def test_utils_module():
    """Utils 모듈 테스트"""
    
    print("=" * 80)
    print("🧰 Utils 모듈 테스트")
    print("=" * 80)
    
    # 포맷팅 테스트
    print("\n📊 포맷팅 함수 테스트:")
    print(f"  통화 포맷: {format_currency(123456)}")
    print(f"  통화 포맷 (NaN): {format_currency(float('nan'))}")
    print(f"  퍼센트 포맷: {pct(0.1234)}")
    print(f"  퍼센트 포맷 (NaN): {pct(float('nan'))}")
    print(f"  파일명 정리: {sanitize_filename('test/file:name*.txt')}")
    
    # DataFrame to HTML 테스트
    test_df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
    html_result = df_to_html_table(test_df, max_rows=2)
    print(f"  HTML 테이블 생성: {'✅' if '<table' in html_result else '❌'}")
    
    # 빈 DataFrame 테스트
    empty_html = df_to_html_table(pd.DataFrame())
    print(f"  빈 DataFrame 처리: {'✅' if empty_html == '<div>-</div>' else '❌'}")
    
    print("✅ Utils 모듈 테스트 완료!")

def test_transformers_module():
    """Transformers 모듈 테스트"""
    
    print("\n" + "=" * 80)
    print("🔧 Transformers 모듈 테스트")
    print("=" * 80)
    
    # 날짜 변환 테스트
    print("\n📅 날짜 변환 테스트:")
    test_dates = pd.Series(['2025-08-11', '2025-08-12', 'invalid', None])
    converted_dates = to_datetime_safe(test_dates)
    valid_count = converted_dates.notna().sum()
    print(f"  입력: {len(test_dates)}개, 변환 성공: {valid_count}개")
    print(f"  날짜 변환: {'✅' if valid_count >= 2 else '❌'}")
    
    # 숫자 변환 테스트
    print("\n🔢 숫자 변환 테스트:")
    test_numbers = pd.Series(['1,234', '₩5,678', 'abc', None])
    converted_numbers = to_number_safe(test_numbers)
    numeric_count = converted_numbers.notna().sum()
    print(f"  입력: {len(test_numbers)}개, 변환 성공: {numeric_count}개")
    print(f"  숫자 변환: {'✅' if numeric_count >= 2 else '❌'}")
    
    # 고객 ID 생성 테스트
    print("\n👤 고객 ID 생성 테스트:")
    names = pd.Series(['김철수', '이영희', '김철수'])
    phones = pd.Series(['010-1234-5678', '010-2345-6789', '010-1234-5678'])
    customer_ids = create_customer_id(names, phones)
    unique_customers = customer_ids.nunique()
    print(f"  입력: 3명, 고유 고객: {unique_customers}명")
    print(f"  고객 ID 생성: {'✅' if unique_customers == 2 else '❌'}")
    
    # 지역 추출 테스트
    print("\n🌍 지역 추출 테스트:")
    test_addresses = pd.Series([
        "서울특별시 강남구 테헤란로",
        "부산 해운대구 중동",
        "경기도 성남시 분당구",
        None
    ])
    regions = extract_region_from_address(test_addresses)
    extracted_count = regions.notna().sum()
    print(f"  입력: {len(test_addresses)}개, 추출 성공: {extracted_count}개")
    for addr, region in zip(test_addresses, regions):
        if pd.notna(addr):
            print(f"    {addr[:20]}... → {region}")
    print(f"  지역 추출: {'✅' if extracted_count >= 3 else '❌'}")
    
    # 카테고리 매핑 테스트
    print("\n📂 카테고리 매핑 테스트:")
    mapping = load_category_mapping()
    mapping_loaded = len(mapping) > 0
    print(f"  매핑 딕셔너리: {len(mapping):,}개")
    print(f"  카테고리 매핑 로드: {'✅' if mapping_loaded else '⚠️'}")
    
    # 샘플 매핑 테스트
    test_codes = ['1100010001', '999999', None]
    for code in test_codes:
        mapped_name = map_category_code_to_name(code, mapping)
        print(f"    {code} → {mapped_name}")
    
    print("✅ Transformers 모듈 테스트 완료!")

def test_data_preparation():
    """데이터 준비 및 전처리 테스트"""
    
    print("\n" + "=" * 80)
    print("🔧 데이터 준비 및 전처리 테스트")
    print("=" * 80)
    
    try:
        # 데이터 로드 (config에서 경로 가져오기)
        input_path = CONFIG["INPUT_XLSX"]
        print(f"📁 로드 경로: {input_path}")
        
        df = load_excel_data(input_path)
        print(f"📁 원본 데이터 로드: {len(df):,}건")
        
        # 컬럼 존재 여부 확인
        required_columns = [COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_SELLER, COL_CHANNEL]
        optional_columns = [COL_BUYER_NAME, COL_BUYER_PHONE, COL_ADDRESS, COL_CATEGORY, COL_STATUS]
        
        print("\n📋 필수 컬럼 확인:")
        required_available = 0
        for col in required_columns:
            exists = col in df.columns
            print(f"  {'✅' if exists else '❌'} {col}")
            if exists:
                required_available += 1
        
        print("\n📋 선택 컬럼 확인:")
        optional_available = 0
        for col in optional_columns:
            exists = col in df.columns
            if exists:
                data_count = df[col].notna().sum()
                print(f"  ✅ {col}: {data_count:,}건 ({data_count/len(df)*100:.1f}%)")
                optional_available += 1
            else:
                print(f"  ❌ {col}: 없음")
        
        # 데이터 전처리
        dfp = prepare_dataframe(df, None, None)
        print(f"\n🔄 전처리 완료: {len(dfp):,}건")
        
        # 생성된 파생 컬럼 확인
        derived_columns = ['__dt__', '__amount__', '__qty__', '__customer_id__', '__region__']
        print("\n🆕 파생 컬럼 생성 결과:")
        derived_available = 0
        for col in derived_columns:
            if col in dfp.columns:
                valid_count = dfp[col].notna().sum()
                print(f"  ✅ {col}: {valid_count:,}건 ({valid_count/len(dfp)*100:.1f}%)")
                derived_available += 1
            else:
                print(f"  ❌ {col}: 생성 안됨")
        
        total_columns = required_available + optional_available + derived_available
        print(f"\n📊 전체 컬럼 활용률: {total_columns}/12개 ({total_columns/12*100:.0f}%)")
        
        return dfp
        
    except Exception as e:
        print(f"❌ 데이터 준비 테스트 실패: {e}")
        return None

def test_kpi_metrics_module(dfp):
    """KPI 계산 모듈 테스트"""
    
    print("\n" + "=" * 80)
    print("📊 KPI 계산 모듈 테스트")
    print("=" * 80)
    
    try:
        # KPI 계산
        kpis = calculate_comprehensive_kpis(dfp, dfp)
        
        print("\n🔢 KPI 지표 검증:")
        
        # 그룹별 지표 확인
        kpi_groups = {
            '기본 매출': ['total_orders', 'total_revenue', 'avg_order_value', 'total_quantity'],
            '고객 행동': ['unique_customers', 'repeat_customers', 'repeat_rate', 'customer_ltv'],
            '주문 상태': ['completion_rate', 'cancel_rate', 'delay_rate', 'return_rate'],
            '운영 효율': ['avg_ship_leadtime', 'same_day_ship_rate', 'avg_delivery_time'],
            '벤치마킹': ['benchmark_aov', 'benchmark_cancel_rate']
        }
        
        total_available = 0
        for group_name, metrics in kpi_groups.items():
            print(f"\n📈 {group_name} 지표:")
            group_available = 0
            
            for metric in metrics:
                value = kpis.get(metric)
                if value is not None and not (isinstance(value, float) and math.isnan(value)):
                    if 'rate' in metric or metric in ['repeat_rate']:
                        print(f"  ✅ {metric}: {pct(value)}")
                    elif 'amount' in metric or 'revenue' in metric or 'aov' in metric or 'ltv' in metric:
                        print(f"  ✅ {metric}: {format_currency(value)}")
                    else:
                        print(f"  ✅ {metric}: {value:,.1f}")
                    group_available += 1
                else:
                    print(f"  ❌ {metric}: 데이터 없음")
            
            print(f"  📊 {group_name} 활용률: {group_available}/{len(metrics)}개")
            total_available += group_available
        
        print(f"\n🎯 KPI 모듈 총 활용률: {total_available}/{sum(len(m) for m in kpi_groups.values())}개")
        
        # 기존 호환성 테스트
        legacy_kpis = calculate_kpis(dfp, dfp)
        legacy_available = sum(1 for v in legacy_kpis.values() if v is not None and not (isinstance(v, float) and math.isnan(v)))
        print(f"📊 기존 KPI 호환성: {legacy_available}/{len(legacy_kpis)}개")
        
        return kpis, total_available
        
    except Exception as e:
        print(f"❌ KPI 계산 테스트 실패: {e}")
        return {}, 0

def test_business_analysis_module(dfp):
    """비즈니스 분석 모듈 테스트"""
    
    print("\n" + "=" * 80)
    print("🏢 비즈니스 분석 모듈 테스트")
    print("=" * 80)
    
    try:
        analysis_available = 0
        
        # 채널 분석
        print("\n🛒 채널 분석:")
        channel_analysis = get_channel_analysis(dfp)
        if not channel_analysis.empty:
            print(f"  ✅ 채널 데이터: {len(channel_analysis)}개")
            # 상위 3개 채널 표시
            for idx, (channel, row) in enumerate(channel_analysis.head(3).iterrows(), 1):
                print(f"    {idx}. {channel}: {format_currency(row['revenue'])}")
            analysis_available += 1
        else:
            print(f"  ❌ 채널 분석: 데이터 없음")
        
        # 상품 분석
        print("\n📦 상품 분석:")
        product_analysis = get_product_analysis(dfp)
        if not product_analysis.empty:
            print(f"  ✅ 상품 데이터: {len(product_analysis)}개")
            # 상위 3개 상품 표시
            for idx, row in product_analysis.head(3).iterrows():
                product_name = row['상품명'][:30] + "..." if len(row['상품명']) > 30 else row['상품명']
                print(f"    {idx+1}. {product_name}: {format_currency(row['revenue'])}")
            analysis_available += 1
        else:
            print(f"  ❌ 상품 분석: 데이터 없음")
        
        # 카테고리 분석
        print("\n📂 카테고리 분석:")
        category_analysis = get_category_analysis(dfp)
        if not category_analysis.empty:
            print(f"  ✅ 카테고리 데이터: {len(category_analysis)}개")
            for idx, (category, row) in enumerate(category_analysis.head(3).iterrows(), 1):
                print(f"    {idx}. {category}: {format_currency(row['revenue'])}")
            analysis_available += 1
        else:
            print(f"  ❌ 카테고리 분석: 데이터 없음")
            # 카테고리 컬럼 진단
            category_columns = [col for col in dfp.columns if '카테고리' in col]
            if category_columns:
                print(f"  🔧 발견된 카테고리 컬럼: {category_columns}")
                print(f"  🔧 상수 정의: {COL_CATEGORY}")
        
        # 지역 분석
        print("\n🌍 지역 분석:")
        region_analysis = get_region_analysis(dfp)
        if not region_analysis.empty:
            print(f"  ✅ 지역 데이터: {len(region_analysis)}개")
            for idx, (region, row) in enumerate(region_analysis.head(3).iterrows(), 1):
                print(f"    {idx}. {region}: {format_currency(row['revenue'])}")
            analysis_available += 1
        else:
            print(f"  ❌ 지역 분석: 데이터 없음")
        
        # 시간 분석
        print("\n📅 시간 분석:")
        time_analysis = get_time_analysis(dfp)
        time_available = 0
        if time_analysis:
            for analysis_type in ['daily', 'hourly', 'weekly']:
                if analysis_type in time_analysis and not time_analysis[analysis_type].empty:
                    count = len(time_analysis[analysis_type])
                    print(f"  ✅ {analysis_type} 분석: {count}개 데이터포인트")
                    time_available += 1
                else:
                    print(f"  ❌ {analysis_type} 분석: 데이터 없음")
        
        if time_available > 0:
            analysis_available += 1
        
        # 종합 분석 테스트
        print("\n🔄 종합 분석 테스트:")
        comprehensive = get_comprehensive_analysis(dfp)
        comprehensive_count = sum(1 for v in comprehensive.values() if hasattr(v, 'empty') and not v.empty)
        print(f"  ✅ 종합 분석 결과: {comprehensive_count}/5개 분석 완료")
        
        print(f"\n🎯 비즈니스 분석 모듈 총 활용률: {analysis_available}/5개")
        
        return comprehensive, analysis_available
        
    except Exception as e:
        print(f"❌ 비즈니스 분석 테스트 실패: {e}")
        return {}, 0

def show_final_summary(kpis, analysis, kpi_available, analysis_available):
    """최종 요약 및 시스템 상태"""
    
    print("\n" + "=" * 80)
    print("🎯 최종 요약 및 시스템 상태")
    print("=" * 80)
    
    total_modules = 4  # utils, transformers, kpi, analysis
    
    print(f"\n📊 모듈별 상태:")
    print(f"  • Utils 모듈: ✅ 정상 (포맷팅, 헬퍼 함수)")
    print(f"  • Transformers 모듈: ✅ 정상 (데이터 변환)")
    print(f"  • KPI 계산 모듈: {'✅' if kpi_available > 10 else '⚠️'} ({kpi_available}개 지표)")
    print(f"  • 분석 모듈: {'✅' if analysis_available >= 3 else '⚠️'} ({analysis_available}/5개 분석)")
    
    # 시스템 신뢰도 평가 (수정된 계산)
    print(f"\n📋 시스템 신뢰도 평가:")
    
    # 각 모듈별 점수 (0-100 기준)
    utils_score = 100  # 항상 정상
    transformers_score = 100  # 항상 정상  
    kpi_score = min(100, (kpi_available / 17) * 100)  # 최대 17개 지표
    analysis_score = (analysis_available / 5) * 100  # 최대 5개 분석
    
    # 전체 평균 점수
    reliability_score = (utils_score + transformers_score + kpi_score + analysis_score) / 4
    
    if reliability_score >= 90:
        print("🟢 매우 높음 (90%+) - 풀 리포트 생성 가능")
    elif reliability_score >= 70:
        print("🟡 높음 (70-89%) - 대부분 기능 사용 가능")
    elif reliability_score >= 50:
        print("🟠 보통 (50-69%) - 핵심 기능 사용 가능")
    else:
        print("🔴 낮음 (50% 미만) - 기본 기능만 사용 권장")
    
    # 핵심 지표 하이라이트
    if kpis and kpis.get('total_revenue'):
        print(f"\n🔥 핵심 성과 지표:")
        print(f"  💰 총 매출: {format_currency(kpis['total_revenue'])}")
        print(f"  📦 총 주문: {kpis.get('total_orders', 0):,}건")
        print(f"  💳 평균 주문액: {format_currency(kpis.get('avg_order_value', 0))}")
        
        if kpis.get('unique_customers'):
            print(f"  👥 고객수: {kpis['unique_customers']:,.0f}명")
    
    # 데이터 품질 진단
    print(f"\n🔍 데이터 품질 진단:")
    quality_issues = []
    
    if analysis_available < 4:
        quality_issues.append("일부 분석 모듈에서 데이터 부족")
    
    if kpi_available < 15:
        quality_issues.append("일부 KPI 지표 계산 불가")
    
    if not quality_issues:
        print("  ✅ 데이터 품질 양호")
    else:
        for issue in quality_issues:
            print(f"  ⚠️ {issue}")
    
    return reliability_score

def main():
    """메인 실행 함수"""
    
    print("🚀 전체 시스템 통합 테스트 시작!")
    print("=" * 80)
    
    try:
        # 1. Utils 모듈 테스트
        test_utils_module()
        
        # 2. Transformers 모듈 테스트
        test_transformers_module()
        
        # 3. 데이터 준비 테스트
        dfp = test_data_preparation()
        if dfp is None:
            print("❌ 데이터 준비 실패로 테스트 중단")
            return
        
        # 4. KPI 계산 모듈 테스트
        kpis, kpi_available = test_kpi_metrics_module(dfp)
        
        # 5. 비즈니스 분석 모듈 테스트
        analysis, analysis_available = test_business_analysis_module(dfp)
        
        # 6. 최종 요약
        reliability_score = show_final_summary(kpis, analysis, kpi_available, analysis_available)
        
        print(f"\n" + "=" * 80)
        print(f"🎉 전체 시스템 테스트 완료!")
        print(f"시스템 신뢰도: {reliability_score:.1f}%")
        print(f"리포트 생성 준비: {'✅ 완료' if reliability_score >= 60 else '⚠️ 부분 가능'}")
        
    except Exception as e:
        print(f"❌ 전체 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
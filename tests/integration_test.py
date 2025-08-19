#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import math
from pathlib import Path
from config import CONFIG
from file_manager import load_excel_data
from constants import *

# 개별 모듈별 import (관계 명확화)
from data_processing import prepare_dataframe, slice_by_seller

# KPI 계산 모듈 (kpi_metrics.py)
from data_processing import calculate_comprehensive_kpis, calculate_kpis

# 비즈니스 분석 모듈 (business_analysis.py)  
from data_processing import (
    get_channel_analysis, get_product_analysis, get_category_analysis,
    get_region_analysis, get_time_analysis, get_comprehensive_analysis
)

from utils import format_currency, pct

def test_data_preparation():
    """1단계: 데이터 준비 및 전처리 테스트"""
    
    print("=" * 80)
    print("🔧 1단계: 데이터 준비 및 전처리 테스트")
    print("=" * 80)
    
    # 데이터 로드
    df = load_excel_data(CONFIG["INPUT_XLSX"])
    print(f"📁 원본 데이터 로드: {len(df):,}건")
    
    # 컬럼 존재 여부 확인
    required_columns = [COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_SELLER, COL_CHANNEL]
    optional_columns = [COL_BUYER_NAME, COL_BUYER_PHONE, COL_ADDRESS, COL_CATEGORY, COL_STATUS]
    
    print("\n📋 필수 컬럼 확인:")
    for col in required_columns:
        exists = col in df.columns
        print(f"  {'✅' if exists else '❌'} {col}: {'있음' if exists else '없음'}")
    
    print("\n📋 선택 컬럼 확인:")
    for col in optional_columns:
        exists = col in df.columns
        if exists:
            data_count = df[col].notna().sum()
            print(f"  ✅ {col}: {data_count:,}건 ({data_count/len(df)*100:.1f}%)")
        else:
            print(f"  ❌ {col}: 없음")
    
    # 카테고리 컬럼 특별 확인
    print(f"\n🔍 카테고리 컬럼 상세 확인:")
    category_columns = [col for col in df.columns if '카테고리' in col]
    print(f"  카테고리 관련 컬럼들: {category_columns}")
    
    if category_columns:
        actual_category_col = category_columns[0]
        print(f"  실제 카테고리 컬럼: '{actual_category_col}'")
        print(f"  상수 정의된 컬럼: '{COL_CATEGORY}'")
        print(f"  일치 여부: {'✅' if actual_category_col == COL_CATEGORY else '❌'}")
        
        if actual_category_col in df.columns:
            category_data = df[actual_category_col].dropna()
            print(f"  카테고리 데이터: {len(category_data):,}건")
            print(f"  카테고리 종류: {category_data.nunique():,}개")
    
    # 데이터 전처리
    dfp = prepare_dataframe(df, None, None)
    print(f"\n🔄 전처리 완료: {len(dfp):,}건")
    
    # 생성된 파생 컬럼 확인
    derived_columns = ['__dt__', '__amount__', '__qty__', '__customer_id__', '__region__']
    print("\n🆕 파생 컬럼 생성 결과:")
    for col in derived_columns:
        if col in dfp.columns:
            valid_count = dfp[col].notna().sum()
            print(f"  ✅ {col}: {valid_count:,}건 ({valid_count/len(dfp)*100:.1f}%)")
        else:
            print(f"  ❌ {col}: 생성 안됨")
    
    return dfp

def test_kpi_metrics_module(dfp):
    """2단계: KPI 계산 모듈 (kpi_metrics.py) 개별 테스트"""
    
    print("\n" + "=" * 80)
    print("📊 2단계: KPI 계산 모듈 (kpi_metrics.py) 테스트")
    print("=" * 80)
    
    # KPI 계산
    kpis = calculate_comprehensive_kpis(dfp, dfp)
    
    print("\n🔢 개별 KPI 지표 검증:")
    
    # 그룹 1: 기본 매출 지표 (5개)
    print("\n📈 Group 1: 기본 매출 지표 (5개) - kpi_metrics.py")
    basic_kpi_metrics = {
        'total_orders': ('총 주문수', 'count'),
        'total_revenue': ('총 매출액', 'currency'), 
        'avg_order_value': ('평균 주문금액', 'currency'),
        'total_quantity': ('총 상품수량', 'count'),
        'avg_product_price': ('평균 상품가격', 'currency')
    }
    
    basic_available = 0
    for key, (name, format_type) in basic_kpi_metrics.items():
        value = kpis.get(key)
        if value is not None and not (isinstance(value, float) and math.isnan(value)):
            if format_type == 'currency':
                print(f"  ✅ {name}: {format_currency(value)}")
            else:
                print(f"  ✅ {name}: {value:,.0f}")
            basic_available += 1
        else:
            print(f"  ❌ {name}: 데이터 없음")
    
    print(f"  📊 기본 매출 지표 활용률: {basic_available}/5 ({basic_available/5*100:.0f}%)")
    
    # 그룹 2: 고객 행동 지표 (6개)
    print("\n👥 Group 2: 고객 행동 지표 (6개) - kpi_metrics.py")
    customer_kpi_metrics = {
        'unique_customers': ('총 고객수', 'count'),
        'repeat_customers': ('재구매 고객수', 'count'),
        'repeat_rate': ('재구매율', 'percent'),
        'avg_orders_per_customer': ('고객당 평균주문수', 'decimal'),
        'customer_ltv': ('고객 생애가치', 'currency')
    }
    
    customer_available = 0
    for key, (name, format_type) in customer_kpi_metrics.items():
        value = kpis.get(key)
        if value is not None and not (isinstance(value, float) and math.isnan(value)):
            if format_type == 'currency':
                print(f"  ✅ {name}: {format_currency(value)}")
            elif format_type == 'percent':
                print(f"  ✅ {name}: {pct(value)}")
            elif format_type == 'decimal':
                print(f"  ✅ {name}: {value:.1f}")
            else:
                print(f"  ✅ {name}: {value:,.0f}")
            customer_available += 1
        else:
            print(f"  ❌ {name}: 데이터 없음")
    
    # 신규 고객 비율 계산 (파생 지표)
    if kpis.get('unique_customers') and kpis.get('repeat_customers'):
        new_customers = kpis['unique_customers'] - kpis['repeat_customers']
        new_customer_rate = new_customers / kpis['unique_customers']
        print(f"  ✅ 신규 고객 비율: {pct(new_customer_rate)}")
        customer_available += 1
    else:
        print(f"  ❌ 신규 고객 비율: 데이터 없음")
    
    print(f"  📊 고객 행동 지표 활용률: {customer_available}/6 ({customer_available/6*100:.0f}%)")
    
    # 그룹 3: 주문 상태 지표 (5개)
    print("\n⚡ Group 3: 주문 상태 지표 (5개) - kpi_metrics.py")
    status_kpi_metrics = {
        'completion_rate': '배송완료율',
        'cancel_rate': '취소율',
        'delay_rate': '지연율', 
        'return_rate': '반품율',
        'exchange_rate': '교환율'
    }
    
    status_available = 0
    for key, name in status_kpi_metrics.items():
        value = kpis.get(key)
        if value is not None and not (isinstance(value, float) and math.isnan(value)):
            print(f"  ✅ {name}: {pct(value)}")
            status_available += 1
        else:
            print(f"  ❌ {name}: 데이터 없음")
    
    print(f"  📊 주문 상태 지표 활용률: {status_available}/5 ({status_available/5*100:.0f}%)")
    
    # 그룹 4: 운영 효율성 지표 (4개)
    print("\n🚚 Group 4: 운영 효율성 지표 (4개) - kpi_metrics.py")
    ops_kpi_metrics = {
        'avg_ship_leadtime': ('평균 출고시간', 'days'),
        'same_day_ship_rate': ('당일출고율', 'percent'),
        'avg_delivery_time': ('평균 배송시간', 'days')
    }
    
    ops_available = 0
    for key, (name, format_type) in ops_kpi_metrics.items():
        value = kpis.get(key)
        if value is not None and not (isinstance(value, float) and math.isnan(value)):
            if format_type == 'percent':
                print(f"  ✅ {name}: {pct(value)}")
            else:
                print(f"  ✅ {name}: {value:.1f}일")
            ops_available += 1
        else:
            print(f"  ❌ {name}: 데이터 없음")
    
    # 전체 배송시간 계산 (파생 지표)
    if '발송처리일' in dfp.columns and '배송완료일' in dfp.columns:
        delivery_data = dfp[dfp['발송처리일'].notna() & dfp['배송완료일'].notna()].copy()
        if not delivery_data.empty:
            from utils import to_datetime_safe
            delivery_data['ship_dt'] = to_datetime_safe(delivery_data['발송처리일'])
            delivery_data['delivery_dt'] = to_datetime_safe(delivery_data['배송완료일'])
            total_delivery_time = (delivery_data['delivery_dt'] - delivery_data['__dt__']).dt.total_seconds() / 86400.0
            avg_total_delivery = total_delivery_time.mean()
            print(f"  ✅ 전체 배송시간 (주문→완료): {avg_total_delivery:.1f}일")
            ops_available += 1
        else:
            print(f"  ❌ 전체 배송시간: 데이터 없음")
    else:
        print(f"  ❌ 전체 배송시간: 필요 컬럼 없음")
    
    print(f"  📊 운영 효율성 지표 활용률: {ops_available}/4 ({ops_available/4*100:.0f}%)")
    
    # 그룹 5: 벤치마킹 지표 (2개)
    print("\n📊 Group 5: 벤치마킹 지표 (2개) - kpi_metrics.py")
    benchmark_kpi_metrics = {
        'benchmark_aov': ('전체 평균 AOV', 'currency'),
        'benchmark_cancel_rate': ('전체 평균 취소율', 'percent')
    }
    
    benchmark_available = 0
    for key, (name, format_type) in benchmark_kpi_metrics.items():
        value = kpis.get(key)
        if value is not None and not (isinstance(value, float) and math.isnan(value)):
            if format_type == 'currency':
                print(f"  ✅ {name}: {format_currency(value)}")
            else:
                print(f"  ✅ {name}: {pct(value)}")
            benchmark_available += 1
        else:
            print(f"  ❌ {name}: 데이터 없음")
    
    print(f"  📊 벤치마킹 지표 활용률: {benchmark_available}/2 ({benchmark_available/2*100:.0f}%)")
    
    total_kpi_available = basic_available + customer_available + status_available + ops_available + benchmark_available
    print(f"\n🎯 KPI 모듈 총 활용률: {total_kpi_available}/22 ({total_kpi_available/22*100:.0f}%)")
    
    return kpis, total_kpi_available

def test_business_analysis_module(dfp):
    """3단계: 비즈니스 분석 모듈 (business_analysis.py) 개별 테스트"""
    
    print("\n" + "=" * 80)
    print("🏢 3단계: 비즈니스 분석 모듈 (business_analysis.py) 테스트")
    print("=" * 80)
    
    analysis_available = 0
    
    # 채널 분석 (5개 지표)
    print("\n🛒 채널 분석 (5개 지표) - business_analysis.py")
    channel_analysis = get_channel_analysis(dfp)
    
    if not channel_analysis.empty:
        print(f"  ✅ 채널별 주문수: {len(channel_analysis)}개 채널")
        print(f"  ✅ 채널별 매출액: 분석 완료")
        print(f"  ✅ 채널별 AOV: 분석 완료")
        print(f"  ✅ 채널별 취소율: 분석 완료")
        
        # 채널 집중도 계산
        total_revenue = channel_analysis['revenue'].sum()
        top3_revenue = channel_analysis.head(3)['revenue'].sum()
        concentration = top3_revenue / total_revenue
        print(f"  ✅ 채널 집중도 (상위3개): {pct(concentration)}")
        
        # 상위 3개 채널 표시
        print("    상위 3개 채널:")
        for idx, (channel, row) in enumerate(channel_analysis.head(3).iterrows(), 1):
            print(f"      {idx}. {channel}: {format_currency(row['revenue'])} ({pct(row['revenue_share'])})")
        
        analysis_available += 5
    else:
        print(f"  ❌ 채널 분석: 데이터 없음")
    
    # 상품 분석 (5개 지표)
    print("\n📦 상품 분석 (5개 지표) - business_analysis.py")
    product_analysis = get_product_analysis(dfp)
    
    if not product_analysis.empty:
        print(f"  ✅ 상품별 주문수: {len(product_analysis)}개 상품")
        print(f"  ✅ 상품별 매출액: 분석 완료")
        print(f"  ✅ 상품별 AOV: 분석 완료")
        print(f"  ✅ 상품별 취소율: 분석 완료")
        print(f"  ✅ 베스트셀러 순위: TOP {len(product_analysis)}")
        
        # 상위 3개 상품 표시
        print("    상위 3개 상품:")
        for idx, row in product_analysis.head(3).iterrows():
            product_name = row['상품명'][:30] + "..." if len(row['상품명']) > 30 else row['상품명']
            print(f"      {idx+1}. {product_name}")
            print(f"         매출: {format_currency(row['revenue'])}")
        
        analysis_available += 5
    else:
        print(f"  ❌ 상품 분석: 데이터 없음")
    
    # 카테고리 분석 (5개 지표) - 특별 진단
    print("\n📂 카테고리 분석 (5개 지표) - business_analysis.py")
    
    # 카테고리 컬럼 진단
    category_columns = [col for col in dfp.columns if '카테고리' in col]
    print(f"  🔍 카테고리 컬럼 탐지: {category_columns}")
    
    if category_columns:
        actual_category_col = category_columns[0]
        print(f"  📋 실제 사용 컬럼: '{actual_category_col}'")
        print(f"  📋 상수 정의 컬럼: '{COL_CATEGORY}'")
        
        # 실제 카테고리 데이터 확인
        if actual_category_col in dfp.columns:
            category_data_count = dfp[actual_category_col].notna().sum()
            category_unique_count = dfp[actual_category_col].nunique()
            print(f"  📊 카테고리 데이터: {category_data_count:,}건")
            print(f"  📊 카테고리 종류: {category_unique_count:,}개")
            
            # 샘플 카테고리 값들
            sample_categories = dfp[actual_category_col].dropna().head(5).tolist()
            print(f"  📋 샘플 카테고리: {sample_categories}")
    
    category_analysis = get_category_analysis(dfp)
    
    if not category_analysis.empty:
        print(f"  ✅ 카테고리별 주문수: {len(category_analysis)}개 카테고리")
        print(f"  ✅ 카테고리별 매출액: 분석 완료")
        print(f"  ✅ 카테고리별 AOV: 분석 완료")
        print(f"  ✅ 카테고리별 점유율: 분석 완료")
        
        # 카테고리 집중도
        top3_cat_revenue = category_analysis.head(3)['revenue'].sum()
        total_cat_revenue = category_analysis['revenue'].sum()
        cat_concentration = top3_cat_revenue / total_cat_revenue
        print(f"  ✅ 카테고리 집중도 (상위3개): {pct(cat_concentration)}")
        
        # 상위 3개 카테고리 표시
        print("    상위 3개 카테고리:")
        for idx, (category, row) in enumerate(category_analysis.head(3).iterrows(), 1):
            print(f"      {idx}. {category}: {format_currency(row['revenue'])} ({pct(row['revenue_share'])})")
        
        analysis_available += 5
    else:
        print(f"  ❌ 카테고리 분석: 데이터 없음")
        if category_columns:
            print(f"  🔧 문제: COL_CATEGORY 상수와 실제 컬럼명 불일치 가능성")
            print(f"       constants.py에서 COL_CATEGORY = '{category_columns[0]}'로 수정 필요")
    
    # 지역 분석 (5개 지표)
    print("\n🌍 지역 분석 (5개 지표) - business_analysis.py")
    region_analysis = get_region_analysis(dfp)
    
    if not region_analysis.empty:
        print(f"  ✅ 지역별 주문수: {len(region_analysis)}개 지역")
        print(f"  ✅ 지역별 매출액: 분석 완료")
        print(f"  ✅ 지역별 AOV: 분석 완료")
        print(f"  ✅ 지역별 점유율: 분석 완료")
        
        # 지역 집중도
        top3_region_revenue = region_analysis.head(3)['revenue'].sum()
        total_region_revenue = region_analysis['revenue'].sum()
        region_concentration = top3_region_revenue / total_region_revenue
        print(f"  ✅ 지역 집중도 (상위3개): {pct(region_concentration)}")
        
        # 상위 3개 지역 표시
        print("    상위 3개 지역:")
        for idx, (region, row) in enumerate(region_analysis.head(3).iterrows(), 1):
            print(f"      {idx}. {region}: {format_currency(row['revenue'])} ({pct(row['revenue_share'])})")
        
        analysis_available += 5
    else:
        print(f"  ❌ 지역 분석: 데이터 없음")
    
    # 시간 분석 (3개 지표)
    print("\n📅 시간 분석 (3개 지표) - business_analysis.py")
    time_analysis = get_time_analysis(dfp)
    
    time_available = 0
    if time_analysis:
        if 'daily' in time_analysis and not time_analysis['daily'].empty:
            daily_count = len(time_analysis['daily'])
            print(f"  ✅ 일별 매출 트렌드: {daily_count}일간")
            time_available += 1
        else:
            print(f"  ❌ 일별 매출 트렌드: 데이터 없음")
        
        if 'hourly' in time_analysis and not time_analysis['hourly'].empty:
            hourly_count = len(time_analysis['hourly'])
            print(f"  ✅ 시간대별 주문 패턴: {hourly_count}시간대")
            time_available += 1
        else:
            print(f"  ❌ 시간대별 주문 패턴: 데이터 없음")
        
        if 'weekly' in time_analysis and not time_analysis['weekly'].empty:
            weekly_count = len(time_analysis['weekly'])
            print(f"  ✅ 요일별 주문 패턴: {weekly_count}요일")
            time_available += 1
        else:
            print(f"  ❌ 요일별 주문 패턴: 데이터 없음")
    else:
        print(f"  ❌ 시간 분석: 데이터 없음")
    
    analysis_available += time_available
    
    print(f"\n🎯 비즈니스 분석 모듈 총 활용률: {analysis_available}/23 ({analysis_available/23*100:.0f}%)")
    
    return {
        'channel_analysis': channel_analysis,
        'product_analysis': product_analysis,
        'category_analysis': category_analysis,
        'region_analysis': region_analysis,
        'time_analysis': time_analysis
    }, analysis_available

def show_final_summary(kpis, analysis, kpi_available, analysis_available):
    """최종 요약 및 권장사항"""
    
    print("\n" + "=" * 80)
    print("🎯 최종 요약 및 권장사항")
    print("=" * 80)
    
    total_available = kpi_available + analysis_available
    total_metrics = 45
    
    print(f"\n📊 전체 지표 활용 현황:")
    print(f"  • KPI 계산 모듈 (kpi_metrics.py): {kpi_available}/22개 ({kpi_available/22*100:.0f}%)")
    print(f"  • 비즈니스 분석 모듈 (business_analysis.py): {analysis_available}/23개 ({analysis_available/23*100:.0f}%)")
    print(f"  • 전체 활용 지표: {total_available}/{total_metrics}개 ({total_available/total_metrics*100:.0f}%)")
    
    # 신뢰도 평가
    print(f"\n📋 시스템 신뢰도 평가:")
    if total_available >= 40:
        print("🟢 매우 높음 (40개+ 지표) - 3페이지 풀 리포트 구성 가능")
    elif total_available >= 30:
        print("🟡 높음 (30-39개 지표) - 2-3페이지 리포트 구성 가능")
    elif total_available >= 20:
        print("🟠 보통 (20-29개 지표) - 2페이지 핵심 리포트 권장")
    else:
        print("🔴 낮음 (20개 미만) - 1페이지 요약 리포트만 권장")
    
    # 핵심 지표 하이라이트
    print(f"\n🔥 핵심 지표 하이라이트:")
    if kpis.get('total_revenue') and kpis.get('total_orders'):
        print(f"  💰 총 매출: {format_currency(kpis['total_revenue'])} ({kpis['total_orders']:,}건)")
        print(f"  💳 평균 주문액: {format_currency(kpis.get('avg_order_value', 0))}")
    
    if kpis.get('unique_customers') and kpis.get('repeat_rate'):
        print(f"  👥 총 고객: {kpis['unique_customers']:,.0f}명 (재구매율 {pct(kpis['repeat_rate'])})")
    
    if 'channel_analysis' in analysis and not analysis['channel_analysis'].empty:
        top_channel = analysis['channel_analysis'].index[0]
        top_share = analysis['channel_analysis'].iloc[0]['revenue_share']
        print(f"  🛒 최대 채널: {top_channel} ({pct(top_share)})")

def main():
    """메인 실행 함수"""
    
    try:
        # 1단계: 데이터 준비
        dfp = test_data_preparation()
        
        # 2단계: KPI 계산 모듈 테스트
        kpis, kpi_available = test_kpi_metrics_module(dfp)
        
        # 3단계: 비즈니스 분석 모듈 테스트
        analysis, analysis_available = test_business_analysis_module(dfp)
        
        # 최종 요약
        show_final_summary(kpis, analysis, kpi_available, analysis_available)
        
        print(f"\n🎉 완전 통합 테스트 완료!")
        print(f"각 모듈의 역할과 지표 사용이 명확히 구분되었습니다.")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
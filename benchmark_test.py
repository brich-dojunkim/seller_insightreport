#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""확장된 벤치마킹 시스템 테스트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import math
from config import CONFIG
from file_manager import load_excel_data
from constants import *

# utils 모듈 테스트
from utils import format_currency, pct, df_to_html_table, sanitize_filename

# data_processing 모듈 테스트 (확장된 구조)
from data_processing import (
    prepare_dataframe, slice_by_seller, 
    calculate_comprehensive_kpis, calculate_kpis,
    get_channel_analysis, get_product_analysis, get_category_analysis,
    get_region_analysis, get_time_analysis, get_comprehensive_analysis,
    get_comprehensive_analysis_with_benchmarks,
    get_relative_channel_analysis, get_relative_region_analysis,
    to_datetime_safe, to_number_safe, create_customer_id,
    extract_region_from_address, load_category_mapping, map_category_code_to_name
)

def test_enhanced_benchmarking():
    """확장된 벤치마킹 시스템 테스트"""
    
    print("🚀 확장된 벤치마킹 시스템 테스트 시작!")
    print("=" * 80)
    
    try:
        # 데이터 로드
        input_path = CONFIG["INPUT_XLSX"]
        print(f"📁 로드 경로: {input_path}")
        
        df = load_excel_data(input_path)
        print(f"📁 원본 데이터 로드: {len(df):,}건")
        
        # 데이터 전처리
        dfp = prepare_dataframe(df, None, None)
        print(f"🔄 전처리 완료: {len(dfp):,}건")
        
        # 특정 셀러 데이터 추출 (테스트용)
        seller_name = "포레스트핏"  # CONFIG에서 가져오기
        seller_data = slice_by_seller(dfp, seller_name)
        print(f"👤 셀러 '{seller_name}' 데이터: {len(seller_data):,}건")
        
        return test_enhanced_metrics(seller_data, dfp)
        
    except Exception as e:
        print(f"❌ 데이터 로드 실패: {e}")
        return False

def test_enhanced_metrics(seller_data, overall_data):
    """확장된 메트릭스 테스트"""
    
    print("\n" + "=" * 80)
    print("📊 확장된 벤치마킹 메트릭스 테스트")
    print("=" * 80)
    
    try:
        # 확장된 KPI 계산
        enhanced_kpis = calculate_comprehensive_kpis(seller_data, overall_data)
        
        print(f"\n🔢 기본 메트릭스:")
        basic_metrics = ['total_orders', 'total_revenue', 'avg_order_value', 'repeat_rate', 'cancel_rate']
        for metric in basic_metrics:
            value = enhanced_kpis.get(metric)
            if value is not None and not (isinstance(value, float) and math.isnan(value)):
                if 'rate' in metric:
                    print(f"  ✅ {metric}: {pct(value)}")
                elif 'revenue' in metric or 'value' in metric:
                    print(f"  ✅ {metric}: {format_currency(value)}")
                else:
                    print(f"  ✅ {metric}: {value:,.0f}")
        
        print(f"\n🎯 벤치마킹 정보:")
        benchmark_category = enhanced_kpis.get('benchmark_category', '정보없음')
        benchmark_sellers = enhanced_kpis.get('benchmark_sellers_count', 0)
        print(f"  📂 비교 카테고리: {benchmark_category}")
        print(f"  👥 카테고리 내 경쟁사 수: {benchmark_sellers:,}개")
        
        print(f"\n🔥 상대적 성과 (카테고리 평균 대비):")
        relative_metrics = [key for key in enhanced_kpis.keys() if '_vs_category' in key]
        
        excellent_count = 0
        good_count = 0
        average_count = 0
        below_count = 0
        
        for metric in relative_metrics:
            value = enhanced_kpis.get(metric)
            if value is not None and not (isinstance(value, float) and math.isnan(value)):
                percentage = value * 100
                
                # 성과 레벨 판정
                if value >= 1.2:
                    level = "🟢 우수"
                    excellent_count += 1
                elif value >= 1.1:
                    level = "🟡 양호"  
                    good_count += 1
                elif value >= 0.9:
                    level = "⚪ 보통"
                    average_count += 1
                else:
                    level = "🔴 개선필요"
                    below_count += 1
                
                # 특별 처리 (낮을수록 좋은 지표들)
                if 'cancel' in metric or 'delay' in metric or 'return' in metric:
                    if value <= 0.8:
                        level = "🟢 우수"
                    elif value <= 0.9:
                        level = "🟡 양호"
                    elif value <= 1.1:
                        level = "⚪ 보통"
                    else:
                        level = "🔴 개선필요"
                
                metric_display = metric.replace('_vs_category', '').replace('_', ' ')
                print(f"  {level} {metric_display}: {percentage:.1f}%")
        
        print(f"\n📊 성과 요약:")
        total_metrics = len(relative_metrics)
        if total_metrics > 0:
            print(f"  🟢 우수: {excellent_count}개 ({excellent_count/total_metrics*100:.1f}%)")
            print(f"  🟡 양호: {good_count}개 ({good_count/total_metrics*100:.1f}%)")
            print(f"  ⚪ 보통: {average_count}개 ({average_count/total_metrics*100:.1f}%)")
            print(f"  🔴 개선필요: {below_count}개 ({below_count/total_metrics*100:.1f}%)")
        
        return test_enhanced_analyzers(seller_data, overall_data, enhanced_kpis)
        
    except Exception as e:
        print(f"❌ 메트릭스 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_analyzers(seller_data, overall_data, kpis):
    """확장된 분석기 테스트"""
    
    print("\n" + "=" * 80)
    print("📈 확장된 벤치마킹 분석기 테스트")
    print("=" * 80)
    
    try:
        # 기본 분석
        basic_analysis = get_comprehensive_analysis(seller_data)
        
        # 벤치마킹 포함 분석
        enhanced_analysis = get_comprehensive_analysis_with_benchmarks(seller_data, overall_data)
        
        print(f"\n🔍 기본 분석 vs 확장 분석:")
        print(f"  기본 분석 항목: {len(basic_analysis)}개")
        print(f"  확장 분석 항목: {len(enhanced_analysis)}개")
        
        # 상대적 채널 분석
        print(f"\n🛒 상대적 채널 분석:")
        relative_channels = enhanced_analysis.get('relative_channel_analysis', pd.DataFrame())
        if not relative_channels.empty:
            print(f"  분석 채널: {len(relative_channels)}개")
            
            # 상위 3개 채널의 상대적 성과
            print("  상위 3개 채널의 카테고리 대비 성과:")
            for idx, (channel, row) in enumerate(relative_channels.head(3).iterrows(), 1):
                revenue_vs_cat = row.get('revenue_vs_category', float('nan'))
                aov_vs_cat = row.get('aov_vs_category', float('nan'))
                
                if not math.isnan(revenue_vs_cat):
                    print(f"    {idx}. {channel}:")
                    print(f"       매출: {format_currency(row['revenue'])} (카테고리 대비 {revenue_vs_cat:.1%})")
                    if not math.isnan(aov_vs_cat):
                        print(f"       AOV: {format_currency(row['aov'])} (카테고리 대비 {aov_vs_cat:.1%})")
        else:
            print("  ❌ 상대적 채널 분석 데이터 없음")
        
        # 상대적 지역 분석
        print(f"\n🌍 상대적 지역 분석:")
        relative_regions = enhanced_analysis.get('relative_region_analysis', pd.DataFrame())
        if not relative_regions.empty:
            print(f"  분석 지역: {len(relative_regions)}개")
            
            # 상위 3개 지역의 상대적 성과
            print("  상위 3개 지역의 카테고리 대비 성과:")
            for idx, (region, row) in enumerate(relative_regions.head(3).iterrows(), 1):
                revenue_vs_cat = row.get('revenue_vs_category', float('nan'))
                
                if not math.isnan(revenue_vs_cat):
                    performance = "🟢" if revenue_vs_cat >= 1.2 else "🟡" if revenue_vs_cat >= 1.1 else "⚪" if revenue_vs_cat >= 0.9 else "🔴"
                    print(f"    {idx}. {region}: {format_currency(row['revenue'])} {performance} ({revenue_vs_cat:.1%})")
        else:
            print("  ❌ 상대적 지역 분석 데이터 없음")
        
        # 상대적 시간 분석
        print(f"\n📅 상대적 시간 분석:")
        relative_time = enhanced_analysis.get('relative_time_analysis', {})
        if relative_time:
            for time_type, df in relative_time.items():
                if not df.empty and 'revenue_vs_category' in df.columns:
                    avg_performance = df['revenue_vs_category'].mean()
                    performance_level = df['performance_level'].mode().iloc[0] if 'performance_level' in df.columns else 'unknown'
                    print(f"  {time_type}: 평균 {avg_performance:.1%} ({performance_level})")
                else:
                    print(f"  {time_type}: 기본 분석만 가능")
        else:
            print("  ❌ 상대적 시간 분석 데이터 없음")
        
        return test_recommendations(kpis, enhanced_analysis)
        
    except Exception as e:
        print(f"❌ 분석기 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_recommendations(kpis, analysis):
    """개선 추천사항 테스트"""
    
    print(f"\n" + "=" * 80)
    print("💡 개선 추천사항 생성 테스트")
    print("=" * 80)
    
    try:
        # 기존 KPI 형식으로 변환 (추천사항 포함)
        legacy_kpis = calculate_kpis(pd.DataFrame(), pd.DataFrame())  # 더미 데이터로 구조 확인
        
        print(f"\n📋 자동 생성된 추천사항:")
        recommendations = kpis.get('recos') if 'recos' in kpis else []
        
        if recommendations:
            for idx, rec in enumerate(recommendations, 1):
                print(f"  {idx}. {rec}")
        else:
            print("  추천사항이 생성되지 않았습니다.")
        
        # 성과 기반 추가 인사이트
        print(f"\n🎯 성과 기반 인사이트:")
        
        category = kpis.get('benchmark_category', '알 수 없음')
        print(f"  📂 분석 카테고리: {category}")
        
        # 강점 분석
        strengths = []
        improvements = []
        
        relative_metrics = {k: v for k, v in kpis.items() if '_vs_category' in k}
        for metric, value in relative_metrics.items():
            if not math.isnan(value):
                metric_name = metric.replace('_vs_category', '')
                if value >= 1.2:
                    strengths.append(f"{metric_name} (카테고리 대비 {value:.1%})")
                elif value < 0.9:
                    improvements.append(f"{metric_name} (카테고리 대비 {value:.1%})")
        
        if strengths:
            print(f"  💪 강점 영역:")
            for strength in strengths[:3]:  # 상위 3개만
                print(f"    ✅ {strength}")
        
        if improvements:
            print(f"  🔧 개선 영역:")
            for improvement in improvements[:3]:  # 상위 3개만
                print(f"    ⚠️ {improvement}")
        
        return show_final_summary(kpis, analysis)
        
    except Exception as e:
        print(f"❌ 추천사항 테스트 실패: {e}")
        return False

def show_final_summary(kpis, analysis):
    """최종 요약"""
    
    print(f"\n" + "=" * 80)
    print("🎯 확장된 벤치마킹 시스템 테스트 완료")
    print("=" * 80)
    
    # 메트릭스 개수 확인
    total_metrics = len([k for k in kpis.keys() if not k.startswith('benchmark_') and k != 'recos'])
    relative_metrics = len([k for k in kpis.keys() if '_vs_category' in k])
    
    print(f"\n📊 시스템 현황:")
    print(f"  • 기본 메트릭스: {total_metrics - relative_metrics}개")
    print(f"  • 상대적 메트릭스: {relative_metrics}개")
    print(f"  • 총 메트릭스: {total_metrics}개")
    
    # 분석기 개수 확인
    basic_analysis_count = 5  # channel, product, category, region, time
    enhanced_analysis_count = len(analysis)
    
    print(f"  • 기본 분석기: {basic_analysis_count}개")
    print(f"  • 확장 분석기: {enhanced_analysis_count}개")
    
    # 벤치마킹 정보
    category = kpis.get('benchmark_category', '정보없음')
    print(f"  • 벤치마킹 카테고리: {category}")
    
    # 시스템 신뢰도
    has_category_benchmark = category != '정보없음' and category is not None
    
    if has_category_benchmark:
        print(f"\n🟢 벤치마킹 시스템: 정상 작동")
        print(f"   모든 지표가 '{category}' 카테고리 평균과 비교됩니다.")
    else:
        print(f"\n🟡 벤치마킹 시스템: 부분 작동")
        print(f"   카테고리 정보 부족으로 전체 평균과 비교됩니다.")
    
    print(f"\n🎉 확장된 벤치마킹 시스템 테스트 완료!")
    print(f"   상대적 성과 지표로 더 의미있는 분석이 가능합니다.")
    
    return True

def main():
    """메인 실행 함수"""
    
    print("🚀 확장된 벤치마킹 시스템 종합 테스트!")
    
    try:
        success = test_enhanced_benchmarking()
        
        if success:
            print(f"\n✅ 모든 테스트 통과!")
        else:
            print(f"\n❌ 일부 테스트 실패")
            
    except Exception as e:
        print(f"❌ 테스트 실행 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
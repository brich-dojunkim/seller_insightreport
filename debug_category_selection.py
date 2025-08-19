#!/usr/bin/env python3
"""카테고리 선택 로직 디버깅 - 모든 셀러 대응"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from config import CONFIG
from file_manager import load_excel_data
from data_processing import prepare_dataframe, slice_by_seller
from utils import format_currency

def get_available_sellers(overall_data):
    """전체 데이터에서 사용 가능한 셀러 목록 반환"""
    if '입점사명' in overall_data.columns:
        sellers = overall_data['입점사명'].value_counts()
        return sellers.to_dict()
    return {}

def debug_category_selection(seller_name=None):
    """카테고리 선택 로직 디버깅"""
    
    print("🔍 카테고리 자동 선택 로직 분석")
    print("=" * 60)
    
    # 데이터 로드
    df = load_excel_data(CONFIG["INPUT_XLSX"])
    dfp = prepare_dataframe(df, None, None)
    
    # 사용 가능한 셀러 목록 확인
    available_sellers = get_available_sellers(dfp)
    
    if not seller_name:
        print("📋 사용 가능한 셀러 목록 (주문수 순):")
        for idx, (seller, count) in enumerate(list(available_sellers.items())[:20], 1):
            print(f"  {idx:2d}. {seller}: {count:,}건")
        
        if len(available_sellers) > 20:
            print(f"  ... 외 {len(available_sellers) - 20}개 셀러")
        
        # 기본값 설정
        seller_name = CONFIG.get("SELLERS", ["포레스트핏"])[0] if CONFIG.get("SELLERS") else list(available_sellers.keys())[0]
        print(f"\n🎯 분석 대상 셀러: {seller_name} (기본값)")
    else:
        if seller_name not in available_sellers:
            print(f"❌ 셀러 '{seller_name}'를 찾을 수 없습니다.")
            print(f"사용 가능한 셀러: {list(available_sellers.keys())[:10]}...")
            return None
        
        print(f"🎯 분석 대상 셀러: {seller_name}")
    
    try:
        seller_data = slice_by_seller(dfp, seller_name)
        print(f"📊 {seller_name} 데이터: {len(seller_data):,}건 (전체의 {len(seller_data)/len(dfp)*100:.1f}%)")
    except ValueError as e:
        print(f"❌ 데이터 추출 실패: {e}")
        return None
    
    # 카테고리별 매출 분석
    if '__category_mapped__' in seller_data.columns:
        print(f"\n📂 {seller_name}의 카테고리별 매출 분석:")
        category_revenue = seller_data.groupby('__category_mapped__')['__amount__'].agg(['count', 'sum']).round(0)
        category_revenue.columns = ['주문수', '매출액']
        category_revenue = category_revenue.sort_values('매출액', ascending=False)
        
        print(f"총 {len(category_revenue)}개 카테고리:")
        
        for idx, (category, row) in enumerate(category_revenue.head(10).iterrows(), 1):
            percentage = (row['매출액'] / seller_data['__amount__'].sum()) * 100
            print(f"  {idx}. {category}")
            print(f"     주문: {row['주문수']:,.0f}건, 매출: {format_currency(row['매출액'])} ({percentage:.1f}%)")
        
        if len(category_revenue) > 10:
            print(f"  ... 외 {len(category_revenue) - 10}개 카테고리")
        
        # 1위 카테고리 확인
        top_category = category_revenue.index[0]
        top_revenue_share = (category_revenue.iloc[0]['매출액'] / seller_data['__amount__'].sum()) * 100
        
        print(f"\n🎯 자동 선택된 비교 카테고리:")
        print(f"   📂 {top_category}")
        print(f"   💰 전체 매출의 {top_revenue_share:.1f}% 차지")
        
        return top_category, seller_name, dfp
    else:
        print("❌ 카테고리 정보 없음")
        return None

def analyze_category_competition(top_category, target_seller, overall_data):
    """선택된 카테고리 내 경쟁 현황 분석"""
    
    print(f"\n🏆 '{top_category}' 카테고리 경쟁 현황")
    print("=" * 80)
    
    if '__category_mapped__' in overall_data.columns:
        # 같은 카테고리 데이터 추출
        category_data = overall_data[overall_data['__category_mapped__'] == top_category]
        
        print(f"📊 카테고리 전체 현황:")
        print(f"  📦 전체 주문: {len(category_data):,}건")
        print(f"  💰 전체 매출: {format_currency(category_data['__amount__'].sum())}")
        print(f"  📅 기간: {category_data['__dt__'].min().strftime('%Y-%m-%d')} ~ {category_data['__dt__'].max().strftime('%Y-%m-%d')}")
        
        if '입점사명' in category_data.columns:
            # 셀러별 성과
            seller_performance = category_data.groupby('입점사명')['__amount__'].agg(['count', 'sum']).round(0)
            seller_performance.columns = ['주문수', '매출액']
            seller_performance = seller_performance.sort_values('매출액', ascending=False)
            
            total_category_revenue = category_data['__amount__'].sum()
            
            print(f"\n👥 카테고리 내 셀러 순위:")
            print(f"  총 {len(seller_performance)}개 셀러")
            
            target_found = False
            for idx, (seller, row) in enumerate(seller_performance.head(15).iterrows(), 1):
                if seller == target_seller:
                    marker = "🎯 (분석 대상)"
                    target_found = True
                else:
                    marker = ""
                    
                market_share = (row['매출액'] / total_category_revenue) * 100
                print(f"    {idx:2d}. {seller} {marker}")
                print(f"        주문: {row['주문수']:,}건, 매출: {format_currency(row['매출액'])} ({market_share:.1f}%)")
            
            if not target_found and target_seller in seller_performance.index:
                target_rank = seller_performance.index.get_loc(target_seller) + 1
                target_row = seller_performance.loc[target_seller]
                target_share = (target_row['매출액'] / total_category_revenue) * 100
                print(f"    ...")
                print(f"    {target_rank:2d}. {target_seller} 🎯 (분석 대상)")
                print(f"        주문: {target_row['주문수']:,}건, 매출: {format_currency(target_row['매출액'])} ({target_share:.1f}%)")
            
            if len(seller_performance) > 15:
                print(f"    ... 외 {len(seller_performance) - 15}개 셀러")
        
        # 분석 대상 셀러 상세 정보
        if '입점사명' in category_data.columns and target_seller in seller_performance.index:
            my_rank = seller_performance.index.get_loc(target_seller) + 1
            total_sellers = len(seller_performance)
            my_revenue = seller_performance.loc[target_seller, '매출액']
            my_share = (my_revenue / total_category_revenue) * 100
            
            print(f"\n🎯 {target_seller} 카테고리 내 위치:")
            print(f"  📍 순위: {my_rank}/{total_sellers} (상위 {(my_rank/total_sellers)*100:.1f}%)")
            print(f"  📊 시장 점유율: {my_share:.1f}%")
            
            # 경쟁 강도 분석
            if my_rank == 1:
                competition_level = "🥇 카테고리 1위 (시장 리더)"
            elif my_rank <= 3:
                competition_level = "🥈 상위권 (주요 경쟁자)"
            elif my_rank <= total_sellers * 0.1:
                competition_level = "🔥 상위 10% (강한 경쟁자)"
            elif my_rank <= total_sellers * 0.3:
                competition_level = "💪 상위 30% (중간 경쟁자)"
            else:
                competition_level = "🌱 하위권 (성장 여지 큼)"
            
            print(f"  🏆 경쟁 위치: {competition_level}")
            
            # 1위와의 격차
            if my_rank > 1:
                leader_revenue = seller_performance.iloc[0]['매출액']
                gap = ((leader_revenue - my_revenue) / my_revenue) * 100
                print(f"  📈 1위와의 격차: {gap:.1f}% (1위 매출 대비)")

def analyze_sellers_by_category():
    """카테고리별 주요 셀러 분석"""
    
    print(f"\n📊 카테고리별 주요 셀러 현황")
    print("=" * 60)
    
    df = load_excel_data(CONFIG["INPUT_XLSX"])
    dfp = prepare_dataframe(df, None, None)
    
    if '__category_mapped__' in dfp.columns:
        # 카테고리별 매출 상위 10개
        category_revenue = dfp.groupby('__category_mapped__')['__amount__'].sum().sort_values(ascending=False)
        
        print(f"📂 매출 상위 10개 카테고리:")
        for idx, (category, revenue) in enumerate(category_revenue.head(10).items(), 1):
            category_data = dfp[dfp['__category_mapped__'] == category]
            seller_count = category_data['입점사명'].nunique() if '입점사명' in category_data.columns else 0
            
            print(f"  {idx:2d}. {category}")
            print(f"      매출: {format_currency(revenue)}, 셀러: {seller_count}개, 주문: {len(category_data):,}건")

def main():
    """메인 실행 함수"""
    
    print("🔍 카테고리 및 경쟁 분석 도구")
    print("=" * 60)
    
    # 사용법 안내
    print("💡 사용법:")
    print("  1. 특정 셀러 분석: python3 debug_category_selection.py [셀러명]")
    print("  2. 전체 현황 보기: python3 debug_category_selection.py")
    print("")
    
    # 명령행 인수 확인
    target_seller = None
    if len(sys.argv) > 1:
        target_seller = sys.argv[1]
        print(f"🎯 지정된 분석 대상: {target_seller}")
    
    # 1. 카테고리 선택 로직 분석
    result = debug_category_selection(target_seller)
    
    if result:
        top_category, seller_name, overall_data = result
        
        # 2. 경쟁 현황 분석
        analyze_category_competition(top_category, seller_name, overall_data)
        
        # 3. 전체 카테고리 현황 (대상 셀러가 지정된 경우만)
        if target_seller:
            analyze_sellers_by_category()
    
    print(f"\n✅ 분석 완료!")
    print(f"💡 다른 셀러 분석: python3 debug_category_selection.py [다른셀러명]")

if __name__ == "__main__":
    main()
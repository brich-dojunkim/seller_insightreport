#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""셀러 성과 대시보드 메인 실행 파일"""

import sys
from pathlib import Path

# 상위 디렉토리를 sys.path에 추가
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

from config import CONFIG
from file_manager import load_excel_data
from constants import COL_SELLER
from data_processing import prepare_dataframe
from utils import format_currency  # excel_formatter에서 가져옴
from core.dashboard import SellerDashboard

def fix_config_paths():
    """config 경로를 현재 실행 위치에 맞게 조정"""
    original_input = CONFIG["INPUT_XLSX"]
    
    # 원본 경로에 파일이 없으면 상위 디렉토리 기준으로 조정
    if not Path(original_input).exists():
        CONFIG["INPUT_XLSX"] = str(parent_dir / original_input)
        if CONFIG.get("CATEGORY_MAPPING_PATH"):
            CONFIG["CATEGORY_MAPPING_PATH"] = str(parent_dir / CONFIG["CATEGORY_MAPPING_PATH"])
        CONFIG["OUTPUT_DIR"] = str(parent_dir / CONFIG.get("OUTPUT_DIR", "./reports"))
    
    return Path(CONFIG["INPUT_XLSX"]).exists()

def main():
    """메인 실행 함수"""
    
    print("📊 셀러 성과 대시보드 엑셀 생성기")
    print("=" * 60)
    
    # 경로 수정
    if not fix_config_paths():
        print(f"❌ 파일을 찾을 수 없습니다: {CONFIG['INPUT_XLSX']}")
        return
    
    # 셀러 지정
    target_seller = sys.argv[1] if len(sys.argv) > 1 else None
    
    if not target_seller:
        # 매출 1위 셀러 자동 선택
        try:
            df = load_excel_data(CONFIG["INPUT_XLSX"])
            dfp = prepare_dataframe(df, None, None)
            
            if COL_SELLER in dfp.columns:
                seller_revenue = dfp.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
                target_seller = seller_revenue.index[0]
                print(f"💡 매출 1위 셀러 '{target_seller}' 자동 선택")
            else:
                target_seller = "전체"
                print(f"💡 셀러 정보 없음 - '전체' 분석 수행")
        except Exception as e:
            print(f"❌ 자동 선택 실패: {e}")
            return
    else:
        print(f"🎯 지정된 셀러: {target_seller}")
    
    try:
        # 대시보드 생성 및 분석
        dashboard = SellerDashboard(target_seller)
        
        print(f"📁 데이터 로딩 중...")
        if not dashboard.load_data():
            return
        
        print(f"📊 {target_seller} 분석 중...")
        dashboard.analyze_all_data()
        
        print(f"📋 엑셀 리포트 생성 중...")
        output_path = dashboard.export_to_excel()
        
        if output_path:
            # 성공 결과 출력
            basic_info = dashboard.analysis_data['basic_info']
            
            print(f"\n🎉 성공!")
            print(f"📂 파일 위치: {output_path}")
            print(f"📊 포함 시트: 6개 (요약, 매출, 고객, 운영, 벤치마킹, 트렌드)")
            print(f"\n📋 분석 요약:")
            print(f"  • 분석기간: {basic_info['period_start']} ~ {basic_info['period_end']}")
            print(f"  • 총 주문수: {dashboard.kpis.get('total_orders', 0):,}건")
            print(f"  • 총 매출액: {dashboard.kpis.get('total_revenue', 0):,.0f}원")
            print(f"  • 평균주문금액: {dashboard.kpis.get('avg_order_value', 0):,.0f}원")
            
            if 'main_category' in basic_info:
                print(f"  • 주력카테고리: {basic_info['main_category']}")
                if 'category_rank' in basic_info:
                    print(f"  • 카테고리 순위: {basic_info['category_rank']}/{basic_info['category_total_sellers']}")
            
            print(f"\n💡 다른 셀러 분석: python main.py [셀러명]")
        
    except Exception as e:
        print(f"❌ 대시보드 생성 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
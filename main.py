#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
B-Flow 입점사 성과 리포트 생성기
Main execution script for B-Flow partner performance report generator

Usage:
    python main.py                              # 포레스트핏 기본 리포트
    python main.py --company "애경티슬로"        # 특정 회사 리포트
    python main.py --file custom_data.xlsx      # 커스텀 데이터 파일
    python main.py --output custom_report.pdf   # 출력 파일명 지정
    python main.py --list-companies             # 사용 가능한 회사 목록 확인
"""

import os
import sys
import argparse
from datetime import datetime
import traceback

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 모듈 import
try:
    from data import DataLoader, MetricsCalculator
    from charts import CoverPageGenerator, ChannelCharts, TimeCharts, ProductCharts, BenchmarkCharts
    from pdf import BFlowPDFBuilder, generate_forestfit_report, generate_custom_report
    from config import COLORS, SUCCESS_MESSAGES, ERROR_MESSAGES
except ImportError as e:
    print(f"❌ 모듈 import 실패: {str(e)}")
    print("💡 필요한 라이브러리가 설치되어 있는지 확인하세요: pip install -r requirements.txt")
    sys.exit(1)

class BFlowReportCLI:
    """B-Flow 리포트 생성기 커맨드라인 인터페이스"""
    
    def __init__(self):
        self.default_excel_file = "order_list_20250818120157_497.xlsx"
        self.output_dir = "output"
        self.ensure_output_directory()
    
    def ensure_output_directory(self):
        """출력 디렉토리 확인/생성"""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            print(f"📁 {self.output_dir} 디렉토리 생성")
    
    def print_banner(self):
        """시작 배너 출력"""
        banner = f"""
{'='*60}
🚀 B-FLOW 입점사 성과 리포트 생성기 v2.0
{'='*60}
📊 데이터 기반 비즈니스 인사이트를 PDF 리포트로 제공
🎯 5페이지 전문 리포트 자동 생성
⚡ 포레스트핏 최적화 + 다른 입점사 지원

생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}
        """
        print(banner)
    
    def list_available_companies(self, excel_file):
        """사용 가능한 회사 목록 출력"""
        print("📋 사용 가능한 입점사 목록 확인 중...")
        
        try:
            loader = DataLoader(excel_file)
            platform_data = loader.load_excel()
            
            if platform_data is None:
                print("❌ 데이터 파일을 읽을 수 없습니다")
                return False
            
            loader.validate_data_structure()
            loader.clean_data()
            
            companies = loader.get_available_companies()
            
            print(f"\n📊 총 {len(companies)}개 입점사 발견")
            print("=" * 50)
            
            # 상위 20개 회사 표시
            for i, (company, count) in enumerate(list(companies.items())[:20], 1):
                # 추천 마크 추가
                if count >= 100:
                    status = "🟢 추천"
                elif count >= 50:
                    status = "🟡 가능"
                else:
                    status = "🔴 데이터 부족"
                
                print(f"{i:2d}. {company:<20} {count:>6,}건 {status}")
            
            if len(companies) > 20:
                print(f"... 및 {len(companies) - 20}개 추가 입점사")
            
            print("\n💡 사용법:")
            print('   python main.py --company "포레스트핏"')
            print('   python main.py --company "애경티슬로"')
            
            return True
            
        except Exception as e:
            print(f"❌ 회사 목록 확인 실패: {str(e)}")
            return False
    
    def generate_report(self, company_name, excel_file, output_file):
        """리포트 생성 메인 함수"""
        print(f"📊 {company_name} 성과 리포트 생성 시작...")
        print("-" * 40)
        
        start_time = datetime.now()
        
        try:
            # 1단계: 데이터 로드
            print("🔄 1단계: 데이터 로드 및 검증...")
            loader = DataLoader(excel_file)
            platform_data = loader.load_excel()
            
            if platform_data is None:
                print("❌ 엑셀 파일 로드 실패")
                return False
            
            if not loader.validate_data_structure():
                print("❌ 데이터 구조 검증 실패")
                return False
            
            cleaned_data = loader.clean_data()
            if cleaned_data is None:
                print("❌ 데이터 정리 실패")
                return False
            
            print(f"   ✅ 전체 {len(cleaned_data):,}건 데이터 로드")
            
            # 2단계: 회사 데이터 필터링
            print(f"🔄 2단계: {company_name} 데이터 필터링...")
            company_data = loader.filter_by_company(company_name)
            
            if company_data is None:
                print(f"❌ {company_name} 데이터가 없습니다")
                return False
            
            print(f"   ✅ {company_name} {len(company_data):,}건 데이터 추출")
            
            # 3단계: 지표 계산
            print("🔄 3단계: 비즈니스 지표 계산...")
            calculator = MetricsCalculator(company_data, platform_data, company_name)
            metrics = calculator.calculate_all_metrics()
            
            if metrics is None:
                print("❌ 지표 계산 실패")
                return False
            
            # 주요 지표 출력
            basic = metrics['basic']
            growth = metrics['growth']
            benchmark = metrics['benchmark']
            
            print("   📈 계산 완료:")
            print(f"      • 총 주문수: {basic['total_orders']:,}건 ({growth['order_growth']:+.1f}%)")
            print(f"      • 총 매출액: ₩{basic['total_revenue']:,.0f} ({growth['revenue_growth']:+.1f}%)")
            print(f"      • 평균 주문금액: ₩{basic['avg_order_value']:,.0f}")
            print(f"      • 시장 점유율: {benchmark['market_share']['revenue']:.2f}%")
            
            # 4단계: PDF 생성
            print("🔄 4단계: PDF 리포트 생성...")
            builder = BFlowPDFBuilder(company_name)
            result_path = builder.build_complete_report(metrics, output_file)
            
            if result_path is None:
                print("❌ PDF 생성 실패")
                return False
            
            # 5단계: 완료
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            file_size = os.path.getsize(result_path) / 1024  # KB
            
            print("🎉 리포트 생성 완료!")
            print("=" * 40)
            print(f"📄 파일명: {result_path}")
            print(f"📁 파일 크기: {file_size:.1f} KB")
            print(f"⏱️ 소요 시간: {duration:.1f}초")
            print(f"📊 총 페이지: 5페이지")
            
            # 성공 메시지
            print("\n✨ 리포트 내용:")
            print("   📄 1페이지: 커버 페이지 + 핵심 KPI")
            print("   📄 2페이지: 채널별 성과 분석")
            print("   📄 3페이지: 시간대별 분석")
            print("   📄 4페이지: 상품 & 배송 현황")
            print("   📄 5페이지: 벤치마크 & 전략 제안")
            
            return True
            
        except Exception as e:
            print(f"❌ 리포트 생성 실패: {str(e)}")
            if '--debug' in sys.argv:
                traceback.print_exc()
            return False
    
    def run(self, args):
        """메인 실행 함수"""
        self.print_banner()
        
        # 파일 존재 확인
        excel_file = args.file or self.default_excel_file
        
        if not os.path.exists(excel_file):
            print(f"❌ 파일을 찾을 수 없습니다: {excel_file}")
            print("💡 현재 디렉토리에 order_list_20250818120157_497.xlsx 파일이 있는지 확인하세요")
            return False
        
        # 회사 목록 확인 모드
        if args.list_companies:
            return self.list_available_companies(excel_file)
        
        # 출력 파일명 생성
        company_name = args.company or "포레스트핏"
        if args.output:
            output_file = args.output
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(self.output_dir, f"{company_name}_성과리포트_{timestamp}.pdf")
        
        # 리포트 생성
        success = self.generate_report(company_name, excel_file, output_file)
        
        if success:
            print(f"\n🚀 {company_name} 리포트가 성공적으로 생성되었습니다!")
            print(f"📁 위치: {os.path.abspath(output_file)}")
        else:
            print(f"\n💥 {company_name} 리포트 생성에 실패했습니다.")
        
        return success

def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(
        description='B-Flow 입점사 성과 리포트 생성기',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  %(prog)s                                    # 포레스트핏 기본 리포트
  %(prog)s --company "애경티슬로"               # 애경티슬로 리포트
  %(prog)s --file custom_data.xlsx            # 커스텀 데이터 파일
  %(prog)s --output report.pdf                # 출력 파일명 지정
  %(prog)s --list-companies                   # 사용 가능한 회사 목록

지원하는 입점사:
  포레스트핏, 애경티슬로, 애경뷰티통합, 나바바, 허니제이 등
  (--list-companies로 전체 목록 확인)
        """
    )
    
    parser.add_argument(
        '--company', '-c',
        type=str,
        default='포레스트핏',
        help='리포트를 생성할 입점사명 (기본값: 포레스트핏)'
    )
    
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='분석할 엑셀 파일 경로 (기본값: order_list_20250818120157_497.xlsx)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='출력할 PDF 파일 경로 (기본값: 자동 생성)'
    )
    
    parser.add_argument(
        '--list-companies', '-l',
        action='store_true',
        help='사용 가능한 입점사 목록 출력'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='디버그 모드 (에러 시 상세 정보 출력)'
    )
    
    parser.add_argument(
        '--version', '-v',
        action='version',
        version='B-Flow Report Generator v2.0.0'
    )
    
    args = parser.parse_args()
    
    # CLI 실행
    cli = BFlowReportCLI()
    success = cli.run(args)
    
    # 종료 코드
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
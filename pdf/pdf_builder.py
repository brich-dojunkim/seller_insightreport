# pdf/pdf_builder.py - 최종 PDF 문서 조립기

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageTemplate, Frame
from reportlab.lib.units import cm
from datetime import datetime
import os
import sys
sys.path.append('..')

from .styles import get_layout, pdf_styles
from .page_builders import PageBuilders, CustomPageTemplate
from data import MetricsCalculator

class BFlowPDFBuilder:
    """B-Flow PDF 리포트 최종 조립기"""
    
    def __init__(self, company_name="포레스트핏"):
        self.company_name = company_name
        self.layout = get_layout()
        self.page_builders = PageBuilders()
        self.page_template = CustomPageTemplate(company_name)
        
    def build_complete_report(self, metrics_data, output_path=None):
        """완전한 5페이지 PDF 리포트 생성"""
        
        # 출력 파일명 설정
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{self.company_name}_성과리포트_{timestamp}.pdf"
        
        print(f"📄 {self.company_name} PDF 리포트 생성 시작...")
        
        try:
            # PDF 문서 설정
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                topMargin=self.layout['margins']['top'],
                bottomMargin=self.layout['margins']['bottom'],
                leftMargin=self.layout['margins']['left'],
                rightMargin=self.layout['margins']['right']
            )
            
            # 페이지 템플릿 설정
            frame = Frame(
                self.layout['margins']['left'],
                self.layout['margins']['bottom'],
                A4[0] - self.layout['margins']['left'] - self.layout['margins']['right'],
                A4[1] - self.layout['margins']['top'] - self.layout['margins']['bottom'],
                id='normal'
            )
            
            # 커버 페이지 템플릿
            cover_template = PageTemplate(
                id='cover',
                frames=[frame],
                onPage=self.page_template.on_first_page
            )
            
            # 일반 페이지 템플릿
            normal_template = PageTemplate(
                id='normal',
                frames=[frame],
                onPage=self.page_template.on_later_pages
            )
            
            doc.addPageTemplates([cover_template, normal_template])
            
            # 스토리 구성
            story = []
            
            # === 1페이지: 커버 ===
            print("📄 1페이지: 커버 페이지 생성...")
            cover_story = self.page_builders.build_page_1_cover(
                company_name=self.company_name,
                metrics_data=metrics_data,
                channel_data=metrics_data['channels'],
                insights=self._generate_insights(metrics_data)
            )
            story.extend(cover_story)
            
            # 템플릿 변경 (2페이지부터 헤더/푸터 적용)
            from reportlab.platypus import NextPageTemplate
            story.append(NextPageTemplate('normal'))
            
            # === 2페이지: 채널별 성과 ===
            print("📄 2페이지: 채널별 성과 분석...")
            channel_story = self.page_builders.build_page_2_channels(
                channel_data=metrics_data['channels']
            )
            story.extend(channel_story)
            
            # === 3페이지: 시간대별 분석 ===
            print("📄 3페이지: 시간대별 분석...")
            time_story = self.page_builders.build_page_3_time_analysis(
                time_data=metrics_data['time']
            )
            story.extend(time_story)
            
            # === 4페이지: 상품 & 배송 현황 ===
            print("📄 4페이지: 상품 & 배송 현황...")
            product_story = self.page_builders.build_page_4_products(
                product_data=metrics_data['products']['all_products'],
                status_data=metrics_data['products']['status_distribution'],
                delivery_data=metrics_data['products']
            )
            story.extend(product_story)
            
            # === 5페이지: 벤치마크 & 제안 ===
            print("📄 5페이지: 벤치마크 & 전략 제안...")
            benchmark_story = self.page_builders.build_page_5_benchmark(
                benchmark_data=metrics_data['benchmark'],
                current_metrics=metrics_data,
                company_name=self.company_name
            )
            story.extend(benchmark_story)
            
            # PDF 생성
            print("🔧 PDF 문서 조립 중...")
            doc.build(story)
            
            print(f"✅ PDF 리포트 생성 완료: {output_path}")
            print(f"📁 파일 크기: {os.path.getsize(output_path) / 1024:.1f} KB")
            
            return output_path
            
        except Exception as e:
            print(f"❌ PDF 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_insights(self, metrics_data):
        """자동 인사이트 생성"""
        insights = []
        
        try:
            # 성장률 기반 인사이트
            revenue_growth = metrics_data['growth']['revenue_growth']
            if revenue_growth > 15:
                insights.append("📈 매출 성장세가 매우 우수합니다")
            elif revenue_growth > 5:
                insights.append("📊 안정적인 매출 성장을 보이고 있습니다")
            else:
                insights.append("🔍 매출 성장 전략이 필요합니다")
            
            # 채널 분석 기반 인사이트
            if 'channels' in metrics_data:
                top_channel = metrics_data['channels'].index[0]
                top_share = metrics_data['channels'].iloc[0]['매출점유율']
                
                if top_share > 50:
                    insights.append(f"⚠️ {top_channel} 채널 의존도가 높습니다")
                else:
                    insights.append(f"✅ {top_channel} 채널에서 우수한 성과를 보입니다")
            
            # 시장 점유율 기반 인사이트
            market_share = metrics_data['benchmark']['market_share']['revenue']
            if market_share > 5:
                insights.append("🏆 플랫폼 내 상위권 위치를 유지하고 있습니다")
            elif market_share > 2:
                insights.append("📈 플랫폼 내 성장 잠재력이 높습니다")
            
            # AOV 비교 인사이트
            aov_diff = metrics_data['benchmark']['performance_vs_platform']['aov_difference']
            if aov_diff > 10:
                insights.append("💎 평균 주문금액이 플랫폼 평균보다 우수합니다")
            elif aov_diff < -10:
                insights.append("📈 평균 주문금액 향상 여지가 있습니다")
            
        except Exception as e:
            print(f"⚠️ 인사이트 생성 중 오류: {str(e)}")
            # 기본 인사이트
            insights = [
                "📊 지속적인 성장세를 보이고 있습니다",
                "🎯 주요 채널에서 안정적인 성과 유지",
                "💡 추가 성장 기회가 존재합니다"
            ]
        
        return insights[:4]  # 최대 4개까지
    
    def generate_report_from_excel(self, excel_file_path, output_path=None):
        """엑셀 파일로부터 직접 리포트 생성"""
        print(f"📊 {excel_file_path}에서 데이터 로드 중...")
        
        try:
            # 데이터 로드 및 처리
            from data import DataLoader
            
            loader = DataLoader(excel_file_path)
            platform_data = loader.load_excel()
            
            if platform_data is None:
                print("❌ 엑셀 파일 로드 실패")
                return None
            
            loader.validate_data_structure()
            cleaned_data = loader.clean_data()
            
            # 회사 데이터 필터링
            company_data = loader.filter_by_company(self.company_name)
            if company_data is None:
                print(f"❌ {self.company_name} 데이터가 없습니다")
                return None
            
            # 지표 계산
            calculator = MetricsCalculator(company_data, platform_data, self.company_name)
            metrics_data = calculator.calculate_all_metrics()
            
            if metrics_data is None:
                print("❌ 지표 계산 실패")
                return None
            
            # PDF 생성
            return self.build_complete_report(metrics_data, output_path)
            
        except Exception as e:
            print(f"❌ 리포트 생성 실패: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def create_sample_report(self, output_path=None):
        """샘플 리포트 생성 (테스트용)"""
        print("🧪 샘플 PDF 리포트 생성...")
        
        # 기본 엑셀 파일 경로
        default_excel = "order_list_20250818120157_497.xlsx"
        
        if os.path.exists(default_excel):
            return self.generate_report_from_excel(default_excel, output_path)
        else:
            print(f"❌ {default_excel} 파일을 찾을 수 없습니다")
            return None

# 편의 함수
def generate_forestfit_report(excel_file_path=None, output_path=None):
    """포레스트핏 리포트 생성 편의 함수"""
    builder = BFlowPDFBuilder("포레스트핏")
    
    if excel_file_path:
        return builder.generate_report_from_excel(excel_file_path, output_path)
    else:
        return builder.create_sample_report(output_path)

def generate_custom_report(company_name, excel_file_path, output_path=None):
    """커스텀 회사 리포트 생성 편의 함수"""
    builder = BFlowPDFBuilder(company_name)
    return builder.generate_report_from_excel(excel_file_path, output_path)
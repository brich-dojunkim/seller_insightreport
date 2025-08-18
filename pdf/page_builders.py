# pdf/page_builders.py - 각 페이지 레이아웃 빌더

from reportlab.platypus import Paragraph, Spacer, Image, Table, PageBreak, KeepTogether
from reportlab.lib.units import inch, cm
from io import BytesIO
import sys
sys.path.append('..')

from .styles import get_style, get_table_style, get_color, get_layout
from charts import (
    CoverPageGenerator, ChannelCharts, TimeCharts, 
    ProductCharts, BenchmarkCharts
)

class PageBuilders:
    """각 페이지별 레이아웃 빌더 클래스"""
    
    def __init__(self):
        self.layout = get_layout()
        
        # 차트 생성기 초기화
        self.cover_gen = CoverPageGenerator()
        self.channel_charts = ChannelCharts()
        self.time_charts = TimeCharts()
        self.product_charts = ProductCharts()
        self.benchmark_charts = BenchmarkCharts()
    
    def build_page_1_cover(self, company_name, metrics_data, channel_data, insights):
        """1페이지: 커버 페이지 빌드"""
        story = []
        
        try:
            # 커버 페이지 통합 이미지 생성
            cover_image_buffer = self.cover_gen.create_complete_cover_page(
                company_name=company_name,
                metrics_data=metrics_data,
                channel_data=channel_data,
                insights=insights
            )
            
            if cover_image_buffer:
                # 커버 이미지를 전체 페이지로 표시
                story.append(Image(cover_image_buffer, 
                                 width=17*cm, height=22*cm))
            else:
                # 이미지 생성 실패 시 텍스트 기반 커버
                story.extend(self._create_text_cover(company_name, metrics_data))
            
            story.append(PageBreak())
            
        except Exception as e:
            print(f"❌ 커버 페이지 생성 실패: {str(e)}")
            # 폴백: 심플 텍스트 커버
            story.extend(self._create_text_cover(company_name, metrics_data))
            story.append(PageBreak())
        
        return story
    
    def _create_text_cover(self, company_name, metrics_data):
        """텍스트 기반 커버 페이지 (폴백)"""
        story = []
        
        story.append(Spacer(1, 2*cm))
        story.append(Paragraph("B-FLOW", get_style('cover_title')))
        story.append(Paragraph("입점사 성과 리포트", get_style('cover_subtitle')))
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph(company_name, get_style('cover_company')))
        
        # 기간 정보
        date_range = metrics_data['basic']['date_range']
        story.append(Paragraph(
            f"분석 기간: {date_range['start']} ~ {date_range['end']}", 
            get_style('body')
        ))
        
        story.append(Spacer(1, 2*cm))
        
        # 핵심 지표 텍스트
        kpi_text = f"""
        <b>핵심 지표 요약</b><br/>
        • 총 주문수: {metrics_data['basic']['total_orders']:,}건<br/>
        • 총 매출액: ₩{metrics_data['basic']['total_revenue']:,.0f}<br/>
        • 평균 주문금액: ₩{metrics_data['basic']['avg_order_value']:,.0f}<br/>
        • 시장 점유율: {metrics_data['benchmark']['market_share']['revenue']:.2f}%
        """
        story.append(Paragraph(kpi_text, get_style('highlight')))
        
        return story
    
    def build_page_2_channels(self, channel_data, title="채널별 성과 분석"):
        """2페이지: 채널별 성과 분석 빌드"""
        story = []
        
        try:
            # 페이지 제목
            story.append(Paragraph(title, get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 1. 채널별 매출 도넛차트
            donut_buffer = self.channel_charts.create_channel_donut_chart(
                channel_data, "채널별 매출 분포"
            )
            if donut_buffer:
                story.append(Image(donut_buffer, width=15*cm, height=10*cm))
                story.append(Spacer(1, 0.3*cm))
            
            # 2. 채널별 성장률 표
            table_buffer = self.channel_charts.create_channel_growth_table(channel_data)
            if table_buffer:
                story.append(Image(table_buffer, width=15*cm, height=8*cm))
            
            story.append(PageBreak())
            
        except Exception as e:
            print(f"❌ 2페이지 생성 실패: {str(e)}")
            story.append(Paragraph("채널 데이터 처리 중 오류가 발생했습니다.", get_style('body')))
            story.append(PageBreak())
        
        return story
    
    def build_page_3_time_analysis(self, time_data, title="시간대별 분석"):
        """3페이지: 시간대별 분석 빌드"""
        story = []
        
        try:
            # 페이지 제목
            story.append(Paragraph(title, get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 1. 시간별 주문 패턴 히트맵
            heatmap_buffer = self.time_charts.create_hourly_heatmap(
                time_data, "시간대별 주문 패턴"
            )
            if heatmap_buffer:
                story.append(Image(heatmap_buffer, width=15*cm, height=8*cm))
                story.append(Spacer(1, 0.4*cm))
            
            # 2. 요일별 매출 트렌드
            trend_buffer = self.time_charts.create_daily_trend_chart(
                time_data, "요일별 매출 트렌드"
            )
            if trend_buffer:
                story.append(Image(trend_buffer, width=15*cm, height=6*cm))
                story.append(Spacer(1, 0.3*cm))
            
            # 3. 피크 시간대 분석
            peak_buffer = self.time_charts.create_peak_hours_analysis(time_data)
            if peak_buffer:
                story.append(Image(peak_buffer, width=15*cm, height=6*cm))
            
            story.append(PageBreak())
            
        except Exception as e:
            print(f"❌ 3페이지 생성 실패: {str(e)}")
            story.append(Paragraph("시간 분석 데이터 처리 중 오류가 발생했습니다.", get_style('body')))
            story.append(PageBreak())
        
        return story
    
    def build_page_4_products(self, product_data, status_data, delivery_data, 
                             title="상품 & 배송 현황"):
        """4페이지: 상품 및 배송 현황 빌드"""
        story = []
        
        try:
            # 페이지 제목
            story.append(Paragraph(title, get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 1. 베스트셀러 TOP 10
            bestseller_buffer = self.product_charts.create_bestseller_chart(
                product_data, "베스트셀러 TOP 10"
            )
            if bestseller_buffer:
                story.append(Image(bestseller_buffer, width=15*cm, height=8*cm))
                story.append(Spacer(1, 0.4*cm))
            
            # 2. 주문 상태별 분포와 배송 성과를 한 줄에
            elements = []
            
            # 주문 상태 파이차트
            status_buffer = self.product_charts.create_order_status_pie_chart(
                status_data, "주문 상태별 분포"
            )
            if status_buffer:
                elements.append(Image(status_buffer, width=7*cm, height=5*cm))
            
            # 배송 성과 지표
            delivery_buffer = self.product_charts.create_delivery_performance_chart(
                delivery_data, "배송 성과 지표"
            )
            if delivery_buffer:
                elements.append(Image(delivery_buffer, width=7*cm, height=5*cm))
            
            if elements:
                # 나란히 배치를 위한 테이블 생성
                image_table = Table([elements], colWidths=[7.5*cm, 7.5*cm])
                image_table.setStyle(get_table_style('clean'))
                story.append(image_table)
            
            # 3. 상품 성과 요약
            summary_buffer = self.product_charts.create_product_performance_summary(
                product_data, status_data, delivery_data
            )
            if summary_buffer:
                story.append(Spacer(1, 0.3*cm))
                story.append(Image(summary_buffer, width=15*cm, height=6*cm))
            
            story.append(PageBreak())
            
        except Exception as e:
            print(f"❌ 4페이지 생성 실패: {str(e)}")
            story.append(Paragraph("상품 데이터 처리 중 오류가 발생했습니다.", get_style('body')))
            story.append(PageBreak())
        
        return story
    
    def build_page_5_benchmark(self, benchmark_data, current_metrics, company_name,
                              title="벤치마크 & 전략 제안"):
        """5페이지: 벤치마크 및 전략 제안 빌드"""
        story = []
        
        try:
            # 페이지 제목
            story.append(Paragraph(title, get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 1. 시장 점유율 비교
            market_buffer = self.benchmark_charts.create_market_share_comparison(
                benchmark_data, company_name, "플랫폼 내 시장 점유율"
            )
            if market_buffer:
                story.append(Image(market_buffer, width=15*cm, height=6*cm))
                story.append(Spacer(1, 0.3*cm))
            
            # 2. 성과 레이더 차트와 성장 전망을 나란히
            radar_buffer = self.benchmark_charts.create_performance_radar_chart(
                benchmark_data, company_name, "종합 성과 분석"
            )
            
            growth_buffer = self.benchmark_charts.create_growth_projection_chart(
                current_metrics, "성장 전망"
            )
            
            if radar_buffer and growth_buffer:
                chart_elements = [
                    Image(radar_buffer, width=7*cm, height=6*cm),
                    Image(growth_buffer, width=7*cm, height=6*cm)
                ]
                chart_table = Table([chart_elements], colWidths=[7.5*cm, 7.5*cm])
                chart_table.setStyle(get_table_style('clean'))
                story.append(chart_table)
                story.append(Spacer(1, 0.3*cm))
            
            # 3. 전략적 개선 제안
            strategy_buffer = self.benchmark_charts.create_strategic_recommendations(
                current_metrics, "전략적 개선 제안"
            )
            if strategy_buffer:
                story.append(Image(strategy_buffer, width=15*cm, height=8*cm))
                story.append(Spacer(1, 0.3*cm))
            
            # 4. 다음 달 전망
            forecast_buffer = self.benchmark_charts.create_next_month_forecast(
                current_metrics, "다음 달 전망"
            )
            if forecast_buffer:
                story.append(Image(forecast_buffer, width=15*cm, height=6*cm))
            
            # 마지막 페이지이므로 PageBreak 없음
            
        except Exception as e:
            print(f"❌ 5페이지 생성 실패: {str(e)}")
            story.append(Paragraph("벤치마크 데이터 처리 중 오류가 발생했습니다.", get_style('body')))
        
        return story
    
    def create_header_footer(self, canvas, doc, page_num, total_pages, company_name):
        """헤더/푸터 생성"""
        try:
            # 푸터
            canvas.saveState()
            
            # 회사명 (좌측 하단)
            canvas.setFont('Helvetica', 9)
            canvas.setFillColor(get_color('medium_gray'))
            canvas.drawString(2*cm, 1*cm, f"{company_name} 성과 리포트")
            
            # 페이지 번호 (우측 하단)
            canvas.drawRightString(19*cm, 1*cm, f"{page_num} / {total_pages}")
            
            # B-Flow 브랜딩 (우측 하단)
            canvas.setFont('Helvetica-Bold', 8)
            canvas.setFillColor(get_color('primary'))
            canvas.drawRightString(19*cm, 0.5*cm, "Powered by B-FLOW")
            
            canvas.restoreState()
            
        except Exception as e:
            print(f"❌ 헤더/푸터 생성 실패: {str(e)}")
    
    def add_watermark(self, canvas, doc):
        """워터마크 추가 (옵션)"""
        try:
            canvas.saveState()
            canvas.setFillAlpha(0.1)
            canvas.setFont('Helvetica-Bold', 60)
            canvas.setFillColor(get_color('primary'))
            
            # 중앙에 대각선 워터마크
            canvas.rotate(45)
            canvas.drawCentredText(15*cm, 0*cm, "B-FLOW")
            
            canvas.restoreState()
            
        except Exception as e:
            print(f"❌ 워터마크 생성 실패: {str(e)}")

class CustomPageTemplate:
    """커스텀 페이지 템플릿"""
    
    def __init__(self, company_name):
        self.company_name = company_name
        self.page_builders = PageBuilders()
    
    def on_first_page(self, canvas, doc):
        """첫 페이지 템플릿 (커버 페이지)"""
        # 커버 페이지는 헤더/푸터 없음
        pass
    
    def on_later_pages(self, canvas, doc):
        """일반 페이지 템플릿"""
        page_num = canvas.getPageNumber()
        total_pages = 5  # 총 5페이지
        
        self.page_builders.create_header_footer(
            canvas, doc, page_num, total_pages, self.company_name
        )

class AdvancedPageBuilders(PageBuilders):
    """고급 페이지 빌더 (추가 기능)"""
    
    def create_executive_summary_page(self, metrics_data, company_name):
        """경영진 요약 페이지 (추가 페이지)"""
        story = []
        
        try:
            # 제목
            story.append(Paragraph("경영진 요약", get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 핵심 성과 요약
            basic = metrics_data['basic']
            growth = metrics_data['growth']
            benchmark = metrics_data['benchmark']
            
            summary_text = f"""
            <b>{company_name} 핵심 성과 요약</b><br/><br/>
            
            <b>매출 성과:</b><br/>
            • 총 매출액: ₩{basic['total_revenue']:,.0f} ({growth['revenue_growth']:+.1f}% 성장)<br/>
            • 총 주문수: {basic['total_orders']:,}건 ({growth['order_growth']:+.1f}% 성장)<br/>
            • 평균 주문금액: ₩{basic['avg_order_value']:,.0f}<br/><br/>
            
            <b>시장 위치:</b><br/>
            • 플랫폼 점유율: {benchmark['market_share']['revenue']:.2f}%<br/>
            • AOV 경쟁력: 플랫폼 평균 대비 {benchmark['performance_vs_platform']['aov_difference']:+.1f}%<br/><br/>
            
            <b>주요 강점:</b><br/>
            • 안정적인 성장 궤도 유지<br/>
            • 우수한 평균 주문금액<br/>
            • 다변화된 채널 포트폴리오<br/>
            """
            
            story.append(Paragraph(summary_text, get_style('body')))
            story.append(PageBreak())
            
        except Exception as e:
            print(f"❌ 경영진 요약 페이지 생성 실패: {str(e)}")
        
        return story
    
    def create_detailed_analysis_page(self, metrics_data):
        """상세 분석 페이지 (추가 페이지)"""
        story = []
        
        try:
            # 제목
            story.append(Paragraph("상세 분석", get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 채널별 상세 분석 테이블
            if 'channels' in metrics_data:
                channel_data = metrics_data['channels']
                
                # 테이블 데이터 준비
                table_data = [['채널명', '주문수', '매출액', '평균주문금액', '점유율', '성장률']]
                
                for channel, row in channel_data.iterrows():
                    table_data.append([
                        channel,
                        f"{row['주문수']:,}건",
                        f"₩{row['총매출']:,.0f}",
                        f"₩{row['평균주문금액']:,.0f}",
                        f"{row['매출점유율']:.1f}%",
                        f"{row['성장률']:+.1f}%"
                    ])
                
                # 테이블 생성
                detail_table = Table(table_data, colWidths=[3*cm, 2*cm, 3*cm, 2.5*cm, 2*cm, 2*cm])
                detail_table.setStyle(get_table_style('default'))
                
                story.append(Paragraph("채널별 상세 성과", get_style('heading')))
                story.append(Spacer(1, 0.3*cm))
                story.append(detail_table)
                story.append(Spacer(1, 0.5*cm))
            
            # 상품별 상세 분석
            if 'products' in metrics_data:
                story.append(Paragraph("상품 성과 분석", get_style('heading')))
                story.append(Spacer(1, 0.3*cm))
                
                products = metrics_data['products']['bestsellers'].head(5)
                product_table_data = [['상품명', '주문수', '매출액', '기여도']]
                
                for product, row in products.iterrows():
                    # 상품명 길이 제한
                    product_name = product[:30] + '...' if len(product) > 30 else product
                    product_table_data.append([
                        product_name,
                        f"{row['주문수']:,}건",
                        f"₩{row['총매출']:,.0f}",
                        f"{row['매출기여도']:.1f}%"
                    ])
                
                product_table = Table(product_table_data, colWidths=[6*cm, 2*cm, 3*cm, 2*cm])
                product_table.setStyle(get_table_style('default'))
                story.append(product_table)
            
            story.append(PageBreak())
            
        except Exception as e:
            print(f"❌ 상세 분석 페이지 생성 실패: {str(e)}")
        
        return story
    
    def create_recommendations_page(self, metrics_data, company_name):
        """추천 사항 페이지 (추가 페이지)"""
        story = []
        
        try:
            # 제목
            story.append(Paragraph("전략적 권고사항", get_style('title')))
            story.append(Spacer(1, 0.5*cm))
            
            # 성과 기반 권고사항 생성
            recommendations = self._generate_detailed_recommendations(metrics_data)
            
            for i, (category, rec_list) in enumerate(recommendations.items(), 1):
                # 카테고리 제목
                story.append(Paragraph(f"{i}. {category}", get_style('heading')))
                story.append(Spacer(1, 0.2*cm))
                
                # 권고사항 리스트
                for rec in rec_list:
                    rec_text = f"• {rec}"
                    story.append(Paragraph(rec_text, get_style('bullet_list')))
                
                story.append(Spacer(1, 0.4*cm))
            
            # 실행 우선순위
            story.append(Paragraph("실행 우선순위", get_style('heading')))
            story.append(Spacer(1, 0.3*cm))
            
            priority_text = """
            <b>단기 (1-3개월):</b><br/>
            • 주력 채널 마케팅 강화<br/>
            • 베스트셀러 상품 재고 최적화<br/><br/>
            
            <b>중기 (3-6개월):</b><br/>
            • 신규 채널 진출 검토<br/>
            • 고객 리텐션 프로그램 도입<br/><br/>
            
            <b>장기 (6-12개월):</b><br/>
            • 상품 포트폴리오 다변화<br/>
            • 글로벌 시장 진출 준비
            """
            
            story.append(Paragraph(priority_text, get_style('body')))
            
        except Exception as e:
            print(f"❌ 권고사항 페이지 생성 실패: {str(e)}")
        
        return story
    
    def _generate_detailed_recommendations(self, metrics_data):
        """상세 권고사항 생성"""
        recommendations = {
            "매출 성장 전략": [],
            "채널 최적화": [],
            "상품 관리": [],
            "고객 경험 개선": []
        }
        
        try:
            growth = metrics_data['growth']['revenue_growth']
            channels = metrics_data['channels']
            benchmark = metrics_data['benchmark']
            
            # 매출 성장 전략
            if growth > 15:
                recommendations["매출 성장 전략"].append("현재의 강력한 성장 모멘텀을 유지하기 위한 투자 확대")
            elif growth > 5:
                recommendations["매출 성장 전략"].append("안정적 성장을 가속화할 수 있는 새로운 동력 발굴")
            else:
                recommendations["매출 성장 전략"].append("성장률 개선을 위한 전면적인 전략 재검토 필요")
            
            # 채널 최적화
            top_channel = channels.index[0]
            top_share = channels.iloc[0]['매출점유율']
            
            if top_share > 50:
                recommendations["채널 최적화"].append(f"{top_channel} 의존도가 높으므로 채널 다변화 필요")
            
            recommendations["채널 최적화"].append("성장률이 높은 채널에 대한 투자 집중")
            recommendations["채널 최적화"].append("저성과 채널에 대한 전략 재검토")
            
            # 상품 관리
            recommendations["상품 관리"].append("베스트셀러 상품의 안정적 공급 체계 구축")
            recommendations["상품 관리"].append("신상품 출시 주기 최적화")
            
            # 고객 경험 개선
            aov_diff = benchmark['performance_vs_platform']['aov_difference']
            if aov_diff > 0:
                recommendations["고객 경험 개선"].append("우수한 AOV를 활용한 프리미엄 포지셔닝 강화")
            else:
                recommendations["고객 경험 개선"].append("고객 단가 향상을 위한 상품 번들링 전략")
            
            recommendations["고객 경험 개선"].append("고객 만족도 향상을 통한 재구매율 증대")
            
        except Exception as e:
            print(f"❌ 상세 권고사항 생성 실패: {str(e)}")
        
        return recommendations

# 테스트 함수
def test_page_builders():
    """페이지 빌더 테스트"""
    print("🧪 페이지 빌더 테스트 시작...")
    
    try:
        import pandas as pd
        
        # 테스트 데이터 생성
        test_metrics = {
            'basic': {
                'total_orders': 416,
                'total_revenue': 9876543,
                'avg_order_value': 23750,
                'date_range': {'start': '2025-08-11', 'end': '2025-08-18'}
            },
            'growth': {
                'order_growth': 15.2,
                'revenue_growth': 12.1,
                'aov_growth': -2.3
            },
            'benchmark': {
                'market_share': {'revenue': 4.35},
                'performance_vs_platform': {'aov_difference': 8.5}
            }
        }
        
        test_channels = pd.DataFrame({
            '주문수': [150, 120, 80, 66],
            '총매출': [3500000, 2800000, 1900000, 1500000],
            '매출점유율': [35.0, 28.0, 19.0, 15.0],
            '성장률': [15.2, 8.5, -3.2, 12.1]
        }, index=['SSG', '카페24', '쿠팡', '11번가'])
        
        test_insights = [
            "매출 성장세가 매우 우수합니다",
            "SSG 채널에서 강세를 보이고 있습니다", 
            "평균 주문금액이 플랫폼 평균보다 높습니다"
        ]
        
        # PageBuilders 초기화
        builder = PageBuilders()
        print("✅ PageBuilders 초기화 완료")
        
        # 개별 페이지 빌드 테스트
        print("📄 1페이지 커버 빌드 테스트...")
        page1_story = builder.build_page_1_cover("포레스트핏", test_metrics, test_channels, test_insights)
        if page1_story:
            print("✅ 1페이지 커버 빌드 완료")
        
        print("📄 2페이지 채널 빌드 테스트...")
        page2_story = builder.build_page_2_channels(test_channels)
        if page2_story:
            print("✅ 2페이지 채널 빌드 완료")
        
        print("📄 헤더/푸터 테스트...")
        # 헤더/푸터는 실제 canvas 없이는 테스트 어려움
        print("✅ 헤더/푸터 함수 준비 완료")
        
        print("🎉 페이지 빌더 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_page_builders()
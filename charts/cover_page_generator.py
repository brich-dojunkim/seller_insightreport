# charts/cover_page_generator.py - 1페이지 커버 페이지 생성기

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .base_chart import BaseChart, KPICard
import sys
sys.path.append('..')
from config import COLORS, REPORT_TEXTS

class CoverPageGenerator(BaseChart):
    """커버 페이지 생성 클래스"""
    
    def __init__(self):
        super().__init__()
        self.kpi_card = KPICard(self)
    
    def create_bflow_logo(self):
        """B-Flow 로고 생성"""
        try:
            fig, ax = self.create_figure(size='small')
            ax.axis('off')
            
            # 로고 배경 박스
            logo_rect = patches.Rectangle((0.1, 0.3), 0.8, 0.4, 
                                        linewidth=0, facecolor=self.colors['primary'])
            ax.add_patch(logo_rect)
            
            # 로고 텍스트
            ax.text(0.5, 0.5, 'B-FLOW', ha='center', va='center',
                   fontsize=24, fontweight='bold', color='white',
                   transform=ax.transAxes)
            
            # 서브 텍스트
            ax.text(0.5, 0.15, '입점사 성과 리포트', ha='center', va='center',
                   fontsize=12, color=self.colors['medium_gray'],
                   transform=ax.transAxes)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 로고 생성 실패: {str(e)}")
            return None
    
    def create_cover_header(self, company_name, date_range):
        """커버 페이지 헤더 생성"""
        try:
            fig, ax = self.create_figure(size='wide')
            ax.axis('off')
            
            # 배경 그라데이션 효과 (시뮬레이션)
            gradient = patches.Rectangle((0, 0.7), 1, 0.3, 
                                       transform=ax.transAxes,
                                       facecolor=self.colors['light_gray'],
                                       alpha=0.5)
            ax.add_patch(gradient)
            
            # 메인 제목
            ax.text(0.05, 0.85, 'B-FLOW', ha='left', va='center',
                   fontsize=28, fontweight='bold', color=self.colors['primary'],
                   transform=ax.transAxes)
            
            ax.text(0.05, 0.75, '입점사 성과 리포트', ha='left', va='center',
                   fontsize=16, color=self.colors['medium_gray'],
                   transform=ax.transAxes)
            
            # 회사명 (강조)
            ax.text(0.05, 0.55, company_name, ha='left', va='center',
                   fontsize=24, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            # 날짜 범위
            ax.text(0.05, 0.45, f"분석 기간: {date_range['start']} ~ {date_range['end']}", 
                   ha='left', va='center', fontsize=12, color=self.colors['dark_gray'],
                   transform=ax.transAxes)
            
            # 생성 일시
            from datetime import datetime
            current_time = datetime.now().strftime('%Y년 %m월 %d일 생성')
            ax.text(0.95, 0.75, current_time, ha='right', va='center',
                   fontsize=10, color=self.colors['medium_gray'],
                   transform=ax.transAxes)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 헤더 생성 실패: {str(e)}")
            return None
    
    def create_kpi_summary_section(self, metrics_data):
        """핵심 지표 요약 섹션 생성"""
        try:
            # KPI 데이터 준비
            kpi_data = {
                '총 주문수': {
                    'value': metrics_data['basic']['total_orders'],
                    'growth': metrics_data['growth']['order_growth'],
                    'format': 'count'
                },
                '총 매출액': {
                    'value': metrics_data['basic']['total_revenue'],
                    'growth': metrics_data['growth']['revenue_growth'],
                    'format': 'currency'
                },
                '평균 주문금액': {
                    'value': metrics_data['basic']['avg_order_value'],
                    'growth': metrics_data['growth']['aov_growth'],
                    'format': 'currency'
                },
                '시장 점유율': {
                    'value': metrics_data['benchmark']['market_share']['revenue'],
                    'growth': None,
                    'format': 'percentage'
                }
            }
            
            return self.kpi_card.create_multi_kpi_dashboard(kpi_data)
            
        except Exception as e:
            print(f"❌ KPI 요약 생성 실패: {str(e)}")
            return None
    
    def create_channel_highlight(self, channel_data):
        """주요 채널 하이라이트 생성"""
        try:
            fig, ax = self.create_figure(size='medium')
            ax.axis('off')
            
            # 상위 2개 채널 추출
            if isinstance(channel_data, dict):
                sorted_channels = sorted(channel_data.items(), key=lambda x: x[1], reverse=True)
                top_channels = sorted_channels[:2]
            else:
                # DataFrame인 경우
                top_channels = [(ch, row['매출점유율']) for ch, row in channel_data.head(2).iterrows()]
            
            # 제목
            ax.text(0.5, 0.9, '주요 채널', ha='center', va='center',
                   fontsize=16, fontweight='bold', color=self.colors['dark_gray'],
                   transform=ax.transAxes)
            
            # 채널 표시
            for i, (channel, value) in enumerate(top_channels):
                y_pos = 0.7 - (i * 0.25)
                
                # 채널명
                ax.text(0.2, y_pos, channel, ha='left', va='center',
                       fontsize=14, fontweight='bold', color=self.colors['primary'],
                       transform=ax.transAxes)
                
                # 점유율 또는 값
                if isinstance(value, (int, float)) and value > 1:
                    display_value = f"{value:.1f}%"
                else:
                    display_value = self.format_currency(value) if value > 1000 else f"{value:.1f}%"
                
                ax.text(0.8, y_pos, display_value, ha='right', va='center',
                       fontsize=14, fontweight='bold', color=self.colors['secondary'],
                       transform=ax.transAxes)
            
            # 배경 박스
            bg_rect = patches.Rectangle((0.05, 0.3), 0.9, 0.65,
                                      linewidth=1, edgecolor=self.colors['border'],
                                      facecolor=self.colors['light_gray'], alpha=0.3,
                                      transform=ax.transAxes)
            ax.add_patch(bg_rect)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 채널 하이라이트 생성 실패: {str(e)}")
            return None
    
    def create_insights_box(self, insights_list):
        """인사이트 박스 생성"""
        try:
            fig, ax = self.create_figure(size='medium')
            ax.axis('off')
            
            # 제목
            ax.text(0.5, 0.95, '📊 핵심 인사이트', ha='center', va='top',
                   fontsize=16, fontweight='bold', color=self.colors['primary'],
                   transform=ax.transAxes)
            
            # 구분선
            line = patches.Rectangle((0.1, 0.85), 0.8, 0.002,
                                   facecolor=self.colors['primary'],
                                   transform=ax.transAxes)
            ax.add_patch(line)
            
            # 인사이트 목록
            y_start = 0.75
            for i, insight in enumerate(insights_list[:4]):  # 최대 4개
                y_pos = y_start - (i * 0.15)
                
                # 불릿 포인트
                ax.text(0.1, y_pos, '•', ha='center', va='center',
                       fontsize=16, color=self.colors['accent'],
                       transform=ax.transAxes)
                
                # 인사이트 텍스트
                ax.text(0.15, y_pos, insight, ha='left', va='center',
                       fontsize=11, color=self.colors['dark_gray'],
                       transform=ax.transAxes, wrap=True)
            
            # 배경 박스
            bg_height = min(len(insights_list) * 0.15 + 0.2, 0.8)
            bg_rect = patches.Rectangle((0.05, 0.95 - bg_height), 0.9, bg_height,
                                      linewidth=2, edgecolor=self.colors['primary'],
                                      facecolor=self.colors['light_gray'], alpha=0.1,
                                      transform=ax.transAxes)
            ax.add_patch(bg_rect)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 인사이트 박스 생성 실패: {str(e)}")
            return None
    
    def create_complete_cover_page(self, company_name, metrics_data, channel_data, insights):
        """완전한 커버 페이지 생성"""
        try:
            fig = plt.figure(figsize=(8.27, 11.69), facecolor='white')  # A4 비율
            
            # 그리드 레이아웃 설정
            gs = fig.add_gridspec(4, 2, height_ratios=[1, 2, 1.5, 1], 
                                 width_ratios=[1, 1], hspace=0.3, wspace=0.2)
            
            # 1. 헤더 (전체 너비)
            ax_header = fig.add_subplot(gs[0, :])
            ax_header.axis('off')
            
            # B-Flow 로고 및 제목
            ax_header.text(0.05, 0.7, 'B-FLOW', ha='left', va='center',
                          fontsize=24, fontweight='bold', color=self.colors['primary'],
                          transform=ax_header.transAxes)
            ax_header.text(0.05, 0.3, '입점사 성과 리포트', ha='left', va='center',
                          fontsize=14, color=self.colors['medium_gray'],
                          transform=ax_header.transAxes)
            
            # 회사명 (오른쪽)
            ax_header.text(0.95, 0.5, company_name, ha='right', va='center',
                          fontsize=20, fontweight='bold', color=self.colors['secondary'],
                          transform=ax_header.transAxes)
            
            # 날짜 정보
            date_range = metrics_data['basic']['date_range']
            ax_header.text(0.05, 0.1, f"{date_range['start']} ~ {date_range['end']}", 
                          ha='left', va='center', fontsize=10, color=self.colors['dark_gray'],
                          transform=ax_header.transAxes)
            
            # 2. KPI 섹션 (전체 너비)
            ax_kpi = fig.add_subplot(gs[1, :])
            ax_kpi.axis('off')
            
            # KPI 카드들
            kpis = [
                ('총 주문수', metrics_data['basic']['total_orders'], 
                 metrics_data['growth']['order_growth'], 'count'),
                ('총 매출액', metrics_data['basic']['total_revenue'], 
                 metrics_data['growth']['revenue_growth'], 'currency'),
                ('평균 주문금액', metrics_data['basic']['avg_order_value'], 
                 metrics_data['growth']['aov_growth'], 'currency'),
                ('시장 점유율', metrics_data['benchmark']['market_share']['revenue'], 
                 None, 'percentage')
            ]
            
            for i, (label, value, growth, format_type) in enumerate(kpis):
                x_pos = 0.125 + (i * 0.25)
                
                # KPI 값
                if format_type == 'currency':
                    formatted_value = self.format_currency(value)
                elif format_type == 'percentage':
                    formatted_value = f'{value:.1f}%'
                elif format_type == 'count':
                    formatted_value = f'{value:,}'
                else:
                    formatted_value = str(value)
                
                # 메인 값
                ax_kpi.text(x_pos, 0.7, formatted_value, ha='center', va='center',
                           fontsize=16, fontweight='bold', color=self.colors['primary'],
                           transform=ax_kpi.transAxes)
                
                # 라벨
                ax_kpi.text(x_pos, 0.5, label, ha='center', va='center',
                           fontsize=10, color=self.colors['medium_gray'],
                           transform=ax_kpi.transAxes)
                
                # 성장률
                if growth is not None:
                    growth_color = self.colors['success'] if growth >= 0 else self.colors['danger']
                    growth_symbol = '+' if growth >= 0 else ''
                    ax_kpi.text(x_pos, 0.3, f'{growth_symbol}{growth:.1f}%',
                               ha='center', va='center', fontsize=12, fontweight='bold',
                               color=growth_color, transform=ax_kpi.transAxes)
                
                # KPI 박스
                rect = patches.Rectangle((x_pos-0.1, 0.1), 0.2, 0.8,
                                       linewidth=1, edgecolor=self.colors['border'],
                                       facecolor=self.colors['light_gray'], alpha=0.3,
                                       transform=ax_kpi.transAxes)
                ax_kpi.add_patch(rect)
            
            # 3. 채널 하이라이트 (왼쪽)
            ax_channel = fig.add_subplot(gs[2, 0])
            ax_channel.axis('off')
            
            ax_channel.text(0.5, 0.9, '주요 채널', ha='center', va='center',
                           fontsize=14, fontweight='bold', color=self.colors['dark_gray'],
                           transform=ax_channel.transAxes)
            
            # 상위 2개 채널
            top_channels = list(channel_data.head(2).iterrows())
            for i, (channel, data) in enumerate(top_channels):
                y_pos = 0.6 - (i * 0.3)
                ax_channel.text(0.1, y_pos, f"{i+1}. {channel}", ha='left', va='center',
                               fontsize=12, fontweight='bold', color=self.colors['primary'],
                               transform=ax_channel.transAxes)
                ax_channel.text(0.9, y_pos, f"{data['매출점유율']:.1f}%", ha='right', va='center',
                               fontsize=12, fontweight='bold', color=self.colors['secondary'],
                               transform=ax_channel.transAxes)
            
            # 4. 인사이트 (오른쪽)
            ax_insights = fig.add_subplot(gs[2, 1])
            ax_insights.axis('off')
            
            ax_insights.text(0.5, 0.9, '📊 핵심 인사이트', ha='center', va='center',
                            fontsize=14, fontweight='bold', color=self.colors['primary'],
                            transform=ax_insights.transAxes)
            
            # 인사이트 목록
            for i, insight in enumerate(insights[:3]):
                y_pos = 0.7 - (i * 0.2)
                ax_insights.text(0.05, y_pos, '•', ha='left', va='center',
                                fontsize=12, color=self.colors['accent'],
                                transform=ax_insights.transAxes)
                ax_insights.text(0.15, y_pos, insight[:40] + ('...' if len(insight) > 40 else ''), 
                                ha='left', va='center', fontsize=9, 
                                color=self.colors['dark_gray'],
                                transform=ax_insights.transAxes)
            
            # 5. 하단 구분선
            ax_footer = fig.add_subplot(gs[3, :])
            ax_footer.axis('off')
            
            # 구분선
            line = patches.Rectangle((0.05, 0.8), 0.9, 0.01,
                                   facecolor=self.colors['primary'],
                                   transform=ax_footer.transAxes)
            ax_footer.add_patch(line)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 완전한 커버 페이지 생성 실패: {str(e)}")
            return None

# 테스트 함수
def test_cover_page_generator():
    """커버 페이지 생성기 테스트"""
    print("🧪 커버 페이지 생성기 테스트 시작...")
    
    try:
        import pandas as pd
        
        # 테스트 데이터
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
                'market_share': {'revenue': 4.35}
            }
        }
        
        test_channels = pd.DataFrame({
            '주문수': [150, 120, 80, 66],
            '총매출': [3500000, 2800000, 1900000, 1500000],
            '매출점유율': [35.0, 28.0, 19.0, 15.0]
        }, index=['SSG', '카페24', '쿠팡', '11번가'])
        
        test_insights = [
            "매출 성장세가 매우 우수합니다",
            "SSG 채널에서 강세를 보이고 있습니다", 
            "평균 주문금액이 플랫폼 평균보다 높습니다"
        ]
        
        # CoverPageGenerator 초기화
        cover_gen = CoverPageGenerator()
        print("✅ CoverPageGenerator 초기화 완료")
        
        # 1. 로고 생성
        logo_buffer = cover_gen.create_bflow_logo()
        if logo_buffer:
            print("✅ B-Flow 로고 생성 완료")
        
        # 2. 완전한 커버 페이지 생성
        complete_cover = cover_gen.create_complete_cover_page(
            "포레스트핏", test_metrics, test_channels, test_insights
        )
        if complete_cover:
            print("✅ 완전한 커버 페이지 생성 완료")
        
        print("🎉 커버 페이지 생성기 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_cover_page_generator()
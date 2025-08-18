# charts/benchmark_charts.py - 벤치마크 비교 및 제안 차트 생성

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .base_chart import BaseChart
import sys
sys.path.append('..')
from config import COLORS, REPORT_TEXTS

class BenchmarkCharts(BaseChart):
    """벤치마크 비교 및 전략 제안 차트 생성 클래스"""
    
    def __init__(self):
        super().__init__()
    
    def create_market_share_comparison(self, benchmark_data, company_name, title="플랫폼 내 시장 점유율"):
        """시장 점유율 비교 차트"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 데이터 준비
            if 'market_share' in benchmark_data:
                company_orders_share = benchmark_data['market_share']['orders']
                company_revenue_share = benchmark_data['market_share']['revenue']
            else:
                company_orders_share = 4.35
                company_revenue_share = 4.65
            
            # 경쟁사 데이터 시뮬레이션
            competitors = ['A사', 'B사', 'C사', 'D사', '기타']
            competitors_orders = [8.2, 6.8, 5.4, 4.1, 71.15]  # 나머지
            competitors_revenue = [9.1, 7.3, 5.8, 4.5, 68.65]  # 나머지
            
            # 회사 데이터 추가
            all_companies = [company_name] + competitors
            all_orders = [company_orders_share] + competitors_orders
            all_revenue = [company_revenue_share] + competitors_revenue
            
            # 색상 설정 (자사는 강조)
            colors = [self.colors['primary']] + [self.colors['light_gray']] * len(competitors)
            colors[1] = self.colors['secondary']  # 주요 경쟁사 강조
            
            # 1. 주문량 점유율 (좌측)
            bars1 = ax1.bar(all_companies, all_orders, color=colors, alpha=0.8)
            
            # 자사 막대 강조
            bars1[0].set_color(self.colors['primary'])
            bars1[0].set_alpha(1.0)
            
            for bar, share in zip(bars1, all_orders):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{share:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax1.set_title('주문량 기준 점유율', fontweight='bold')
            ax1.set_ylabel('점유율 (%)')
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            
            # 2. 매출액 점유율 (우측)
            bars2 = ax2.bar(all_companies, all_revenue, color=colors, alpha=0.8)
            
            # 자사 막대 강조
            bars2[0].set_color(self.colors['primary'])
            bars2[0].set_alpha(1.0)
            
            for bar, share in zip(bars2, all_revenue):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{share:.1f}%', ha='center', va='bottom', fontweight='bold')
            
            ax2.set_title('매출액 기준 점유율', fontweight='bold')
            ax2.set_ylabel('점유율 (%)')
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # 스타일 적용
            for ax in [ax1, ax2]:
                self.apply_minimal_style(ax)
                
            plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 시장 점유율 비교 차트 생성 실패: {str(e)}")
            return None
    
    def create_performance_radar_chart(self, benchmark_data, company_name, title="종합 성과 레이더 차트"):
        """성과 지표 레이더 차트"""
        try:
            fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
            
            # 평가 지표
            categories = ['매출 성장률', '주문량 증가', '평균 주문금액', '배송 완료율', '고객 만족도', '시장 점유율']
            
            # 자사 성과 (0-100 스케일)
            if 'performance_vs_platform' in benchmark_data:
                aov_performance = max(50, min(100, 50 + benchmark_data['performance_vs_platform']['aov_difference']))
            else:
                aov_performance = 75
            
            company_scores = [85, 80, aov_performance, 75, 82, 65]  # 시뮬레이션
            
            # 업계 평균 (벤치마크)
            industry_avg = [70, 65, 60, 70, 75, 50]
            
            # 각도 계산
            angles = np.linspace(0, 2 * np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # 닫힌 도형을 위해 첫 번째 값 추가
            
            company_scores += company_scores[:1]
            industry_avg += industry_avg[:1]
            
            # 자사 성과 플롯
            ax.plot(angles, company_scores, 'o-', linewidth=2, label=company_name,
                   color=self.colors['primary'])
            ax.fill(angles, company_scores, alpha=0.25, color=self.colors['primary'])
            
            # 업계 평균 플롯
            ax.plot(angles, industry_avg, 'o--', linewidth=2, label='업계 평균',
                   color=self.colors['medium_gray'])
            ax.fill(angles, industry_avg, alpha=0.1, color=self.colors['medium_gray'])
            
            # 카테고리 라벨
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=11)
            
            # 반경 설정
            ax.set_ylim(0, 100)
            ax.set_yticks([20, 40, 60, 80, 100])
            ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=9)
            
            # 그리드 스타일
            ax.grid(True, alpha=0.3)
            
            # 범례
            ax.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            
            # 제목
            plt.title(title, size=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 레이더 차트 생성 실패: {str(e)}")
            return None
    
    def create_growth_projection_chart(self, current_metrics, title="성장 전망 및 목표"):
        """성장 전망 차트"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 현재 지표
            current_revenue = current_metrics['basic']['total_revenue']
            current_orders = current_metrics['basic']['total_orders']
            
            # 월별 전망 (6개월)
            months = ['8월', '9월', '10월', '11월', '12월', '1월']
            
            # 매출 전망 (15% 성장 추세)
            revenue_base = current_revenue
            revenue_projection = []
            for i in range(6):
                monthly_growth = 1 + (0.15 / 12)  # 월 1.25% 성장
                projected_value = revenue_base * (monthly_growth ** (i + 1))
                revenue_projection.append(projected_value)
            
            # 주문량 전망 (12% 성장 추세)
            orders_base = current_orders
            orders_projection = []
            for i in range(6):
                monthly_growth = 1 + (0.12 / 12)  # 월 1% 성장
                projected_value = orders_base * (monthly_growth ** (i + 1))
                orders_projection.append(int(projected_value))
            
            # 1. 매출 전망 (좌측)
            line1 = ax1.plot(months, revenue_projection, marker='o', linewidth=3,
                           color=self.colors['primary'], markersize=8, markerfacecolor='white',
                           markeredgewidth=2, markeredgecolor=self.colors['primary'])
            
            # 현재 값 표시
            ax1.axhline(y=current_revenue, color=self.colors['medium_gray'], 
                       linestyle='--', alpha=0.7, label='현재 수준')
            
            # 목표선 (20% 증가)
            target_revenue = current_revenue * 1.2
            ax1.axhline(y=target_revenue, color=self.colors['success'], 
                       linestyle='-.', alpha=0.8, label='목표 수준 (+20%)')
            
            # 영역 채우기
            ax1.fill_between(months, revenue_projection, current_revenue, 
                           alpha=0.3, color=self.colors['primary'])
            
            ax1.set_title('매출 성장 전망', fontweight='bold')
            ax1.set_ylabel('매출액')
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: self.format_currency(x)))
            ax1.legend()
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            
            # 2. 주문량 전망 (우측)
            line2 = ax2.plot(months, orders_projection, marker='s', linewidth=3,
                           color=self.colors['secondary'], markersize=8, markerfacecolor='white',
                           markeredgewidth=2, markeredgecolor=self.colors['secondary'])
            
            # 현재 값 표시
            ax2.axhline(y=current_orders, color=self.colors['medium_gray'], 
                       linestyle='--', alpha=0.7, label='현재 수준')
            
            # 목표선 (15% 증가)
            target_orders = current_orders * 1.15
            ax2.axhline(y=target_orders, color=self.colors['success'], 
                       linestyle='-.', alpha=0.8, label='목표 수준 (+15%)')
            
            # 영역 채우기
            ax2.fill_between(months, orders_projection, current_orders, 
                           alpha=0.3, color=self.colors['secondary'])
            
            ax2.set_title('주문량 성장 전망', fontweight='bold')
            ax2.set_ylabel('주문 건수')
            ax2.legend()
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # 스타일 적용
            for ax in [ax1, ax2]:
                self.apply_minimal_style(ax)
            
            plt.suptitle(title, fontsize=16, fontweight='bold', y=1.02)
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 성장 전망 차트 생성 실패: {str(e)}")
            return None
    
    def create_strategic_recommendations(self, metrics_data, title="전략적 개선 제안"):
        """전략적 개선 제안 차트"""
        try:
            fig, ax = self.create_figure(size='large')
            ax.axis('off')
            
            # 제목
            ax.text(0.5, 0.95, title, ha='center', va='top',
                   fontsize=18, fontweight='bold', color=self.colors['primary'],
                   transform=ax.transAxes)
            
            # 구분선
            ax.axhline(y=0.88, xmin=0.1, xmax=0.9, color=self.colors['primary'], 
                      linewidth=3, transform=ax.transAxes)
            
            # 현재 성과 요약
            current_revenue = metrics_data['basic']['total_revenue']
            revenue_growth = metrics_data['growth']['revenue_growth']
            market_share = metrics_data['benchmark']['market_share']['revenue']
            
            ax.text(0.05, 0.8, '📊 현재 성과', ha='left', va='center',
                   fontsize=16, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            performance_summary = [
                f"• 총 매출: {self.format_currency(current_revenue)} (성장률: {revenue_growth:+.1f}%)",
                f"• 시장 점유율: {market_share:.2f}% (상위 5위권 진입)",
                f"• 주요 강점: 높은 평균 주문금액, 안정적인 고객층"
            ]
            
            y_pos = 0.72
            for summary in performance_summary:
                ax.text(0.1, y_pos, summary, ha='left', va='center',
                       fontsize=12, color=self.colors['dark_gray'],
                       transform=ax.transAxes)
                y_pos -= 0.06
            
            # 개선 영역 분석
            ax.text(0.05, 0.5, '🎯 개선 우선순위', ha='left', va='center',
                   fontsize=16, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            # 우선순위별 제안
            recommendations = [
                {
                    'priority': '높음',
                    'area': '채널 다변화',
                    'action': '신규 채널 진출로 매출 확대',
                    'impact': '+20% 매출 증대 기대',
                    'color': self.colors['danger']
                },
                {
                    'priority': '중간',
                    'area': '고객 리텐션',
                    'action': '재구매율 향상 프로그램 도입',
                    'impact': '+15% 고객 재방문율',
                    'color': self.colors['accent']
                },
                {
                    'priority': '낮음',
                    'area': '운영 효율성',
                    'action': '배송 시스템 최적화',
                    'impact': '+10% 고객 만족도',
                    'color': self.colors['success']
                }
            ]
            
            y_start = 0.42
            for i, rec in enumerate(recommendations):
                y_base = y_start - (i * 0.12)
                
                # 우선순위 배지
                priority_rect = plt.Rectangle((0.08, y_base - 0.02), 0.06, 0.04,
                                            facecolor=rec['color'], alpha=0.8,
                                            transform=ax.transAxes)
                ax.add_patch(priority_rect)
                
                ax.text(0.11, y_base, rec['priority'], ha='center', va='center',
                       fontsize=10, fontweight='bold', color='white',
                       transform=ax.transAxes)
                
                # 제안 내용
                ax.text(0.18, y_base + 0.01, f"[{rec['area']}] {rec['action']}", 
                       ha='left', va='center', fontsize=12, fontweight='bold',
                       color=self.colors['dark_gray'], transform=ax.transAxes)
                
                ax.text(0.18, y_base - 0.015, f"기대 효과: {rec['impact']}", 
                       ha='left', va='center', fontsize=10,
                       color=self.colors['medium_gray'], transform=ax.transAxes)
            
            # 실행 로드맵
            ax.text(0.05, 0.05, '🗓 실행 로드맵', ha='left', va='center',
                   fontsize=16, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            timeline = [
                "1Q: 신규 채널 파트너십 체결 및 테스트 론칭",
                "2Q: 고객 데이터 분석 기반 개인화 서비스 도입",
                "3Q: 배송 네트워크 확장 및 물류 시스템 업그레이드",
                "4Q: 성과 분석 및 차년도 전략 수립"
            ]
            
            y_pos = -0.03
            for milestone in timeline:
                ax.text(0.1, y_pos, f"• {milestone}", ha='left', va='center',
                       fontsize=10, color=self.colors['dark_gray'],
                       transform=ax.transAxes)
                y_pos -= 0.04
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 전략 제안 차트 생성 실패: {str(e)}")
            return None
    
    def create_competitive_positioning_chart(self, benchmark_data, company_name, title="경쟁사 포지셔닝 분석"):
        """경쟁사 포지셔닝 매트릭스"""
        try:
            fig, ax = self.create_figure(size='large')
            
            # 경쟁사 데이터 (시뮬레이션)
            companies = [company_name, 'A사', 'B사', 'C사', 'D사', 'E사']
            
            # X축: 시장 점유율, Y축: 성장률
            market_shares = [4.65, 8.2, 6.8, 5.4, 4.1, 3.2]  # %
            growth_rates = [12.1, 8.5, 15.2, 6.3, 18.7, -2.1]  # %
            
            # 버블 크기: 평균 주문금액 (상대적)
            if 'avg_order_value' in benchmark_data.get('basic', {}):
                company_aov = benchmark_data['basic']['avg_order_value']
            else:
                company_aov = 25000
            
            bubble_sizes = [company_aov, 22000, 28000, 18000, 31000, 15000]
            # 버블 크기 정규화 (50-500 범위)
            min_size, max_size = min(bubble_sizes), max(bubble_sizes)
            normalized_sizes = [50 + (size - min_size) / (max_size - min_size) * 450 
                              for size in bubble_sizes]
            
            # 색상 설정 (자사 강조)
            colors = [self.colors['primary']] + [self.colors['light_gray']] * (len(companies) - 1)
            alphas = [0.8] + [0.6] * (len(companies) - 1)
            
            # 버블 차트 생성
            for i, (company, x, y, size, color, alpha) in enumerate(
                zip(companies, market_shares, growth_rates, normalized_sizes, colors, alphas)):
                
                ax.scatter(x, y, s=size, c=color, alpha=alpha, 
                          edgecolors='white', linewidth=2, label=company if i == 0 else "")
                
                # 회사명 라벨
                if company == company_name:
                    ax.annotate(company, (x, y), xytext=(5, 5), textcoords='offset points',
                               fontsize=12, fontweight='bold', color=self.colors['primary'])
                else:
                    ax.annotate(company, (x, y), xytext=(5, 5), textcoords='offset points',
                               fontsize=10, color=self.colors['dark_gray'])
            
            # 사분면 구분선
            avg_share = np.mean(market_shares)
            avg_growth = np.mean(growth_rates)
            
            ax.axvline(x=avg_share, color=self.colors['medium_gray'], 
                      linestyle='--', alpha=0.5)
            ax.axhline(y=avg_growth, color=self.colors['medium_gray'], 
                      linestyle='--', alpha=0.5)
            
            # 사분면 라벨
            ax.text(avg_share + 0.5, max(growth_rates) - 1, 'Star\n(높은점유율,높은성장)', 
                   ha='left', va='top', fontsize=10, style='italic',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['success'], alpha=0.3))
            
            ax.text(max(market_shares) - 1, avg_growth - 1, 'Cash Cow\n(높은점유율,낮은성장)', 
                   ha='right', va='top', fontsize=10, style='italic',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['accent'], alpha=0.3))
            
            ax.text(avg_share - 1, max(growth_rates) - 1, 'Question Mark\n(낮은점유율,높은성장)', 
                   ha='right', va='top', fontsize=10, style='italic',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['warning'], alpha=0.3))
            
            ax.text(avg_share - 1, min(growth_rates) + 1, 'Dog\n(낮은점유율,낮은성장)', 
                   ha='right', va='bottom', fontsize=10, style='italic',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['danger'], alpha=0.3))
            
            # 축 설정
            ax.set_xlabel('시장 점유율 (%)', fontsize=12)
            ax.set_ylabel('성장률 (%)', fontsize=12)
            ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
            
            # 범례 (버블 크기 설명)
            legend_sizes = [15000, 25000, 35000]
            legend_bubbles = [50, 250, 450]
            
            for size, bubble in zip(legend_sizes, legend_bubbles):
                ax.scatter([], [], s=bubble, c=self.colors['medium_gray'], alpha=0.6,
                          label=f'AOV: {self.format_currency(size)}')
            
            ax.legend(loc='upper left', title='평균 주문금액', frameon=True)
            
            # 스타일 적용
            self.apply_minimal_style(ax)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 경쟁사 포지셔닝 차트 생성 실패: {str(e)}")
            return None
    
    def create_next_month_forecast(self, current_metrics, title="다음 달 전망"):
        """다음 달 전망 요약"""
        try:
            fig, ax = self.create_figure(size='medium')
            ax.axis('off')
            
            # 제목
            ax.text(0.5, 0.95, title, ha='center', va='top',
                   fontsize=18, fontweight='bold', color=self.colors['primary'],
                   transform=ax.transAxes)
            
            # 현재 성과 기반 예측
            current_revenue = current_metrics['basic']['total_revenue']
            current_orders = current_metrics['basic']['total_orders']
            revenue_growth = current_metrics['growth']['revenue_growth']
            
            # 다음 달 예측 (현재 성장률 기반)
            monthly_growth_rate = revenue_growth / 12  # 월 성장률
            next_month_revenue = current_revenue * (1 + monthly_growth_rate / 100)
            next_month_orders = current_orders * (1 + (monthly_growth_rate * 0.8) / 100)
            
            # 예측 지표 박스
            forecasts = [
                {
                    'label': '예상 매출액',
                    'value': self.format_currency(next_month_revenue),
                    'change': f'+{monthly_growth_rate:.1f}%',
                    'color': self.colors['success']
                },
                {
                    'label': '예상 주문수',
                    'value': f'{int(next_month_orders):,}건',
                    'change': f'+{monthly_growth_rate*0.8:.1f}%',
                    'color': self.colors['primary']
                },
                {
                    'label': '목표 AOV',
                    'value': self.format_currency(current_metrics['basic']['avg_order_value'] * 1.05),
                    'change': '+5.0%',
                    'color': self.colors['accent']
                }
            ]
            
            y_start = 0.75
            for i, forecast in enumerate(forecasts):
                y_pos = y_start - (i * 0.15)
                
                # 박스 배경
                rect = plt.Rectangle((0.1, y_pos - 0.05), 0.8, 0.1,
                                   facecolor=forecast['color'], alpha=0.1,
                                   transform=ax.transAxes)
                ax.add_patch(rect)
                
                # 라벨
                ax.text(0.15, y_pos, forecast['label'], ha='left', va='center',
                       fontsize=12, fontweight='bold', color=self.colors['dark_gray'],
                       transform=ax.transAxes)
                
                # 값
                ax.text(0.85, y_pos + 0.02, forecast['value'], ha='right', va='center',
                       fontsize=14, fontweight='bold', color=forecast['color'],
                       transform=ax.transAxes)
                
                # 변화율
                ax.text(0.85, y_pos - 0.02, forecast['change'], ha='right', va='center',
                       fontsize=10, color=forecast['color'],
                       transform=ax.transAxes)
            
            # 주요 이벤트 및 기회
            ax.text(0.5, 0.25, '🎯 주요 기회 요소', ha='center', va='center',
                   fontsize=14, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            opportunities = [
                "추석 시즌 특별 프로모션 기대",
                "신규 상품 라인 출시 예정",
                "주요 채널 마케팅 캠페인 진행"
            ]
            
            y_pos = 0.15
            for opp in opportunities:
                ax.text(0.1, y_pos, f"• {opp}", ha='left', va='center',
                       fontsize=11, color=self.colors['dark_gray'],
                       transform=ax.transAxes)
                y_pos -= 0.04
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 다음 달 전망 생성 실패: {str(e)}")
            return None
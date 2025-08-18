# charts/product_charts.py - 상품 및 배송 관련 차트 생성

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from .base_chart import BaseChart
import sys
sys.path.append('..')
from config import COLORS

class ProductCharts(BaseChart):
    """상품 및 배송 관련 차트 생성 클래스"""
    
    def __init__(self):
        super().__init__()
    
    def create_bestseller_chart(self, product_data, title="베스트셀러 TOP 10", top_n=10):
        """베스트셀러 상품 차트 생성"""
        try:
            fig, ax = self.create_figure(size='large')
            
            # 데이터 준비
            if isinstance(product_data, pd.DataFrame):
                # 매출 기준 정렬
                top_products = product_data.sort_values('총매출', ascending=True).tail(top_n)
                product_names = top_products.index.tolist()
                revenues = top_products['총매출'].values
            else:
                # 딕셔너리 형태인 경우
                sorted_products = sorted(product_data.items(), key=lambda x: x[1], reverse=True)[:top_n]
                product_names = [name[:30] + '...' if len(name) > 30 else name 
                               for name, _ in reversed(sorted_products)]
                revenues = [revenue for _, revenue in reversed(sorted_products)]
            
            # 상품명 정리 (너무 길면 줄임)
            clean_names = []
            for name in product_names:
                if len(name) > 25:
                    # 키워드 추출 시도
                    if '/' in name:
                        clean_name = name.split('/')[0][:25] + '...'
                    else:
                        clean_name = name[:25] + '...'
                else:
                    clean_name = name
                clean_names.append(clean_name)
            
            # 수평 막대 차트
            colors = [self.colors['primary'] if i == len(revenues)-1 else self.colors['light_gray'] 
                     for i in range(len(revenues))]
            colors[-1] = self.colors['primary']  # 1위 강조
            if len(colors) > 1:
                colors[-2] = self.colors['secondary']  # 2위 강조
            if len(colors) > 2:
                colors[-3] = self.colors['accent']  # 3위 강조
            
            bars = ax.barh(range(len(clean_names)), revenues, 
                          color=colors, alpha=0.8, height=0.7)
            
            # 순위 표시
            for i, (bar, revenue) in enumerate(zip(bars, revenues)):
                rank = len(revenues) - i
                
                # 매출액 라벨
                ax.text(revenue + max(revenues) * 0.02, bar.get_y() + bar.get_height()/2,
                       self.format_currency(revenue), va='center', fontsize=10, fontweight='bold')
                
                # 순위 배지
                if rank <= 3:
                    badge_colors = {1: self.colors['primary'], 2: self.colors['secondary'], 3: self.colors['accent']}
                    ax.text(max(revenues) * 0.02, bar.get_y() + bar.get_height()/2,
                           f'{rank}위', va='center', ha='left', fontsize=9, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.3', facecolor=badge_colors[rank], 
                                   alpha=0.8, edgecolor='white'),
                           color='white')
            
            ax.set_yticks(range(len(clean_names)))
            ax.set_yticklabels(clean_names, fontsize=10)
            
            # 스타일 적용
            self.apply_minimal_style(ax, title=title, xlabel='매출액', ylabel='상품명')
            
            # Y축 라벨 색상 조정
            ax.tick_params(axis='y', colors=self.colors['dark_gray'])
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 베스트셀러 차트 생성 실패: {str(e)}")
            return None
    
    def create_order_status_pie_chart(self, status_data, title="주문 상태별 분포"):
        """주문 상태별 파이차트 생성"""
        try:
            fig, ax = self.create_figure(size='medium')
            
            # 데이터 준비
            if isinstance(status_data, dict):
                labels = list(status_data.keys())
                values = list(status_data.values())
            else:
                labels = status_data.index.tolist()
                values = status_data.values
            
            # 상태별 색상 매핑
            status_colors = {
                '배송완료': self.colors['success'],
                '출고완료': self.colors['primary'],
                '배송준비': self.colors['accent'],
                '배송중': self.colors['secondary'],
                '결제확인': self.colors['light_gray'],
                '결제취소': self.colors['danger'],
                '반품': self.colors['warning'],
                '교환': self.colors['medium_gray']
            }
            
            # 라벨에 맞는 색상 선택
            colors = [status_colors.get(label, self.colors['light_gray']) for label in labels]
            
            # 파이차트 생성
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                textprops={'fontsize': 11}
            )
            
            # 퍼센트 텍스트 스타일링
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            # 범례 추가 (건수 포함)
            legend_labels = [f'{label}: {value:,}건' for label, value in zip(labels, values)]
            ax.legend(wedges, legend_labels, loc="center left", 
                     bbox_to_anchor=(1, 0, 0.5, 1), frameon=False, fontsize=10)
            
            ax.set_title(title, fontsize=16, fontweight='bold', 
                        color=self.colors['dark_gray'], pad=20)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 주문 상태 파이차트 생성 실패: {str(e)}")
            return None
    
    def create_delivery_performance_chart(self, delivery_data, title="배송 성과 지표"):
        """배송 성과 지표 차트"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            
            # 기본 배송 지표 (시뮬레이션 포함)
            if isinstance(delivery_data, dict) and 'delivery_metrics' in delivery_data:
                metrics = delivery_data['delivery_metrics']
                completion_rate = metrics.get('completion_rate', 75.5)
                cancel_rate = metrics.get('cancel_rate', 5.2)
            else:
                completion_rate = 75.5
                cancel_rate = 5.2
            
            processing_rate = 100 - completion_rate - cancel_rate
            
            # 1. 배송 완료율 게이지 (좌상)
            self._create_gauge_chart(ax1, completion_rate, "배송 완료율", 
                                   self.colors['success'], "%")
            
            # 2. 취소율 게이지 (우상)
            self._create_gauge_chart(ax2, cancel_rate, "취소율", 
                                   self.colors['danger'], "%")
            
            # 3. 배송 방법별 분포 (좌하)
            delivery_methods = ['택배', '당일배송', '픽업', '기타']
            method_counts = [65, 20, 10, 5]  # 시뮬레이션
            
            bars3 = ax3.bar(delivery_methods, method_counts, 
                           color=[self.colors['primary'], self.colors['secondary'], 
                                 self.colors['accent'], self.colors['light_gray']])
            
            for bar, count in zip(bars3, method_counts):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{count}%', ha='center', va='bottom', fontweight='bold')
            
            ax3.set_title('배송 방법별 분포', fontweight='bold')
            ax3.set_ylabel('비율 (%)')
            
            # 4. 배송 시간 분포 (우하)
            delivery_days = ['당일', '1일', '2일', '3일', '4일+']
            day_percentages = [15, 45, 25, 10, 5]  # 시뮬레이션
            
            bars4 = ax4.bar(delivery_days, day_percentages,
                           color=self.colors['primary'], alpha=0.7)
            
            for bar, pct in zip(bars4, day_percentages):
                ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                        f'{pct}%', ha='center', va='bottom', fontweight='bold')
            
            ax4.set_title('배송 소요 시간 분포', fontweight='bold')
            ax4.set_ylabel('주문 비율 (%)')
            ax4.set_xlabel('배송 소요일')
            
            # 스타일 적용
            for ax in [ax3, ax4]:
                self.apply_minimal_style(ax)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 배송 성과 차트 생성 실패: {str(e)}")
            return None
    
    def _create_gauge_chart(self, ax, value, title, color, unit):
        """게이지 차트 생성 헬퍼 함수"""
        # 반원 게이지
        theta1, theta2 = 0, np.pi
        
        # 배경 반원
        theta_bg = np.linspace(theta1, theta2, 100)
        x_bg = np.cos(theta_bg)
        y_bg = np.sin(theta_bg)
        
        # 배경 그리기
        ax.fill_between(x_bg, y_bg, 0, color=self.colors['light_gray'], alpha=0.3)
        
        # 값에 따른 각도 계산
        value_angle = theta1 + (theta2 - theta1) * (value / 100)
        theta_val = np.linspace(theta1, value_angle, 100)
        x_val = np.cos(theta_val)
        y_val = np.sin(theta_val)
        
        # 값 반원 그리기
        ax.fill_between(x_val, y_val, 0, color=color, alpha=0.8)
        
        # 중앙 텍스트
        ax.text(0, 0.3, f'{value:.1f}{unit}', ha='center', va='center',
               fontsize=16, fontweight='bold', color=color)
        ax.text(0, 0.1, title, ha='center', va='center',
               fontsize=12, color=self.colors['dark_gray'])
        
        # 축 설정
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
    
    def create_product_category_analysis(self, product_data, title="상품 카테고리 분석"):
        """상품 카테고리별 분석 차트"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 카테고리별 데이터 시뮬레이션 (실제로는 상품명에서 추출)
            categories = ['의류', '액세서리', '신발', '가방', '기타']
            category_counts = [45, 25, 15, 10, 5]  # 시뮬레이션
            category_revenue = [4500000, 2800000, 1900000, 1200000, 600000]  # 시뮬레이션
            
            # 1. 카테고리별 상품 수 (좌측)
            bars1 = ax1.bar(categories, category_counts, 
                           color=self.get_color_palette(len(categories)), alpha=0.8)
            
            for bar, count in zip(bars1, category_counts):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{count}개', ha='center', va='bottom', fontweight='bold')
            
            ax1.set_title('카테고리별 상품 수', fontweight='bold')
            ax1.set_ylabel('상품 수')
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            
            # 2. 카테고리별 매출 (우측)
            bars2 = ax2.bar(categories, category_revenue,
                           color=self.get_color_palette(len(categories)), alpha=0.8)
            
            for bar, revenue in zip(bars2, category_revenue):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(category_revenue)*0.02,
                        self.format_currency(revenue), ha='center', va='bottom', 
                        fontweight='bold', fontsize=9)
            
            ax2.set_title('카테고리별 매출', fontweight='bold')
            ax2.set_ylabel('매출액')
            ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: self.format_currency(x)))
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # 스타일 적용
            for ax in [ax1, ax2]:
                self.apply_minimal_style(ax)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 상품 카테고리 분석 차트 생성 실패: {str(e)}")
            return None
    
    def create_inventory_status_chart(self, product_data, title="재고 현황 분석"):
        """재고 현황 분석 차트 (시뮬레이션)"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            
            # 1. 재고 상태 분포 (좌상)
            stock_status = ['정상', '부족', '과다', '품절']
            stock_counts = [60, 25, 10, 5]
            colors_stock = [self.colors['success'], self.colors['warning'], 
                           self.colors['accent'], self.colors['danger']]
            
            wedges1, texts1, autotexts1 = ax1.pie(stock_counts, labels=stock_status,
                                                 autopct='%1.1f%%', colors=colors_stock,
                                                 startangle=90)
            ax1.set_title('재고 상태 분포', fontweight='bold')
            
            # 2. 주문량 vs 재고량 (우상)
            if isinstance(product_data, pd.DataFrame) and '주문수' in product_data.columns:
                # 실제 데이터 사용
                top_5_products = product_data.head(5)
                product_names = [name[:15] + '...' if len(name) > 15 else name 
                               for name in top_5_products.index]
                order_counts = top_5_products['주문수'].values
                # 재고량은 시뮬레이션 (주문량의 2-5배)
                stock_levels = [count * np.random.uniform(2, 5) for count in order_counts]
            else:
                # 시뮬레이션 데이터
                product_names = ['상품A', '상품B', '상품C', '상품D', '상품E']
                order_counts = [45, 38, 32, 28, 22]
                stock_levels = [90, 76, 64, 112, 44]
            
            x = np.arange(len(product_names))
            width = 0.35
            
            bars1 = ax2.bar(x - width/2, order_counts, width, label='주문량',
                           color=self.colors['primary'], alpha=0.8)
            bars2 = ax2.bar(x + width/2, stock_levels, width, label='재고량',
                           color=self.colors['secondary'], alpha=0.8)
            
            ax2.set_title('상위 상품 주문량 vs 재고량', fontweight='bold')
            ax2.set_xticks(x)
            ax2.set_xticklabels(product_names, rotation=45, ha='right')
            ax2.legend()
            
            # 3. 회전율 분석 (좌하)
            turnover_labels = ['높음', '보통', '낮음']
            turnover_values = [30, 50, 20]
            colors_turnover = [self.colors['success'], self.colors['accent'], self.colors['warning']]
            
            bars3 = ax3.bar(turnover_labels, turnover_values, 
                           color=colors_turnover, alpha=0.8)
            
            for bar, value in zip(bars3, turnover_values):
                ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{value}%', ha='center', va='bottom', fontweight='bold')
            
            ax3.set_title('재고 회전율 분포', fontweight='bold')
            ax3.set_ylabel('상품 비율 (%)')
            
            # 4. 월별 재고 추이 (우하)
            months = ['1월', '2월', '3월', '4월', '5월', '6월']
            stock_trend = [100, 95, 105, 98, 110, 108]  # 시뮬레이션
            
            line4 = ax4.plot(months, stock_trend, marker='o', linewidth=2,
                           color=self.colors['primary'], markersize=6)
            ax4.fill_between(months, stock_trend, alpha=0.3, color=self.colors['primary'])
            
            ax4.set_title('월별 평균 재고 수준 추이', fontweight='bold')
            ax4.set_ylabel('재고 지수')
            plt.setp(ax4.get_xticklabels(), rotation=45, ha='right')
            
            # 스타일 적용
            for ax in [ax2, ax3, ax4]:
                self.apply_minimal_style(ax)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 재고 현황 차트 생성 실패: {str(e)}")
            return None
    
    def create_product_performance_summary(self, product_data, status_data, delivery_data):
        """상품 및 배송 성과 종합 요약"""
        try:
            fig, ax = self.create_figure(size='large')
            ax.axis('off')
            
            # 제목
            ax.text(0.5, 0.95, '📦 상품 & 배송 성과 요약', ha='center', va='top',
                   fontsize=18, fontweight='bold', color=self.colors['primary'],
                   transform=ax.transAxes)
            
            # 구분선
            ax.axhline(y=0.88, xmin=0.1, xmax=0.9, color=self.colors['primary'], 
                      linewidth=2, transform=ax.transAxes)
            
            # 상품 성과 섹션
            ax.text(0.05, 0.8, '🏆 상품 성과', ha='left', va='center',
                   fontsize=14, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            # 베스트셀러 정보
            if isinstance(product_data, pd.DataFrame):
                top_product = product_data.index[0] if len(product_data) > 0 else "데이터 없음"
                top_revenue = product_data.iloc[0]['총매출'] if len(product_data) > 0 else 0
                total_products = len(product_data)
                
                product_insights = [
                    f"• 총 판매 상품: {total_products}개",
                    f"• 베스트셀러: {top_product[:30]}{'...' if len(top_product) > 30 else ''}",
                    f"• 최고 매출 상품: {self.format_currency(top_revenue)}",
                    f"• 상위 20% 상품이 전체 매출의 약 60% 차지"
                ]
            else:
                product_insights = [
                    "• 다양한 상품 포트폴리오 운영 중",
                    "• 상위 상품들의 안정적인 성과",
                    "• 신상품 출시 및 기존 상품 관리 균형"
                ]
            
            y_pos = 0.72
            for insight in product_insights:
                ax.text(0.1, y_pos, insight, ha='left', va='center',
                       fontsize=11, color=self.colors['dark_gray'],
                       transform=ax.transAxes)
                y_pos -= 0.06
            
            # 배송 성과 섹션
            ax.text(0.05, 0.45, '🚚 배송 성과', ha='left', va='center',
                   fontsize=14, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            # 배송 지표
            if isinstance(delivery_data, dict) and 'delivery_metrics' in delivery_data:
                completion_rate = delivery_data['delivery_metrics'].get('completion_rate', 75.5)
                cancel_rate = delivery_data['delivery_metrics'].get('cancel_rate', 5.2)
            else:
                completion_rate = 75.5
                cancel_rate = 5.2
            
            delivery_insights = [
                f"• 배송 완료율: {completion_rate:.1f}% (우수 수준)",
                f"• 주문 취소율: {cancel_rate:.1f}% (양호 수준)",
                f"• 평균 배송 소요일: 1-2일 (빠른 배송)",
                f"• 고객 만족도: 배송 관련 긍정 피드백 증가"
            ]
            
            y_pos = 0.37
            for insight in delivery_insights:
                ax.text(0.1, y_pos, insight, ha='left', va='center',
                       fontsize=11, color=self.colors['dark_gray'],
                       transform=ax.transAxes)
                y_pos -= 0.06
            
            # 개선 제안 섹션
            ax.text(0.05, 0.1, '💡 개선 제안', ha='left', va='center',
                   fontsize=14, fontweight='bold', color=self.colors['accent'],
                   transform=ax.transAxes)
            
            recommendations = [
                "베스트셀러 상품의 재고 관리 최적화",
                "배송 지연 상품에 대한 고객 안내 강화",
                "신규 상품 출시 전략 수립"
            ]
            
            y_pos = 0.02
            for rec in recommendations:
                ax.text(0.1, y_pos, f"▶ {rec}", ha='left', va='center',
                       fontsize=10, color=self.colors['medium_gray'],
                       transform=ax.transAxes)
                y_pos -= 0.04
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 상품 성과 요약 생성 실패: {str(e)}")
            return None
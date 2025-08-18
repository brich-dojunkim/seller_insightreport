# charts/time_charts.py - 시간대별 분석 차트 생성

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
from .base_chart import BaseChart
import sys
sys.path.append('..')
from config import COLORS

class TimeCharts(BaseChart):
    """시간대별 분석 차트 생성 클래스"""
    
    def __init__(self):
        super().__init__()
    
    def create_hourly_heatmap(self, time_data, title="시간대별 주문 패턴"):
        """시간별 주문 패턴 히트맵 생성"""
        try:
            fig, ax = self.create_figure(size='large')
            
            # 24시간 x 7일 데이터 매트릭스 생성
            hours = list(range(24))
            days_korean = ['월', '화', '수', '목', '금', '토', '일']
            days_english = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            
            # 실제 시간별 데이터가 있다면 사용, 없으면 시뮬레이션
            if 'hourly_orders' in time_data:
                hourly_base = time_data['hourly_orders']
            else:
                # 기본 패턴 생성 (업무시간과 저녁시간에 피크)
                hourly_base = {}
                for h in hours:
                    if h in [10, 11, 14, 15, 20, 21]:  # 피크 시간
                        hourly_base[h] = np.random.randint(20, 40)
                    elif h in [6, 7, 8, 18, 19]:  # 준피크 시간
                        hourly_base[h] = np.random.randint(10, 25)
                    elif h in [0, 1, 2, 3, 4, 5]:  # 새벽 시간
                        hourly_base[h] = np.random.randint(1, 8)
                    else:  # 일반 시간
                        hourly_base[h] = np.random.randint(5, 18)
            
            # 요일별 패턴 적용하여 히트맵 데이터 생성
            heatmap_data = []
            for day_eng, day_kor in zip(days_english, days_korean):
                day_pattern = []
                for hour in hours:
                    base_value = hourly_base.get(hour, 10)
                    
                    # 요일별 가중치 적용
                    if day_eng in ['Saturday', 'Sunday']:  # 주말
                        if hour in [10, 11, 12, 14, 15, 16]:  # 주말 쇼핑 시간
                            weight = 1.4
                        elif hour in [20, 21, 22]:  # 주말 저녁
                            weight = 1.3
                        else:
                            weight = 0.8
                    else:  # 평일
                        if hour in [12, 13]:  # 점심시간
                            weight = 1.2
                        elif hour in [20, 21]:  # 퇴근 후
                            weight = 1.5
                        elif hour in [9, 10, 11]:  # 오전 업무시간
                            weight = 1.1
                        else:
                            weight = 1.0
                    
                    final_value = int(base_value * weight)
                    day_pattern.append(final_value)
                
                heatmap_data.append(day_pattern)
            
            # 히트맵 생성
            heatmap_array = np.array(heatmap_data)
            
            # 색상맵 설정 (블루 계열)
            im = ax.imshow(heatmap_array, cmap='Blues', aspect='auto', interpolation='nearest')
            
            # 축 설정
            ax.set_xticks(range(24))
            ax.set_xticklabels([f'{h:02d}' for h in hours])
            ax.set_yticks(range(7))
            ax.set_yticklabels(days_korean)
            
            # 라벨
            ax.set_xlabel('시간 (24시간)', fontsize=12)
            ax.set_ylabel('요일', fontsize=12)
            
            # 값 표시 (옵션 - 너무 많으면 생략)
            if heatmap_array.max() < 100:  # 값이 크지 않을 때만 표시
                for i in range(len(days_korean)):
                    for j in range(24):
                        value = heatmap_array[i, j]
                        if value > heatmap_array.max() * 0.7:  # 높은 값만 흰색
                            text_color = 'white'
                        else:
                            text_color = 'black'
                        
                        if j % 3 == 0:  # 3시간마다만 표시 (가독성)
                            ax.text(j, i, f'{value}', ha='center', va='center',
                                   color=text_color, fontsize=8, fontweight='bold')
            
            # 컬러바
            cbar = plt.colorbar(im, ax=ax, shrink=0.6)
            cbar.set_label('주문 건수', rotation=270, labelpad=15)
            
            # 제목
            ax.set_title(title, fontsize=16, fontweight='bold', 
                        color=self.colors['dark_gray'], pad=20)
            
            # 그리드 제거
            ax.grid(False)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 히트맵 생성 실패: {str(e)}")
            return None
    
    def create_daily_trend_chart(self, time_data, title="요일별 매출 트렌드"):
        """요일별 매출 트렌드 차트 생성"""
        try:
            fig, ax = self.create_figure(size='medium')
            
            # 요일별 데이터 준비
            if 'daily_revenue' in time_data:
                daily_data = time_data['daily_revenue']
                days = list(daily_data.keys())
                values = list(daily_data.values())
            else:
                # 시뮬레이션 데이터
                days = ['월', '화', '수', '목', '금', '토', '일']
                # 주말에 더 높은 매출
                base_values = [100, 95, 90, 105, 110, 140, 135]
                values = [v * np.random.uniform(8000, 12000) for v in base_values]
            
            # 라인 차트 생성
            line = ax.plot(days, values, 
                          color=self.colors['primary'], linewidth=3, 
                          marker='o', markersize=8, markerfacecolor='white',
                          markeredgewidth=2, markeredgecolor=self.colors['primary'])
            
            # 영역 채우기 (그라데이션 효과)
            ax.fill_between(days, values, alpha=0.3, color=self.colors['primary'])
            
            # 최고/최저 포인트 강조
            max_idx = values.index(max(values))
            min_idx = values.index(min(values))
            
            ax.scatter(days[max_idx], values[max_idx], 
                      color=self.colors['success'], s=100, zorder=5)
            ax.scatter(days[min_idx], values[min_idx], 
                      color=self.colors['danger'], s=100, zorder=5)
            
            # 최고/최저 라벨
            ax.annotate(f'최고\n{self.format_currency(values[max_idx])}', 
                       xy=(days[max_idx], values[max_idx]),
                       xytext=(10, 20), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['success'], alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color=self.colors['success']),
                       fontsize=9, fontweight='bold', color='white')
            
            ax.annotate(f'최저\n{self.format_currency(values[min_idx])}', 
                       xy=(days[min_idx], values[min_idx]),
                       xytext=(10, -30), textcoords='offset points',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=self.colors['danger'], alpha=0.7),
                       arrowprops=dict(arrowstyle='->', color=self.colors['danger']),
                       fontsize=9, fontweight='bold', color='white')
            
            # Y축 포맷팅
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: self.format_currency(x)))
            
            # 스타일 적용
            self.apply_minimal_style(ax, title=title, xlabel='요일', ylabel='매출액')
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 요일별 트렌드 차트 생성 실패: {str(e)}")
            return None
    
    def create_peak_hours_analysis(self, time_data, title="피크 시간대 분석"):
        """피크 시간대 분석 차트"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 피크 시간대 데이터 준비
            if 'peak_hours' in time_data:
                peak_hours = time_data['peak_hours']['hours']
                peak_orders = time_data['peak_hours']['orders']
            else:
                # 시뮬레이션
                peak_hours = [11, 15, 21]
                peak_orders = [45, 38, 52]
            
            # 전체 시간대 데이터
            if 'hourly_orders' in time_data:
                hourly_data = time_data['hourly_orders']
            else:
                hourly_data = {h: np.random.randint(5, 30) for h in range(24)}
                # 피크 시간 강화
                for h in peak_hours:
                    hourly_data[h] = np.random.randint(35, 55)
            
            hours = list(hourly_data.keys())
            orders = list(hourly_data.values())
            
            # 1. 24시간 전체 패턴 (왼쪽)
            bars1 = ax1.bar(hours, orders, color=self.colors['light_gray'], alpha=0.7)
            
            # 피크 시간 강조
            for i, hour in enumerate(hours):
                if hour in peak_hours:
                    bars1[i].set_color(self.colors['primary'])
                    bars1[i].set_alpha(0.9)
            
            ax1.set_title('24시간 주문 패턴', fontsize=14, fontweight='bold')
            ax1.set_xlabel('시간')
            ax1.set_ylabel('주문 건수')
            ax1.set_xticks(range(0, 24, 3))
            
            # 2. 피크 시간 TOP 3 (오른쪽)
            colors_peak = [self.colors['primary'], self.colors['secondary'], self.colors['accent']]
            bars2 = ax2.bar(range(len(peak_hours)), peak_orders, 
                           color=colors_peak[:len(peak_hours)], alpha=0.8)
            
            # 값 라벨
            for bar, value in zip(bars2, peak_orders):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{value}건', ha='center', va='bottom', 
                        fontsize=10, fontweight='bold')
            
            # 피크 시간 라벨
            peak_labels = [f'{h:02d}:00' for h in peak_hours]
            ax2.set_xticks(range(len(peak_hours)))
            ax2.set_xticklabels(peak_labels)
            ax2.set_title('피크 시간대 TOP 3', fontsize=14, fontweight='bold')
            ax2.set_ylabel('주문 건수')
            
            # 스타일 적용
            for ax in [ax1, ax2]:
                self.apply_minimal_style(ax)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 피크 시간 분석 차트 생성 실패: {str(e)}")
            return None
    
    def create_time_insights_summary(self, time_data):
        """시간 분석 인사이트 요약"""
        try:
            fig, ax = self.create_figure(size='medium')
            ax.axis('off')
            
            # 인사이트 생성
            insights = []
            
            # 피크 시간 분석
            if 'peak_hours' in time_data:
                peak_hours = time_data['peak_hours']['hours']
                peak_time_str = ', '.join([f'{h:02d}시' for h in peak_hours[:3]])
                insights.append(f"🕐 주요 주문 시간: {peak_time_str}")
            
            # 요일별 패턴
            if 'daily_revenue' in time_data:
                daily_data = time_data['daily_revenue']
                max_day = max(daily_data.items(), key=lambda x: x[1])[0]
                min_day = min(daily_data.items(), key=lambda x: x[1])[0]
                insights.append(f"📅 최고 매출 요일: {max_day}요일")
                insights.append(f"📅 최저 매출 요일: {min_day}요일")
            
            # 주말 vs 평일 비교
            if 'daily_revenue' in time_data:
                weekend_avg = (daily_data.get('토', 0) + daily_data.get('일', 0)) / 2
                weekday_avg = sum([daily_data.get(day, 0) for day in ['월', '화', '수', '목', '금']]) / 5
                
                if weekend_avg > weekday_avg:
                    diff_pct = ((weekend_avg - weekday_avg) / weekday_avg) * 100
                    insights.append(f"📈 주말 매출이 평일보다 {diff_pct:.1f}% 높음")
                else:
                    diff_pct = ((weekday_avg - weekend_avg) / weekend_avg) * 100
                    insights.append(f"📊 평일 매출이 주말보다 {diff_pct:.1f}% 높음")
            
            # 기본 인사이트
            if not insights:
                insights = [
                    "🕐 오전 11시, 오후 3시, 저녁 9시에 주문 집중",
                    "📅 주말 매출이 평일보다 높은 경향",
                    "🛒 점심시간과 퇴근 후 시간대가 주요 쇼핑 시간"
                ]
            
            # 제목
            ax.text(0.5, 0.95, '⏰ 시간대별 쇼핑 패턴 분석', ha='center', va='top',
                   fontsize=16, fontweight='bold', color=self.colors['primary'],
                   transform=ax.transAxes)
            
            # 구분선
            ax.axhline(y=0.85, xmin=0.1, xmax=0.9, color=self.colors['primary'], 
                      linewidth=2, transform=ax.transAxes)
            
            # 인사이트 리스트
            y_start = 0.75
            for i, insight in enumerate(insights[:5]):  # 최대 5개
                y_pos = y_start - (i * 0.12)
                
                ax.text(0.1, y_pos, '▶', ha='left', va='center',
                       fontsize=14, color=self.colors['accent'],
                       transform=ax.transAxes)
                
                ax.text(0.15, y_pos, insight, ha='left', va='center',
                       fontsize=12, color=self.colors['dark_gray'],
                       transform=ax.transAxes)
            
            # 추천 사항
            ax.text(0.5, 0.15, '💡 운영 최적화 제안', ha='center', va='center',
                   fontsize=14, fontweight='bold', color=self.colors['secondary'],
                   transform=ax.transAxes)
            
            recommendations = [
                "피크 시간대 재고 및 배송 준비 강화",
                "저조한 시간대 프로모션 기획",
                "요일별 맞춤 마케팅 전략 수립"
            ]
            
            for i, rec in enumerate(recommendations):
                y_pos = 0.05 - (i * 0.08)
                ax.text(0.1, y_pos, f"• {rec}", ha='left', va='center',
                       fontsize=10, color=self.colors['medium_gray'],
                       transform=ax.transAxes)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 시간 인사이트 요약 생성 실패: {str(e)}")
            return None
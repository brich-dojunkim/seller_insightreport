# charts/channel_charts.py - 채널별 성과 차트 생성

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from .base_chart import BaseChart
import sys
sys.path.append('..')
from config import COLORS

class ChannelCharts(BaseChart):
    """채널별 성과 차트 생성 클래스"""
    
    def __init__(self):
        super().__init__()
    
    def create_channel_pie_chart(self, channel_data, title="채널별 매출 분포"):
        """채널별 매출 파이차트 생성"""
        try:
            fig, ax = self.create_figure(size='medium')
            
            # 데이터 준비
            if isinstance(channel_data, pd.DataFrame):
                labels = channel_data.index.tolist()
                values = channel_data['총매출'].values if '총매출' in channel_data.columns else channel_data.values
            else:
                labels = list(channel_data.keys())
                values = list(channel_data.values())
            
            # 색상 설정
            colors = self.get_color_palette(len(labels))
            
            # 파이차트 생성
            wedges, texts, autotexts = ax.pie(
                values, 
                labels=labels,
                autopct='%1.1f%%',
                colors=colors,
                startangle=90,
                pctdistance=0.85,
                textprops={'fontsize': 11}
            )
            
            # 스타일 개선
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(12)
            
            # 제목 설정
            ax.set_title(title, fontsize=16, fontweight='bold', 
                        color=self.colors['dark_gray'], pad=20)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 파이차트 생성 실패: {str(e)}")
            return None
    
    def create_channel_donut_chart(self, channel_data, title="채널별 매출 분포"):
        """채널별 매출 도넛차트 생성 (모던한 스타일)"""
        try:
            fig, ax = self.create_figure(size='large')
            
            # 데이터 준비
            if isinstance(channel_data, pd.DataFrame):
                labels = channel_data.index.tolist()
                values = channel_data['총매출'].values if '총매출' in channel_data.columns else channel_data.values
                total_value = sum(values)
            else:
                labels = list(channel_data.keys())
                values = list(channel_data.values())
                total_value = sum(values)
            
            # 색상 설정 (그라데이션 효과)
            colors = self.get_color_palette(len(labels))
            
            # 도넛차트 생성
            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,  # 라벨은 별도로 표시
                autopct='',   # 퍼센트는 별도로 표시
                colors=colors,
                startangle=90,
                pctdistance=0.85,
                wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
            )
            
            # 중앙 원 (도넛 효과)
            centre_circle = plt.Circle((0,0), 0.60, fc='white', linewidth=2, 
                                     edgecolor=self.colors['border'])
            fig.gca().add_artist(centre_circle)
            
            # 중앙 텍스트
            ax.text(0, 0.1, '총 매출', ha='center', va='center', 
                   fontsize=14, color=self.colors['medium_gray'])
            ax.text(0, -0.1, self.format_currency(total_value), ha='center', va='center', 
                   fontsize=18, fontweight='bold', color=self.colors['primary'])
            
            # 범례 (오른쪽에 배치)
            legend_labels = []
            for i, (label, value) in enumerate(zip(labels, values)):
                percentage = (value / total_value) * 100
                legend_labels.append(f'{label}\n{self.format_currency(value)} ({percentage:.1f}%)')
            
            ax.legend(wedges, legend_labels, loc="center left", 
                     bbox_to_anchor=(1, 0, 0.5, 1), frameon=False, fontsize=11)
            
            # 제목
            ax.set_title(title, fontsize=16, fontweight='bold', 
                        color=self.colors['dark_gray'], pad=30)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 도넛차트 생성 실패: {str(e)}")
            return None
    
    def create_channel_bar_chart(self, channel_data, title="채널별 주문량", 
                                metric='주문수', horizontal=True):
        """채널별 막대그래프 생성"""
        try:
            fig, ax = self.create_figure(size='medium')
            
            # 데이터 준비
            if isinstance(channel_data, pd.DataFrame):
                labels = channel_data.index.tolist()
                values = channel_data[metric].values if metric in channel_data.columns else channel_data.values
            else:
                labels = list(channel_data.keys())
                values = list(channel_data.values())
            
            # 정렬 (값 기준)
            sorted_data = sorted(zip(labels, values), key=lambda x: x[1], reverse=False)
            sorted_labels, sorted_values = zip(*sorted_data)
            
            # 색상 설정
            main_color = self.colors['primary']
            
            if horizontal:
                # 수평 막대그래프
                bars = ax.barh(range(len(sorted_labels)), sorted_values,
                              color=main_color, alpha=0.8, height=0.7)
                
                ax.set_yticks(range(len(sorted_labels)))
                ax.set_yticklabels(sorted_labels)
                ax.set_xlabel(metric)
                
                # 값 라벨 추가
                for i, (bar, value) in enumerate(zip(bars, sorted_values)):
                    ax.text(value + max(sorted_values) * 0.02, 
                           bar.get_y() + bar.get_height()/2,
                           f'{value:,}' if metric == '주문수' else self.format_currency(value),
                           va='center', fontsize=10, fontweight='bold')
            else:
                # 수직 막대그래프
                bars = ax.bar(range(len(sorted_labels)), sorted_values,
                             color=main_color, alpha=0.8, width=0.7)
                
                ax.set_xticks(range(len(sorted_labels)))
                ax.set_xticklabels(sorted_labels, rotation=45, ha='right')
                ax.set_ylabel(metric)
                
                # 값 라벨 추가
                for bar, value in zip(bars, sorted_values):
                    ax.text(bar.get_x() + bar.get_width()/2, 
                           bar.get_height() + max(sorted_values) * 0.02,
                           f'{value:,}' if metric == '주문수' else self.format_currency(value),
                           ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # 스타일 적용
            self.apply_minimal_style(ax, title=title)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 막대차트 생성 실패: {str(e)}")
            return None
    
    def create_channel_growth_table(self, channel_data, title="채널별 성장률"):
        """채널별 성장률 표 생성 (차트 형태)"""
        try:
            fig, ax = self.create_figure(size='medium')
            ax.axis('off')
            
            # 데이터 준비
            if isinstance(channel_data, pd.DataFrame):
                table_data = []
                table_data.append(['채널명', '주문수', '매출액', '점유율', '성장률'])
                
                for channel, row in channel_data.iterrows():
                    table_data.append([
                        channel,
                        f"{row['주문수']:,}건",
                        self.format_currency(row['총매출']),
                        f"{row['매출점유율']:.1f}%",
                        f"{row['성장률']:+.1f}%" if '성장률' in row else "N/A"
                    ])
            else:
                # 딕셔너리 형태의 데이터 처리
                table_data = []
                table_data.append(['채널명', '값'])
                for key, value in channel_data.items():
                    table_data.append([key, str(value)])
            
            # 테이블 생성
            table = ax.table(cellText=table_data[1:], colLabels=table_data[0],
                           cellLoc='center', loc='center',
                           colWidths=[0.25, 0.15, 0.25, 0.15, 0.15])
            
            # 테이블 스타일링
            table.auto_set_font_size(False)
            table.set_fontsize(10)
            table.scale(1.2, 1.8)
            
            # 헤더 스타일
            for i in range(len(table_data[0])):
                table[(0, i)].set_facecolor(self.colors['primary'])
                table[(0, i)].set_text_props(weight='bold', color='white')
            
            # 데이터 행 스타일
            for i in range(1, len(table_data)):
                for j in range(len(table_data[0])):
                    if i % 2 == 0:
                        table[(i, j)].set_facecolor(self.colors['light_gray'])
                    
                    # 성장률 컬럼 색상 처리
                    if j == 4 and len(table_data[0]) > 4:  # 성장률 컬럼
                        cell_text = table_data[i][j]
                        if '+' in cell_text:
                            table[(i, j)].set_text_props(color=self.colors['success'], weight='bold')
                        elif '-' in cell_text:
                            table[(i, j)].set_text_props(color=self.colors['danger'], weight='bold')
            
            # 제목 추가
            ax.text(0.5, 0.95, title, ha='center', va='top', 
                   fontsize=16, fontweight='bold', color=self.colors['dark_gray'],
                   transform=ax.transAxes)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 성장률 표 생성 실패: {str(e)}")
            return None
    
    def create_channel_comparison_chart(self, channel_data):
        """채널별 비교 차트 (주문수 vs 매출액)"""
        try:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
            
            # 데이터 준비
            if isinstance(channel_data, pd.DataFrame):
                channels = channel_data.index.tolist()
                orders = channel_data['주문수'].values
                revenue = channel_data['총매출'].values
            else:
                return None
            
            colors = self.get_color_palette(len(channels))
            
            # 주문수 차트 (왼쪽)
            bars1 = ax1.bar(channels, orders, color=colors[0], alpha=0.8)
            ax1.set_title('채널별 주문수', fontsize=14, fontweight='bold')
            ax1.set_ylabel('주문수')
            plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
            
            # 값 라벨 추가
            for bar, value in zip(bars1, orders):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(orders) * 0.02,
                        f'{value:,}', ha='center', va='bottom', fontsize=9, fontweight='bold')
            
            # 매출액 차트 (오른쪽)
            bars2 = ax2.bar(channels, revenue, color=colors[1], alpha=0.8)
            ax2.set_title('채널별 매출액', fontsize=14, fontweight='bold')
            ax2.set_ylabel('매출액')
            plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
            
            # 값 라벨 추가
            for bar, value in zip(bars2, revenue):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(revenue) * 0.02,
                        self.format_currency(value), ha='center', va='bottom', 
                        fontsize=9, fontweight='bold')
            
            # 스타일 적용
            for ax in [ax1, ax2]:
                self.apply_minimal_style(ax)
            
            plt.tight_layout()
            return self.save_chart_to_buffer(fig)
            
        except Exception as e:
            print(f"❌ 비교 차트 생성 실패: {str(e)}")
            return None

# 테스트 함수
def test_channel_charts():
    """채널 차트 테스트"""
    print("🧪 채널 차트 테스트 시작...")
    
    try:
        # 테스트 데이터 생성
        test_data = pd.DataFrame({
            '주문수': [150, 120, 80, 66],
            '총매출': [3500000, 2800000, 1900000, 1500000],
            '매출점유율': [35.0, 28.0, 19.0, 15.0],
            '성장률': [15.2, 8.5, -3.2, 12.1]
        }, index=['SSG', '카페24', '쿠팡', '11번가'])
        
        # ChannelCharts 초기화
        charts = ChannelCharts()
        print("✅ ChannelCharts 초기화 완료")
        
        # 1. 파이차트 생성
        pie_buffer = charts.create_channel_pie_chart(test_data)
        if pie_buffer:
            print("✅ 파이차트 생성 완료")
        
        # 2. 도넛차트 생성
        donut_buffer = charts.create_channel_donut_chart(test_data)
        if donut_buffer:
            print("✅ 도넛차트 생성 완료")
        
        # 3. 막대그래프 생성 (수평)
        bar_buffer = charts.create_channel_bar_chart(test_data, metric='주문수')
        if bar_buffer:
            print("✅ 수평 막대그래프 생성 완료")
        
        # 4. 성장률 표 생성
        table_buffer = charts.create_channel_growth_table(test_data)
        if table_buffer:
            print("✅ 성장률 표 생성 완료")
        
        # 5. 비교 차트 생성
        comparison_buffer = charts.create_channel_comparison_chart(test_data)
        if comparison_buffer:
            print("✅ 비교 차트 생성 완료")
        
        print("🎉 채널 차트 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_channel_charts()
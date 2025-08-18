# charts/base_chart.py - 차트 생성 기본 클래스

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
import numpy as np
from io import BytesIO
import sys
sys.path.append('..')
from config import COLORS, CHART_SETTINGS, CHART_COLORS

class BaseChart:
    """모든 차트의 기본 클래스"""
    
    def __init__(self):
        self.colors = COLORS
        self.chart_colors = CHART_COLORS
        self.settings = CHART_SETTINGS
        self._setup_style()
    
    def _setup_style(self):
        """차트 기본 스타일 설정"""
        # matplotlib 한글 폰트 설정
        plt.rcParams['font.family'] = 'DejaVu Sans'
        plt.rcParams['axes.unicode_minus'] = False
        
        # 기본 스타일 설정
        plt.style.use('default')
        sns.set_palette(self.chart_colors)
        
        # 전역 폰트 크기 설정
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 11
        plt.rcParams['xtick.labelsize'] = 9
        plt.rcParams['ytick.labelsize'] = 9
        plt.rcParams['legend.fontsize'] = 10
    
    def create_figure(self, size='medium', facecolor='white'):
        """기본 figure 생성"""
        figsize = self.settings['figure_size'][size]
        fig, ax = plt.subplots(figsize=figsize, facecolor=facecolor)
        return fig, ax
    
    def apply_minimal_style(self, ax, title=None, xlabel=None, ylabel=None):
        """미니멀 스타일 적용"""
        # 제목 설정
        if title:
            ax.set_title(title, fontsize=16, fontweight='bold', 
                        color=self.colors['dark_gray'], pad=20)
        
        # 축 라벨 설정
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12, color=self.colors['medium_gray'])
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12, color=self.colors['medium_gray'])
        
        # 스파인 스타일링
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.colors['border'])
        ax.spines['bottom'].set_color(self.colors['border'])
        
        # 그리드 설정
        ax.grid(True, alpha=self.settings['grid_alpha'], 
               linestyle='-', linewidth=0.5, color=self.colors['border'])
        ax.set_axisbelow(True)
        
        return ax
    
    def save_chart_to_buffer(self, fig, dpi=None):
        """차트를 BytesIO 버퍼로 저장"""
        if dpi is None:
            dpi = self.settings['dpi']
        
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png', dpi=dpi, bbox_inches='tight',
                   facecolor='white', edgecolor='none', pad_inches=0.1)
        img_buffer.seek(0)
        plt.close(fig)
        
        return img_buffer
    
    def format_currency(self, value):
        """통화 포맷팅"""
        if value >= 1_000_000:
            return f'₩{value/1_000_000:.1f}M'
        elif value >= 1_000:
            return f'₩{value/1_000:.0f}K'
        else:
            return f'₩{value:,.0f}'
    
    def format_percentage(self, value, decimal_places=1):
        """퍼센트 포맷팅"""
        return f'{value:.{decimal_places}f}%'
    
    def get_color_palette(self, n_colors):
        """색상 팔레트 생성"""
        if n_colors <= len(self.chart_colors):
            return self.chart_colors[:n_colors]
        else:
            # 더 많은 색상이 필요한 경우 색상 보간
            base_colors = self.chart_colors
            additional_colors = []
            for i in range(n_colors - len(base_colors)):
                color_idx = i % len(base_colors)
                additional_colors.append(base_colors[color_idx])
            return base_colors + additional_colors
    
    def add_value_labels(self, ax, bars, format_func=None, offset_factor=0.01):
        """막대 차트에 값 라벨 추가"""
        if format_func is None:
            format_func = lambda x: f'{x:,.0f}'
        
        for bar in bars:
            height = bar.get_height() if hasattr(bar, 'get_height') else bar.get_width()
            
            if hasattr(bar, 'get_height'):  # 세로 막대
                x_pos = bar.get_x() + bar.get_width() / 2
                y_pos = height + (ax.get_ylim()[1] * offset_factor)
                ax.text(x_pos, y_pos, format_func(height), 
                       ha='center', va='bottom', fontweight='600', fontsize=10)
            else:  # 가로 막대
                x_pos = height + (ax.get_xlim()[1] * offset_factor)
                y_pos = bar.get_y() + bar.get_height() / 2
                ax.text(x_pos, y_pos, format_func(height),
                       ha='left', va='center', fontweight='600', fontsize=10)
    
    def create_legend(self, ax, labels, colors=None, loc='best'):
        """커스텀 범례 생성"""
        if colors is None:
            colors = self.get_color_palette(len(labels))
        
        handles = []
        for label, color in zip(labels, colors):
            handles.append(plt.Rectangle((0,0),1,1, facecolor=color, alpha=0.8))
        
        legend = ax.legend(handles, labels, loc=loc, frameon=False, 
                          fontsize=10, bbox_to_anchor=(1.05, 1))
        return legend

class KPICard:
    """KPI 카드 생성 클래스"""
    
    def __init__(self, base_chart):
        self.base = base_chart
        self.colors = base_chart.colors
    
    def create_kpi_card(self, value, label, growth=None, format_type='currency'):
        """개별 KPI 카드 생성"""
        fig, ax = self.base.create_figure(size='small')
        
        # 배경 제거
        ax.axis('off')
        
        # 메인 값 표시
        if format_type == 'currency':
            formatted_value = self.base.format_currency(value)
        elif format_type == 'percentage':
            formatted_value = self.base.format_percentage(value)
        elif format_type == 'count':
            formatted_value = f'{value:,}'
        else:
            formatted_value = str(value)
        
        # 큰 숫자 표시
        ax.text(0.5, 0.6, formatted_value, 
               ha='center', va='center', fontsize=24, fontweight='bold',
               color=self.colors['primary'], transform=ax.transAxes)
        
        # 라벨 표시
        ax.text(0.5, 0.3, label,
               ha='center', va='center', fontsize=12,
               color=self.colors['medium_gray'], transform=ax.transAxes)
        
        # 성장률 표시 (옵션)
        if growth is not None:
            growth_color = self.colors['success'] if growth >= 0 else self.colors['danger']
            growth_symbol = '+' if growth >= 0 else ''
            ax.text(0.5, 0.1, f'{growth_symbol}{growth:.1f}%',
                   ha='center', va='center', fontsize=14, fontweight='bold',
                   color=growth_color, transform=ax.transAxes)
        
        # 카드 테두리 (옵션)
        rect = plt.Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=2, 
                           edgecolor=self.colors['border'], facecolor='none',
                           transform=ax.transAxes)
        ax.add_patch(rect)
        
        plt.tight_layout()
        return self.base.save_chart_to_buffer(fig)
    
    def create_multi_kpi_dashboard(self, kpi_data):
        """다중 KPI 대시보드 생성"""
        n_kpis = len(kpi_data)
        cols = min(4, n_kpis)  # 최대 4열
        rows = (n_kpis + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(16, 4*rows), facecolor='white')
        
        if rows == 1:
            axes = [axes] if n_kpis == 1 else axes
        else:
            axes = axes.flatten()
        
        for i, (label, data) in enumerate(kpi_data.items()):
            ax = axes[i]
            ax.axis('off')
            
            # KPI 값 표시
            value = data['value']
            growth = data.get('growth')
            format_type = data.get('format', 'currency')
            
            if format_type == 'currency':
                formatted_value = self.base.format_currency(value)
            elif format_type == 'percentage':
                formatted_value = self.base.format_percentage(value)
            elif format_type == 'count':
                formatted_value = f'{value:,}'
            else:
                formatted_value = str(value)
            
            # 메인 값
            ax.text(0.5, 0.6, formatted_value,
                   ha='center', va='center', fontsize=20, fontweight='bold',
                   color=self.colors['primary'], transform=ax.transAxes)
            
            # 라벨
            ax.text(0.5, 0.4, label,
                   ha='center', va='center', fontsize=11,
                   color=self.colors['medium_gray'], transform=ax.transAxes)
            
            # 성장률
            if growth is not None:
                growth_color = self.colors['success'] if growth >= 0 else self.colors['danger']
                growth_symbol = '+' if growth >= 0 else ''
                ax.text(0.5, 0.2, f'{growth_symbol}{growth:.1f}%',
                       ha='center', va='center', fontsize=12, fontweight='bold',
                       color=growth_color, transform=ax.transAxes)
            
            # 카드 배경
            rect = plt.Rectangle((0.05, 0.05), 0.9, 0.9, linewidth=1.5,
                               edgecolor=self.colors['border'], 
                               facecolor=self.colors['light_gray'], alpha=0.3,
                               transform=ax.transAxes)
            ax.add_patch(rect)
        
        # 빈 subplot 숨기기
        for i in range(n_kpis, len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        return self.base.save_chart_to_buffer(fig)

# 테스트 함수
def test_base_chart():
    """기본 차트 클래스 테스트"""
    print("🧪 기본 차트 클래스 테스트 시작...")
    
    try:
        # BaseChart 초기화
        base = BaseChart()
        print("✅ BaseChart 초기화 완료")
        
        # KPI 카드 테스트
        kpi = KPICard(base)
        
        # 개별 KPI 카드 생성
        kpi_buffer = kpi.create_kpi_card(
            value=65432100, 
            label="총 매출액", 
            growth=12.5,
            format_type='currency'
        )
        print("✅ 개별 KPI 카드 생성 완료")
        
        # 다중 KPI 대시보드 생성
        kpi_data = {
            '총 주문수': {'value': 416, 'growth': 15.2, 'format': 'count'},
            '총 매출액': {'value': 9876543, 'growth': 12.1, 'format': 'currency'},
            '평균 주문금액': {'value': 23750, 'growth': -2.3, 'format': 'currency'},
            '시장 점유율': {'value': 4.35, 'growth': 8.7, 'format': 'percentage'}
        }
        
        dashboard_buffer = kpi.create_multi_kpi_dashboard(kpi_data)
        print("✅ 다중 KPI 대시보드 생성 완료")
        
        # 색상 팔레트 테스트
        colors = base.get_color_palette(6)
        print(f"✅ 색상 팔레트 생성: {len(colors)}개 색상")
        
        print("🎉 기본 차트 클래스 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {str(e)}")
        return False

if __name__ == "__main__":
    test_base_chart()
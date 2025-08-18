# charts/__init__.py - 차트 모듈 초기화 (업데이트)

"""
비플로우 리포트 생성기 - 완전한 차트 생성 모듈

이 모듈은 5페이지 PDF 리포트에 필요한 모든 차트와 시각화를 담당합니다.

주요 클래스:
    - BaseChart: 모든 차트의 기본 클래스 및 KPI 카드
    - ChannelCharts: 채널별 성과 차트 (2페이지)
    - CoverPageGenerator: 커버 페이지 생성 (1페이지)
    - TimeCharts: 시간대별 분석 차트 (3페이지)
    - ProductCharts: 상품 및 배송 차트 (4페이지)
    - BenchmarkCharts: 벤치마크 및 제안 차트 (5페이지)

페이지별 차트 구성:
    📄 1페이지 (커버):
        - B-Flow 로고 및 헤더
        - 핵심 KPI 카드 4개 (주문수, 매출액, AOV, 점유율)
        - 주요 채널 하이라이트
        - 자동 생성 인사이트

    📄 2페이지 (채널별 성과):
        - 채널별 매출 도넛차트
        - 채널별 주문량 막대그래프
        - 채널별 성장률 표
        - 채널 성과 비교 차트

    📄 3페이지 (시간대별 분석):
        - 시간별 주문 패턴 히트맵 (24h x 7일)
        - 요일별 매출 트렌드 차트
        - 피크 시간대 분석
        - 시간 패턴 인사이트 요약

    📄 4페이지 (상품 & 배송 현황):
        - 베스트셀러 TOP 10 차트
        - 주문상태별 분포 파이차트
        - 배송 성과 지표 (완료율, 취소율 등)
        - 상품 카테고리별 분석

    📄 5페이지 (벤치마크 & 제안):
        - 플랫폼 내 시장 점유율 비교
        - 종합 성과 레이더 차트
        - 성장 전망 및 목표 설정
        - 전략적 개선 제안
        - 경쟁사 포지셔닝 분석
        - 다음 달 전망

사용법:
    from charts import (
        CoverPageGenerator, ChannelCharts, TimeCharts, 
        ProductCharts, BenchmarkCharts
    )
    
    # 1페이지: 커버
    cover_gen = CoverPageGenerator()
    cover_page = cover_gen.create_complete_cover_page(company, metrics, channels, insights)
    
    # 2페이지: 채널 성과
    channel_charts = ChannelCharts()
    donut_chart = channel_charts.create_channel_donut_chart(channel_data)
    bar_chart = channel_charts.create_channel_bar_chart(channel_data)
    growth_table = channel_charts.create_channel_growth_table(channel_data)
    
    # 3페이지: 시간 분석
    time_charts = TimeCharts()
    heatmap = time_charts.create_hourly_heatmap(time_data)
    daily_trend = time_charts.create_daily_trend_chart(time_data)
    peak_analysis = time_charts.create_peak_hours_analysis(time_data)
    
    # 4페이지: 상품 & 배송
    product_charts = ProductCharts()
    bestseller = product_charts.create_bestseller_chart(product_data)
    status_pie = product_charts.create_order_status_pie_chart(status_data)
    delivery_perf = product_charts.create_delivery_performance_chart(delivery_data)
    
    # 5페이지: 벤치마크 & 제안
    benchmark_charts = BenchmarkCharts()
    market_share = benchmark_charts.create_market_share_comparison(benchmark_data, company)
    radar_chart = benchmark_charts.create_performance_radar_chart(benchmark_data, company)
    growth_proj = benchmark_charts.create_growth_projection_chart(current_metrics)
    recommendations = benchmark_charts.create_strategic_recommendations(metrics_data)
"""

# 기본 차트 클래스
from .base_chart import BaseChart, KPICard

# 페이지별 차트 생성기
from .cover_page_generator import CoverPageGenerator    # 1페이지
from .channel_charts import ChannelCharts              # 2페이지  
from .time_charts import TimeCharts                    # 3페이지
from .product_charts import ProductCharts              # 4페이지
from .benchmark_charts import BenchmarkCharts          # 5페이지

__all__ = [
    # 기본 클래스
    'BaseChart',
    'KPICard',
    
    # 페이지별 생성기
    'CoverPageGenerator',    # 1페이지 커버
    'ChannelCharts',         # 2페이지 채널 성과
    'TimeCharts',            # 3페이지 시간 분석
    'ProductCharts',         # 4페이지 상품 & 배송
    'BenchmarkCharts'        # 5페이지 벤치마크 & 제안
]

# 버전 정보
__version__ = "2.0.0"
__author__ = "B-Flow Data Team"
__description__ = "Complete 5-page PDF report chart generation system"

# 차트 생성 순서 가이드
CHART_GENERATION_ORDER = {
    1: "CoverPageGenerator.create_complete_cover_page",
    2: [
        "ChannelCharts.create_channel_donut_chart",
        "ChannelCharts.create_channel_bar_chart", 
        "ChannelCharts.create_channel_growth_table"
    ],
    3: [
        "TimeCharts.create_hourly_heatmap",
        "TimeCharts.create_daily_trend_chart",
        "TimeCharts.create_peak_hours_analysis",
        "TimeCharts.create_time_insights_summary"
    ],
    4: [
        "ProductCharts.create_bestseller_chart",
        "ProductCharts.create_order_status_pie_chart",
        "ProductCharts.create_delivery_performance_chart",
        "ProductCharts.create_product_performance_summary"
    ],
    5: [
        "BenchmarkCharts.create_market_share_comparison",
        "BenchmarkCharts.create_performance_radar_chart", 
        "BenchmarkCharts.create_growth_projection_chart",
        "BenchmarkCharts.create_strategic_recommendations",
        "BenchmarkCharts.create_next_month_forecast"
    ]
}
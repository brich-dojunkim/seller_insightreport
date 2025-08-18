# data/__init__.py - 데이터 모듈 초기화

"""
비플로우 리포트 생성기 - 데이터 처리 모듈

이 모듈은 엑셀 데이터 로드, 검증, 정리 및 비즈니스 지표 계산을 담당합니다.

주요 클래스:
    - DataLoader: 엑셀 파일 로드 및 데이터 검증
    - MetricsCalculator: 비즈니스 지표 계산 및 분석

사용법:
    from data import DataLoader, MetricsCalculator
    
    # 데이터 로드
    loader = DataLoader("order_data.xlsx")
    platform_data = loader.load_excel()
    loader.validate_data_structure()
    cleaned_data = loader.clean_data()
    
    # 특정 회사 데이터 필터링
    company_data = loader.filter_by_company("포레스트핏")
    
    # 지표 계산
    calculator = MetricsCalculator(company_data, platform_data, "포레스트핏")
    metrics = calculator.calculate_all_metrics()
"""

from .data_loader import DataLoader
from .metrics_calculator import MetricsCalculator

__all__ = ['DataLoader', 'MetricsCalculator']

# 버전 정보
__version__ = "1.0.0"
__author__ = "B-Flow Data Team"
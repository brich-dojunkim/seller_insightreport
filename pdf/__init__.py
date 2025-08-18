# pdf/__init__.py - PDF 생성 모듈 초기화

"""
비플로우 리포트 생성기 - PDF 생성 모듈

이 모듈은 분석된 데이터와 생성된 차트를 하나의 PDF 문서로 조립합니다.

주요 클래스:
    - PDFStyles: PDF 스타일 및 레이아웃 정의
    - PageBuilders: 각 페이지별 레이아웃 빌더
    - BFlowPDFBuilder: 최종 PDF 조립기
    - CustomPageTemplate: 커스텀 페이지 템플릿

PDF 구성:
    📄 5페이지 A4 사이즈 리포트
    🎨 미니멀/모던 디자인
    📊 차트와 텍스트의 조화로운 배치
    🎯 입점사별 맞춤 분석

사용법:
    from pdf import BFlowPDFBuilder, generate_forestfit_report
    
    # 방법 1: 직접 빌더 사용
    builder = BFlowPDFBuilder("포레스트핏")
    report_path = builder.generate_report_from_excel("data.xlsx")
    
    # 방법 2: 편의 함수 사용
    report_path = generate_forestfit_report("data.xlsx", "output.pdf")
    
    # 방법 3: 다른 회사 리포트
    from pdf import generate_custom_report
    report_path = generate_custom_report("애경티슬로", "data.xlsx")

페이지 구성:
    1페이지: 커버 페이지
        - B-Flow 로고 및 브랜딩
        - 회사명 및 분석 기간
        - 핵심 KPI 4개 카드
        - 주요 채널 하이라이트
        - 자동 생성 인사이트

    2페이지: 채널별 성과 분석
        - 채널별 매출 도넛차트
        - 채널별 성장률 상세 테이블
        - 채널 성과 비교 분석

    3페이지: 시간대별 분석
        - 24시간 x 7일 주문 패턴 히트맵
        - 요일별 매출 트렌드
        - 피크 시간대 분석

    4페이지: 상품 & 배송 현황
        - 베스트셀러 TOP 10
        - 주문상태별 분포
        - 배송 성과 지표
        - 상품 성과 종합 요약

    5페이지: 벤치마크 & 전략 제안
        - 플랫폼 내 시장 점유율 비교
        - 종합 성과 레이더 차트
        - 성장 전망 및 목표
        - 전략적 개선 제안
        - 다음 달 전망

스타일 특징:
    - B-Flow 브랜드 컬러 (#2E86AB, #A23B72, #F18F01)
    - 미니멀한 레이아웃과 충분한 여백
    - 데이터 중심의 명확한 정보 전달
    - 헤더/푸터로 일관된 브랜딩
"""

from .styles import PDFStyles, get_style, get_table_style, get_color, get_layout
from .page_builders import PageBuilders, CustomPageTemplate
from .pdf_builder import BFlowPDFBuilder, generate_forestfit_report, generate_custom_report

__all__ = [
    # 스타일 관련
    'PDFStyles',
    'get_style',
    'get_table_style', 
    'get_color',
    'get_layout',
    
    # 페이지 빌더
    'PageBuilders',
    'CustomPageTemplate',
    
    # PDF 조립기
    'BFlowPDFBuilder',
    
    # 편의 함수
    'generate_forestfit_report',
    'generate_custom_report'
]

# 버전 정보
__version__ = "1.0.0"
__author__ = "B-Flow Data Team"
__description__ = "Professional PDF report generation system for B-Flow partners"

# PDF 생성 흐름
PDF_GENERATION_FLOW = {
    "단계 1": "데이터 로드 및 검증 (data 모듈)",
    "단계 2": "지표 계산 및 분석 (data.MetricsCalculator)", 
    "단계 3": "차트 생성 (charts 모듈)",
    "단계 4": "페이지별 레이아웃 구성 (PageBuilders)",
    "단계 5": "PDF 문서 조립 (BFlowPDFBuilder)",
    "단계 6": "최종 PDF 파일 생성"
}

# 지원하는 출력 형식
SUPPORTED_FORMATS = {
    "pdf": "Adobe PDF (기본)",
    "png": "페이지별 PNG 이미지 (개발 중)",
    "html": "HTML 리포트 (개발 중)"
}

# 최적화 설정
OPTIMIZATION_SETTINGS = {
    "image_compression": True,
    "chart_dpi": 300,
    "font_embedding": True,
    "file_size_target": "< 5MB"
}
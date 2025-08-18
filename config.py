# config.py - 비플로우 리포트 전역 설정

# 비플로우 브랜드 컬러 팔레트
COLORS = {
    'primary': '#2E86AB',       # B-Flow 메인 블루
    'secondary': '#A23B72',     # 포인트 핑크  
    'accent': '#F18F01',        # 액센트 오렌지
    'success': '#06D6A0',       # 성공 그린
    'warning': '#F77F00',       # 경고 오렌지
    'danger': '#E63946',        # 위험 레드
    'light_gray': '#F8F9FA',    # 라이트 배경
    'medium_gray': '#6C757D',   # 미디엄 그레이
    'dark_gray': '#343A40',     # 다크 그레이
    'border': '#DEE2E6',        # 보더 컬러
    'white': '#FFFFFF',         # 화이트
    'black': '#000000'          # 블랙
}

# 차트 색상 시퀀스 (데이터 시각화용)
CHART_COLORS = [
    COLORS['primary'],
    COLORS['secondary'], 
    COLORS['accent'],
    COLORS['success'],
    COLORS['warning'],
    COLORS['danger']
]

# 폰트 설정
FONTS = {
    'title': 'Helvetica-Bold',
    'heading': 'Helvetica-Bold', 
    'body': 'Helvetica',
    'caption': 'Helvetica',
    'korean_fallback': 'DejaVu Sans'  # 한글 폰트 대체
}

# 폰트 크기
FONT_SIZES = {
    'title': 24,
    'subtitle': 18,
    'heading': 16,
    'subheading': 14,
    'body': 11,
    'caption': 9,
    'small': 8
}

# PDF 레이아웃 설정
PDF_SETTINGS = {
    'page_size': 'A4',
    'margins': {
        'top': 2.0,      # cm
        'bottom': 2.0,   # cm  
        'left': 2.0,     # cm
        'right': 2.0     # cm
    },
    'logo_height': 1.5,  # cm
    'section_spacing': 0.5  # cm
}

# 차트 설정
CHART_SETTINGS = {
    'dpi': 300,
    'figure_size': {
        'small': (8, 6),
        'medium': (10, 8), 
        'large': (12, 10),
        'wide': (14, 6)
    },
    'style': 'default',
    'grid_alpha': 0.3,
    'spine_color': COLORS['border']
}

# 회사별 설정 (확장 가능)
COMPANY_SETTINGS = {
    '포레스트핏': {
        'category': '패션',
        'accent_color': COLORS['secondary'],
        'target_aov': 25000,  # 목표 평균 주문금액
        'benchmark_growth': 15  # 목표 성장률 (%)
    },
    '애경티슬로': {
        'category': '뷰티',
        'accent_color': COLORS['accent'],
        'target_aov': 20000,
        'benchmark_growth': 20
    }
}

# 메트릭 표시 형식
METRIC_FORMATS = {
    'currency': '₩{:,.0f}',
    'percentage': '{:.1f}%',
    'growth': '{:+.1f}%',
    'count': '{:,}',
    'ratio': '{:.2f}'
}

# 리포트 텍스트 템플릿
REPORT_TEXTS = {
    'title': 'B-FLOW 입점사 성과 리포트',
    'subtitle': '데이터 기반 비즈니스 인사이트',
    'cover_insights': {
        'high_growth': '📈 성장세가 매우 우수합니다',
        'stable_growth': '📊 안정적인 성장을 보이고 있습니다', 
        'need_improvement': '🔍 개선이 필요한 영역이 있습니다'
    },
    'recommendations': {
        'channel_focus': '주력 채널에서의 점유율 확대',
        'diversification': '신규 채널 진출을 통한 매출 다변화',
        'aov_improvement': '평균 주문금액 향상 전략 필요',
        'retention': '고객 재구매율 개선 방안 마련'
    }
}

# 데이터 검증 규칙
DATA_VALIDATION = {
    'required_columns': [
        '상품주문번호', '주문번호', '판매채널', '결제일', '주문상태',
        '입점사명', '상품명', '상품가격', '수량', '상품별 총 주문금액'
    ],
    'company_name_column': '입점사명',
    'min_records_for_analysis': 10,
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# 에러 메시지
ERROR_MESSAGES = {
    'file_not_found': '❌ 엑셀 파일을 찾을 수 없습니다: {}',
    'no_company_data': '❌ {}의 주문 데이터가 없습니다',
    'insufficient_data': '❌ 분석하기에 데이터가 부족합니다 (최소 {}건 필요)',
    'invalid_date_format': '❌ 날짜 형식이 올바르지 않습니다',
    'missing_columns': '❌ 필수 컬럼이 없습니다: {}'
}

# 성공 메시지  
SUCCESS_MESSAGES = {
    'data_loaded': '✅ 데이터 로드 완료: {}건',
    'company_filtered': '✅ {} 데이터 필터링 완료: {}건',
    'metrics_calculated': '✅ 지표 계산 완료',
    'charts_generated': '✅ 차트 생성 완료: {}개',
    'pdf_created': '✅ PDF 리포트 생성 완료: {}'
}
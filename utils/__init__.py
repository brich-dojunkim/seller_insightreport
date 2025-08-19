# utils/__init__.py
"""유틸리티 패키지 - 기능별 모듈화"""

from .data_conversion import (
    to_datetime_safe,
    to_number_safe
)

from .customer_identification import (
    create_customer_id
)

from .category_mapping import (
    load_category_mapping,
    map_category_code_to_name
)

from .region_extraction import (
    extract_region_from_address
)

from .formatting import (
    format_currency,
    pct,
    df_to_html_table,
    sanitize_filename
)

# 전체 함수 리스트 (기존 호환성)
__all__ = [
    # 데이터 변환
    'to_datetime_safe',
    'to_number_safe',
    
    # 고객 식별
    'create_customer_id',
    
    # 카테고리 매핑
    'load_category_mapping',
    'map_category_code_to_name',
    
    # 지역 추출
    'extract_region_from_address',
    
    # 포맷팅
    'format_currency',
    'pct',
    'df_to_html_table',
    'sanitize_filename'
]
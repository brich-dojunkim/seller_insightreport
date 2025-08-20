"""포맷팅 유틸리티"""

import re

def format_currency(amount, unit="원"):
    """금액 포맷팅 (억, 만 단위)"""
    if amount >= 100000000:  # 1억 이상
        return f"{amount/100000000:.1f}억{unit}"
    elif amount >= 10000:    # 1만 이상
        return f"{amount/10000:.1f}만{unit}"
    else:
        return f"{amount:,.0f}{unit}"

def pct(value, decimal=1):
    """퍼센트 포맷팅"""
    return f"{value*100:.{decimal}f}%"

def sanitize_filename(filename):
    """파일명에서 특수문자 제거"""
    return re.sub(r'[<>:"/\\|?*]', '_', filename)
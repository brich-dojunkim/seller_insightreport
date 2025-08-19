# fonts.py
"""한글 폰트 설정"""

from matplotlib import rcParams, font_manager

def setup_korean_font():
    """한글 폰트 자동 선택"""
    candidates = [
        "Apple SD Gothic Neo",  # macOS
        "AppleGothic",          # macOS
        "Noto Sans KR",         # 공용
        "NanumGothic",          # 공용
        "Malgun Gothic",        # Windows
        "Noto Sans CJK KR",     # 환경에 따라 이 이름일 수도 있음
    ]
    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in available:
            rcParams["font.family"] = [name]
            break
    rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지
# charts.py
"""차트 생성 함수들"""

import base64
import io
import matplotlib.pyplot as plt
from functools import lru_cache

def _apply_common_style(ax, title, xlabel=None, ylabel=None, rotation=0):
    """공통 차트 스타일 적용"""
    ax.set_title(title, fontsize=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=8)
    if rotation:
        for t in ax.get_xticklabels():
            t.set_rotation(rotation)
            t.set_ha("right")

def fig_to_base64(fig) -> str:
    """Figure를 base64로 변환"""
    buf = io.BytesIO()
    try:
        fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("ascii")
    finally:
        plt.close(fig)
        buf.close()

@lru_cache(maxsize=50)
def make_bar(x_tuple, y_tuple, title, xlabel=None, ylabel=None, rotation=0):
    """막대 차트 생성 (캐시됨)"""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(x_tuple, y_tuple)
    _apply_common_style(ax, title, xlabel, ylabel, rotation)
    return fig_to_base64(fig)

@lru_cache(maxsize=50)
def make_pie(labels_tuple, values_tuple, title):
    """파이 차트 생성 (캐시됨)"""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values_tuple, labels=labels_tuple, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
    ax.set_title(title, fontsize=10)
    return fig_to_base64(fig)

@lru_cache(maxsize=50)
def make_line(x_tuple, y_tuple, title, xlabel=None, ylabel=None):
    """라인 차트 생성 (캐시됨)"""
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(x_tuple, y_tuple, marker="o", markersize=3)
    _apply_common_style(ax, title, xlabel, ylabel)
    fig.autofmt_xdate()
    return fig_to_base64(fig)

def make_heatmap(arr2d, xlabels, ylabels, title):
    """히트맵 생성"""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.imshow(arr2d, aspect="auto")
    ax.set_title(title, fontsize=10)
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels, fontsize=8)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels, fontsize=8)
    return fig_to_base64(fig)

# 캐시용 헬퍼 함수들
def make_bar_cached(x, y, title, xlabel=None, ylabel=None, rotation=0):
    return make_bar(tuple(map(str, x)), tuple(y), title, xlabel, ylabel, rotation)

def make_pie_cached(labels, values, title):
    return make_pie(tuple(map(str, labels)), tuple(values), title)

def make_line_cached(x, y, title, xlabel=None, ylabel=None):
    return make_line(tuple(map(str, x)), tuple(y), title, xlabel, ylabel)
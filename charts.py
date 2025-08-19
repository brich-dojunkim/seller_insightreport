# charts.py
"""차트 생성 함수들"""

import base64
import io
import matplotlib.pyplot as plt

def fig_to_base64(fig) -> str:
    """Figure를 base64로 변환"""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=120)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")

def make_bar(x, y, title, xlabel=None, ylabel=None, rotation=0):
    """막대 차트 생성"""
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.bar(x, y)
    ax.set_title(title, fontsize=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=8)
    if rotation:
        for t in ax.get_xticklabels():
            t.set_rotation(rotation)
            t.set_ha("right")
    return fig_to_base64(fig)

def make_pie(labels, values, title):
    """파이 차트 생성"""
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, textprops={'fontsize': 8})
    ax.set_title(title, fontsize=10)
    return fig_to_base64(fig)

def make_line(x, y, title, xlabel=None, ylabel=None):
    """라인 차트 생성"""
    fig, ax = plt.subplots(figsize=(8, 3))
    ax.plot(x, y, marker="o", markersize=3)
    ax.set_title(title, fontsize=10)
    if xlabel: ax.set_xlabel(xlabel, fontsize=9)
    if ylabel: ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(labelsize=8)
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
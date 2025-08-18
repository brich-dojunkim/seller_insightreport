# charts.py
import base64, io
import matplotlib.pyplot as plt

def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")

def bar(x, y, title, xlabel=None, ylabel=None, rotation=0) -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x, y)  # 색상 미지정
    ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if rotation:
        for t in ax.get_xticklabels():
            t.set_rotation(rotation)
            t.set_ha("right")
    return _fig_to_base64(fig)

def pie(labels, values, title) -> str:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    return _fig_to_base64(fig)

def line(x, y, title, xlabel=None, ylabel=None) -> str:
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, marker="o")  # 색상 미지정
    ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    fig.autofmt_xdate()
    return _fig_to_base64(fig)

def heatmap(arr2d, xlabels, ylabels, title) -> str:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(arr2d, aspect="auto")  # 색상 미지정
    ax.set_title(title)
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels)
    return _fig_to_base64(fig)

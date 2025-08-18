#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
비플로우 주문리스트 → 지정한 셀러별 리포트(HTML, 결제일 기준)
- 이번 데이터의 '정확한 칼럼명'만 사용 (패턴/추론/자동매핑 없음)
- matplotlib만 사용(색상 지정 안 함), 차트당 1개 Figure
- 한글 폰트: macOS/Windows/공용 후보 중 시스템에 있는 폰트 자동 선택
- 환불 지표: '환불율(주문 기준·신청 포함)'만 표기
- 터미널 인자 없이 CONFIG로 제어
"""

from __future__ import annotations

import base64
import io
import math
from pathlib import Path
from typing import Dict, Optional, Tuple, List

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams, font_manager

# ─────────────────────────────────────────────────────────────────────
# 0) 실행 설정 (여기만 수정해서 사용하세요)
# ─────────────────────────────────────────────────────────────────────
CONFIG = {
    # 입력 엑셀 경로
    "INPUT_XLSX": "/Users/brich/Desktop/seller_insightreport/order_list_20250818120157_497.xlsx",
    # 출력 폴더 (없으면 생성)
    "OUTPUT_DIR": "./reports",
    # 기간 필터 (결제일 기준). None이면 전체 사용
    "START_DATE": None,          # 예: "2025-08-11"
    "END_DATE":   None,          # 예: "2025-08-18"
    # 리포트 생성 대상 셀러명 리스트 (정확히 일치). 빈 리스트면 파일의 모든 셀러 자동 생성
    "SELLERS": ["포레스트핏"],     # 예: ["포레스트핏", "ABC몰"]  / []면 전체
    # 모든 셀러 합산 리포트도 생성할지
    "BUILD_OVERALL_REPORT": True,
    # 인덱스 페이지(셀러별 리포트 링크 모음) 생성할지
    "BUILD_INDEX": True,
}

# ─────────────────────────────────────────────────────────────────────
# 1) 한글 폰트 자동 선택(후보 순회)
# ─────────────────────────────────────────────────────────────────────
_KOREAN_FONT_CANDIDATES = [
    "Apple SD Gothic Neo",  # macOS
    "AppleGothic",          # macOS
    "Noto Sans KR",         # 공용
    "NanumGothic",          # 공용
    "Malgun Gothic",        # Windows
    "Noto Sans CJK KR",     # 환경에 따라 이 이름일 수도 있음
]
_available = {f.name for f in font_manager.fontManager.ttflist}
for _name in _KOREAN_FONT_CANDIDATES:
    if _name in _available:
        rcParams["font.family"] = [_name]
        break
rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

# ─────────────────────────────────────────────────────────────────────
# 2) 이번 파일의 '정확한 칼럼명' 고정 매핑 (변경 시 여기를 고치세요)
# ─────────────────────────────────────────────────────────────────────
COL_PAYMENT_DATE   = "결제일"
COL_ORDER_AMOUNT   = "상품별 총 주문금액"
COL_SELLER         = "입점사명"
COL_CHANNEL        = "판매채널"
COL_STATUS         = "주문상태"   # G열
COL_REFUND_FIELD   = "클레임"     # H열  (예: '취소:1', '반품:1')
COL_ITEM_NAME      = "상품명"
COL_QTY            = "수량"
COL_SHIP_DATE      = "발송처리일"
COL_DELIVERED_DATE = "배송완료일"
COL_ORDER_ID       = "주문번호"
COL_CUSTOMER       = "구매자아이디"

# ─────────────────────────────────────────────────────────────────────
# 3) 유틸
# ─────────────────────────────────────────────────────────────────────
def to_datetime_safe(s: pd.Series) -> pd.Series:
    # pandas 2.x: infer_datetime_format deprecated → 제거
    return pd.to_datetime(s, errors="coerce")

def to_number_safe(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(r"[^0-9\.-]", "", regex=True), errors="coerce")

def fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight", dpi=160)
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")

def make_bar(x, y, title, xlabel=None, ylabel=None, rotation=0):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(x, y)  # 색상 미지정
    ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    if rotation:
        for t in ax.get_xticklabels():
            t.set_rotation(rotation)
            t.set_ha("right")
    return fig_to_base64(fig)

def make_pie(labels, values, title):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    return fig_to_base64(fig)

def make_line(x, y, title, xlabel=None, ylabel=None):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(x, y, marker="o")  # 색상 미지정
    ax.set_title(title)
    if xlabel: ax.set_xlabel(xlabel)
    if ylabel: ax.set_ylabel(ylabel)
    fig.autofmt_xdate()
    return fig_to_base64(fig)

def make_heatmap(arr2d, xlabels, ylabels, title):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.imshow(arr2d, aspect="auto")  # 색상 미지정
    ax.set_title(title)
    ax.set_xticks(range(len(xlabels)))
    ax.set_xticklabels(xlabels)
    ax.set_yticks(range(len(ylabels)))
    ax.set_yticklabels(ylabels)
    return fig_to_base64(fig)

def format_currency(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"₩{int(round(float(v))):,}"

def pct(v):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{float(v)*100:.1f}%"

def df_to_html_table(d: Optional[pd.DataFrame], max_rows: int = 15) -> str:
    if d is None or d.empty:
        return "<p>데이터 없음</p>"
    return d.head(max_rows).to_html(index=False, border=1, justify="center")

def sanitize_filename(s: str) -> str:
    return (
        s.replace("/", "_")
         .replace("\\", "_")
         .replace(" ", "_")
         .replace(":", "_")
         .replace("*", "_")
         .replace("?", "_")
         .replace('"', "_")
         .replace("<", "_")
         .replace(">", "_")
         .replace("|", "_")
    )

# ─────────────────────────────────────────────────────────────────────
# 4) 리포트 생성
# ─────────────────────────────────────────────────────────────────────
def build_report_html(
    df: pd.DataFrame,
    seller_name: Optional[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Tuple[str, str, str]:

    # 필수 컬럼 점검
    for col in [COL_PAYMENT_DATE, COL_ORDER_AMOUNT]:
        if col not in df.columns:
            raise KeyError(f"필수 칼럼이 없습니다: {col}")

    dfp = df.copy()
    dfp["__dt__"] = to_datetime_safe(dfp[COL_PAYMENT_DATE])
    dfp["__amount__"] = to_number_safe(dfp[COL_ORDER_AMOUNT])
    dfp["__qty__"] = to_number_safe(dfp[COL_QTY]) if COL_QTY in dfp.columns else 1

    # 유효 데이터만
    dfp = dfp[dfp["__dt__"].notna() & dfp["__amount__"].notna()]

    # 기간 필터
    if start: dfp = dfp[dfp["__dt__"] >= pd.to_datetime(start)]
    if end:   dfp = dfp[dfp["__dt__"] < pd.to_datetime(end) + pd.to_timedelta(1, "D")]

    # 셀러 슬라이스
    if seller_name and COL_SELLER in dfp.columns:
        sdf = dfp[dfp[COL_SELLER].astype(str) == str(seller_name)].copy()
    else:
        sdf = dfp.copy()

    # 기간 문자열
    dmin, dmax = sdf["__dt__"].min(), sdf["__dt__"].max()
    period_str = f"{dmin:%Y-%m-%d} ~ {dmax:%Y-%m-%d}" if pd.notna(dmin) and pd.notna(dmax) else "기간 정보 없음"

    # KPI
    orders = int(len(sdf))
    revenue = float(sdf["__amount__"].sum())
    aov = (revenue / orders) if orders else float("nan")

    # --- 환불/취소 관련 지표 (주문 기준·신청 포함) ---
    # 캡처 그룹() → 비캡처 그룹(?:)로 변경해 경고 제거
    REFUND_REGEX_OPEN = r"(?:환불|취소|반품|refund|cancel)"

    ref_any = pd.Series(False, index=sdf.index)
    if COL_REFUND_FIELD in sdf.columns:
        ref_any = ref_any | sdf[COL_REFUND_FIELD].astype(str).str.contains(REFUND_REGEX_OPEN, case=False, regex=True, na=False)
    if COL_STATUS in sdf.columns:
        ref_any = ref_any | sdf[COL_STATUS].astype(str).str.contains(REFUND_REGEX_OPEN, case=False, regex=True, na=False)
    refund_rate_any = float(ref_any.mean()) if orders else float("nan")

    # 고객/재구매
    unique_customers = float("nan")
    repurchase_rate  = float("nan")
    if COL_CUSTOMER in sdf.columns:
        counts = sdf[COL_CUSTOMER].astype(str).value_counts()
        if counts.shape[0] > 0:
            unique_customers = float(counts.shape[0])
            repurchase_rate  = float((counts >= 2).sum() / counts.shape[0])

    # 리드타임
    lead_ship = float("nan")
    lead_deliv = float("nan")
    if COL_SHIP_DATE in sdf.columns:
        ship_dt = to_datetime_safe(sdf[COL_SHIP_DATE])
        lead_ship = float(((ship_dt - sdf["__dt__"]).dt.total_seconds() / 86400.0).mean())
    if COL_DELIVERED_DATE in sdf.columns and COL_SHIP_DATE in sdf.columns:
        ship_dt = to_datetime_safe(sdf[COL_SHIP_DATE])
        deliv_dt = to_datetime_safe(sdf[COL_DELIVERED_DATE])
        lead_deliv = float(((deliv_dt - ship_dt).dt.total_seconds() / 86400.0).mean())

    # 채널 성과
    images: Dict[str, str] = {}
    ch_tbl = pd.DataFrame()
    if COL_CHANNEL in sdf.columns and len(sdf):
        ch_tbl = (sdf.groupby(COL_CHANNEL)
                    .agg(orders=("__amount__", "size"), revenue=("__amount__", "sum"))
                    .sort_values("revenue", ascending=False))
        if not ch_tbl.empty:
            ch_top = ch_tbl.head(8)
            images["channel_bar"] = make_bar(
                ch_top.index.astype(str), ch_top["orders"].values,
                "채널별 주문수 (Top 8)", "채널", "주문수", rotation=30
            )
            images["channel_pie"] = make_pie(
                ch_top.index.astype(str), ch_top["revenue"].values,
                "채널별 매출 비중 (Top 8)"
            )

    # 일자 추이
    images["daily_line"] = ""
    if len(sdf):
        daily = (sdf.groupby(sdf["__dt__"].dt.date)
                    .agg(revenue=("__amount__", "sum"), orders=("__amount__", "size"))
                    .reset_index())
        if not daily.empty:
            images["daily_line"] = make_line(
                daily.iloc[:,0].astype(str), daily["revenue"].values,
                "일자별 매출 추이", "일자", "매출"
            )

    # 요일×시간 히트맵
    images["heatmap"] = ""
    if len(sdf):
        sdf["__hour__"] = sdf["__dt__"].dt.hour
        sdf["__dow__"]  = sdf["__dt__"].dt.weekday  # 0=Mon
        heat = sdf.pivot_table(index="__dow__", columns="__hour__", values="__amount__", aggfunc="sum", fill_value=0.0)
        for h in range(24):
            if h not in heat.columns:
                heat[h] = 0.0
        heat = heat[sorted(heat.columns)]
        heat_arr = heat.reindex(range(0,7)).fillna(0.0).values
        images["heatmap"] = make_heatmap(
            heat_arr,
            [str(h) for h in sorted(heat.columns)],
            ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
            "요일×시간대 매출 히트맵"
        )

    # 베스트셀러
    prod_top = pd.DataFrame()
    if COL_ITEM_NAME in sdf.columns and len(sdf):
        prod_top = (sdf.groupby(COL_ITEM_NAME)
                      .agg(orders=("__amount__", "size"), revenue=("__amount__", "sum"))
                      .sort_values("revenue", ascending=False)
                      .reset_index()
                      .head(10))

    # 상태 분포
    status_img_html = "<p>상태 데이터 없음</p>"
    if COL_STATUS in sdf.columns and len(sdf):
        st = sdf[COL_STATUS].astype(str).value_counts().reset_index()
        st.columns = ["status", "count"]
        if not st.empty:
            status_img = make_bar(
                st["status"].head(10).values, st["count"].head(10).values,
                "주문상태 분포 (Top10)", "상태", "건수", rotation=30
            )
            status_img_html = f'<img src="data:image/png;base64,{status_img}" alt="주문상태 분포" style="width:100%"/>'

    # 전체 벤치마크(같은 입력 내 · 같은 기간 필터 적용 결과)
    overall = dfp
    overall_orders = len(overall)
    overall_revenue = float(overall["__amount__"].sum())
    overall_aov = (overall_revenue / overall_orders) if overall_orders else float("nan")

    # 전체 환불율(주문 기준·신청 포함)
    REFUND_REGEX_OPEN = r"(?:환불|취소|반품|refund|cancel)"
    overall_ref_any = pd.Series(False, index=overall.index)
    if COL_REFUND_FIELD in overall.columns:
        overall_ref_any = overall_ref_any | overall[COL_REFUND_FIELD].astype(str).str.contains(REFUND_REGEX_OPEN, regex=True, case=False, na=False)
    if COL_STATUS in overall.columns:
        overall_ref_any = overall_ref_any | overall[COL_STATUS].astype(str).str.contains(REFUND_REGEX_OPEN, regex=True, case=False, na=False)
    overall_refund_rate_any = float(overall_ref_any.mean()) if overall_orders else float("nan")

    # 간단 제안
    recos: List[str] = []
    if (not math.isnan(refund_rate_any)) and (not math.isnan(overall_refund_rate_any)) and refund_rate_any > overall_refund_rate_any * 1.2:
        recos.append("환불율이 전체 평균 대비 높습니다. 상위 환불 사유/상품/채널 점검과 상세페이지·CS 스크립트 보완을 권장합니다.")
    if (not math.isnan(aov)) and (not math.isnan(overall_aov)) and aov < overall_aov * 0.8:
        recos.append("AOV가 전체 평균 대비 낮습니다. 번들/세트 구성 또는 배송비 임계값 기반 업셀 전략을 검토하세요.")
    if not recos:
        recos = ["이번 기간 주요 이상징후는 확인되지 않았습니다. 채널 믹스와 리드타임을 지속 모니터링하세요."]

    # 표들
    ch_table_html = df_to_html_table(ch_tbl.reset_index().rename(columns={COL_CHANNEL: "채널"})) if not ch_tbl.empty else "<p>채널 데이터 없음</p>"
    prod_table_html = df_to_html_table(prod_top.rename(columns={COL_ITEM_NAME: "상품"})) if not prod_top.empty else "<p>상품 데이터 없음</p>"

    # KPI 표
    kpi_rows = [
        ("총 주문수", f"{orders:,}"),
        ("총 매출액(결제)", format_currency(revenue)),
        ("AOV(평균주문금액)", format_currency(aov)),
        ("환불율(주문 기준·신청 포함)", pct(refund_rate_any)),
        ("구매고객수",     f"{int(unique_customers):,}" if not math.isnan(unique_customers) else "-"),
        ("재구매율",       pct(repurchase_rate) if not math.isnan(repurchase_rate) else "-"),
        ("출고 리드타임(일)", f"{lead_ship:.2f}" if not math.isnan(lead_ship) else "-"),
        ("배송 리드타임(일)", f"{lead_deliv:.2f}" if not math.isnan(lead_deliv) else "-"),
    ]

    # HTML
    seller_title = seller_name or "전체"
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{seller_title} 월간 성과 리포트</title>
<style>
  @page {{ size: A4; margin: 18mm; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif; }}
  h1, h2, h3 {{ margin: 0 0 8px 0; }}
  .page {{ page-break-after: always; }}
  .kpis {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 16px; margin-top: 12px; }}
  .kpis div {{ padding: 8px 10px; border: 1px solid #ddd; border-radius: 8px; }}
  .row {{ display: flex; gap: 12px; align-items: flex-start; }}
  .col {{ flex: 1; }}
  .imgbox {{ border: 1px solid #eee; padding: 8px; border-radius: 6px; }}
  table {{ font-size: 12px; border-collapse: collapse; width: 100%; }}
  th, td {{ border: 1px solid #ddd; padding: 6px 8px; }}
  .muted {{ color: #555; font-size: 12px; }}
</style>
</head>
<body>

<section class="page">
  <h1>입점사 월간 성과 리포트</h1>
  <h2>{seller_title}</h2>
  <div class="muted">결제일 기준: {period_str}</div>
  <hr/>
  <h3>핵심 지표 요약</h3>
  <div class="kpis">
    {''.join(f'<div><b>{k}</b><br/>{v}</div>' for k, v in kpi_rows)}
  </div>
  <div style="margin-top:14px" class="muted">
    * 환불율은 G열 '{COL_STATUS}'(상태)와 H열 '{COL_REFUND_FIELD}'(클레임) 텍스트에서
      '환불/취소/반품' 키워드가 있는 주문의 비율(신청/발생 포함)을 의미합니다.
  </div>
</section>

<section class="page">
  <h2>채널별 성과</h2>
  <div class="row">
    <div class="col imgbox">
      <img src="data:image/png;base64,{images.get('channel_bar','')}" alt="채널별 주문수" style="width:100%"/>
    </div>
    <div class="col imgbox">
      <img src="data:image/png;base64,{images.get('channel_pie','')}" alt="채널별 매출 비중" style="width:100%"/>
    </div>
  </div>
  <h3 style="margin-top:12px">채널 상위표</h3>
  {ch_table_html}
</section>

<section class="page">
  <h2>시간대/요일 분석</h2>
  <div class="imgbox">
    <img src="data:image/png;base64,{images.get('daily_line','')}" alt="일자별 매출" style="width:100%"/>
  </div>
  <div style="height:8px"></div>
  <div class="imgbox">
    <img src="data:image/png;base64,{images.get('heatmap','')}" alt="요일x시간 히트맵" style="width:100%"/>
  </div>
</section>

<section class="page">
  <h2>상품 & 배송 현황</h2>
  <h3>베스트셀러 TOP 10</h3>
  {prod_table_html}
  <div style="height:8px"></div>
  <h3>주문상태 분포</h3>
  <div class="imgbox">
    {status_img_html}
  </div>
</section>

<section class="page">
  <h2>벤치마크 & 제안</h2>
  <table>
    <tr><th>지표</th><th>{seller_title}</th><th>전체 평균</th></tr>
    <tr><td>AOV</td><td>{format_currency(aov)}</td><td>{format_currency(overall_aov)}</td></tr>
    <tr><td>환불율(주문 기준·신청 포함)</td><td>{pct(refund_rate_any)}</td><td>{pct(overall_refund_rate_any)}</td></tr>
  </table>
  <h3 style="margin-top:10px">개선 제안</h3>
  <ul>
    {''.join(f'<li>{r}</li>' for r in recos)}
  </ul>
  <div class="muted" style="margin-top:10px">
    ※ 본 리포트는 결제일 기준으로 산출되며, 매핑된 칼럼 이외의 지표는 계산하지 않습니다.
  </div>
</section>

</body>
</html>
"""
    return html, (f"{dmin:%Y-%m-%d}" if pd.notna(dmin) else "NA"), (f"{dmax:%Y-%m-%d}" if pd.notna(dmax) else "NA")

# ─────────────────────────────────────────────────────────────────────
# 5) 인덱스 페이지(옵션)
# ─────────────────────────────────────────────────────────────────────
def build_index_html(title: str, items: List[Tuple[str, str]]) -> str:
    # items: [(표시명, 파일명), ...]
    links = "\n".join([f'<li><a href="{fname}" target="_blank">{name}</a></li>' for name, fname in items])
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans KR', 'Apple SD Gothic Neo', 'Malgun Gothic', Arial, sans-serif; padding: 24px; }}
    h1 {{ margin-top: 0; }}
    ul {{ line-height: 1.8; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <ul>
    {links}
  </ul>
</body>
</html>
"""

# ─────────────────────────────────────────────────────────────────────
# 6) 메인: CONFIG 기반 일괄 생성
# ─────────────────────────────────────────────────────────────────────
def main():
    in_path  = Path(CONFIG["INPUT_XLSX"])
    out_dir  = Path(CONFIG["OUTPUT_DIR"]); out_dir.mkdir(parents=True, exist_ok=True)
    start    = CONFIG.get("START_DATE")
    end      = CONFIG.get("END_DATE")
    wanted   = CONFIG.get("SELLERS") or []

    if not in_path.exists():
        raise FileNotFoundError(f"Input not found: {in_path}")

    # 가장 큰 시트를 메인으로 사용
    xls = pd.ExcelFile(in_path)
    sheets = {name: xls.parse(name) for name in xls.sheet_names}
    main_name, df = max(sheets.items(), key=lambda kv: len(kv[1]))
    df.columns = [str(c).strip() for c in df.columns]

    if COL_PAYMENT_DATE not in df.columns or COL_ORDER_AMOUNT not in df.columns:
        raise KeyError(f"필수 칼럼 부족: '{COL_PAYMENT_DATE}', '{COL_ORDER_AMOUNT}'")

    # 생성 대상 셀러 집합 결정
    if len(wanted) == 0:
        if COL_SELLER not in df.columns:
            raise KeyError(f"모든 셀러 생성에는 '{COL_SELLER}' 칼럼이 필요합니다.")
        sellers = df[COL_SELLER].dropna().astype(str).unique().tolist()
    else:
        sellers = wanted

    index_items: List[Tuple[str, str]] = []

    # 지정 셀러들 생성
    for s in sellers:
        if COL_SELLER in df.columns and s not in df[COL_SELLER].astype(str).unique():
            print(f"⚠️  스킵: '{s}'는 데이터에 없음")
            continue
        html, dmin, dmax = build_report_html(df, seller_name=s, start=start, end=end)
        fname = f"seller_report_{sanitize_filename(s)}_{dmin}_{dmax}.html"
        (out_dir / fname).write_text(html, encoding="utf-8")
        index_items.append((s, fname))
        print(f"✔ Saved: {out_dir / fname}")

    # 전체(합산) 리포트
    if CONFIG.get("BUILD_OVERALL_REPORT", True):
        html, dmin, dmax = build_report_html(df, seller_name=None, start=start, end=end)
        fname = f"seller_report_전체_{dmin}_{dmax}.html"
        (out_dir / fname).write_text(html, encoding="utf-8")
        index_items.insert(0, ("전체", fname))
        print(f"✔ Saved: {out_dir / fname}")

    # 인덱스 페이지
    if CONFIG.get("BUILD_INDEX", True) and index_items:
        idx_html = build_index_html("셀러 리포트 인덱스", index_items)
        (out_dir / "index.html").write_text(idx_html, encoding="utf-8")
        print(f"✔ Saved: {out_dir / 'index.html'}")

if __name__ == "__main__":
    main()

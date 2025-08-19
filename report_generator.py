# report_generator.py
"""HTML 리포트 생성"""

import math
import pandas as pd
from typing import Optional, Tuple, Dict
from utils import format_currency, pct, df_to_html_table
from charts import make_bar, make_pie, make_line, make_heatmap
from data_processor import *

def _build_html_template(seller_title, period_str, kpis, customers_str, repurchase_str, 
                        lead_ship_str, lead_deliv_str, daily_img, images, ch_table_html, 
                        prod_table_html, heatmap_img, status_img):
    """HTML 템플릿 생성"""
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<title>{seller_title} 성과 리포트</title>
<style>
@page {{ size: A4; margin: 12mm; }}
body {{ font-family: -apple-system, sans-serif; font-size: 11px; margin: 0; }}
.page {{ page-break-after: always; height: 270mm; }}
.q {{ font-size: 18px; font-weight: 600; margin: 0 0 2px 0; }}
.theme {{ font-size: 12px; color: #666; margin: 0 0 8px 0; }}
.period {{ font-size: 10px; color: #999; margin: 0 0 12px 0; }}
.grid2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }}
.kpi {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; margin: 8px 0; }}
.kpi-item {{ border: 1px solid #ddd; padding: 6px; text-align: center; }}
.kpi-item b {{ display: block; font-size: 9px; }}
.kpi-item span {{ font-size: 13px; font-weight: 600; }}
.chart {{ border: 1px solid #eee; padding: 4px; }}
.chart img {{ width: 100%; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9px; }}
th, td {{ border: 1px solid #ddd; padding: 3px 4px; }}
th {{ background: #f5f5f5; font-weight: 600; }}
.bench {{ display: grid; grid-template-columns: 2fr 1fr; gap: 8px; }}
.reco {{ font-size: 10px; }}
.reco li {{ margin: 2px 0; }}
</style>
</head>
<body>

<!-- 페이지 1: 전체 성과는 어때? -->
<section class="page">
<div class="q">전체 성과는 어때?</div>
<div class="theme">성과 개요</div>
<div class="period">{seller_title} | {period_str}</div>

<div class="kpi">
<div class="kpi-item"><b>총 주문수</b><span>{kpis['orders']:,}</span></div>
<div class="kpi-item"><b>총 매출액</b><span>{format_currency(kpis['revenue'])}</span></div>
<div class="kpi-item"><b>평균주문금액</b><span>{format_currency(kpis['aov'])}</span></div>
<div class="kpi-item"><b>환불율</b><span>{pct(kpis['refund_rate_any'])}</span></div>
</div>

<div class="chart">
<img src="data:image/png;base64,{daily_img}" alt="매출추이"/>
</div>

<div style="margin-top:8px;">
<div class="kpi">
<div class="kpi-item"><b>구매고객수</b><span>{customers_str}</span></div>
<div class="kpi-item"><b>재구매율</b><span>{repurchase_str}</span></div>
<div class="kpi-item"><b>출고리드타임</b><span>{lead_ship_str}</span></div>
<div class="kpi-item"><b>배송리드타임</b><span>{lead_deliv_str}</span></div>
</div>
</div>
</section>

<!-- 페이지 2: 어디서 잘되고 있지? -->
<section class="page">
<div class="q">어디서 잘되고 있지?</div>
<div class="theme">채널 & 상품 분석</div>

<div class="grid2" style="margin-bottom:8px;">
<div class="chart">
<img src="data:image/png;base64,{images.get('channel_bar','')}" alt="채널주문"/>
</div>
<div class="chart">
<img src="data:image/png;base64,{images.get('channel_pie','')}" alt="채널매출"/>
</div>
</div>

<div class="grid2">
<div>
<b style="font-size:12px;">채널 성과</b>
{ch_table_html}
</div>
<div>
<b style="font-size:12px;">베스트셀러</b>
{prod_table_html}
</div>
</div>
</section>

<!-- 페이지 3: 문제는 없나? 어떻게 개선할까? -->
<section class="page">
<div class="q">문제는 없나? 어떻게 개선할까?</div>
<div class="theme">운영 분석 & 개선안</div>

<div class="grid2" style="margin-bottom:8px;">
<div class="chart">
<img src="data:image/png;base64,{heatmap_img}" alt="시간패턴"/>
</div>
<div class="chart">
<img src="data:image/png;base64,{status_img}" alt="주문상태"/>
</div>
</div>

<div class="bench">
<div>
<b style="font-size:12px;">벤치마크 비교</b>
<table style="margin-top:4px;">
<tr><th>지표</th><th>{seller_title}</th><th>전체평균</th></tr>
<tr><td>AOV</td><td>{format_currency(kpis['aov'])}</td><td>{format_currency(kpis['overall_aov'])}</td></tr>
<tr><td>환불율</td><td>{pct(kpis['refund_rate_any'])}</td><td>{pct(kpis['overall_refund_rate_any'])}</td></tr>
</table>
</div>
<div>
<b style="font-size:12px;">개선 제안</b>
<ul class="reco">
{''.join(f'<li>{r}</li>' for r in kpis["recos"])}
</ul>
</div>
</div>
</section>

</body>
</html>"""

def generate_report_html(
    df: pd.DataFrame,
    seller_name: Optional[str],
    start: Optional[str] = None,
    end: Optional[str] = None,
) -> Tuple[str, str, str]:
    """컴팩트 HTML 리포트 생성"""
    
    # 필수 컬럼 점검
    for col in [COL_PAYMENT_DATE, COL_ORDER_AMOUNT]:
        if col not in df.columns:
            raise KeyError(f"필수 칼럼이 없습니다: {col}")

    # 데이터 전처리
    dfp = prepare_dataframe(df, start, end)
    sdf = slice_by_seller(dfp, seller_name)
    
    # 기간 문자열
    dmin, dmax = sdf["__dt__"].min(), sdf["__dt__"].max()
    period_str = f"{dmin:%Y-%m-%d} ~ {dmax:%Y-%m-%d}" if pd.notna(dmin) and pd.notna(dmax) else "기간 정보 없음"
    
    # KPI 계산
    kpis = calculate_kpis(sdf, dfp)
    
    # 분석 데이터
    ch_tbl = get_channel_analysis(sdf)
    daily = get_daily_trend(sdf)
    heat_data = get_heatmap_data(sdf)
    prod_top = get_product_analysis(sdf)
    status_data = get_status_analysis(sdf)
    
    # 차트 생성
    images = {}
    
    if not ch_tbl.empty:
        ch_top = ch_tbl.head(6)
        images["channel_bar"] = make_bar(
            ch_top.index.astype(str), ch_top["orders"].values,
            "채널별 주문수", rotation=30
        )
        images["channel_pie"] = make_pie(
            ch_top.index.astype(str), ch_top["revenue"].values,
            "채널별 매출 비중"
        )

    daily_img = ""
    if not daily.empty:
        daily_img = make_line(
            daily.iloc[:,0].astype(str), daily["revenue"].values,
            "일자별 매출 추이"
        )

    heatmap_img = ""
    if heat_data[0] is not None:
        heat_arr, xlabels, ylabels = heat_data
        heatmap_img = make_heatmap(heat_arr, xlabels, ylabels, "요일×시간 매출 패턴")

    status_img = ""
    if not status_data.empty:
        status_img = make_bar(
            status_data["status"].head(8).values, 
            status_data["count"].head(8).values,
            "주문상태 분포", rotation=30
        )

    # 테이블 HTML
    ch_table_html = df_to_html_table(ch_tbl.reset_index().rename(columns={COL_CHANNEL: "채널"})) if not ch_tbl.empty else "<div>-</div>"
    prod_table_html = df_to_html_table(prod_top.rename(columns={COL_ITEM_NAME: "상품"})) if not prod_top.empty else "<div>-</div>"

    # 셀러 타이틀
    seller_title = seller_name or "전체"

    # KPI 값들을 미리 포맷팅
    customers_str = f"{int(kpis['unique_customers']):,}" if not math.isnan(kpis['unique_customers']) else "-"
    repurchase_str = pct(kpis['repurchase_rate']) if not math.isnan(kpis['repurchase_rate']) else "-"
    lead_ship_str = f"{kpis['lead_ship']:.1f}일" if not math.isnan(kpis['lead_ship']) else "-"
    lead_deliv_str = f"{kpis['lead_deliv']:.1f}일" if not math.isnan(kpis['lead_deliv']) else "-"

    # HTML 생성
    html = _build_html_template(
        seller_title, period_str, kpis, customers_str, repurchase_str,
        lead_ship_str, lead_deliv_str, daily_img, images, ch_table_html,
        prod_table_html, heatmap_img, status_img
    )
    
    return html, (f"{dmin:%Y-%m-%d}" if pd.notna(dmin) else "NA"), (f"{dmax:%Y-%m-%d}" if pd.notna(dmax) else "NA")
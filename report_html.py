# report_html.py
import pandas as pd
from typing import Dict, Tuple

from .utils import df_to_html_table, format_currency, pct
from .charts import bar, pie, line, heatmap

def render_report(
    seller_title: str,
    period_str: str,
    kpi: Dict,
    ch_tbl: pd.DataFrame,
    daily: pd.DataFrame,
    heat_arr_tuple,    # (arr, xlabels, ylabels)
    prod_top: pd.DataFrame,
    status_df: pd.DataFrame,
    cols_hint: Tuple[str, str] = ("주문상태", "클레임"),
) -> str:
    images: Dict[str, str] = {}

    if ch_tbl is not None and not ch_tbl.empty:
        ch_top = ch_tbl.head(8)
        images["channel_bar"] = bar(ch_top.index.astype(str), ch_top["orders"].values, "채널별 주문수 (Top 8)", "채널", "주문수", rotation=30)
        images["channel_pie"] = pie(ch_top.index.astype(str), ch_top["revenue"].values, "채널별 매출 비중 (Top 8)")

    images["daily_line"] = ""
    if daily is not None and not daily.empty:
        images["daily_line"] = line(daily.iloc[:,0].astype(str), daily["revenue"].values, "일자별 매출 추이", "일자", "매출")

    images["heatmap"] = ""
    if heat_arr_tuple is not None and heat_arr_tuple[0] is not None:
        arr, xl, yl = heat_arr_tuple
        images["heatmap"] = heatmap(arr, xl, yl, "요일×시간대 매출 히트맵")

    status_img_html = "<p>상태 데이터 없음</p>"
    if status_df is not None and not status_df.empty:
        status_img = bar(status_df["status"].head(10).values, status_df["count"].head(10).values, "주문상태 분포 (Top10)", "상태", "건수", rotation=30)
        status_img_html = f'<img src="data:image/png;base64,{status_img}" alt="주문상태 분포" style="width:100%"/>'

    ch_table_html   = df_to_html_table(ch_tbl.reset_index().rename(columns={"판매채널": "채널"})) if (ch_tbl is not None and not ch_tbl.empty) else "<p>채널 데이터 없음</p>"
    prod_table_html = df_to_html_table(prod_top.rename(columns={"상품명": "상품"})) if (prod_top is not None and not prod_top.empty) else "<p>상품 데이터 없음</p>"

    kpi_rows = [
        ("총 주문수", f"{kpi['orders']:,}"),
        ("총 매출액(결제)", format_currency(kpi['revenue'])),
        ("AOV(평균주문금액)", format_currency(kpi['aov'])),
        ("환불율(주문 기준·신청 포함)", pct(kpi['refund_rate_any'])),
        ("구매고객수", f"{int(kpi['unique_customers']):,}" if pd.notna(kpi['unique_customers']) else "-"),
        ("재구매율", pct(kpi['repurchase_rate']) if pd.notna(kpi['repurchase_rate']) else "-"),
        ("출고 리드타임(일)", f"{kpi['lead_ship']:.2f}" if pd.notna(kpi['lead_ship']) else "-"),
        ("배송 리드타임(일)", f"{kpi['lead_deliv']:.2f}" if pd.notna(kpi['lead_deliv']) else "-"),
    ]

    recos_html = "".join(f"<li>{r}</li>" for r in kpi["recos"])

    html = f"""<!DOCTYPE html>
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
    * 환불율은 G열 '{cols_hint[0]}'(상태)와 H열 '{cols_hint[1]}'(클레임) 텍스트에서
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
  {df_to_html_table(prod_top.rename(columns={{"상품명":"상품"}})) if (prod_top is not None and not prod_top.empty) else "<p>상품 데이터 없음</p>"}
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
    <tr><td>AOV</td><td>{format_currency(kpi['aov'])}</td><td>{format_currency(kpi['overall_aov'])}</td></tr>
    <tr><td>환불율(주문 기준·신청 포함)</td><td>{pct(kpi['refund_rate_any'])}</td><td>{pct(kpi['overall_refund_rate_any'])}</td></tr>
  </table>
  <h3 style="margin-top:10px">개선 제안</h3>
  <ul>
    {recos_html}
  </ul>
  <div class="muted" style="margin-top:10px">
    ※ 본 리포트는 결제일 기준으로 산출되며, 매핑된 칼럼 이외의 지표는 계산하지 않습니다.
  </div>
</section>

</body>
</html>
"""
    return html

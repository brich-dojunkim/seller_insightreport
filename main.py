# main.py
from pathlib import Path

from .config import CONFIG
from .fonts import select_korean_font
from .constants import COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_STATUS, COL_REFUND_FIELD
from .utils import sanitize_filename
from .dataio import load_main_sheet, resolve_sellers
from .metrics import (
    prepare_base, slice_seller, compute_kpis, channel_table,
    daily_summary, heatmap_matrix, product_top, status_counts
)
from .report_html import render_report
from .index_html import build_index_html

def main():
    # 폰트 세팅
    select_korean_font()

    in_path  = CONFIG["INPUT_XLSX"]
    out_dir  = Path(CONFIG["OUTPUT_DIR"]); out_dir.mkdir(parents=True, exist_ok=True)
    start    = CONFIG.get("START_DATE")
    end      = CONFIG.get("END_DATE")
    wanted   = CONFIG.get("SELLERS") or []

    df = load_main_sheet(in_path)
    if COL_PAYMENT_DATE not in df.columns or COL_ORDER_AMOUNT not in df.columns:
        raise KeyError(f"필수 칼럼 부족: '{COL_PAYMENT_DATE}', '{COL_ORDER_AMOUNT}'")

    # 기간 필터/전처리
    base = prepare_base(df, start, end)

    # 대상 셀러 집합
    sellers = resolve_sellers(df, wanted)

    # 인덱스 아이템
    index_items: list[tuple[str, str]] = []

    # 전체(합산) 리포트
    if CONFIG.get("BUILD_OVERALL_REPORT", True):
        sdf = slice_seller(base, None)
        kpi = compute_kpis(sdf, overall=base)
        dmin, dmax = sdf["__dt__"].min(), sdf["__dt__"].max()
        period_str = f"{dmin:%Y-%m-%d} ~ {dmax:%Y-%m-%d}" if (dmin is not None and dmax is not None) else "기간 정보 없음"

        ch_tbl = channel_table(sdf)
        daily  = daily_summary(sdf)
        hmtx   = heatmap_matrix(sdf)
        ptop   = product_top(sdf)
        st_df  = status_counts(sdf)

        html = render_report(
            seller_title="전체",
            period_str=period_str,
            kpi=kpi,
            ch_tbl=ch_tbl,
            daily=daily,
            heat_arr_tuple=hmtx,
            prod_top=ptop,
            status_df=st_df,
            cols_hint=(COL_STATUS, COL_REFUND_FIELD),
        )
        fname = f"seller_report_전체_{dmin:%Y-%m-%d}_{dmax:%Y-%m-%d}.html" if (dmin is not None and dmax is not None) else "seller_report_전체.html"
        (out_dir / fname).write_text(html, encoding="utf-8")
        index_items.append(("전체", fname))
        print(f"✔ Saved: {out_dir / fname}")

    # 지정 셀러 리포트
    for s in sellers:
        if s == "전체":
            continue
        if s not in df.get("입점사명", [] if df.empty else df["입점사명"].astype(str).unique()):
            print(f"⚠️  스킵: '{s}'는 데이터에 없음")
            continue

        sdf = slice_seller(base, s)
        if sdf.empty:
            print(f"⚠️  스킵: '{s}'는 기간 필터에 데이터가 없음")
            continue

        kpi = compute_kpis(sdf, overall=base)
        dmin, dmax = sdf["__dt__"].min(), sdf["__dt__"].max()
        period_str = f"{dmin:%Y-%m-%d} ~ {dmax:%Y-%m-%d}" if (dmin is not None and dmax is not None) else "기간 정보 없음"

        ch_tbl = channel_table(sdf)
        daily  = daily_summary(sdf)
        hmtx   = heatmap_matrix(sdf)
        ptop   = product_top(sdf)
        st_df  = status_counts(sdf)

        html = render_report(
            seller_title=s,
            period_str=period_str,
            kpi=kpi,
            ch_tbl=ch_tbl,
            daily=daily,
            heat_arr_tuple=hmtx,
            prod_top=ptop,
            status_df=st_df,
            cols_hint=(COL_STATUS, COL_REFUND_FIELD),
        )
        safe = sanitize_filename(s)
        fname = f"seller_report_{safe}_{dmin:%Y-%m-%d}_{dmax:%Y-%m-%d}.html" if (dmin is not None and dmax is not None) else f"seller_report_{safe}.html"
        (out_dir / fname).write_text(html, encoding="utf-8")
        index_items.append((s, fname))
        print(f"✔ Saved: {out_dir / fname}")

    # 인덱스 생성
    if CONFIG.get("BUILD_INDEX", True) and index_items:
        title = CONFIG.get("INDEX_TITLE", "셀러 리포트 인덱스")
        idx_html = build_index_html(title, index_items)
        (out_dir / "index.html").write_text(idx_html, encoding="utf-8")
        print(f"✔ Saved: {out_dir / 'index.html'}")

if __name__ == "__main__":
    main()

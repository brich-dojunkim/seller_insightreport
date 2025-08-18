# metrics.py
import math
import pandas as pd

from .utils import to_datetime_safe, to_number_safe, build_pseudokey_row
from .constants import (
    COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_QTY, COL_SELLER, COL_CHANNEL,
    COL_STATUS, COL_REFUND_FIELD, COL_ITEM_NAME, COL_SHIP_DATE,
    COL_DELIVERED_DATE, REFUND_REGEX_OPEN,
    COL_CUSTOMER_NAME, COL_CUSTOMER_ID,
    COL_BUYER_PHONE, COL_POSTCODE, COL_ADDRESS_LINE,
)

def prepare_base(df: pd.DataFrame, start: str | None, end: str | None) -> pd.DataFrame:
    d = df.copy()
    d["__dt__"]     = to_datetime_safe(d[COL_PAYMENT_DATE])
    d["__amount__"] = to_number_safe(d[COL_ORDER_AMOUNT])
    d["__qty__"]    = to_number_safe(d[COL_QTY]) if COL_QTY in d.columns else 1
    d = d[d["__dt__"].notna() & d["__amount__"].notna()]
    if start:
        d = d[d["__dt__"] >= pd.to_datetime(start)]
    if end:
        d = d[d["__dt__"] < pd.to_datetime(end) + pd.to_timedelta(1, "D")]
    return d

def slice_seller(d: pd.DataFrame, seller_name: str | None) -> pd.DataFrame:
    if seller_name and COL_SELLER in d.columns:
        return d[d[COL_SELLER].astype(str) == str(seller_name)].copy()
    return d.copy()

# ── 가명키 컬럼 구성 ─────────────────────────────────────────────
def _choose_customer_name_col(df: pd.DataFrame) -> str | None:
    # 이름 우선, 없으면 아이디
    if COL_CUSTOMER_NAME in df.columns and df[COL_CUSTOMER_NAME].notna().any():
        return COL_CUSTOMER_NAME
    if COL_CUSTOMER_ID in df.columns and df[COL_CUSTOMER_ID].notna().any():
        return COL_CUSTOMER_ID
    return None

def _pseudokey_series(df: pd.DataFrame) -> pd.Series:
    name_col = _choose_customer_name_col(df)
    phone_col = COL_BUYER_PHONE if COL_BUYER_PHONE in df.columns else None
    pc_col    = COL_POSTCODE if COL_POSTCODE in df.columns else None
    addr_col  = COL_ADDRESS_LINE if COL_ADDRESS_LINE in df.columns else None

    def _one(i):
        name = df.at[i, name_col] if name_col else None
        phone = df.at[i, phone_col] if phone_col else None
        pc = df.at[i, pc_col] if pc_col else None
        addr = df.at[i, addr_col] if addr_col else None
        return build_pseudokey_row(name, phone, pc, addr)

    return pd.Series({_i: _one(_i) for _i in df.index})

def _unique_and_repurchase_by_pseudokey(df: pd.DataFrame) -> tuple[float, float]:
    keys = _pseudokey_series(df)
    keys = keys.dropna().astype(str)
    keys = keys[keys.str.strip() != ""]
    if keys.empty:
        return float("nan"), float("nan")
    counts = keys.value_counts()
    unique_customers = float(counts.shape[0])
    repurchase_rate  = float((counts >= 2).sum() / counts.shape[0])
    return unique_customers, repurchase_rate

def compute_kpis(sdf: pd.DataFrame, overall: pd.DataFrame) -> dict:
    orders  = int(len(sdf))
    revenue = float(sdf["__amount__"].sum())
    aov     = (revenue / orders) if orders else float("nan")

    # 환불율(주문 기준·신청 포함)
    ref_any = pd.Series(False, index=sdf.index)
    if COL_REFUND_FIELD in sdf.columns:
        ref_any = ref_any | sdf[COL_REFUND_FIELD].astype(str)\
            .str.contains(REFUND_REGEX_OPEN, case=False, regex=True, na=False)
    if COL_STATUS in sdf.columns:
        ref_any = ref_any | sdf[COL_STATUS].astype(str)\
            .str.contains(REFUND_REGEX_OPEN, case=False, regex=True, na=False)
    refund_rate_any = float(ref_any.mean()) if orders else float("nan")

    # 고객/재구매 — 가명키 기반
    unique_customers, repurchase_rate = _unique_and_repurchase_by_pseudokey(sdf)

    # 리드타임
    lead_ship = float("nan")
    lead_deliv = float("nan")
    if COL_SHIP_DATE in sdf.columns:
        ship_dt = pd.to_datetime(sdf[COL_SHIP_DATE], errors="coerce")
        lead_ship = float(((ship_dt - sdf["__dt__"]).dt.total_seconds() / 86400.0).mean())
    if COL_DELIVERED_DATE in sdf.columns and COL_SHIP_DATE in sdf.columns:
        ship_dt = pd.to_datetime(sdf[COL_SHIP_DATE], errors="coerce")
        deliv_dt = pd.to_datetime(sdf[COL_DELIVERED_DATE], errors="coerce")
        lead_deliv = float(((deliv_dt - ship_dt).dt.total_seconds() / 86400.0).mean())

    # 전체 벤치마크
    overall_orders  = len(overall)
    overall_revenue = float(overall["__amount__"].sum())
    overall_aov     = (overall_revenue / overall_orders) if overall_orders else float("nan")

    overall_ref_any = pd.Series(False, index=overall.index)
    if COL_REFUND_FIELD in overall.columns:
        overall_ref_any = overall_ref_any | overall[COL_REFUND_FIELD].astype(str)\
            .str.contains(REFUND_REGEX_OPEN, regex=True, case=False, na=False)
    if COL_STATUS in overall.columns:
        overall_ref_any = overall_ref_any | overall[COL_STATUS].astype(str)\
            .str.contains(REFUND_REGEX_OPEN, regex=True, case=False, na=False)
    overall_refund_rate_any = float(overall_ref_any.mean()) if overall_orders else float("nan")

    # 간단 제안
    recos: list[str] = []
    if (not math.isnan(refund_rate_any)) and (not math.isnan(overall_refund_rate_any)) and refund_rate_any > overall_refund_rate_any * 1.2:
        recos.append("환불율이 전체 평균 대비 높습니다. 상위 환불 사유/상품/채널 점검과 상세페이지·CS 스크립트 보완을 권장합니다.")
    if (not math.isnan(aov)) and (not math.isnan(overall_aov)) and aov < overall_aov * 0.8:
        recos.append("AOV가 전체 평균 대비 낮습니다. 번들/세트 구성 또는 배송비 임계값 기반 업셀 전략을 검토하세요.")
    if not recos:
        recos = ["이번 기간 주요 이상징후는 확인되지 않았습니다. 채널 믹스와 리드타임을 지속 모니터링하세요."]

    return dict(
        orders=orders, revenue=revenue, aov=aov,
        refund_rate_any=refund_rate_any,
        unique_customers=unique_customers, repurchase_rate=repurchase_rate,
        lead_ship=lead_ship, lead_deliv=lead_deliv,
        overall_aov=overall_aov, overall_refund_rate_any=overall_refund_rate_any,
        recos=recos
    )

def channel_table(sdf: pd.DataFrame) -> pd.DataFrame:
    if COL_CHANNEL not in sdf.columns or not len(sdf):
        return pd.DataFrame()
    return (sdf.groupby(COL_CHANNEL)
              .agg(orders=("__amount__", "size"), revenue=("__amount__", "sum"))
              .sort_values("revenue", ascending=False))

def daily_summary(sdf: pd.DataFrame) -> pd.DataFrame:
    if not len(sdf):
        return pd.DataFrame()
    return (sdf.groupby(sdf["__dt__"].dt.date)
              .agg(revenue=("__amount__", "sum"), orders=("__amount__", "size"))
              .reset_index())

def heatmap_matrix(sdf: pd.DataFrame):
    if not len(sdf):
        return None, None, None
    sdf = sdf.copy()
    sdf["__hour__"] = sdf["__dt__"].dt.hour
    sdf["__dow__"]  = sdf["__dt__"].dt.weekday  # 0=Mon
    heat = sdf.pivot_table(index="__dow__", columns="__hour__", values="__amount__", aggfunc="sum", fill_value=0.0)
    for h in range(24):
        if h not in heat.columns:
            heat[h] = 0.0
    heat = heat[sorted(heat.columns)]
    arr = heat.reindex(range(0,7)).fillna(0.0).values
    xlabels = [str(h) for h in sorted(heat.columns)]
    ylabels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    return arr, xlabels, ylabels

def product_top(sdf: pd.DataFrame, topn: int = 10) -> pd.DataFrame:
    if COL_ITEM_NAME not in sdf.columns or not len(sdf):
        return pd.DataFrame()
    return (sdf.groupby(COL_ITEM_NAME)
              .agg(orders=("__amount__", "size"), revenue=("__amount__", "sum"))
              .sort_values("revenue", ascending=False)
              .reset_index()
              .head(topn))

def status_counts(sdf: pd.DataFrame) -> pd.DataFrame:
    if COL_STATUS not in sdf.columns or not len(sdf):
        return pd.DataFrame()
    st = sdf[COL_STATUS].astype(str).value_counts().reset_index()
    st.columns = ["status", "count"]
    return st

# data_processor.py
"""데이터 처리 및 분석 함수들"""

import math
import pandas as pd
from typing import Optional, Tuple, List, Dict
from constants import *
from utils import to_datetime_safe, to_number_safe

def validate_dataframe(df: pd.DataFrame) -> None:
    """데이터프레임 유효성 검사"""
    if df.empty:
        raise ValueError("입력 데이터가 비어있습니다.")
    
    required_cols = [COL_PAYMENT_DATE, COL_ORDER_AMOUNT]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise KeyError(f"필수 컬럼이 없습니다: {missing_cols}")

def prepare_dataframe(df: pd.DataFrame, start: Optional[str], end: Optional[str]) -> pd.DataFrame:
    """데이터프레임 전처리 (메모리 최적화)"""
    validate_dataframe(df)
    
    # 필요한 컬럼만 선택
    needed_cols = [COL_PAYMENT_DATE, COL_ORDER_AMOUNT, COL_SELLER, COL_CHANNEL, 
                   COL_QTY, COL_STATUS, COL_REFUND_FIELD, COL_SHIP_DATE, 
                   COL_DELIVERED_DATE, COL_CUSTOMER, COL_ITEM_NAME, COL_ORDER_ID]
    available_cols = [col for col in needed_cols if col in df.columns]
    
    dfp = df[available_cols].copy()
    dfp["__dt__"] = to_datetime_safe(dfp[COL_PAYMENT_DATE])
    dfp["__amount__"] = to_number_safe(dfp[COL_ORDER_AMOUNT])
    dfp["__qty__"] = to_number_safe(dfp[COL_QTY]) if COL_QTY in dfp.columns else 1

    # 유효 데이터만
    dfp = dfp[dfp["__dt__"].notna() & dfp["__amount__"].notna()]
    if dfp.empty:
        raise ValueError("유효한 데이터가 없습니다.")

    # 기간 필터
    if start: dfp = dfp[dfp["__dt__"] >= pd.to_datetime(start)]
    if end:   dfp = dfp[dfp["__dt__"] < pd.to_datetime(end) + pd.to_timedelta(1, "D")]

    return dfp

def slice_by_seller(df: pd.DataFrame, seller_name: Optional[str]) -> pd.DataFrame:
    """셀러별 데이터 슬라이싱"""
    if seller_name and COL_SELLER in df.columns:
        filtered = df[df[COL_SELLER].astype(str) == str(seller_name)].copy()
        if filtered.empty:
            raise ValueError(f"셀러 '{seller_name}'의 데이터가 없습니다.")
        return filtered
    return df.copy()

def safe_divide(a, b):
    """안전한 나누기"""
    if b == 0 or pd.isna(b):
        return float("nan")
    return a / b

def calculate_kpis(sdf: pd.DataFrame, overall: pd.DataFrame) -> Dict:
    """KPI 계산 (개선된 에러 처리)"""
    if sdf.empty:
        raise ValueError("분석할 데이터가 없습니다.")
    
    orders = int(len(sdf))
    revenue = float(sdf["__amount__"].sum())
    aov = safe_divide(revenue, orders)

    # 환불/취소 관련 지표
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
            repurchase_rate = safe_divide((counts >= 2).sum(), counts.shape[0])

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

    # 전체 벤치마크
    overall_orders = len(overall) if not overall.empty else 0
    overall_revenue = float(overall["__amount__"].sum()) if not overall.empty else 0
    overall_aov = safe_divide(overall_revenue, overall_orders)

    overall_ref_any = pd.Series(False, index=overall.index) if not overall.empty else pd.Series(dtype=bool)
    if not overall.empty:
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

    return {
        'orders': orders, 'revenue': revenue, 'aov': aov,
        'refund_rate_any': refund_rate_any,
        'unique_customers': unique_customers, 'repurchase_rate': repurchase_rate,
        'lead_ship': lead_ship, 'lead_deliv': lead_deliv,
        'overall_aov': overall_aov, 'overall_refund_rate_any': overall_refund_rate_any,
        'recos': recos
    }

def get_channel_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """채널별 분석"""
    if COL_CHANNEL not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    return (sdf.groupby(COL_CHANNEL)
              .agg(orders=("__amount__", "size"), revenue=("__amount__", "sum"))
              .sort_values("revenue", ascending=False))

def get_daily_trend(sdf: pd.DataFrame) -> pd.DataFrame:
    """일자별 추이"""
    if sdf.empty:
        return pd.DataFrame()
    return (sdf.groupby(sdf["__dt__"].dt.date)
              .agg(revenue=("__amount__", "sum"), orders=("__amount__", "size"))
              .reset_index())

def get_heatmap_data(sdf: pd.DataFrame) -> Tuple:
    """히트맵 데이터"""
    if sdf.empty:
        return None, None, None
    
    sdf = sdf.copy()
    sdf["__hour__"] = sdf["__dt__"].dt.hour
    sdf["__dow__"]  = sdf["__dt__"].dt.weekday  # 0=Mon
    
    try:
        heat = sdf.pivot_table(index="__dow__", columns="__hour__", values="__amount__", aggfunc="sum", fill_value=0.0)
        
        for h in range(24):
            if h not in heat.columns:
                heat[h] = 0.0
        heat = heat[sorted(heat.columns)]
        heat_arr = heat.reindex(range(0,7)).fillna(0.0).values
        xlabels = [str(h) for h in sorted(heat.columns)]
        ylabels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
        
        return heat_arr, xlabels, ylabels
    except Exception:
        return None, None, None

def get_product_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """상품 분석"""
    if COL_ITEM_NAME not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    return (sdf.groupby(COL_ITEM_NAME)
              .agg(orders=("__amount__", "size"), revenue=("__amount__", "sum"))
              .sort_values("revenue", ascending=False)
              .reset_index()
              .head(8))

def get_status_analysis(sdf: pd.DataFrame) -> pd.DataFrame:
    """상태 분석"""
    if COL_STATUS not in sdf.columns or sdf.empty:
        return pd.DataFrame()
    st = sdf[COL_STATUS].astype(str).value_counts().reset_index()
    st.columns = ["status", "count"]
    return st
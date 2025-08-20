#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""통합 셀러 성과 대시보드 테스트 - 기술검증과 비즈니스 인사이트 통합
단일 시트(1개) 엑셀(xlsx) 아웃풋 — 콘솔과 동일한 구성/로직을 유지하되
엑셀 셀 단위로 매핑/디자인하여 배치
"""

import sys
import math
from pathlib import Path
from typing import Optional, List, Tuple
from datetime import datetime

import pandas as pd

# 로컬 모듈
sys.path.insert(0, str(Path(__file__).parent))
from config import CONFIG
from file_manager import load_excel_data
from constants import *
from utils import format_currency, pct, sanitize_filename

# data_processing 모듈
from data_processing import (
    prepare_dataframe, slice_by_seller, 
    calculate_comprehensive_kpis, calculate_kpis,
    get_channel_analysis, get_product_analysis, get_category_analysis,
    get_region_analysis, get_time_analysis, get_comprehensive_analysis,
    get_comprehensive_analysis_with_benchmarks,
    to_datetime_safe, to_number_safe, create_customer_id,
    extract_region_from_address, load_category_mapping
)


# ──────────────────────────────────────────────────────────────────────────────
# 엑셀 유틸
# ──────────────────────────────────────────────────────────────────────────────
def _safe_sheet_name(name: str) -> str:
    bad = ['\\','/','*','?','[',']',':']
    for b in bad:
        name = name.replace(b, ' ')
    name = name.strip() or "Sheet"
    return name[:31]


class SellerDashboard:
    """셀러 성과 대시보드 클래스"""
    
    def __init__(self, seller_name: Optional[str] = None):
        self.seller_name = seller_name
        self.df = None
        self.dfp = None
        self.seller_data = None
        self.kpis = None
        self.analysis = None
        self.system_health = {}
        self.competitive_analysis = {}
        
    def load_and_prepare_data(self):
        """1️⃣ 데이터 로딩 및 전처리"""
        try:
            input_path = CONFIG["INPUT_XLSX"]
            self.df = load_excel_data(input_path)
            self.dfp = prepare_dataframe(self.df, None, None)
            
            # 셀러 결정 (지정되지 않으면 자동 선택)
            if not self.seller_name:
                if COL_SELLER in self.dfp.columns:
                    seller_revenue = self.dfp.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
                    self.seller_name = seller_revenue.index[0]
                else:
                    self.seller_name = "전체"
            
            # 셀러 데이터 추출
            if self.seller_name != "전체":
                self.seller_data = slice_by_seller(self.dfp, self.seller_name)
            else:
                self.seller_data = self.dfp.copy()
                
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            return False
    
    def check_system_health(self):
        """시스템 상태 체크"""
        health = {
            'data_quality': 0,
            'module_health': 0,
            'feature_availability': 0,
            'benchmark_capability': 0
        }
        
        # 데이터 품질 체크
        if self.dfp is not None and len(self.dfp) > 0:
            required_cols = ['__dt__', '__amount__', '__qty__']
            available = sum(1 for col in required_cols if col in self.dfp.columns and self.dfp[col].notna().any())
            health['data_quality'] = (available / len(required_cols)) * 100
        
        # 모듈 기능 체크
        try:
            test_kpis = calculate_comprehensive_kpis(self.seller_data, self.dfp)
            test_analysis = get_comprehensive_analysis(self.seller_data)
            
            kpi_score = sum(1 for v in test_kpis.values() if v is not None and not (isinstance(v, float) and math.isnan(v)))
            analysis_score = sum(1 for v in test_analysis.values() if hasattr(v, 'empty') and not v.empty)
            
            health['module_health'] = min(100, (kpi_score / 15) * 100)  # 15개 주요 KPI 기준
            health['feature_availability'] = (analysis_score / 5) * 100  # 5개 분석 기준
            
        except Exception:
            health['module_health'] = 0
            health['feature_availability'] = 0
        
        # 벤치마킹 능력 체크
        if '__category_mapped__' in self.dfp.columns:
            health['benchmark_capability'] = 100
        elif COL_CATEGORY in self.dfp.columns:
            health['benchmark_capability'] = 50
        else:
            health['benchmark_capability'] = 0
        
        self.system_health = health
        return health
    
    def analyze_seller_profile(self):
        """2️⃣ 셀러 프로필 분석"""
        profile = {}
        
        # 기본 정보
        profile['total_orders'] = len(self.seller_data)
        profile['total_revenue'] = self.seller_data['__amount__'].sum()
        profile['date_range'] = (
            self.seller_data['__dt__'].min().strftime('%Y-%m-%d'),
            self.seller_data['__dt__'].max().strftime('%Y-%m-%d')
        )
        
        # 고객 정보
        if '__customer_id__' in self.seller_data.columns:
            profile['unique_customers'] = self.seller_data['__customer_id__'].nunique()
        else:
            profile['unique_customers'] = None
        
        # 주력 카테고리 분석
        if '__category_mapped__' in self.seller_data.columns:
            category_revenue = self.seller_data.groupby('__category_mapped__')['__amount__'].sum()
            if not category_revenue.empty:
                profile['main_category'] = category_revenue.idxmax()
                profile['main_category_share'] = (category_revenue.max() / profile['total_revenue']) * 100 if profile['total_revenue'] else None
            else:
                profile['main_category'] = None
        else:
            profile['main_category'] = None
        
        # 채널 믹스
        if COL_CHANNEL in self.seller_data.columns:
            channel_revenue = self.seller_data.groupby(COL_CHANNEL)['__amount__'].sum()
            profile['channel_count'] = len(channel_revenue)
            profile['main_channel'] = channel_revenue.idxmax() if not channel_revenue.empty else None
        else:
            profile['channel_count'] = 0
            profile['main_channel'] = None
        
        return profile
    
    def calculate_performance_metrics(self):
        """3️⃣ 핵심 성과 지표 계산"""
        self.kpis = calculate_comprehensive_kpis(self.seller_data, self.dfp)
        self.analysis = get_comprehensive_analysis_with_benchmarks(self.seller_data, self.dfp)
        return self.kpis
    
    def analyze_competition(self):
        """4️⃣ 경쟁 분석"""
        competition = {
            'category_position': None,
            'market_share': None,
            'competitive_strengths': [],
            'improvement_areas': [],
            'category_stats': {}
        }
        
        # 카테고리 내 포지션 분석
        main_category = None
        if '__category_mapped__' in self.dfp.columns and '__category_mapped__' in self.seller_data.columns:
            seller_categories = self.seller_data['__category_mapped__'].value_counts()
            if not seller_categories.empty:
                main_category = seller_categories.index[0]
                
                # 카테고리 내 경쟁 분석
                category_data = self.dfp[self.dfp['__category_mapped__'] == main_category]
                
                if COL_SELLER in category_data.columns and len(category_data) > 0:
                    seller_performance = category_data.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
                    
                    if self.seller_name in seller_performance.index:
                        rank = seller_performance.index.get_loc(self.seller_name) + 1
                        total_sellers = len(seller_performance)
                        total_sum = seller_performance.sum()
                        market_share = (seller_performance[self.seller_name] / total_sum) * 100 if total_sum else 0
                        
                        competition['category_position'] = {
                            'rank': rank,
                            'total_sellers': total_sellers,
                            'percentile': ((total_sellers - rank) / total_sellers) * 100
                        }
                        competition['market_share'] = market_share
                        
                        # 카테고리 통계
                        competition['category_stats'] = {
                            'total_revenue': category_data['__amount__'].sum(),
                            'total_orders': len(category_data),
                            'avg_aov': category_data['__amount__'].mean()
                        }
        
        # 상대적 성과 분석 (강점/약점)
        relative_metrics = {k: v for k, v in (self.kpis or {}).items() if '_vs_category' in k}
        
        strengths = []
        weaknesses = []
        
        for metric, value in relative_metrics.items():
            if value is None or (isinstance(value, float) and math.isnan(value)):
                continue
            metric_name = metric.replace('_vs_category', '').replace('_', ' ')
            
            # 낮을수록 좋은 지표들 (취소율 등)
            if any(bad_word in metric for bad_word in ['cancel', 'delay', 'return']):
                if value <= 0.8:  # 20% 이상 좋음
                    strengths.append(f"{metric_name} (카테고리 대비 {(1-value)*100:.0f}% 우수)")
                elif value >= 1.2:  # 20% 이상 나쁨
                    weaknesses.append(f"{metric_name} (카테고리 대비 {(value-1)*100:.0f}% 높음)")
            else:
                # 높을수록 좋은 지표들
                if value >= 1.2:  # 20% 이상 좋음
                    strengths.append(f"{metric_name} (카테고리 대비 +{(value-1)*100:.0f}%)")
                elif value <= 0.8:  # 20% 이상 나쁨
                    weaknesses.append(f"{metric_name} (카테고리 대비 {(1-value)*100:.0f}% 낮음)")
        
        competition['competitive_strengths'] = strengths[:5]  # 상위 5개
        competition['improvement_areas'] = weaknesses[:5]    # 상위 5개
        
        self.competitive_analysis = competition
        return competition
    
    def generate_action_items(self):
        """5️⃣ 액션 아이템 생성"""
        actions = []
        
        # 개선 영역 기반 액션 아이템
        if self.competitive_analysis.get('improvement_areas'):
            for area in self.competitive_analysis['improvement_areas'][:3]:
                if 'aov' in area.lower() or '주문금액' in area:
                    actions.append({
                        'priority': 'HIGH',
                        'area': 'AOV 개선',
                        'target': '현재 대비 +15%',
                        'methods': ['상향판매 전략', '번들상품 구성', '무료배송 임계값 조정']
                    })
                elif 'repeat' in area.lower() or '재구매' in area:
                    actions.append({
                        'priority': 'HIGH',
                        'area': '재구매율 개선',
                        'target': '현재 대비 +20%',
                        'methods': ['리타겟팅 강화', '멤버십 프로그램', '구매후기 인센티브']
                    })
                elif 'cancel' in area.lower() or '취소' in area:
                    actions.append({
                        'priority': 'MEDIUM',
                        'area': '취소율 감소',
                        'target': '현재 대비 -30%',
                        'methods': ['상품정보 개선', '고객문의 응답 단축', '결제 프로세스 최적화']
                    })
        
        # 강점 활용 기회
        if self.competitive_analysis.get('competitive_strengths'):
            for strength in self.competitive_analysis['competitive_strengths'][:2]:
                if 'aov' in strength.lower():
                    actions.append({
                        'priority': 'OPPORTUNITY',
                        'area': 'AOV 강점 확대',
                        'target': '프리미엄 라인 론칭',
                        'methods': ['고가 상품 라인 확장', '럭셔리 브랜딩', 'VIP 고객 프로그램']
                    })
        
        return actions[:4]  # 최대 4개 액션 아이템
    
    # ──────────────────────────────────────────────────────────────────────────
    # 콘솔 대시보드 출력 (소스 오브 트루스: 엑셀도 이 로직과 동일 데이터 사용)
    # ──────────────────────────────────────────────────────────────────────────
    def print_dashboard(self):
        """대시보드 출력 (엑셀 구성은 이 섹션 순서/값을 그대로 반영)"""
        
        # 헤더
        print("=" * 100)
        print(f"🎯 {self.seller_name} 성과 대시보드 | 📅 {self.seller_data['__dt__'].min().strftime('%m/%d')}~{self.seller_data['__dt__'].max().strftime('%m/%d')} | 📊 신뢰도: {self._calculate_reliability_score():.0f}%")
        print("=" * 100)
        
        # 1️⃣ 시스템 상태
        self._print_system_status()
        
        # 2️⃣ 셀러 프로필
        profile = self.analyze_seller_profile()
        self._print_seller_profile(profile)
        
        # 3️⃣ 핵심 성과 지표
        self._print_performance_metrics()
        
        # 4️⃣ 경쟁 분석
        self._print_competitive_analysis()
        
        # 5️⃣ 액션 아이템
        actions = self.generate_action_items()
        self._print_action_items(actions)
        
        print("=" * 100)

    # ──────────────────────────────────────────────────────────────────────────
    # 단일 시트 "Dashboard"에 콘솔과 '같은 구성'으로 셀 배치/디자인
    # ──────────────────────────────────────────────────────────────────────────
    def export_to_excel(self, out_path: Optional[str] = None):
        """
        콘솔 대시보드와 '동일한 섹션 구성과 값'을 단일 시트에 표 형태로 디자인해 저장합니다.
        (xlsxwriter 권장: pip install xlsxwriter)
        """
        # 파일 경로
        if out_path is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base = sanitize_filename(self.seller_name or "전체")
            out_dir = Path(CONFIG.get("OUTPUT_DIR", "."))
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = str(out_dir / f"seller_dashboard_{base}_{ts}.xlsx")

        # 콘솔과 동일 소스 값 준비
        profile = self.analyze_seller_profile()
        kpis = self.kpis or {}
        health = self.system_health or {}
        comp = self.competitive_analysis or {}
        actions = self.generate_action_items() or []
        analysis = self.analysis or {}

        # 도우미: NaN 안전 숫자 반환
        def _num(x):
            if x is None:
                return None
            if isinstance(x, (int,)):
                return x
            try:
                if isinstance(x, float) and math.isnan(x):
                    return None
            except Exception:
                pass
            return x

        # 성과지표 파생(콘솔과 동일)
        aov            = _num(kpis.get('avg_order_value'))
        aov_vs_cat     = _num(kpis.get('avg_order_value_vs_category'))
        revenue_total  = _num(kpis.get('total_revenue'))
        repeat_rate    = _num(kpis.get('repeat_rate'))
        repeat_vs_cat  = _num(kpis.get('repeat_rate_vs_category'))
        ltv            = _num(kpis.get('customer_ltv'))
        ltv_vs_cat     = _num(kpis.get('customer_ltv_vs_category'))
        cancel_rate    = _num(kpis.get('cancel_rate'))
        cancel_vs_cat  = _num(kpis.get('cancel_rate_vs_category'))
        ship_time      = _num(kpis.get('avg_ship_leadtime'))
        ship_vs_cat    = _num(kpis.get('avg_ship_leadtime_vs_category'))

        # 종합점수/등급 (콘솔과 동일)
        vs_list_pos = [v for v in [aov_vs_cat, repeat_vs_cat, ltv_vs_cat] if isinstance(v, (int,float))]
        vs_list_inv = [v for v in [cancel_vs_cat, ship_vs_cat] if isinstance(v, (int,float))]
        scores: List[float] = []
        scores.extend(vs_list_pos)
        scores.extend([2 - v for v in vs_list_inv])  # 역방향 보정
        overall_score = sum(scores)/len(scores) if scores else 1.0
        if   overall_score >= 1.3: overall_grade = "A+"
        elif overall_score >= 1.2: overall_grade = "A"
        elif overall_score >= 1.1: overall_grade = "A-"
        elif overall_score >= 1.0: overall_grade = "B+"
        elif overall_score >= 0.9: overall_grade = "B"
        else:                      overall_grade = "C"

        with pd.ExcelWriter(out_path, engine="xlsxwriter") as writer:
            wb = writer.book
            sname = _safe_sheet_name("Dashboard")
            ws = wb.add_worksheet(sname)
            writer.sheets[sname] = ws

            # 공통 스타일
            fmt_title   = wb.add_format({"bold": True, "font_size": 16})
            fmt_section = wb.add_format({"bold": True, "bg_color": "#E8F4FF", "border": 1, "align": "left", "valign": "vcenter"})
            fmt_label   = wb.add_format({"bold": True, "bg_color": "#F7F7F7", "border": 1})
            fmt_cell    = wb.add_format({"border": 1})
            fmt_won     = wb.add_format({"border": 1, "num_format": u'₩#,##0'})
            fmt_int     = wb.add_format({"border": 1, "num_format": "#,##0"})
            fmt_pct     = wb.add_format({"border": 1, "num_format": "0.0%"})
            fmt_float1  = wb.add_format({"border": 1, "num_format": "0.0"})
            fmt_note    = wb.add_format({"italic": True, "font_color": "#666666"})
            fmt_badge   = wb.add_format({"border": 1, "align": "center", "valign": "vcenter"})
            fmt_emoji   = wb.add_format({"border": 1, "align": "center"})

            # 상태 칩 색상
            def _status_fmt(rate: Optional[float]) -> dict:
                if rate is None:
                    return {"bg_color": "#DDDDDD"}  # 회색
                if rate >= 90:   return {"bg_color": "#C6EFCE"}  # 녹색
                if rate >= 70:   return {"bg_color": "#FFEB9C"}  # 노랑
                return {"bg_color": "#F2DCDB"}                   # 빨강

            # 셀 폭
            ws.set_column("A:A", 18)
            ws.set_column("B:B", 20)
            ws.set_column("C:C", 16)
            ws.set_column("D:D", 18)
            ws.set_column("E:E", 16)
            ws.set_column("F:F", 18)
            ws.set_column("G:G", 18)
            ws.set_column("H:H", 22)
            ws.set_column("I:I", 18)
            ws.set_column("J:J", 18)
            ws.set_column("K:K", 18)
            ws.set_column("L:L", 18)
            ws.set_column("M:M", 18)

            r = 0  # 현재 행 포인터

            # ── 헤더
            ws.merge_range(r, 0, r, 12, f"통합 셀러 성과 대시보드 - {self.seller_name}", fmt_title); r += 1
            period = f"{profile.get('date_range', ('',''))[0]} ~ {profile.get('date_range', ('',''))[1]}"
            ws.write(r, 0, "분석기간", fmt_label); ws.write(r, 1, period, fmt_cell)
            ws.write(r, 3, "신뢰도(%)", fmt_label); ws.write(r, 4, round(self._calculate_reliability_score(),1), fmt_float1); r += 2

            # ── 1) 시스템 상태
            ws.merge_range(r, 0, r, 12, "① 시스템 상태 (System Health)", fmt_section); r += 1
            ws.write_row(r, 0, ["지표", "값(%)", "상태"], fmt_label); r += 1

            def _write_health_row(name: str, value: Optional[float]):
                nonlocal r
                ws.write(r, 0, name, fmt_cell)
                if value is None:
                    ws.write(r, 1, "", fmt_cell)
                    ws.write(r, 2, "N/A", fmt_badge)
                else:
                    ws.write_number(r, 1, value/100.0, fmt_pct)
                    st = _status_fmt(value)
                    fmt = wb.add_format({**st, "border":1, "align":"center"})
                    ws.write(r, 2, ("🟢 정상" if value>=90 else "🟡 보통" if value>=70 else "🔴 주의"), fmt)
                r += 1

            _write_health_row("데이터 품질",         health.get('data_quality'))
            _write_health_row("모듈 동작",           health.get('module_health'))
            _write_health_row("기능 가용성",         health.get('feature_availability'))
            _write_health_row("벤치마킹 가능성",     health.get('benchmark_capability'))
            r += 1

            # ── 2) 셀러 프로필
            ws.merge_range(r, 0, r, 12, "② 셀러 프로필 (Seller Profile)", fmt_section); r += 1
            # 좌측 표
            ws.write(r, 0, "총 매출", fmt_label); ws.write_number(r, 1, _num(profile.get("total_revenue")) or 0, fmt_won)
            ws.write(r, 2, "주문수", fmt_label);   ws.write_number(r, 3, _num(profile.get("total_orders")) or 0, fmt_int)
            ws.write(r, 4, "고객수", fmt_label);   ws.write(r, 5, _num(profile.get("unique_customers")) or 0, fmt_int)
            ws.write(r, 6, "주력 카테고리", fmt_label); ws.write(r, 7, profile.get("main_category") or "정보없음", fmt_cell)
            ws.write(r, 8, "메인 채널", fmt_label); ws.write(r, 9, profile.get("main_channel") or "정보없음", fmt_cell)
            # 카테고리 포지션/점유율
            pos = comp.get('category_position')
            market_share = comp.get('market_share')
            r += 1
            ws.write(r, 0, "카테고리 순위", fmt_label)
            if pos:
                ws.write(r, 1, f"{pos.get('rank')}/{pos.get('total_sellers')}위", fmt_cell)
                ws.write(r, 2, "상위%", fmt_label); ws.write_number(r, 3, (100 - pos.get('percentile',0))/100.0, fmt_pct)
            else:
                ws.write(r, 1, "분석불가", fmt_cell)
            ws.write(r, 4, "점유율", fmt_label)
            if isinstance(market_share, (int,float)):
                ws.write_number(r, 5, market_share/100.0, fmt_pct)
            else:
                ws.write(r, 5, "", fmt_cell)
            r += 2

            # ── 3) 핵심 성과 지표 (콘솔과 동일한 묶음)
            ws.merge_range(r, 0, r, 12, "③ 핵심 성과 지표 (KPIs)", fmt_section); r += 1
            ws.write_row(r, 0, ["구분", "값", "vs 카테고리", "퍼포먼스", "변화"], fmt_label); r += 1

            def perf_emoji(v: Optional[float], inverse=False) -> str:
                if v is None:
                    return "⚪"
                if inverse:
                    if v <= 0.8: return "🟢"
                    if v <= 0.9: return "🟡"
                    if v <= 1.1: return "⚪"
                    return "🔴"
                else:
                    if v >= 1.2: return "🟢"
                    if v >= 1.1: return "🟡"
                    if v >= 0.9: return "⚪"
                    return "🔴"

            def vs_change(v: Optional[float], inverse=False) -> Optional[float]:
                if v is None: return None
                return (1 - v) if inverse else (v - 1)

            # AOV
            ws.write(r, 0, "AOV", fmt_cell)
            ws.write_number(r, 1, aov or 0, fmt_won)
            if aov_vs_cat is None:
                ws.write(r, 2, "", fmt_cell); ws.write(r, 3, "⚪", fmt_emoji); ws.write(r, 4, "", fmt_cell)
            else:
                ws.write_number(r, 2, aov_vs_cat, fmt_float1)
                ws.write(r, 3, perf_emoji(aov_vs_cat), fmt_emoji)
                ws.write_number(r, 4, vs_change(aov_vs_cat), fmt_float1)
            r += 1

            # 매출
            ws.write(r, 0, "매출", fmt_cell)
            ws.write_number(r, 1, revenue_total or 0, fmt_won)
            ws.write(r, 2, "", fmt_cell); ws.write(r, 3, "", fmt_cell); ws.write(r, 4, "", fmt_cell)
            r += 1

            # 재구매율
            ws.write(r, 0, "재구매율", fmt_cell)
            if repeat_rate is None: ws.write(r, 1, "", fmt_cell)
            else: ws.write_number(r, 1, repeat_rate, fmt_pct)
            if repeat_vs_cat is None:
                ws.write(r, 2, "", fmt_cell); ws.write(r, 3, "⚪", fmt_emoji); ws.write(r, 4, "", fmt_cell)
            else:
                ws.write_number(r, 2, repeat_vs_cat, fmt_float1)
                ws.write(r, 3, perf_emoji(repeat_vs_cat), fmt_emoji)
                ws.write_number(r, 4, vs_change(repeat_vs_cat), fmt_float1)
            r += 1

            # LTV
            ws.write(r, 0, "LTV", fmt_cell)
            ws.write_number(r, 1, ltv or 0, fmt_won)
            if ltv_vs_cat is None:
                ws.write(r, 2, "", fmt_cell); ws.write(r, 3, "⚪", fmt_emoji); ws.write(r, 4, "", fmt_cell)
            else:
                ws.write_number(r, 2, ltv_vs_cat, fmt_float1)
                ws.write(r, 3, perf_emoji(ltv_vs_cat), fmt_emoji)
                ws.write_number(r, 4, vs_change(ltv_vs_cat), fmt_float1)
            r += 1

            # 취소율 (inverse)
            ws.write(r, 0, "취소율", fmt_cell)
            if cancel_rate is None: ws.write(r, 1, "", fmt_cell)
            else: ws.write_number(r, 1, cancel_rate, fmt_pct)
            if cancel_vs_cat is None:
                ws.write(r, 2, "", fmt_cell); ws.write(r, 3, "⚪", fmt_emoji); ws.write(r, 4, "", fmt_cell)
            else:
                ws.write_number(r, 2, cancel_vs_cat, fmt_float1)
                ws.write(r, 3, perf_emoji(cancel_vs_cat, inverse=True), fmt_emoji)
                ws.write_number(r, 4, vs_change(cancel_vs_cat, inverse=True), fmt_float1)
            r += 1

            # 배송일 (inverse)
            ws.write(r, 0, "평균 배송일", fmt_cell)
            if ship_time is None: ws.write(r, 1, "", fmt_cell)
            else: ws.write_number(r, 1, ship_time, fmt_float1)
            if ship_vs_cat is None:
                ws.write(r, 2, "", fmt_cell); ws.write(r, 3, "⚪", fmt_emoji); ws.write(r, 4, "", fmt_cell)
            else:
                ws.write_number(r, 2, ship_vs_cat, fmt_float1)
                ws.write(r, 3, perf_emoji(ship_vs_cat, inverse=True), fmt_emoji)
                ws.write_number(r, 4, vs_change(ship_vs_cat, inverse=True), fmt_float1)
            r += 1

            # 종합
            ws.write(r, 0, "종합 등급", fmt_label); ws.write(r, 1, overall_grade, fmt_cell)
            ws.write(r, 2, "종합 점수", fmt_label); ws.write_number(r, 3, overall_score, fmt_float1)
            r += 2

            # ── 4) 경쟁 분석
            ws.merge_range(r, 0, r, 12, "④ 경쟁 분석 (Competitive Analysis)", fmt_section); r += 1
            ws.write_row(r, 0, ["강점 (상위 20%)", "개선 영역 (하위 30%)"], fmt_label); r += 1
            strengths = comp.get("competitive_strengths", []) or []
            weaknesses = comp.get("improvement_areas", []) or []
            max_len = max(len(strengths), len(weaknesses), 1)
            for i in range(max_len):
                ws.write(r, 0, strengths[i] if i < len(strengths) else "", fmt_cell)
                ws.write(r, 1, weaknesses[i] if i < len(weaknesses) else "", fmt_cell)
                r += 1
            r += 1

            # ── 5) 액션 아이템
            ws.merge_range(r, 0, r, 12, "⑤ 액션 아이템 (Action Items)", fmt_section); r += 1
            ws.write_row(r, 0, ["우선순위", "영역", "목표", "실행방안"], fmt_label); r += 1
            for a in actions:
                methods = ", ".join(a.get("methods", [])) if isinstance(a.get("methods"), list) else (a.get("methods") or "")
                ws.write(r, 0, a.get("priority",""), fmt_cell)
                ws.write(r, 1, a.get("area",""), fmt_cell)
                ws.write(r, 2, a.get("target",""), fmt_cell)
                ws.write(r, 3, methods, fmt_cell)
                r += 1
            if not actions:
                ws.write(r, 0, "제안된 액션 없음", fmt_note); r += 1
            r += 1

            # ── 6) 세부 분석 (있을 경우 일부 표 형태로 아래에 덧붙임)
            if isinstance(analysis, dict):
                for key, df in analysis.items():
                    if isinstance(df, pd.DataFrame) and not df.empty:
                        ws.merge_range(r, 0, r, 12, f"⑥ 세부 분석 - {key}", fmt_section); r += 1
                        # 헤더
                        for c, col in enumerate(df.columns[:10]):  # 넓이 제한: 상위 10열
                            ws.write(r, c, str(col), fmt_label)
                        # 데이터 (상위 200행 제한)
                        max_rows = min(len(df), 200)
                        for i in range(max_rows):
                            for c, col in enumerate(df.columns[:10]):
                                val = df.iloc[i, c]
                                # 숫자/문자 서식 간단 적용
                                if isinstance(val, (int,)) or (isinstance(val, float) and not math.isnan(val)):
                                    ws.write_number(r+1+i, c, float(val), fmt_cell)
                                else:
                                    ws.write(r+1+i, c, "" if (isinstance(val, float) and math.isnan(val)) else val, fmt_cell)
                        r += (1 + max_rows + 1)

            # 끝
            ws.freeze_panes(2, 0)

        print(f"✅ 엑셀 보고서 저장 완료: {out_path}")
        return out_path
    
    # ──────────────────────────────────────────────────────────────────────────
    # 콘솔 출력 도우미
    # ──────────────────────────────────────────────────────────────────────────
    def _calculate_reliability_score(self):
        """신뢰도 점수 계산"""
        if not self.system_health:
            return 0
        return sum(self.system_health.values()) / len(self.system_health)
    
    def _print_system_status(self):
        """시스템 상태 출력"""
        health = self.system_health
        
        data_status = "🟢 정상" if health['data_quality'] >= 90 else "🟡 양호" if health['data_quality'] >= 70 else "🔴 불량"
        module_status = "🟢 정상" if health['module_health'] >= 90 else "🟡 부분" if health['module_health'] >= 70 else "🔴 제한"
        quality_status = "🟢 양호" if health['feature_availability'] >= 80 else "🟡 보통" if health['feature_availability'] >= 60 else "🔴 부족"
        bench_status = "🟢 가능" if health['benchmark_capability'] >= 80 else "🟡 제한" if health['benchmark_capability'] >= 50 else "🔴 불가"
        
        print("┌─ 1️⃣ 시스템 상태 " + "─" * 82 + "┐")
        print(f"│ 🔧 데이터: {data_status}    🔧 모듈: {module_status}    🔧 품질: {quality_status}    🔧 벤치마킹: {bench_status}       │")
        print("└" + "─" * 98 + "┘")
        print()
    
    def _print_seller_profile(self, profile):
        """셀러 프로필 출력"""
        revenue_str = format_currency(profile['total_revenue'])
        orders_str = f"{profile['total_orders']:,}건"
        customers_str = f"{profile['unique_customers']:,}명" if profile['unique_customers'] else "N/A"
        category_str = profile['main_category'] if profile['main_category'] else "정보없음"
        
        # 카테고리 포지션 정보
        position_info = ""
        if self.competitive_analysis.get('category_position'):
            pos = self.competitive_analysis['category_position']
            market_share = self.competitive_analysis.get('market_share', 0)
            position_info = f"🏆 카테고리 순위: {pos['rank']}/{pos['total_sellers']}위 (상위 {100-pos['percentile']:.0f}%)    📊 점유율: {market_share:.1f}%"
        else:
            position_info = "🏆 카테고리 순위: 분석불가    📊 점유율: N/A"
        
        print("┌─ 2️⃣ 셀러 프로필 " + "─" * 82 + "┐")
        print(f"│ 📊 총 매출: {revenue_str}    📦 주문수: {orders_str}    👥 고객수: {customers_str}    📂 주력: {category_str[:10]}       │")
        print(f"│ {position_info}    🔥 경쟁강도: {'높음' if position_info.find('상위') != -1 else '보통'}      │")
        print("└" + "─" * 98 + "┘")
        print()
    
    def _print_performance_metrics(self):
        """성과 지표 출력"""
        if not self.kpis:
            return
        
        # 매출 성과
        aov = self.kpis.get('avg_order_value', 0)
        aov_vs_cat = self.kpis.get('avg_order_value_vs_category', float('nan'))
        aov_performance = self._get_performance_emoji(aov_vs_cat)
        aov_change = f"{(aov_vs_cat-1)*100:+.0f}%" if not math.isnan(aov_vs_cat) else "N/A"
        
        revenue = self.kpis.get('total_revenue', 0)
        
        # 고객 성과
        repeat_rate = self.kpis.get('repeat_rate', float('nan'))
        repeat_vs_cat = self.kpis.get('repeat_rate_vs_category', float('nan'))
        repeat_performance = self._get_performance_emoji(repeat_vs_cat)
        repeat_change = f"{(repeat_vs_cat-1)*100:+.0f}%" if not math.isnan(repeat_vs_cat) else "N/A"
        
        ltv = self.kpis.get('customer_ltv', float('nan'))
        ltv_vs_cat = self.kpis.get('customer_ltv_vs_category', float('nan'))
        ltv_performance = self._get_performance_emoji(ltv_vs_cat)
        ltv_change = f"{(ltv_vs_cat-1)*100:+.0f}%" if not math.isnan(ltv_vs_cat) else "N/A"
        
        # 운영 성과
        cancel_rate = self.kpis.get('cancel_rate', float('nan'))
        cancel_vs_cat = self.kpis.get('cancel_rate_vs_category', float('nan'))
        cancel_performance = self._get_performance_emoji(cancel_vs_cat, inverse=True)  # 낮을수록 좋음
        cancel_change = f"{(1-cancel_vs_cat)*100:+.0f}%" if not math.isnan(cancel_vs_cat) else "N/A"
        
        ship_time = self.kpis.get('avg_ship_leadtime', float('nan'))
        ship_vs_cat = self.kpis.get('avg_ship_leadtime_vs_category', float('nan'))
        ship_performance = self._get_performance_emoji(ship_vs_cat, inverse=True)  # 낮을수록 좋음
        ship_change = f"{(1-ship_vs_cat)*100:+.0f}%" if not math.isnan(ship_vs_cat) else "N/A"
        
        # 종합 점수 계산
        scores = []
        for vs_cat in [aov_vs_cat, repeat_vs_cat, ltv_vs_cat]:
            if not math.isnan(vs_cat):
                scores.append(vs_cat)
        for vs_cat in [cancel_vs_cat, ship_vs_cat]:  # 역방향 지표
            if not math.isnan(vs_cat):
                scores.append(2 - vs_cat)  # 역전
        
        overall_score = sum(scores) / len(scores) if scores else 1.0
        overall_grade = "A+" if overall_score >= 1.3 else "A" if overall_score >= 1.2 else "A-" if overall_score >= 1.1 else "B+" if overall_score >= 1.0 else "B" if overall_score >= 0.9 else "C"
        
        print("┌─ 3️⃣ 핵심 성과 지표 " + "─" * 79 + "┐")
        print(f"│ 💰 매출성과     📊 vs 카테고리평균    │ 👥 고객성과     📊 vs 카테고리평균            │")
        print(f"│   AOV: {format_currency(aov):<10} {aov_performance} {aov_change:<8} │   재구매율: {pct(repeat_rate):<8} {repeat_performance} {repeat_change:<8}        │")
        print(f"│   매출: {format_currency(revenue):<10}               │   LTV: {format_currency(ltv):<10} {ltv_performance} {ltv_change:<8}        │")
        print(f"│                                    │                                              │")
        print(f"│ ⚙️ 운영성과     📊 vs 카테고리평균    │ 🎯 종합점수     📊 vs 카테고리평균            │")
        print(f"│   취소율: {pct(cancel_rate):<8} {cancel_performance} {cancel_change:<8} │   종합등급: {overall_grade:<6} 🟢 상위 {(overall_score-1)*100:+.0f}%            │")
        print(f"│   배송일: {ship_time:.1f}일      {ship_performance} {ship_change:<8} │   개선영역: {len(self.competitive_analysis.get('improvement_areas', []))}개   💡 성장여지 있음            │")
        print("└" + "─" * 98 + "┘")
        print()
    
    def _print_competitive_analysis(self):
        """경쟁 분석 출력"""
        strengths = self.competitive_analysis.get('competitive_strengths', [])
        weaknesses = self.competitive_analysis.get('improvement_areas', [])
        
        print("┌─ 4️⃣ 경쟁 분석 " + "─" * 84 + "┐")
        print(f"│ 🏆 강점 영역 (카테고리 상위 20%)     │ ⚠️ 개선 영역 (카테고리 하위 30%)              │")
        
        # 최대 3개씩 표시
        max_items = max(len(strengths), len(weaknesses), 3)
        
        for i in range(max_items):
            strength_text = f"  ✅ {strengths[i][:30]}..." if i < len(strengths) else " " * 35
            weakness_text = f"  🔧 {weaknesses[i][:30]}..." if i < len(weaknesses) else " " * 35
            
            print(f"│ {strength_text:<35} │ {weakness_text:<35}            │")
        
        print("└" + "─" * 98 + "┘")
        print()
    
    def _print_action_items(self, actions):
        """액션 아이템 출력"""
        print("┌─ 5️⃣ 액션 아이템 " + "─" * 82 + "┐")
        
        priority_actions = [a for a in actions if a['priority'] == 'HIGH']
        opportunity_actions = [a for a in actions if a['priority'] == 'OPPORTUNITY']
        
        # 우선순위 액션들
        for i, action in enumerate(priority_actions[:2], 1):
            methods_str = ", ".join(action['methods'][:3])
            print(f"│ 🔥 우선순위 {i}: {action['area']} (목표: {action['target']})                                      │")
            print(f"│   📋 실행방안: {methods_str[:80]}       │")
            if i < len(priority_actions):
                print(f"│                                                                                        │")
        
        # 기회 액션들
        for action in opportunity_actions[:1]:
            methods_str = ", ".join(action['methods'][:2])
            print(f"│ 💡 장기 기회: {action['area']} - {methods_str}                                        │")
        
        print("└" + "─" * 98 + "┘")
    
    def _get_performance_emoji(self, vs_category_value, inverse=False):
        """성과 대비 이모지 반환"""
        if isinstance(vs_category_value, float) and math.isnan(vs_category_value):
            return "⚪"
        
        if inverse:  # 낮을수록 좋은 지표 (취소율, 배송시간 등)
            if vs_category_value <= 0.8:
                return "🟢"
            elif vs_category_value <= 0.9:
                return "🟡"
            elif vs_category_value <= 1.1:
                return "⚪"
            else:
                return "🔴"
        else:  # 높을수록 좋은 지표 (AOV, 재구매율 등)
            if vs_category_value >= 1.2:
                return "🟢"
            elif vs_category_value >= 1.1:
                return "🟡"
            elif vs_category_value >= 0.9:
                return "⚪"
            else:
                return "🔴"
    
    def run_full_analysis(self):
        """전체 분석 실행"""
        print("🚀 셀러 성과 대시보드 분석 시작...")
        print()
        
        # 데이터 로딩
        if not self.load_and_prepare_data():
            return False
        
        # 시스템 상태 체크
        self.check_system_health()
        
        # 성과 지표 계산
        self.calculate_performance_metrics()
        
        # 경쟁 분석
        self.analyze_competition()
        
        # 대시보드 출력
        self.print_dashboard()
        
        return True


def test_multiple_sellers():
    """여러 셀러 비교 테스트"""
    
    print("\n" + "🔄 다중 셀러 비교 분석")
    print("=" * 100)
    
    try:
        # 데이터 로드
        df = load_excel_data(CONFIG["INPUT_XLSX"])
        dfp = prepare_dataframe(df, None, None)
        
        # 상위 매출 셀러들 찾기
        if COL_SELLER in dfp.columns:
            seller_revenue = dfp.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
            top_sellers = seller_revenue.head(5).index.tolist()
            
            print(f"📊 상위 5개 셀러 비교:")
            print(f"{'순위':<4} {'셀러명':<20} {'매출액':<15} {'주문수':<10} {'AOV':<12}")
            print("-" * 70)
            
            for i, seller in enumerate(top_sellers, 1):
                seller_data = dfp[dfp[COL_SELLER] == seller]
                revenue = seller_data['__amount__'].sum()
                orders = len(seller_data)
                aov = revenue / orders if orders > 0 else 0
                print(f"{i:<4} {seller[:18]:<20} {format_currency(revenue):<15} {orders:<10,} {format_currency(aov):<12}")
            
            return top_sellers
        else:
            print("❌ 셀러 정보가 없어 비교 분석을 수행할 수 없습니다.")
            return []
            
    except Exception as e:
        print(f"❌ 다중 셀러 비교 실패: {e}")
        return []


def test_data_quality_diagnosis():
    """데이터 품질 진단"""
    
    print("\n" + "🔍 데이터 품질 종합 진단")
    print("=" * 100)
    
    try:
        df = load_excel_data(CONFIG["INPUT_XLSX"])
        dfp = prepare_dataframe(df, None, None)
        
        print(f"📊 데이터 개요:")
        print(f"  원본 데이터: {len(df):,}건")
        print(f"  처리 후: {len(dfp):,}건 ({len(dfp)/len(df)*100:.1f}% 유효)")
        print(f"  기간: {dfp['__dt__'].min().strftime('%Y-%m-%d')} ~ {dfp['__dt__'].max().strftime('%Y-%m-%d')}")
        
        # 필수 필드 완성도
        print(f"\n📋 필드 완성도:")
        essential_fields = {
            '결제일': '__dt__',
            '주문금액': '__amount__',
            '수량': '__qty__',
            '셀러': COL_SELLER,
            '채널': COL_CHANNEL,
            '고객ID': '__customer_id__',
            '지역': '__region__',
            '카테고리': '__category_mapped__'
        }
        
        for field_name, col_name in essential_fields.items():
            if col_name in dfp.columns:
                completeness = (dfp[col_name].notna().sum() / len(dfp)) * 100
                status = "🟢" if completeness >= 90 else "🟡" if completeness >= 70 else "🔴"
                print(f"  {status} {field_name:<10}: {completeness:5.1f}% 완성")
            else:
                print(f"  ❌ {field_name:<10}: 필드 없음")
        
        # 벤치마킹 가능성
        print(f"\n🎯 벤치마킹 분석 가능성:")
        if '__category_mapped__' in dfp.columns:
            categories = dfp['__category_mapped__'].value_counts()
            print(f"  ✅ 카테고리 매핑: {len(categories)}개 카테고리")
            print(f"  📂 주요 카테고리: {categories.head(3).index.tolist()}")
            
            if COL_SELLER in dfp.columns:
                sellers_per_category = dfp.groupby('__category_mapped__')[COL_SELLER].nunique()
                avg_competitors = sellers_per_category.mean()
                print(f"  🏆 평균 경쟁사 수: {avg_competitors:.1f}개/카테고리")
                print(f"  💪 벤치마킹 신뢰도: {'높음' if avg_competitors >= 5 else '보통' if avg_competitors >= 3 else '낮음'}")
            else:
                print("  ⚠️ 셀러 정보 부족으로 경쟁 분석 제한")
        else:
            print("  ❌ 카테고리 정보 없음 - 기본 벤치마킹만 가능")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터 품질 진단 실패: {e}")
        return False


def main():
    """메인 실행 함수"""
    
    print("🎯 통합 셀러 성과 대시보드 & 시스템 테스트")
    print("=" * 100)
    
    # 명령행 인수로 셀러 지정 가능
    target_seller = None
    if len(sys.argv) > 1:
        target_seller = sys.argv[1]
        print(f"🎯 지정된 분석 대상: {target_seller}")
    
    try:
        # 1. 데이터 품질 진단
        quality_ok = test_data_quality_diagnosis()
        
        if not quality_ok:
            print("❌ 데이터 품질 문제로 분석을 중단합니다.")
            return
        
        # 2. 다중 셀러 개요 (대상이 지정되지 않은 경우)
        if not target_seller:
            top_sellers = test_multiple_sellers()
            if top_sellers:
                target_seller = top_sellers[0]  # 1위 셀러를 기본 대상으로
                print(f"\n💡 매출 1위 셀러 '{target_seller}' 대시보드를 생성합니다.")
            else:
                target_seller = "전체"
        
        print("\n" + "=" * 100)
        
        # 3. 메인 대시보드 분석
        dashboard = SellerDashboard(target_seller)
        success = dashboard.run_full_analysis()
        
        if success:
            print(f"\n🎉 {target_seller} 대시보드 분석 완료!")
            
            # 👉 엑셀 저장 (단일 시트, 콘솔 구성 그대로 셀 매핑)
            try:
                out_path = dashboard.export_to_excel()
                print(f"📁 엑셀 리포트(디자인): {out_path}")
            except Exception as e:
                print(f"⚠️ 엑셀 리포트 저장 중 오류: {e}")
            
            # 4. 추가 분석 제안
            print(f"\n💡 추가 분석 옵션:")
            print(f"  • 다른 셀러 분석: python dashboard_test.py [셀러명]")
            print(f"  • 전체 현황 분석: python dashboard_test.py 전체")
            print(f"  • 카테고리 비교: python debug_category_selection.py")
            
            # 신뢰도 점수에 따른 권장사항
            reliability = dashboard._calculate_reliability_score()
            if reliability >= 90:
                print(f"  🟢 시스템 신뢰도 우수 - 모든 기능 활용 가능")
            elif reliability >= 70:
                print(f"  🟡 시스템 신뢰도 양호 - 대부분 기능 사용 가능")
            else:
                print(f"  🔴 시스템 신뢰도 개선 필요 - 데이터 보완 권장")
        else:
            print("❌ 대시보드 분석 실패")
            
    except Exception as e:
        print(f"❌ 프로그램 실행 실패: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

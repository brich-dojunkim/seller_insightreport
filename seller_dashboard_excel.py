#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""셀러 성과 대시보드 엑셀 출력기 - 상세 분석 리포트"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import numpy as np
import math
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from config import CONFIG
from file_manager import load_excel_data
from constants import *
from utils import format_currency, pct, sanitize_filename

# data_processing 모듈
from data_processing import (
    prepare_dataframe, slice_by_seller, 
    calculate_comprehensive_kpis,
    get_channel_analysis, get_product_analysis, get_category_analysis,
    get_region_analysis, get_time_analysis
)

class SellerDashboardExcel:
    """셀러 성과 대시보드 엑셀 생성기"""
    
    def __init__(self, seller_name: str):
        self.seller_name = seller_name
        self.df = None
        self.dfp = None
        self.seller_data = None
        self.overall_data = None
        self.kpis = None
        self.analysis_data = {}
        
    def load_data(self):
        """데이터 로딩 및 전처리"""
        try:
            input_path = CONFIG["INPUT_XLSX"]
            self.df = load_excel_data(input_path)
            self.dfp = prepare_dataframe(self.df, None, None)
            self.overall_data = self.dfp.copy()
            
            if self.seller_name != "전체":
                self.seller_data = slice_by_seller(self.dfp, self.seller_name)
            else:
                self.seller_data = self.dfp.copy()
                
            self.kpis = calculate_comprehensive_kpis(self.seller_data, self.overall_data)
            return True
            
        except Exception as e:
            print(f"❌ 데이터 로딩 실패: {e}")
            return False
    
    def analyze_all_data(self):
        """모든 분석 데이터 생성"""
        
        # 1. 셀러 기본 정보
        self.analysis_data['basic_info'] = self._analyze_basic_info()
        
        # 2. 매출 분석
        self.analysis_data['sales'] = self._analyze_sales()
        
        # 3. 고객 분석
        self.analysis_data['customers'] = self._analyze_customers()
        
        # 4. 운영 분석
        self.analysis_data['operations'] = self._analyze_operations()
        
        # 5. 벤치마킹 분석
        self.analysis_data['benchmarking'] = self._analyze_benchmarking()
        
        # 6. 트렌드 분석
        self.analysis_data['trends'] = self._analyze_trends()
        
        print(f"✅ {self.seller_name} 분석 완료 - {len(self.analysis_data)}개 영역")
    
    def _analyze_basic_info(self) -> Dict:
        """기본 정보 분석"""
        info = {}
        
        # 기본 통계
        info['seller_name'] = self.seller_name
        info['analysis_date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        info['period_start'] = self.seller_data['__dt__'].min().strftime('%Y-%m-%d')
        info['period_end'] = self.seller_data['__dt__'].max().strftime('%Y-%m-%d')
        info['total_days'] = (self.seller_data['__dt__'].max() - self.seller_data['__dt__'].min()).days + 1
        
        # 주력 카테고리
        if '__category_mapped__' in self.seller_data.columns:
            cat_revenue = self.seller_data.groupby('__category_mapped__')['__amount__'].sum()
            if not cat_revenue.empty:
                info['main_category'] = cat_revenue.idxmax()
                info['main_category_share'] = (cat_revenue.max() / self.seller_data['__amount__'].sum()) * 100
                
                # 카테고리 내 순위 계산
                if '__category_mapped__' in self.overall_data.columns and COL_SELLER in self.overall_data.columns:
                    category_data = self.overall_data[self.overall_data['__category_mapped__'] == info['main_category']]
                    seller_perf = category_data.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
                    
                    if self.seller_name in seller_perf.index:
                        rank = seller_perf.index.get_loc(self.seller_name) + 1
                        total_sellers = len(seller_perf)
                        market_share = (seller_perf[self.seller_name] / seller_perf.sum()) * 100
                        
                        info['category_rank'] = rank
                        info['category_total_sellers'] = total_sellers
                        info['category_percentile'] = ((total_sellers - rank) / total_sellers) * 100
                        info['market_share'] = market_share
        
        return info
    
    def _analyze_sales(self) -> Dict:
        """매출 분석"""
        sales = {}
        
        # A. 기본 매출 지표
        basic_metrics = {
            '총_매출액': self.seller_data['__amount__'].sum(),
            '총_주문수': len(self.seller_data),
            '평균주문금액': self.seller_data['__amount__'].mean(),
            '총_판매수량': self.seller_data['__qty__'].sum(),
            '일평균_매출액': self.seller_data['__amount__'].sum() / self.analysis_data['basic_info']['total_days']
        }
        
        if COL_PRODUCT_PRICE in self.seller_data.columns:
            basic_metrics['평균상품가격'] = pd.to_numeric(self.seller_data[COL_PRODUCT_PRICE], errors='coerce').mean()
        
        sales['basic_metrics'] = basic_metrics
        
        # B. 채널별 매출 분석
        if COL_CHANNEL in self.seller_data.columns:
            channel_analysis = self.seller_data.groupby(COL_CHANNEL).agg({
                '__amount__': ['sum', 'count', 'mean'],
                '__qty__': 'sum'
            }).round(2)
            
            channel_analysis.columns = ['매출액', '주문수', 'AOV', '판매수량']
            channel_analysis['매출비중'] = (channel_analysis['매출액'] / channel_analysis['매출액'].sum()) * 100
            channel_analysis = channel_analysis.sort_values('매출액', ascending=False)
            
            sales['channel_analysis'] = channel_analysis
        
        # C. 상품별 매출 TOP 20
        if COL_ITEM_NAME in self.seller_data.columns:
            product_analysis = self.seller_data.groupby(COL_ITEM_NAME).agg({
                '__amount__': ['sum', 'count', 'mean'],
                '__qty__': 'sum'
            }).round(2)
            
            product_analysis.columns = ['매출액', '주문수', 'AOV', '판매수량']
            product_analysis['매출기여도'] = (product_analysis['매출액'] / product_analysis['매출액'].sum()) * 100
            product_analysis = product_analysis.sort_values('매출액', ascending=False).head(20)
            
            sales['product_analysis'] = product_analysis
        
        # D. 시간대별 매출 패턴
        hourly_pattern = self.seller_data.groupby(self.seller_data['__dt__'].dt.hour).agg({
            '__amount__': ['sum', 'count', 'mean']
        }).round(2)
        hourly_pattern.columns = ['매출액', '주문수', 'AOV']
        hourly_pattern['시간대'] = hourly_pattern.index.map(lambda x: f"{x:02d}-{x+1:02d}시")
        
        sales['hourly_pattern'] = hourly_pattern
        
        # E. 요일별 매출 패턴
        daily_pattern = self.seller_data.groupby(self.seller_data['__dt__'].dt.day_name()).agg({
            '__amount__': ['sum', 'count', 'mean']
        }).round(2)
        daily_pattern.columns = ['매출액', '주문수', 'AOV']
        
        # 요일 순서 정렬
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_pattern = daily_pattern.reindex([day for day in day_order if day in daily_pattern.index])
        
        sales['daily_pattern'] = daily_pattern
        
        return sales
    
    def _analyze_customers(self) -> Dict:
        """고객 분석"""
        customers = {}
        
        if '__customer_id__' not in self.seller_data.columns or self.seller_data['__customer_id__'].isna().all():
            customers['error'] = "고객 식별 정보가 없어 고객 분석을 수행할 수 없습니다."
            return customers
        
        # 고객별 구매 데이터 집계
        customer_data = self.seller_data[self.seller_data['__customer_id__'].notna()].copy()
        customer_summary = customer_data.groupby('__customer_id__').agg({
            '__amount__': ['sum', 'count', 'mean'],
            '__dt__': ['min', 'max']
        }).round(2)
        
        customer_summary.columns = ['총구매금액', '구매횟수', '평균구매금액', '첫구매일', '최근구매일']
        
        # A. 고객 기본 지표
        total_customers = len(customer_summary)
        new_customers = (customer_summary['구매횟수'] == 1).sum()
        repeat_customers = (customer_summary['구매횟수'] >= 2).sum()
        
        basic_metrics = {
            '총_고객수': total_customers,
            '신규_고객수': new_customers,
            '기존_고객수': repeat_customers,
            '재구매율': (repeat_customers / total_customers * 100) if total_customers > 0 else 0,
            '평균_구매횟수': customer_summary['구매횟수'].mean(),
            '평균_고객생애가치': customer_summary['총구매금액'].mean()
        }
        
        customers['basic_metrics'] = basic_metrics
        
        # B. 퍼센타일 기반 고객 세그먼트 분석
        segments = self._create_customer_segments(customer_summary)
        customers['segment_analysis'] = segments
        
        # C. 지역별 고객 분석
        if '__region__' in customer_data.columns:
            region_analysis = customer_data.groupby('__region__').agg({
                '__customer_id__': 'nunique',
                '__amount__': ['sum', 'mean'],
                '__dt__': 'count'
            }).round(2)
            
            region_analysis.columns = ['고객수', '매출액', 'AOV', '주문수']
            region_analysis['고객당_매출'] = region_analysis['매출액'] / region_analysis['고객수']
            region_analysis = region_analysis.sort_values('매출액', ascending=False).head(10)
            
            customers['region_analysis'] = region_analysis
        
        # D. 고객 생애주기 분석 (구매 차수별)
        lifecycle_analysis = customer_summary['구매횟수'].value_counts().sort_index()
        lifecycle_df = pd.DataFrame({
            '구매차수': lifecycle_analysis.index,
            '고객수': lifecycle_analysis.values
        })
        lifecycle_df['누적고객수'] = lifecycle_df['고객수'].cumsum()
        lifecycle_df['잔존율'] = (lifecycle_df['누적고객수'] / total_customers * 100)
        
        # 각 차수별 평균 구매금액
        for purchase_count in lifecycle_df['구매차수']:
            customers_at_count = customer_summary[customer_summary['구매횟수'] >= purchase_count]
            if len(customers_at_count) > 0:
                avg_amount = customers_at_count['총구매금액'].mean()
                lifecycle_df.loc[lifecycle_df['구매차수'] == purchase_count, '평균누적구매금액'] = avg_amount
        
        customers['lifecycle_analysis'] = lifecycle_df.head(10)  # 상위 10차수까지
        
        return customers
    
    def _create_customer_segments(self, customer_summary: pd.DataFrame) -> pd.DataFrame:
        """퍼센타일 기반 고객 세그먼트 생성"""
        
        # 총구매금액 기준으로 퍼센타일 계산
        customer_summary['percentile'] = customer_summary['총구매금액'].rank(pct=True) * 100
        
        # 세그먼트 정의
        def assign_segment(percentile):
            if percentile >= 90:
                return 'VIP (상위 10%)'
            elif percentile >= 70:
                return '골드 (상위 11-30%)'
            elif percentile >= 30:
                return '실버 (상위 31-70%)'
            else:
                return '브론즈 (하위 30%)'
        
        customer_summary['세그먼트'] = customer_summary['percentile'].apply(assign_segment)
        
        # 세그먼트별 집계
        segment_analysis = customer_summary.groupby('세그먼트').agg({
            '총구매금액': ['count', 'sum', 'mean'],
            '구매횟수': 'mean',
            '평균구매금액': 'mean'
        }).round(2)
        
        segment_analysis.columns = ['고객수', '총매출기여', '평균구매금액', '평균구매횟수', '평균AOV']
        
        # 비율 계산
        total_customers = customer_summary.shape[0]
        total_revenue = customer_summary['총구매금액'].sum()
        
        segment_analysis['고객비율'] = (segment_analysis['고객수'] / total_customers * 100)
        segment_analysis['매출기여도'] = (segment_analysis['총매출기여'] / total_revenue * 100)
        segment_analysis['고객생애가치'] = segment_analysis['총매출기여'] / segment_analysis['고객수']
        
        # 세그먼트 순서 정렬
        segment_order = ['VIP (상위 10%)', '골드 (상위 11-30%)', '실버 (상위 31-70%)', '브론즈 (하위 30%)']
        segment_analysis = segment_analysis.reindex([seg for seg in segment_order if seg in segment_analysis.index])
        
        return segment_analysis
    
    def _analyze_operations(self) -> Dict:
        """운영 분석"""
        operations = {}
        
        # A. 주문 처리 현황
        if COL_STATUS in self.seller_data.columns:
            status_analysis = self.seller_data[COL_STATUS].value_counts()
            status_df = pd.DataFrame({
                '상태': status_analysis.index,
                '건수': status_analysis.values,
                '비율': (status_analysis.values / len(self.seller_data) * 100).round(2)
            })
            
            operations['status_analysis'] = status_df
            
            # 주요 지표 계산
            total_orders = len(self.seller_data)
            operations['key_metrics'] = {
                '전체주문수': total_orders,
                '배송완료율': (status_analysis.get('배송완료', 0) / total_orders * 100),
                '취소율': (status_analysis.get('결제취소', 0) / total_orders * 100),
                '지연율': (status_analysis.get('배송지연', 0) / total_orders * 100),
                '반품률': (status_analysis.get('반품', 0) / total_orders * 100)
            }
        
        # B. 배송 성과 분석
        shipping_metrics = {}
        
        if COL_SHIP_DATE in self.seller_data.columns:
            ship_data = self.seller_data[self.seller_data[COL_SHIP_DATE].notna()].copy()
            if not ship_data.empty:
                ship_data['ship_dt'] = pd.to_datetime(ship_data[COL_SHIP_DATE], errors='coerce')
                ship_data['출고소요시간'] = (ship_data['ship_dt'] - ship_data['__dt__']).dt.total_seconds() / 86400.0
                
                shipping_metrics['평균출고시간'] = ship_data['출고소요시간'].mean()
                shipping_metrics['당일발송률'] = (ship_data['출고소요시간'] <= 1).mean() * 100
                
        if COL_DELIVERED_DATE in self.seller_data.columns and COL_SHIP_DATE in self.seller_data.columns:
            delivery_data = self.seller_data[
                self.seller_data[COL_DELIVERED_DATE].notna() & 
                self.seller_data[COL_SHIP_DATE].notna()
            ].copy()
            
            if not delivery_data.empty:
                delivery_data['delivery_dt'] = pd.to_datetime(delivery_data[COL_DELIVERED_DATE], errors='coerce')
                delivery_data['ship_dt'] = pd.to_datetime(delivery_data[COL_SHIP_DATE], errors='coerce')
                delivery_data['배송소요시간'] = (delivery_data['delivery_dt'] - delivery_data['ship_dt']).dt.total_seconds() / 86400.0
                
                shipping_metrics['평균배송시간'] = delivery_data['배송소요시간'].mean()
                shipping_metrics['빠른배송률'] = (delivery_data['배송소요시간'] <= 2).mean() * 100
        
        operations['shipping_metrics'] = shipping_metrics
        
        # C. 클레임 분석 (환불 필드 기준)
        if COL_REFUND_FIELD in self.seller_data.columns:
            refund_data = self.seller_data[self.seller_data[COL_REFUND_FIELD].notna()]
            if not refund_data.empty:
                claim_analysis = refund_data[COL_REFUND_FIELD].value_counts()
                claim_df = pd.DataFrame({
                    '클레임유형': claim_analysis.index,
                    '건수': claim_analysis.values,
                    '발생률': (claim_analysis.values / len(self.seller_data) * 100).round(3)
                })
                operations['claim_analysis'] = claim_df
        
        return operations
    
    def _analyze_benchmarking(self) -> Dict:
        """벤치마킹 분석"""
        benchmarking = {}
        
        # A. 카테고리 내 포지션
        main_category = self.analysis_data['basic_info'].get('main_category')
        
        if main_category and '__category_mapped__' in self.overall_data.columns and COL_SELLER in self.overall_data.columns:
            category_data = self.overall_data[self.overall_data['__category_mapped__'] == main_category]
            
            # 셀러별 성과 집계
            seller_performance = category_data.groupby(COL_SELLER).agg({
                '__amount__': ['sum', 'count', 'mean'],
                '__customer_id__': 'nunique' if '__customer_id__' in category_data.columns else lambda x: np.nan
            }).round(2)
            
            seller_performance.columns = ['총매출', '주문수', 'AOV', '고객수']
            seller_performance = seller_performance.sort_values('총매출', ascending=False)
            
            # 내 순위 정보
            if self.seller_name in seller_performance.index:
                my_rank = seller_performance.index.get_loc(self.seller_name) + 1
                total_sellers = len(seller_performance)
                
                position_metrics = {
                    '매출순위': f"{my_rank}/{total_sellers}",
                    '상위퍼센트': f"{((total_sellers - my_rank) / total_sellers * 100):.1f}%"
                }
                
                # 각 지표별 순위
                for metric in ['총매출', '주문수', 'AOV', '고객수']:
                    if not seller_performance[metric].isna().all():
                        metric_rank = seller_performance[metric].rank(ascending=False)[self.seller_name]
                        position_metrics[f'{metric}_순위'] = f"{int(metric_rank)}/{total_sellers}"
                
                benchmarking['position_metrics'] = position_metrics
                
                # 경쟁사 TOP 5 (나를 포함)
                top_competitors = seller_performance.head(10)
                benchmarking['top_competitors'] = top_competitors
        
        # B. 상대적 성과 분석
        relative_performance = {}
        
        for key, value in self.kpis.items():
            if '_vs_category' in key and not (isinstance(value, float) and math.isnan(value)):
                metric_name = key.replace('_vs_category', '')
                relative_performance[metric_name] = {
                    '상대성과': value,
                    '성과등급': self._get_performance_grade(value, metric_name),
                    '개선여지': self._get_improvement_potential(value, metric_name)
                }
        
        benchmarking['relative_performance'] = relative_performance
        
        return benchmarking
    
    def _analyze_trends(self) -> Dict:
        """트렌드 분석"""
        trends = {}
        
        # A. 월별 트렌드 (데이터 기간이 충분한 경우)
        monthly_trend = self.seller_data.groupby(self.seller_data['__dt__'].dt.to_period('M')).agg({
            '__amount__': ['sum', 'count', 'mean'],
            '__customer_id__': 'nunique' if '__customer_id__' in self.seller_data.columns else lambda x: np.nan
        }).round(2)
        
        monthly_trend.columns = ['매출액', '주문수', 'AOV', '고객수']
        monthly_trend.index = monthly_trend.index.astype(str)
        
        # 성장률 계산
        if len(monthly_trend) > 1:
            monthly_trend['매출성장률'] = monthly_trend['매출액'].pct_change() * 100
            monthly_trend['주문성장률'] = monthly_trend['주문수'].pct_change() * 100
        
        trends['monthly_trend'] = monthly_trend
        
        # B. 주별 트렌드
        weekly_trend = self.seller_data.groupby(self.seller_data['__dt__'].dt.to_period('W')).agg({
            '__amount__': ['sum', 'count'],
        }).round(2)
        
        weekly_trend.columns = ['매출액', '주문수']
        weekly_trend.index = weekly_trend.index.astype(str)
        
        trends['weekly_trend'] = weekly_trend
        
        # C. 일별 트렌드 (최근 30일)
        recent_30days = self.seller_data[
            self.seller_data['__dt__'] >= (self.seller_data['__dt__'].max() - timedelta(days=30))
        ]
        
        daily_trend = recent_30days.groupby(recent_30days['__dt__'].dt.date).agg({
            '__amount__': ['sum', 'count'],
        }).round(2)
        
        daily_trend.columns = ['매출액', '주문수']
        daily_trend.index = daily_trend.index.astype(str)
        
        trends['daily_trend'] = daily_trend
        
        return trends
    
    def _get_performance_grade(self, value: float, metric_name: str) -> str:
        """성과 등급 계산"""
        # 낮을수록 좋은 지표들
        if any(bad_word in metric_name for bad_word in ['cancel', 'delay', 'return']):
            if value <= 0.7: return 'A+'
            elif value <= 0.8: return 'A'
            elif value <= 0.9: return 'B+'
            elif value <= 1.1: return 'B'
            else: return 'C'
        else:
            # 높을수록 좋은 지표들
            if value >= 1.3: return 'A+'
            elif value >= 1.2: return 'A'
            elif value >= 1.1: return 'B+'
            elif value >= 0.9: return 'B'
            else: return 'C'
    
    def _get_improvement_potential(self, value: float, metric_name: str) -> str:
        """개선 여지 평가"""
        # 낮을수록 좋은 지표들
        if any(bad_word in metric_name for bad_word in ['cancel', 'delay', 'return']):
            if value <= 0.8: return '유지'
            elif value <= 1.1: return '중간'
            else: return '높음'
        else:
            # 높을수록 좋은 지표들
            if value >= 1.2: return '유지'
            elif value >= 0.9: return '중간'
            else: return '높음'
    
    def export_to_excel(self, output_path: str = None):
        """엑셀 파일로 출력"""
        
        if not output_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            safe_seller_name = sanitize_filename(self.seller_name)
            output_path = f"./reports/셀러성과대시보드_{safe_seller_name}_{timestamp}.xlsx"
        
        # 출력 디렉토리 생성
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                
                # 1. 대시보드 요약
                self._write_dashboard_summary(writer)
                
                # 2. 매출 분석
                self._write_sales_analysis(writer)
                
                # 3. 고객 분석  
                self._write_customer_analysis(writer)
                
                # 4. 운영 분석
                self._write_operations_analysis(writer)
                
                # 5. 벤치마킹
                self._write_benchmarking_analysis(writer)
                
                # 6. 트렌드 분석
                self._write_trends_analysis(writer)
            
            print(f"✅ 엑셀 리포트 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 엑셀 출력 실패: {e}")
            return None
    
    def _write_dashboard_summary(self, writer):
        """대시보드 요약 시트 작성"""
        
        # 기본 정보
        basic_info = self.analysis_data['basic_info']
        current_row = 0
        
        # A. 셀러 기본 정보
        # 제목 추가
        title_df = pd.DataFrame([['A. 셀러 기본 정보']], columns=[''])
        title_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False, header=False)
        current_row += 2
        
        seller_info = pd.DataFrame([
            ['셀러명', basic_info['seller_name']],
            ['분석기간', f"{basic_info['period_start']} ~ {basic_info['period_end']}"],
            ['분석일시', basic_info['analysis_date']],
            ['총 분석일수', f"{basic_info['total_days']}일"],
            ['주력카테고리', basic_info.get('main_category', 'N/A')],
            ['카테고리 점유율', f"{basic_info.get('main_category_share', 0):.1f}%"],
            ['카테고리 순위', f"{basic_info.get('category_rank', 'N/A')}/{basic_info.get('category_total_sellers', 'N/A')}"],
            ['시장점유율', f"{basic_info.get('market_share', 0):.1f}%"]
        ], columns=['구분', '값'])
        
        seller_info.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False)
        current_row += len(seller_info) + 3
        
        # B. KPI 스코어카드
        # 제목 추가
        title_df = pd.DataFrame([['B. KPI 스코어카드 (카테고리 평균 대비)']], columns=[''])
        title_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False, header=False)
        current_row += 2
        
        kpi_scorecard = []
        
        # 주요 KPI들과 카테고리 대비 성과
        kpi_mapping = {
            '총매출액': ('total_revenue', 'total_revenue_vs_category'),
            '평균주문금액': ('avg_order_value', 'avg_order_value_vs_category'),
            '재구매율': ('repeat_rate', 'repeat_rate_vs_category'),
            '취소율': ('cancel_rate', 'cancel_rate_vs_category'),
            '배송완료시간': ('avg_delivery_time', 'avg_delivery_time_vs_category'),
            '고객수': ('unique_customers', 'unique_customers_vs_category')
        }
        
        for kpi_name, (base_key, vs_key) in kpi_mapping.items():
            current_value = self.kpis.get(base_key, np.nan)
            vs_category = self.kpis.get(vs_key, np.nan)
            
            if not pd.isna(current_value):
                # 값 포맷팅
                if '금액' in kpi_name or '매출' in kpi_name:
                    formatted_value = format_currency(current_value)
                elif '율' in kpi_name:
                    formatted_value = f"{current_value*100:.1f}%"
                elif '시간' in kpi_name:
                    formatted_value = f"{current_value:.1f}일"
                else:
                    formatted_value = f"{current_value:,.0f}"
                
                # 상대 성과
                if not pd.isna(vs_category):
                    is_inverse = any(word in kpi_name for word in ['취소', '시간', '지연'])
                    if is_inverse:
                        relative_perf = f"{(1-vs_category)*100:+.1f}%"
                        grade = self._get_performance_grade(vs_category, 'cancel')
                    else:
                        relative_perf = f"{(vs_category-1)*100:+.1f}%"
                        grade = self._get_performance_grade(vs_category, 'normal')
                else:
                    relative_perf = "N/A"
                    grade = "N/A"
                
                kpi_scorecard.append([kpi_name, formatted_value, relative_perf, grade])
        
        kpi_df = pd.DataFrame(kpi_scorecard, columns=['지표', '현재값', '카테고리대비', '등급'])
        kpi_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False)
        current_row += len(kpi_df) + 3
        
        # C. 성과 점수 (레이더 차트용 데이터)
        # 제목 추가
        title_df = pd.DataFrame([['C. 영역별 성과 점수 (0-100점)']], columns=[''])
        title_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False, header=False)
        current_row += 2
        performance_scores = {
            '매출성과': self._calculate_sales_score(),
            '고객성과': self._calculate_customer_score(),
            '운영성과': self._calculate_operations_score(),
            '시장성과': self._calculate_market_score()
        }
        
        scores_df = pd.DataFrame(list(performance_scores.items()), columns=['영역', '점수'])
        scores_df.to_excel(writer, sheet_name='대시보드요약', startrow=current_row, index=False)
    
    def _write_sales_analysis(self, writer):
        """매출 분석 시트 작성"""
        
        sales_data = self.analysis_data['sales']
        current_row = 0
        
        # A. 기본 매출 지표
        if 'basic_metrics' in sales_data:
            # 제목 추가
            title_df = pd.DataFrame([['A. 기본 매출 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            basic_df = pd.DataFrame(list(sales_data['basic_metrics'].items()), columns=['지표', '값'])
            # 값 포맷팅
            for idx, row in basic_df.iterrows():
                if '매출' in row['지표'] or '금액' in row['지표']:
                    basic_df.loc[idx, '값'] = format_currency(row['값'])
                elif '수' in row['지표']:
                    basic_df.loc[idx, '값'] = f"{row['값']:,.0f}"
            
            basic_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False)
            current_row += len(basic_df) + 3
        
        # B. 채널별 매출 분석
        if 'channel_analysis' in sales_data:
            # 제목 추가
            title_df = pd.DataFrame([['B. 채널별 매출 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            channel_df = sales_data['channel_analysis'].reset_index()
            channel_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False)
            current_row += len(channel_df) + 3
        
        # C. 상품별 매출 TOP 20
        if 'product_analysis' in sales_data:
            # 제목 추가
            title_df = pd.DataFrame([['C. 상품별 매출 TOP 20']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            product_df = sales_data['product_analysis'].reset_index()
            product_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False)
            current_row += len(product_df) + 3
        
        # D. 시간대별 매출 패턴
        if 'hourly_pattern' in sales_data:
            # 제목 추가
            title_df = pd.DataFrame([['D. 시간대별 매출 패턴']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            hourly_df = sales_data['hourly_pattern'].reset_index()
            hourly_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False)
            current_row += len(hourly_df) + 3
        
        # E. 요일별 매출 패턴
        if 'daily_pattern' in sales_data:
            # 제목 추가
            title_df = pd.DataFrame([['E. 요일별 매출 패턴']], columns=[''])
            title_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            daily_df = sales_data['daily_pattern'].reset_index()
            daily_df.to_excel(writer, sheet_name='매출분석', startrow=current_row, index=False)
    
    def _write_customer_analysis(self, writer):
        """고객 분석 시트 작성"""
        
        customers_data = self.analysis_data['customers']
        current_row = 0
        
        if 'error' in customers_data:
            error_df = pd.DataFrame([['오류', customers_data['error']]], columns=['구분', '내용'])
            error_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False)
            return
        
        # A. 고객 기본 지표
        if 'basic_metrics' in customers_data:
            # 제목 추가
            title_df = pd.DataFrame([['A. 고객 기본 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            basic_df = pd.DataFrame(list(customers_data['basic_metrics'].items()), columns=['지표', '값'])
            # 값 포맷팅
            for idx, row in basic_df.iterrows():
                if '율' in row['지표']:
                    basic_df.loc[idx, '값'] = f"{row['값']:.1f}%"
                elif '가치' in row['지표']:
                    basic_df.loc[idx, '값'] = format_currency(row['값'])
                else:
                    basic_df.loc[idx, '값'] = f"{row['값']:,.1f}"
            
            basic_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False)
            current_row += len(basic_df) + 3
        
        # B. 고객 세그먼트 분석 (퍼센타일 기반)
        if 'segment_analysis' in customers_data:
            # 제목 추가
            title_df = pd.DataFrame([['B. 고객 세그먼트 분석 (퍼센타일 기반)']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            segment_df = customers_data['segment_analysis'].reset_index()
            segment_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False)
            current_row += len(segment_df) + 3
        
        # C. 지역별 고객 분석
        if 'region_analysis' in customers_data:
            # 제목 추가
            title_df = pd.DataFrame([['C. 지역별 고객 분석 TOP 10']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            region_df = customers_data['region_analysis'].reset_index()
            region_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False)
            current_row += len(region_df) + 3
        
        # D. 고객 생애주기 분석
        if 'lifecycle_analysis' in customers_data:
            # 제목 추가
            title_df = pd.DataFrame([['D. 고객 생애주기 분석 (구매 차수별)']], columns=[''])
            title_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            lifecycle_df = customers_data['lifecycle_analysis']
            lifecycle_df.to_excel(writer, sheet_name='고객분석', startrow=current_row, index=False)
    
    def _write_operations_analysis(self, writer):
        """운영 분석 시트 작성"""
        
        operations_data = self.analysis_data['operations']
        current_row = 0
        
        # A. 주요 운영 지표
        if 'key_metrics' in operations_data:
            # 제목 추가
            title_df = pd.DataFrame([['A. 주요 운영 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            key_df = pd.DataFrame(list(operations_data['key_metrics'].items()), columns=['지표', '값'])
            # 값 포맷팅
            for idx, row in key_df.iterrows():
                if '율' in row['지표'] or '률' in row['지표']:
                    key_df.loc[idx, '값'] = f"{row['값']:.2f}%"
                else:
                    key_df.loc[idx, '값'] = f"{row['값']:,.0f}"
            
            key_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
            current_row += len(key_df) + 3
        
        # B. 주문 상태 분석
        if 'status_analysis' in operations_data:
            # 제목 추가
            title_df = pd.DataFrame([['B. 주문 상태 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            status_df = operations_data['status_analysis']
            status_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
            current_row += len(status_df) + 3
        
        # C. 배송 성과 지표
        if 'shipping_metrics' in operations_data:
            # 제목 추가
            title_df = pd.DataFrame([['C. 배송 성과 지표']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            shipping_df = pd.DataFrame(list(operations_data['shipping_metrics'].items()), columns=['지표', '값'])
            # 값 포맷팅
            for idx, row in shipping_df.iterrows():
                if '시간' in row['지표']:
                    shipping_df.loc[idx, '값'] = f"{row['값']:.1f}일"
                elif '률' in row['지표'] or '율' in row['지표']:
                    shipping_df.loc[idx, '값'] = f"{row['값']:.1f}%"
            
            shipping_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
            current_row += len(shipping_df) + 3
        
        # D. 클레임 분석
        if 'claim_analysis' in operations_data:
            # 제목 추가
            title_df = pd.DataFrame([['D. 클레임 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            claim_df = operations_data['claim_analysis']
            claim_df.to_excel(writer, sheet_name='운영분석', startrow=current_row, index=False)
    
    def _write_benchmarking_analysis(self, writer):
        """벤치마킹 분석 시트 작성"""
        
        benchmarking_data = self.analysis_data['benchmarking']
        current_row = 0
        
        # A. 카테고리 내 포지션
        if 'position_metrics' in benchmarking_data:
            # 제목 추가
            title_df = pd.DataFrame([['A. 카테고리 내 포지션']], columns=[''])
            title_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False, header=False)
            current_row += 2
            
            position_df = pd.DataFrame(list(benchmarking_data['position_metrics'].items()), columns=['지표', '값'])
            position_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False)
            current_row += len(position_df) + 3
        
        # B. 경쟁사 비교 (TOP 10)
        if 'top_competitors' in benchmarking_data:
            # 제목 추가
            title_df = pd.DataFrame([['B. 카테고리 내 경쟁사 비교 TOP 10']], columns=[''])
            title_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False, header=False)
            current_row += 2
            
            competitors_df = benchmarking_data['top_competitors'].reset_index()
            competitors_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False)
            current_row += len(competitors_df) + 3
        
        # C. 상대적 성과 분석
        if 'relative_performance' in benchmarking_data:
            # 제목 추가
            title_df = pd.DataFrame([['C. 상대적 성과 분석 (카테고리 평균 대비)']], columns=[''])
            title_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False, header=False)
            current_row += 2
            
            relative_data = []
            for metric, data in benchmarking_data['relative_performance'].items():
                relative_data.append([
                    metric,
                    f"{data['상대성과']:.2f}",
                    data['성과등급'],
                    data['개선여지']
                ])
            
            relative_df = pd.DataFrame(relative_data, columns=['지표', '상대성과', '등급', '개선여지'])
            relative_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False)
        if 'relative_performance' in benchmarking_data:
            relative_data = []
            for metric, data in benchmarking_data['relative_performance'].items():
                relative_data.append([
                    metric,
                    f"{data['상대성과']:.2f}",
                    data['성과등급'],
                    data['개선여지']
                ])
            
            relative_df = pd.DataFrame(relative_data, columns=['지표', '상대성과', '등급', '개선여지'])
            relative_df.to_excel(writer, sheet_name='벤치마킹', startrow=current_row, index=False)
    
    def _write_trends_analysis(self, writer):
        """트렌드 분석 시트 작성"""
        
        trends_data = self.analysis_data['trends']
        current_row = 0
        
        # A. 월별 트렌드
        if 'monthly_trend' in trends_data:
            # 제목 추가
            title_df = pd.DataFrame([['A. 월별 트렌드 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            monthly_df = trends_data['monthly_trend'].reset_index()
            monthly_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False)
            current_row += len(monthly_df) + 3
        
        # B. 주별 트렌드
        if 'weekly_trend' in trends_data:
            # 제목 추가
            title_df = pd.DataFrame([['B. 주별 트렌드 분석']], columns=[''])
            title_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            weekly_df = trends_data['weekly_trend'].reset_index()
            weekly_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False)
            current_row += len(weekly_df) + 3
        
        # C. 일별 트렌드 (최근 30일)
        if 'daily_trend' in trends_data:
            # 제목 추가
            title_df = pd.DataFrame([['C. 일별 트렌드 분석 (최근 30일)']], columns=[''])
            title_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False, header=False)
            current_row += 2
            
            daily_df = trends_data['daily_trend'].reset_index()
            daily_df.to_excel(writer, sheet_name='트렌드분석', startrow=current_row, index=False)
    
    def _calculate_sales_score(self) -> float:
        """매출 성과 점수 계산 (0-100)"""
        scores = []
        
        # AOV, 매출 성장률 등을 기준으로 점수 계산
        aov_vs = self.kpis.get('avg_order_value_vs_category', 1.0)
        revenue_vs = self.kpis.get('total_revenue_vs_category', 1.0)
        
        if not pd.isna(aov_vs):
            scores.append(min(100, max(0, (aov_vs - 0.5) * 100)))
        if not pd.isna(revenue_vs):
            scores.append(min(100, max(0, (revenue_vs - 0.5) * 100)))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _calculate_customer_score(self) -> float:
        """고객 성과 점수 계산 (0-100)"""
        scores = []
        
        repeat_vs = self.kpis.get('repeat_rate_vs_category', 1.0)
        ltv_vs = self.kpis.get('customer_ltv_vs_category', 1.0)
        
        if not pd.isna(repeat_vs):
            scores.append(min(100, max(0, (repeat_vs - 0.5) * 100)))
        if not pd.isna(ltv_vs):
            scores.append(min(100, max(0, (ltv_vs - 0.5) * 100)))
        
        return sum(scores) / len(scores) if scores else 50
    
    def _calculate_operations_score(self) -> float:
        """운영 성과 점수 계산 (0-100)"""
        scores = []
        
        cancel_vs = self.kpis.get('cancel_rate_vs_category', 1.0)
        delivery_vs = self.kpis.get('avg_delivery_time_vs_category', 1.0)
        
        if not pd.isna(cancel_vs):
            scores.append(min(100, max(0, (2 - cancel_vs - 0.5) * 100)))  # 역방향
        if not pd.isna(delivery_vs):
            scores.append(min(100, max(0, (2 - delivery_vs - 0.5) * 100)))  # 역방향
        
        return sum(scores) / len(scores) if scores else 50
    
    def _calculate_market_score(self) -> float:
        """시장 성과 점수 계산 (0-100)"""
        # 카테고리 내 순위 기반
        basic_info = self.analysis_data['basic_info']
        
        if 'category_percentile' in basic_info:
            return basic_info['category_percentile']
        
        return 50

def main():
    """메인 실행 함수"""
    
    print("📊 셀러 성과 대시보드 엑셀 생성기")
    print("=" * 60)
    
    # 명령행 인수로 셀러 지정
    target_seller = None
    if len(sys.argv) > 1:
        target_seller = sys.argv[1]
    else:
        # 기본값: 매출 상위 셀러 자동 선택
        try:
            df = load_excel_data(CONFIG["INPUT_XLSX"])
            dfp = prepare_dataframe(df, None, None)
            
            if COL_SELLER in dfp.columns:
                seller_revenue = dfp.groupby(COL_SELLER)['__amount__'].sum().sort_values(ascending=False)
                target_seller = seller_revenue.index[0]
                print(f"💡 매출 1위 셀러 '{target_seller}' 자동 선택")
            else:
                target_seller = "전체"
                print(f"💡 셀러 정보 없음 - '전체' 분석 수행")
                
        except Exception as e:
            print(f"❌ 자동 선택 실패: {e}")
            return
    
    try:
        # 대시보드 생성
        dashboard = SellerDashboardExcel(target_seller)
        
        print(f"📁 데이터 로딩 중...")
        if not dashboard.load_data():
            return
        
        print(f"📊 {target_seller} 분석 중...")
        dashboard.analyze_all_data()
        
        print(f"📋 엑셀 리포트 생성 중...")
        output_path = dashboard.export_to_excel()
        
        if output_path:
            print(f"\n🎉 성공!")
            print(f"📂 파일 위치: {output_path}")
            print(f"📊 포함 시트: 6개 (요약, 매출, 고객, 운영, 벤치마킹, 트렌드)")
            
            # 분석 결과 요약 출력
            basic_info = dashboard.analysis_data['basic_info']
            print(f"\n📋 분석 요약:")
            print(f"  • 분석기간: {basic_info['period_start']} ~ {basic_info['period_end']}")
            print(f"  • 총 주문수: {dashboard.kpis.get('total_orders', 0):,}건")
            print(f"  • 총 매출액: {format_currency(dashboard.kpis.get('total_revenue', 0))}")
            print(f"  • 평균주문금액: {format_currency(dashboard.kpis.get('avg_order_value', 0))}")
            
            if 'main_category' in basic_info:
                print(f"  • 주력카테고리: {basic_info['main_category']}")
                if 'category_rank' in basic_info:
                    print(f"  • 카테고리 순위: {basic_info['category_rank']}/{basic_info['category_total_sellers']}")
        
        print(f"\n💡 다른 셀러 분석: python seller_dashboard_excel.py [셀러명]")
        
    except Exception as e:
        print(f"❌ 대시보드 생성 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
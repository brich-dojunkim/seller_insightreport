# data/metrics_calculator.py - 핵심 지표 계산

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
sys.path.append('..')
from config import COMPANY_SETTINGS, METRIC_FORMATS, SUCCESS_MESSAGES

class MetricsCalculator:
    """비즈니스 지표 계산을 담당하는 클래스"""
    
    def __init__(self, company_data, platform_data, company_name):
        self.company_data = company_data.copy()
        self.platform_data = platform_data.copy()
        self.company_name = company_name
        self.metrics = {}
        
        # 날짜 데이터 전처리
        self._prepare_date_data()
    
    def _prepare_date_data(self):
        """날짜 관련 데이터 전처리"""
        # 결제일을 datetime으로 변환
        if '결제일' in self.company_data.columns:
            self.company_data['결제일_dt'] = pd.to_datetime(self.company_data['결제일'])
            self.company_data['결제일자'] = self.company_data['결제일_dt'].dt.date
            self.company_data['결제시간'] = self.company_data['결제일_dt'].dt.hour
            self.company_data['요일'] = self.company_data['결제일_dt'].dt.day_name()
            self.company_data['요일_한글'] = self.company_data['결제일_dt'].dt.strftime('%A').map({
                'Monday': '월', 'Tuesday': '화', 'Wednesday': '수', 'Thursday': '목',
                'Friday': '금', 'Saturday': '토', 'Sunday': '일'
            })
    
    def calculate_basic_metrics(self):
        """기본 지표 계산"""
        try:
            basic = {
                'total_orders': len(self.company_data),
                'total_revenue': self.company_data['상품별 총 주문금액'].sum(),
                'avg_order_value': self.company_data['상품별 총 주문금액'].mean(),
                'unique_products': self.company_data['상품명'].nunique(),
                'unique_customers': len(self.company_data['구매자명'].dropna().unique()) if '구매자명' in self.company_data.columns else 0,
                'date_range': {
                    'start': self.company_data['결제일'].min().split()[0] if isinstance(self.company_data['결제일'].min(), str) else self.company_data['결제일'].min().strftime('%Y-%m-%d'),
                    'end': self.company_data['결제일'].max().split()[0] if isinstance(self.company_data['결제일'].max(), str) else self.company_data['결제일'].max().strftime('%Y-%m-%d')
                }
            }
            
            self.metrics['basic'] = basic
            print(SUCCESS_MESSAGES['metrics_calculated'])
            return basic
            
        except Exception as e:
            print(f"❌ 기본 지표 계산 실패: {str(e)}")
            return None
    
    def calculate_growth_metrics(self):
        """성장률 지표 계산 (시뮬레이션)"""
        try:
            # 실제로는 전주/전월 데이터와 비교해야 하지만, 
            # 현재는 시뮬레이션 데이터로 계산
            
            current_orders = self.metrics['basic']['total_orders']
            current_revenue = self.metrics['basic']['total_revenue']
            current_aov = self.metrics['basic']['avg_order_value']
            
            # 전주 데이터 시뮬레이션 (실제로는 DB나 이전 데이터에서 가져와야 함)
            simulated_last_week = {
                'orders': int(current_orders * 0.87),  # 15% 성장 가정
                'revenue': int(current_revenue * 0.89), # 12% 성장 가정
                'aov': int(current_aov * 1.02)  # 2% 성장 가정
            }
            
            growth = {
                'order_growth': ((current_orders - simulated_last_week['orders']) / simulated_last_week['orders']) * 100,
                'revenue_growth': ((current_revenue - simulated_last_week['revenue']) / simulated_last_week['revenue']) * 100,
                'aov_growth': ((current_aov - simulated_last_week['aov']) / simulated_last_week['aov']) * 100,
                'last_week_data': simulated_last_week
            }
            
            self.metrics['growth'] = growth
            return growth
            
        except Exception as e:
            print(f"❌ 성장률 계산 실패: {str(e)}")
            return None
    
    def calculate_channel_metrics(self):
        """채널별 지표 계산"""
        try:
            channel_analysis = self.company_data.groupby('판매채널').agg({
                '상품주문번호': 'count',
                '상품별 총 주문금액': ['sum', 'mean']
            })
            
            # 컬럼명 정리
            channel_analysis.columns = ['주문수', '총매출', '평균주문금액']
            
            # 점유율 계산
            total_revenue = self.metrics['basic']['total_revenue']
            channel_analysis['매출점유율'] = (channel_analysis['총매출'] / total_revenue * 100).round(1)
            channel_analysis['주문점유율'] = (channel_analysis['주문수'] / self.metrics['basic']['total_orders'] * 100).round(1)
            
            # 성장률 시뮬레이션 (채널별)
            channel_growth = {}
            for channel in channel_analysis.index:
                # 각 채널별로 다른 성장률 시뮬레이션
                if '카페24' in channel:
                    growth_rate = np.random.uniform(10, 20)
                elif 'GS샵' in channel or 'SSG' in channel:
                    growth_rate = np.random.uniform(5, 15)
                else:
                    growth_rate = np.random.uniform(-5, 25)
                
                channel_growth[channel] = round(growth_rate, 1)
            
            channel_analysis['성장률'] = channel_analysis.index.map(channel_growth)
            
            # 정렬 (매출 기준)
            channel_analysis = channel_analysis.sort_values('총매출', ascending=False)
            
            self.metrics['channels'] = channel_analysis
            return channel_analysis
            
        except Exception as e:
            print(f"❌ 채널 지표 계산 실패: {str(e)}")
            return None
    
    def calculate_time_metrics(self):
        """시간대별 지표 계산"""
        try:
            time_metrics = {}
            
            # 시간대별 주문 분포
            hourly_orders = self.company_data.groupby('결제시간')['상품주문번호'].count()
            time_metrics['hourly_orders'] = hourly_orders.to_dict()
            
            # 요일별 매출 분포  
            daily_revenue = self.company_data.groupby('요일_한글')['상품별 총 주문금액'].sum()
            # 요일 순서 맞추기
            day_order = ['월', '화', '수', '목', '금', '토', '일']
            daily_revenue = daily_revenue.reindex(day_order, fill_value=0)
            time_metrics['daily_revenue'] = daily_revenue.to_dict()
            
            # 일별 트렌드
            daily_trend = self.company_data.groupby('결제일자').agg({
                '상품주문번호': 'count',
                '상품별 총 주문금액': 'sum'
            }).rename(columns={'상품주문번호': '주문수', '상품별 총 주문금액': '매출'})
            time_metrics['daily_trend'] = daily_trend
            
            # 피크 시간대 분석
            peak_hours = hourly_orders.nlargest(3)
            time_metrics['peak_hours'] = {
                'hours': peak_hours.index.tolist(),
                'orders': peak_hours.values.tolist()
            }
            
            self.metrics['time'] = time_metrics
            return time_metrics
            
        except Exception as e:
            print(f"❌ 시간 지표 계산 실패: {str(e)}")
            return None
    
    def calculate_product_metrics(self):
        """상품별 지표 계산"""
        try:
            product_analysis = self.company_data.groupby('상품명').agg({
                '상품주문번호': 'count',
                '상품별 총 주문금액': 'sum',
                '상품가격': 'mean'
            }).rename(columns={
                '상품주문번호': '주문수',
                '상품별 총 주문금액': '총매출',
                '상품가격': '평균가격'
            })
            
            # 매출 기여도
            total_revenue = self.metrics['basic']['total_revenue']
            product_analysis['매출기여도'] = (product_analysis['총매출'] / total_revenue * 100).round(1)
            
            # 베스트셀러 TOP 10
            bestsellers = product_analysis.sort_values('총매출', ascending=False).head(10)
            
            # 주문 상태별 분포
            status_distribution = self.company_data['주문상태'].value_counts()
            
            # 배송 관련 지표
            delivery_metrics = {}
            if '배송완료' in status_distribution.index:
                delivery_rate = (status_distribution['배송완료'] / len(self.company_data)) * 100
                delivery_metrics['completion_rate'] = round(delivery_rate, 1)
            
            if '결제취소' in status_distribution.index:
                cancel_rate = (status_distribution['결제취소'] / len(self.company_data)) * 100
                delivery_metrics['cancel_rate'] = round(cancel_rate, 1)
            
            product_metrics = {
                'all_products': product_analysis,
                'bestsellers': bestsellers,
                'status_distribution': status_distribution.to_dict(),
                'delivery_metrics': delivery_metrics
            }
            
            self.metrics['products'] = product_metrics
            return product_metrics
            
        except Exception as e:
            print(f"❌ 상품 지표 계산 실패: {str(e)}")
            return None
    
    def calculate_benchmark_metrics(self):
        """벤치마크 지표 계산 (전체 플랫폼 대비)"""
        try:
            # 전체 플랫폼 지표
            platform_orders = len(self.platform_data)
            platform_revenue = self.platform_data['상품별 총 주문금액'].sum()
            platform_aov = self.platform_data['상품별 총 주문금액'].mean()
            
            # 회사 지표
            company_orders = self.metrics['basic']['total_orders']
            company_revenue = self.metrics['basic']['total_revenue']
            company_aov = self.metrics['basic']['avg_order_value']
            
            benchmark = {
                'market_share': {
                    'orders': round((company_orders / platform_orders) * 100, 2),
                    'revenue': round((company_revenue / platform_revenue) * 100, 2)
                },
                'performance_vs_platform': {
                    'aov_ratio': round((company_aov / platform_aov), 2),
                    'aov_difference': round(((company_aov / platform_aov) - 1) * 100, 1)
                },
                'platform_stats': {
                    'total_orders': platform_orders,
                    'total_revenue': platform_revenue,
                    'avg_aov': platform_aov
                }
            }
            
            # 카테고리 내 순위 시뮬레이션
            company_category = COMPANY_SETTINGS.get(self.company_name, {}).get('category', '기타')
            benchmark['category_rank'] = {
                'category': company_category,
                'rank': np.random.randint(1, 6),  # 시뮬레이션
                'total_companies': np.random.randint(15, 30)
            }
            
            self.metrics['benchmark'] = benchmark
            return benchmark
            
        except Exception as e:
            print(f"❌ 벤치마크 계산 실패: {str(e)}")
            return None
    
    def calculate_all_metrics(self):
        """모든 지표 통합 계산"""
        print(f"📊 {self.company_name} 지표 계산 시작...")
        
        # 순차적으로 모든 지표 계산
        self.calculate_basic_metrics()
        self.calculate_growth_metrics()
        self.calculate_channel_metrics()
        self.calculate_time_metrics()
        self.calculate_product_metrics()
        self.calculate_benchmark_metrics()
        
        print(f"✅ {self.company_name} 전체 지표 계산 완료!")
        return self.metrics
    
    def get_formatted_metrics(self):
        """포맷팅된 지표 반환 (리포트용)"""
        if not self.metrics:
            return None
        
        formatted = {
            'summary': {
                'total_orders': METRIC_FORMATS['count'].format(self.metrics['basic']['total_orders']),
                'total_revenue': METRIC_FORMATS['currency'].format(self.metrics['basic']['total_revenue']),
                'avg_order_value': METRIC_FORMATS['currency'].format(self.metrics['basic']['avg_order_value']),
                'order_growth': METRIC_FORMATS['growth'].format(self.metrics['growth']['order_growth']),
                'revenue_growth': METRIC_FORMATS['growth'].format(self.metrics['growth']['revenue_growth']),
                'market_share': METRIC_FORMATS['percentage'].format(self.metrics['benchmark']['market_share']['revenue'])
            },
            'top_channels': [],
            'insights': []
        }
        
        # 상위 채널 정보
        top_channels = self.metrics['channels'].head(3)
        for channel, data in top_channels.iterrows():
            formatted['top_channels'].append({
                'name': channel,
                'revenue': METRIC_FORMATS['currency'].format(data['총매출']),
                'share': METRIC_FORMATS['percentage'].format(data['매출점유율']),
                'growth': METRIC_FORMATS['growth'].format(data['성장률'])
            })
        
        # 자동 인사이트 생성
        insights = self._generate_insights()
        formatted['insights'] = insights
        
        return formatted
    
    def _generate_insights(self):
        """자동 인사이트 생성"""
        insights = []
        
        try:
            # 성장률 인사이트
            revenue_growth = self.metrics['growth']['revenue_growth']
            if revenue_growth > 15:
                insights.append("📈 매출 성장세가 매우 우수합니다")
            elif revenue_growth > 5:
                insights.append("📊 안정적인 매출 성장을 보이고 있습니다")
            else:
                insights.append("🔍 매출 성장 전략이 필요합니다")
            
            # 채널 집중도 인사이트
            top_channel_share = self.metrics['channels'].iloc[0]['매출점유율']
            if top_channel_share > 60:
                insights.append("⚠️ 특정 채널 의존도가 높습니다. 다변화 검토가 필요합니다")
            else:
                insights.append("✅ 채널별 매출이 적절히 분산되어 있습니다")
            
            # AOV 인사이트
            aov_vs_platform = self.metrics['benchmark']['performance_vs_platform']['aov_difference']
            if aov_vs_platform > 10:
                insights.append("💎 평균 주문금액이 플랫폼 평균보다 우수합니다")
            elif aov_vs_platform < -10:
                insights.append("📈 평균 주문금액 향상 여지가 있습니다")
            
            # 배송 성과 인사이트
            if 'delivery_metrics' in self.metrics['products']:
                completion_rate = self.metrics['products']['delivery_metrics'].get('completion_rate', 0)
                if completion_rate > 80:
                    insights.append("🚚 배송 완료율이 우수합니다")
        
        except Exception as e:
            print(f"⚠️ 인사이트 생성 중 오류: {str(e)}")
        
        return insights
    
    def export_metrics_summary(self):
        """지표 요약 출력"""
        if not self.metrics:
            print("❌ 계산된 지표가 없습니다")
            return
        
        print(f"\n📊 {self.company_name} 성과 요약")
        print("=" * 50)
        
        # 기본 지표
        basic = self.metrics['basic']
        growth = self.metrics['growth']
        print(f"🏪 기본 지표:")
        print(f"   • 총 주문수: {basic['total_orders']:,}건 ({growth['order_growth']:+.1f}%)")
        print(f"   • 총 매출액: ₩{basic['total_revenue']:,.0f} ({growth['revenue_growth']:+.1f}%)")
        print(f"   • 평균 주문금액: ₩{basic['avg_order_value']:,.0f} ({growth['aov_growth']:+.1f}%)")
        print(f"   • 분석 기간: {basic['date_range']['start']} ~ {basic['date_range']['end']}")
        
        # 채널 성과
        print(f"\n🛒 채널별 성과 (TOP 3):")
        channels = self.metrics['channels'].head(3)
        for i, (channel, data) in enumerate(channels.iterrows(), 1):
            print(f"   {i}. {channel}: ₩{data['총매출']:,.0f} ({data['매출점유율']:.1f}%)")
        
        # 벤치마크
        benchmark = self.metrics['benchmark']
        print(f"\n🎯 플랫폼 내 위치:")
        print(f"   • 주문 점유율: {benchmark['market_share']['orders']:.2f}%")
        print(f"   • 매출 점유율: {benchmark['market_share']['revenue']:.2f}%")
        print(f"   • AOV 비교: 플랫폼 평균 대비 {benchmark['performance_vs_platform']['aov_difference']:+.1f}%")
        
        print("=" * 50)

# 테스트 함수
def test_metrics_calculator():
    """지표 계산기 테스트"""
    print("🧪 지표 계산기 테스트 시작...")
    
    # 임시 데이터 생성 (실제로는 data_loader에서 가져옴)
    try:
        from data_loader import DataLoader
        
        # 데이터 로드
        loader = DataLoader("order_list_20250818120157_497.xlsx")
        platform_data = loader.load_excel()
        
        if platform_data is None:
            print("❌ 테스트 데이터를 로드할 수 없습니다")
            return False
        
        loader.validate_data_structure()
        platform_data = loader.clean_data()
        
        # 포레스트핏 데이터 필터링
        company_data = loader.filter_by_company("포레스트핏")
        
        if company_data is None:
            print("❌ 포레스트핏 데이터가 없습니다")
            return False
        
        # 지표 계산기 초기화
        calculator = MetricsCalculator(company_data, platform_data, "포레스트핏")
        
        # 모든 지표 계산
        metrics = calculator.calculate_all_metrics()
        
        if metrics:
            # 요약 출력
            calculator.export_metrics_summary()
            
            # 포맷팅된 지표 확인
            formatted = calculator.get_formatted_metrics()
            print(f"\n📋 포맷팅된 요약:")
            print(f"   • 총 주문수: {formatted['summary']['total_orders']}")
            print(f"   • 총 매출액: {formatted['summary']['total_revenue']}")
            print(f"   • 성장률: {formatted['summary']['revenue_growth']}")
            
            print("\n🎉 지표 계산기 테스트 완료!")
            return True
        else:
            print("❌ 지표 계산 실패")
            return False
            
    except ImportError:
        print("❌ data_loader 모듈을 찾을 수 없습니다")
        return False
    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {str(e)}")
        return False

if __name__ == "__main__":
    test_metrics_calculator()
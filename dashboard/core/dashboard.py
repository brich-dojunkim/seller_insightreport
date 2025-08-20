"""셀러 성과 대시보드 메인 클래스"""

from config import CONFIG
from file_manager import load_excel_data
from data_processing import prepare_dataframe, slice_by_seller, calculate_comprehensive_kpis
from analyzers.basic_info_analyzer import BasicInfoAnalyzer
from analyzers.sales_analyzer import SalesAnalyzer
from analyzers.customer_analyzer import CustomerAnalyzer
from analyzers.operations_analyzer import OperationsAnalyzer
from analyzers.benchmarking_analyzer import BenchmarkingAnalyzer
from analyzers.trends_analyzer import TrendsAnalyzer
from exporters.excel_exporter import ExcelExporter

class SellerDashboard:
    """셀러 성과 대시보드"""
    
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
        
        # 분석기 인스턴스 생성
        analyzers = {
            'basic_info': BasicInfoAnalyzer(self.seller_data, self.overall_data, self.seller_name),
            'sales': SalesAnalyzer(self.seller_data, self.overall_data, self.seller_name),
            'customers': CustomerAnalyzer(self.seller_data, self.overall_data, self.seller_name),
            'operations': OperationsAnalyzer(self.seller_data, self.overall_data, self.seller_name),
            'benchmarking': BenchmarkingAnalyzer(self.seller_data, self.overall_data, self.seller_name, self.kpis),
            'trends': TrendsAnalyzer(self.seller_data, self.overall_data, self.seller_name)
        }
        
        # 각 분석 실행
        for key, analyzer in analyzers.items():
            self.analysis_data[key] = analyzer.analyze()
        
        print(f"✅ {self.seller_name} 분석 완료 - {len(self.analysis_data)}개 영역")
    
    def export_to_excel(self, output_path: str = None):
        """엑셀 파일로 출력"""
        exporter = ExcelExporter(self.seller_name, self.analysis_data, self.kpis)
        return exporter.export(output_path)
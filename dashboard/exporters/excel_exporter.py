"""엑셀 출력기"""

import pandas as pd
from datetime import datetime
from pathlib import Path
from .base_exporter import BaseExporter
from .writers import (
    DashboardWriter, SalesWriter, CustomerWriter,
    OperationsWriter, BenchmarkingWriter, TrendsWriter
)
from utils import sanitize_filename

class ExcelExporter(BaseExporter):
    """엑셀 출력기"""
    
    def export(self, output_path: str = None) -> str:
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
                dashboard_writer = DashboardWriter(self.analysis_data, self.kpis)
                dashboard_writer.write(writer)
                
                # 2. 매출 분석
                sales_writer = SalesWriter(self.analysis_data['sales'])
                sales_writer.write(writer)
                
                # 3. 고객 분석  
                customer_writer = CustomerWriter(self.analysis_data['customers'])
                customer_writer.write(writer)
                
                # 4. 운영 분석
                operations_writer = OperationsWriter(self.analysis_data['operations'])
                operations_writer.write(writer)
                
                # 5. 벤치마킹
                benchmarking_writer = BenchmarkingWriter(self.analysis_data['benchmarking'])
                benchmarking_writer.write(writer)
                
                # 6. 트렌드 분석
                trends_writer = TrendsWriter(self.analysis_data['trends'])
                trends_writer.write(writer)
            
            print(f"✅ 엑셀 리포트 생성 완료: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ 엑셀 출력 실패: {e}")
            return None
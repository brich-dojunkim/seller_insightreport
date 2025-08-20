"""익스포터 베이스 클래스"""

from abc import ABC, abstractmethod

class BaseExporter(ABC):
    """익스포터 베이스 클래스"""
    
    def __init__(self, seller_name: str, analysis_data: dict, kpis: dict):
        self.seller_name = seller_name
        self.analysis_data = analysis_data
        self.kpis = kpis
    
    @abstractmethod
    def export(self, output_path: str = None) -> str:
        """출력 실행 - 하위 클래스에서 구현"""
        pass
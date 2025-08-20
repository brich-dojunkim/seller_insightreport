"""분석기 베이스 클래스"""

from abc import ABC, abstractmethod
import pandas as pd

class BaseAnalyzer(ABC):
    """분석기 베이스 클래스"""
    
    def __init__(self, seller_data: pd.DataFrame, overall_data: pd.DataFrame, seller_name: str):
        self.seller_data = seller_data
        self.overall_data = overall_data
        self.seller_name = seller_name
    
    @abstractmethod
    def analyze(self) -> dict:
        """분석 실행 - 하위 클래스에서 구현"""
        pass
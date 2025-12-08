# core/base_analyzer.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class AnalysisResult:
    """Base class untuk hasil analisis"""
    stock_code: str
    timestamp: str
    data: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        return {
            'stock_code': self.stock_code,
            'timestamp': self.timestamp,
            'data': self.data
        }

class BaseAnalyzer(ABC):
    """Abstract base class untuk semua analyzer"""
    
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    @abstractmethod
    def analyze(self, stock_code: str) -> AnalysisResult:
        pass
    
    def validate_input(self, stock_code: str) -> bool:
        """Validasi input sebelum analisis"""
        return bool(stock_code and isinstance(stock_code, str))

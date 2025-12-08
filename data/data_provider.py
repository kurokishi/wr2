# data/data_provider.py
from abc import ABC, abstractmethod
import pandas as pd

class DataProvider(ABC):
    """Interface untuk semua data provider"""
    
    @abstractmethod
    def get_historical_data(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        pass
    
    @abstractmethod
    def get_stock_info(self, ticker: str) -> Dict:
        pass
    
    @abstractmethod
    def get_dividend_data(self, ticker: str) -> Dict:
        pass

# data/yahoo_finance.py
class YahooFinanceProvider(DataProvider):
    """Implementasi Yahoo Finance"""
    
    def __init__(self):
        import yfinance as yf
        self.yf = yf
    
    def get_historical_data(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        # Implementasi dengan yfinance
        pass
    
    def get_stock_info(self, ticker: str) -> Dict:
        # Implementasi dengan yfinance
        pass

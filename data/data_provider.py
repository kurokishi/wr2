# data/data_provider.py
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Optional, Any, Union

class DataProvider(ABC):
    """Interface for all data providers"""
    
    @abstractmethod
    def get_historical_data(self, ticker: str, period: str = "2y") -> pd.DataFrame:
        """Get historical price data"""
        pass
    
    @abstractmethod
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Get stock information"""
        pass
    
    @abstractmethod
    def get_dividend_data(self, ticker: str) -> Dict[str, Any]:
        """Get dividend information"""
        pass
    
    @abstractmethod
    def get_current_price(self, ticker: str) -> float:
        """Get current stock price"""
        pass
    
    @abstractmethod
    def get_stock_metadata(self, ticker: str) -> Dict[str, Any]:
        """Get stock metadata (name, sector, etc.)"""
        pass
    
    @abstractmethod
    def get_fundamental_data(self, ticker: str) -> Dict[str, Any]:
        """Get fundamental data"""
        pass

# main.py
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import Config
from data.yahoo_finance import YahooFinanceProvider
from analysis.fundamental import FundamentalAnalyzer
from analysis.technical import TechnicalAnalyzer
from analysis.dividend import DividendAnalyzer
from utils.formatter import Formatter

class WarrenAI:
    """Main Warren AI application"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.formatter = Formatter()
        
        # Initialize data provider
        self.data_provider = YahooFinanceProvider(self.config)
        
        # Initialize analyzers
        self.fundamental_analyzer = FundamentalAnalyzer(self.data_provider)
        self.technical_analyzer = TechnicalAnalyzer(
            self.data_provider, 
            {
                'rsi_period': self.config.rsi_period,
                'moving_averages': self.config.moving_averages,
                'default_period': self.config.default_period

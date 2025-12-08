# data/yahoo_finance.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union
import warnings
from .data_provider import DataProvider

warnings.filterwarnings('ignore')

class YahooFinanceProvider(DataProvider):
    """Data provider using Yahoo Finance API"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def _get_ticker_object(self, ticker: str):
        """Get ticker object with proper suffix handling"""
        # For Indonesian stocks
        if not ticker.endswith('.JK'):
            ticker = f"{ticker}.JK"
        
        return yf.Ticker(ticker)
    
    def get_stock_metadata(self, ticker: str) -> Dict[str, Any]:
        """Get stock metadata"""
        try:
            stock = self._get_ticker_object(ticker)
            info = stock.info
            
            return {
                'code': ticker.replace('.JK', ''),
                'name': info.get('longName', info.get('shortName', ticker)),
                'exchange': info.get('exchange', 'JK'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'country': info.get('country', 'Indonesia')
            }
        except Exception as e:
            return {
                'code': ticker,
                'name': ticker,
                'exchange': 'N/A',
                'sector': 'N/A',
                'industry': 'N/A',
                'country': 'Indonesia'
            }
    
    def get_historical_data(self, ticker: str, period: str = "1y") -> pd.DataFrame:
        """Get historical price data"""
        try:
            stock = self._get_ticker_object(ticker)
            df = stock.history(period=period)
            
            if df.empty:
                # Try without .JK for international stocks
                stock = yf.Ticker(ticker)
                df = stock.history(period=period)
            
            return df
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")
    
    def get_stock_info(self, ticker: str) -> Dict[str, Any]:
        """Get stock information"""
        try:
            stock = self._get_ticker_object(ticker)
            return stock.info
        except:
            return {}
    
    def get_fundamental_data(self, ticker: str) -> Dict[str, Any]:
        """Get fundamental data"""
        info = self.get_stock_info(ticker)
        
        return {
            'pe_ratio': info.get('trailingPE', info.get('forwardPE')),
            'pb_ratio': info.get('priceToBook'),
            'roe': info.get('returnOnEquity'),
            'debt_to_equity': info.get('debtToEquity'),
            'profit_margin': info.get('profitMargins'),
            'revenue_growth': info.get('revenueGrowth'),
            'earnings_growth': info.get('earningsGrowth'),
            'market_cap': info.get('marketCap'),
            'current_ratio': info.get('currentRatio'),
            'quick_ratio': info.get('quickRatio'),
            'gross_margin': info.get('grossMargins'),
            'operating_margin': info.get('operatingMargins')
        }
    
    def get_dividend_data(self, ticker: str) -> Dict[str, Any]:
        """Get dividend information"""
        try:
            stock = self._get_ticker_object(ticker)
            info = stock.info
            
            return {
                'dividend_yield': info.get('dividendYield', 0),
                'five_year_avg_yield': info.get('fiveYearAvgDividendYield', 0),
                'payout_ratio': info.get('payoutRatio'),
                'dividend_rate': info.get('dividendRate')
            }
        except:
            return {
                'dividend_yield': 0,
                'five_year_avg_yield': 0,
                'payout_ratio': None,
                'dividend_rate': 0
            }
    
    def get_current_price(self, ticker: str) -> float:
        """Get current price"""
        try:
            stock = self._get_ticker_object(ticker)
            info = stock.info
            
            # Try different price fields
            current_price = info.get('currentPrice', 
                                   info.get('regularMarketPrice',
                                           info.get('previousClose')))
            
            if not current_price:
                hist = stock.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
            
            return float(current_price) if current_price else 0.0
        except:
            return 0.0
    
    def get_batch_data(self, tickers: List[str]) -> Dict[str, Dict[str, Any]]:
        """Get data for multiple tickers at once"""
        results = {}
        for ticker in tickers:
            try:
                results[ticker] = {
                    'metadata': self.get_stock_metadata(ticker),
                    'current_price': self.get_current_price(ticker),
                    'fundamental': self.get_fundamental_data(ticker)
                }
            except Exception as e:
                print(f"Error fetching data for {ticker}: {str(e)}")
                continue
        
        return results

# data/yahoo_finance.py
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import warnings
from .data_provider import DataProvider
from models.stock import StockMetadata, PriceData, FundamentalMetrics, DividendInfo

warnings.filterwarnings('ignore')

class YahooFinanceProvider(DataProvider):
    """Data provider menggunakan Yahoo Finance API"""
    
    def __init__(self, config=None):
        self.config = config
    
    def _get_ticker_object(self, ticker: str):
        """Get ticker object with proper suffix handling"""
        # Untuk saham Indonesia
        if not ticker.endswith('.JK'):
            ticker = f"{ticker}.JK"
        
        return yf.Ticker(ticker)
    
    def get_stock_metadata(self, ticker: str) -> StockMetadata:
        """Get stock metadata"""
        stock = self._get_ticker_object(ticker)
        info = stock.info
        
        return StockMetadata(
            code=ticker.replace('.JK', ''),
            name=info.get('longName', info.get('shortName', ticker)),
            exchange=info.get('exchange', 'JK'),
            sector=info.get('sector', None),
            industry=info.get('industry', None),
            country=info.get('country', 'Indonesia')
        )
    
    def get_historical_data(self, ticker: str, period: str = "2y") -> List[PriceData]:
        """Get historical price data"""
        stock = self._get_ticker_object(ticker)
        
        try:
            df = stock.history(period=period)
            if df.empty:
                # Try without .JK for international stocks
                stock = yf.Ticker(ticker)
                df = stock.history(period=period)
        except Exception as e:
            raise ValueError(f"Failed to fetch data for {ticker}: {str(e)}")
        
        price_data = []
        for idx, row in df.iterrows():
            price_data.append(PriceData(
                date=idx.to_pydatetime(),
                open=row['Open'],
                high=row['High'],
                low=row['Low'],
                close=row['Close'],
                volume=row['Volume'],
                adj_close=row.get('Close', None)
            ))
        
        return price_data
    
    def get_fundamental_data(self, ticker: str) -> FundamentalMetrics:
        """Get fundamental data"""
        stock = self._get_ticker_object(ticker)
        info = stock.info
        
        # Get financial statements
        try:
            balance_sheet = stock.balance_sheet
            income_stmt = stock.income_stmt
            cash_flow = stock.cash_flow
        except:
            balance_sheet = pd.DataFrame()
            income_stmt = pd.DataFrame()
            cash_flow = pd.DataFrame()
        
        # Calculate additional metrics if available
        total_equity = None
        total_assets = None
        total_debt = None
        
        if not balance_sheet.empty:
            # Get latest balance sheet
            latest_bs = balance_sheet.iloc[:, 0]
            total_equity = latest_bs.get('Total Stockholder Equity')
            total_assets = latest_bs.get('Total Assets')
            total_debt = latest_bs.get('Total Debt', latest_bs.get('Long Term Debt'))
        
        net_income = None
        revenue = None
        if not income_stmt.empty:
            latest_is = income_stmt.iloc[:, 0]
            net_income = latest_is.get('Net Income')
            revenue = latest_is.get('Total Revenue')
        
        # Calculate ROE and ROA
        roe = None
        roa = None
        if net_income and total_equity:
            roe = net_income / total_equity
        if net_income and total_assets:
            roa = net_income / total_assets
        
        # Calculate debt to equity
        debt_to_equity = None
        if total_debt and total_equity:
            debt_to_equity = total_debt / total_equity
        
        return FundamentalMetrics(
            pe_ratio=info.get('trailingPE', info.get('forwardPE')),
            pb_ratio=info.get('priceToBook'),
            ps_ratio=info.get('priceToSalesTrailing12Months'),
            ev_to_ebitda=info.get('enterpriseToEbitda'),
            roe=info.get('returnOnEquity', roe),
            roa=roa,
            gross_margin=info.get('grossMargins'),
            operating_margin=info.get('operatingMargins'),
            net_margin=info.get('profitMargins'),
            revenue_growth_yoy=info.get('revenueGrowth'),
            earnings_growth_yoy=info.get('earningsGrowth'),
            debt_to_equity=info.get('debtToEquity', debt_to_equity),
            current_ratio=info.get('currentRatio'),
            market_cap=info.get('marketCap'),
            enterprise_value=info.get('enterpriseValue')
        )
    
    def get_dividend_data(self, ticker: str) -> DividendInfo:
        """Get dividend information"""
        stock = self._get_ticker_object(ticker)
        info = stock.info
        
        # Get dividend history
        try:
            dividends = stock.dividends
            if not dividends.empty:
                latest_dividend = dividends.iloc[-1]
                ex_dividend_date = dividends.index[-1].to_pydatetime()
            else:
                latest_dividend = 0
                ex_dividend_date = None
        except:
            latest_dividend = 0
            ex_dividend_date = None
        
        return DividendInfo(
            dividend_yield=info.get('dividendYield'),
            dividend_per_share=info.get('dividendRate', latest_dividend),
            payout_ratio=info.get('payoutRatio'),
            ex_dividend_date=ex_dividend_date,
            five_year_avg_yield=info.get('fiveYearAvgDividendYield')
        )
    
    def get_current_price(self, ticker: str) -> float:
        """Get current price"""
        stock = self._get_ticker_object(ticker)
        
        try:
            # Try to get current price
            info = stock.info
            current_price = info.get('currentPrice', 
                                   info.get('regularMarketPrice',
                                           info.get('previousClose')))
            
            # Fallback: use last close from history
            if not current_price:
                hist = stock.history(period="1d")
                current_price = hist['Close'].iloc[-1] if not hist.empty else 0
        except:
            current_price = 0
        
        return current_price
    
    def get_batch_data(self, tickers: List[str]) -> Dict[str, Dict]:
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

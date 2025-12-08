# utils/formatter.py
from typing import Union, Optional
import locale
from datetime import datetime

class Formatter:
    """Formatting utilities"""
    
    def __init__(self, currency: str = "IDR", locale_str: str = "id_ID"):
        self.currency = currency
        
        try:
            locale.setlocale(locale.LC_ALL, locale_str)
        except:
            locale.setlocale(locale.LC_ALL, '')
    
    def format_currency(self, value: float, decimals: int = 0) -> str:
        """Format currency value"""
        if value is None:
            return "N/A"
        
        if value == 0:
            return "Rp 0"
        
        if self.currency == "IDR":
            return self._format_idr(value, decimals)
        else:
            return locale.currency(value, grouping=True)
    
    def _format_idr(self, value: float, decimals: int = 0) -> str:
        """Format Indonesian Rupiah"""
        try:
            if value >= 1e12:
                return f"Rp {value/1e12:.{decimals}f} T"
            elif value >= 1e9:
                return f"Rp {value/1e9:.{decimals}f} M"
            elif value >= 1e6:
                return f"Rp {value/1e6:.{decimals}f} Jt"
            elif value >= 1e3:
                return f"Rp {value/1e3:.{decimals}f} Rb"
            else:
                return f"Rp {value:,.{decimals}f}"
        except:
            return f"Rp {value:,.{decimals}f}"
    
    def format_percentage(self, value: float, decimals: int = 2) -> str:
        """Format percentage"""
        if value is None:
            return "N/A"
        
        try:
            return f"{value*100:.{decimals}f}%"
        except:
            return "N/A"
    
    def format_number(self, value: float, decimals: int = 2) -> str:
        """Format number"""
        if value is None:
            return "N/A"
        
        try:
            return f"{value:,.{decimals}f}"
        except:
            return "N/A"
    
    def format_date(self, date_str: str) -> str:
        """Format date string"""
        try:
            if not date_str:
                return "N/A"
            
            if isinstance(date_str, str):
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                return date_obj.strftime("%d %b %Y %H:%M")
            else:
                return str(date_str)
        except:
            return date_str
    
    def format_trend(self, trend: str) -> str:
        """Format trend with emoji"""
        trend_map = {
            'strong_bullish': '🟢🟢 BULLISH KUAT',
            'bullish': '🟢 BULLISH',
            'sideways': '⚪ SIDEWAYS',
            'bearish': '🔴 BEARISH',
            'strong_bearish': '🔴🔴 BEARISH KUAT'
        }
        return trend_map.get(trend, trend)
    
    def format_recommendation(self, recommendation: str) -> str:
        """Format recommendation with emoji"""
        rec_map = {
            'strong_buy': '🎯 STRONG BUY',
            'buy': '✅ BUY',
            'hold': '⏸️ HOLD',
            'sell': '🔻 SELL',
            'strong_sell': '❌ STRONG SELL'
        }
        return rec_map.get(recommendation, recommendation)

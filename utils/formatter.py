# utils/formatter.py
from typing import Union, Optional
import locale
from datetime import datetime

class Formatter:
    """Utility class for formatting data"""
    
    def __init__(self, currency: str = "IDR", locale_str: str = "id_ID"):
        self.currency = currency
        self.locale_str = locale_str
        
        try:
            locale.setlocale(locale.LC_ALL, locale_str)
        except locale.Error:
            # Fallback to default
            locale.setlocale(locale.LC_ALL, '')
    
    def format_currency(self, value: float, decimals: int = 0) -> str:
        """Format currency value"""
        if value is None:
            return "N/A"
        
        if self.currency == "IDR":
            return self._format_idr(value, decimals)
        else:
            return locale.currency(value, grouping=True)
    
    def _format_idr(self, value: float, decimals: int = 0) -> str:
        """Format Indonesian Rupiah"""
        if value >= 1e12:  # Trillion
            formatted = f"Rp {value/1e12:,.{decimals}f} T"
        elif value >= 1e9:  # Billion (Miliar)
            formatted = f"Rp {value/1e9:,.{decimals}f} M"
        elif value >= 1e6:  # Million (Juta)
            formatted = f"Rp {value/1e6:,.{decimals}f} Jt"
        elif value >= 1e3:  # Thousand (Ribu)
            formatted = f"Rp {value/1e3:,.{decimals}f} Rb"
        else:
            formatted = f"Rp {value:,.{decimals}f}"
        
        return formatted
    
    def format_percentage(self, value: float, decimals: int = 2) -> str:
        """Format percentage value"""
        if value is None:
            return "N/A"
        
        return f"{value*100:.{decimals}f}%"
    
    def format_number(self, value: float, decimals: int = 2) -> str:
        """Format general number"""
        if value is None:
            return "N/A"
        
        return f"{value:,.{decimals}f}"
    
    def format_date(self, date: datetime, format_str: str = "%d %b %Y") -> str:
        """Format date"""
        if date is None:
            return "N/A"
        
        return date.strftime(format_str)
    
    def format_score(self, score: float, max_score: float = 10) -> str:
        """Format score with emoji"""
        if score >= 9:
            return f"🎯 {score:.1f}/{max_score} (Excellent)"
        elif score >= 7:
            return f"✅ {score:.1f}/{max_score} (Good)"
        elif score >= 5:
            return f"⚠️ {score:.1f}/{max_score} (Fair)"
        else:
            return f"❌ {score:.1f}/{max_score} (Poor)"
    
    def format_trend(self, trend: str) -> str:
        """Format trend with emoji"""
        trend_map = {
            'strong_bullish': '🟢🟢 BULLISH KUAT',
            'bullish': '🟢 BULLISH',
            'sideways': '⚪ SIDEWAYS',
            'bearish': '🔴 BEARISH',
            'strong_bearish': '🔴🔴 BEARISH KUAT'
        }
        return trend_map.get(trend.lower(), trend)
    
    def format_recommendation(self, recommendation: str) -> str:
        """Format recommendation with emoji"""
        rec_map = {
            'strong_buy': '🎯 STRONG BUY',
            'buy': '✅ BUY',
            'hold': '⏸️ HOLD',
            'sell': '🔻 SELL',
            'strong_sell': '❌ STRONG SELL'
        }
        return rec_map.get(recommendation.lower(), recommendation)

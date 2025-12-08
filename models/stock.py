# models/stock.py
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TrendDirection(Enum):
    """Arah trend saham"""
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    SIDEWAYS = "sideways"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"

class RSISignal(Enum):
    """Signal RSI"""
    OVERSOLD = "oversold"
    NEUTRAL = "neutral"
    OVERBOUGHT = "overbought"

class Recommendation(Enum):
    """Rekomendasi investasi"""
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class StockMetadata:
    """Metadata dasar saham"""
    code: str
    name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: str = "Indonesia"
    
    def to_dict(self):
        return asdict(self)

@dataclass
class PriceData:
    """Data harga dan volume"""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    adj_close: Optional[float] = None
    
    def to_dict(self):
        data = asdict(self)
        data['date'] = self.date.isoformat()
        return data

@dataclass
class FundamentalMetrics:
    """Metrik fundamental saham"""
    # Valuation
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ps_ratio: Optional[float] = None
    ev_to_ebitda: Optional[float] = None
    
    # Profitability
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    
    # Growth
    revenue_growth_yoy: Optional[float] = None
    earnings_growth_yoy: Optional[float] = None
    eps_growth: Optional[float] = None
    
    # Financial Health
    debt_to_equity: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    
    # Size
    market_cap: Optional[float] = None
    enterprise_value: Optional[float] = None
    
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class TechnicalIndicators:
    """Indikator teknikal"""
    # Moving Averages
    ma_20: Optional[float] = None
    ma_50: Optional[float] = None
    ma_200: Optional[float] = None
    
    # Oscillators
    rsi: Optional[float] = None
    rsi_signal: Optional[RSISignal] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
    
    # Bollinger Bands
    bb_upper: Optional[float] = None
    bb_middle: Optional[float] = None
    bb_lower: Optional[float] = None
    bb_width: Optional[float] = None
    
    # Support & Resistance
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    
    # Volume
    volume_avg_20: Optional[float] = None
    volume_ratio: Optional[float] = None
    
    # Trend
    trend_direction: Optional[TrendDirection] = None
    trend_strength: Optional[float] = None  # 0-100
    
    def to_dict(self):
        data = asdict(self)
        # Convert enums to strings
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class DividendInfo:
    """Informasi dividen"""
    dividend_yield: Optional[float] = None
    dividend_per_share: Optional[float] = None
    payout_ratio: Optional[float] = None
    ex_dividend_date: Optional[datetime] = None
    payment_date: Optional[datetime] = None
    five_year_avg_yield: Optional[float] = None
    dividend_growth_5y: Optional[float] = None
    
    def to_dict(self):
        data = asdict(self)
        # Convert dates to strings
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class AnalysisResult:
    """Hasil analisis lengkap"""
    stock_metadata: StockMetadata
    fundamental: FundamentalMetrics
    technical: TechnicalIndicators
    dividend: DividendInfo
    current_price: float
    analysis_date: datetime
    recommendation: Optional[Recommendation] = None
    confidence_score: Optional[float] = None  # 0-100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'stock': self.stock_metadata.to_dict(),
            'fundamental': self.fundamental.to_dict(),
            'technical': self.technical.to_dict(),
            'dividend': self.dividend.to_dict(),
            'current_price': self.current_price,
            'analysis_date': self.analysis_date.isoformat(),
            'recommendation': self.recommendation.value if self.recommendation else None,
            'confidence_score': self.confidence_score
        }

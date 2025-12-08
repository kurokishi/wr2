# models/stock.py
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class TrendDirection(Enum):
    STRONG_BULLISH = "strong_bullish"
    BULLISH = "bullish"
    SIDEWAYS = "sideways"
    BEARISH = "bearish"
    STRONG_BEARISH = "strong_bearish"

class RSISignal(Enum):
    OVERSOLD = "oversold"
    NEUTRAL = "neutral"
    OVERBOUGHT = "overbought"

class Recommendation(Enum):
    STRONG_BUY = "strong_buy"
    BUY = "buy"
    HOLD = "hold"
    SELL = "sell"
    STRONG_SELL = "strong_sell"

@dataclass
class StockMetadata:
    """Stock metadata"""
    code: str
    name: str
    exchange: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    country: str = "Indonesia"
    
    def to_dict(self):
        return asdict(self)

@dataclass
class FundamentalMetrics:
    """Fundamental metrics"""
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    roe: Optional[float] = None
    debt_to_equity: Optional[float] = None
    profit_margin: Optional[float] = None
    revenue_growth: Optional[float] = None
    earnings_growth: Optional[float] = None
    market_cap: Optional[float] = None
    current_ratio: Optional[float] = None
    quick_ratio: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class TechnicalIndicators:
    """Technical indicators"""
    ma_20: Optional[float] = None
    ma_50: Optional[float] = None
    ma_200: Optional[float] = None
    rsi: Optional[float] = None
    rsi_signal: Optional[RSISignal] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    support_level: Optional[float] = None
    resistance_level: Optional[float] = None
    trend_direction: Optional[TrendDirection] = None
    trend_strength: Optional[float] = None
    
    def to_dict(self):
        data = asdict(self)
        # Convert enums to strings
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return {k: v for k, v in data.items() if v is not None}

@dataclass
class DividendInfo:
    """Dividend information"""
    dividend_yield: Optional[float] = None
    five_year_avg_yield: Optional[float] = None
    payout_ratio: Optional[float] = None
    dividend_rate: Optional[float] = None
    
    def to_dict(self):
        return {k: v for k, v in asdict(self).items() if v is not None}

@dataclass
class AnalysisResult:
    """Complete analysis result"""
    metadata: StockMetadata
    fundamental: FundamentalMetrics
    technical: TechnicalIndicators
    dividend: DividendInfo
    current_price: float
    analysis_date: datetime
    recommendation: Optional[Recommendation] = None
    confidence_score: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'metadata': self.metadata.to_dict(),
            'fundamental': self.fundamental.to_dict(),
            'technical': self.technical.to_dict(),
            'dividend': self.dividend.to_dict(),
            'current_price': self.current_price,
            'analysis_date': self.analysis_date.isoformat(),
            'recommendation': self.recommendation.value if self.recommendation else None,
            'confidence_score': self.confidence_score
        }

# models/stock.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class StockFundamental:
    """Model untuk data fundamental saham"""
    code: str
    current_price: float
    pe_ratio: Optional[float]
    pb_ratio: Optional[float]
    roe: Optional[float]
    debt_to_equity: Optional[float]
    market_cap: Optional[float]
    
    def to_dict(self):
        return {
            'code': self.code,
            'current_price': self.current_price,
            'pe_ratio': self.pe_ratio,
            # ... lainnya
        }

@dataclass
class TechnicalIndicators:
    """Model untuk indikator teknikal"""
    ma20: float
    ma50: float
    ma200: float
    rsi: float
    macd: float
    # ... lainnya

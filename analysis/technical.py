# analysis/technical.py
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.base_analyzer import BaseAnalyzer, AnalysisResult
from models.stock import (
    TechnicalIndicators, PriceData, TrendDirection, RSISignal
)
from data.data_provider import DataProvider

class TechnicalAnalyzer(BaseAnalyzer):
    """Analisis teknikal dengan multiple indikator"""
    
    def __init__(self, data_provider: DataProvider, config=None):
        super().__init__(data_provider)
        self.config = config or {}
        self.rsi_period = self.config.get('rsi_period', 14)
        self.moving_averages = self.config.get('moving_averages', [20, 50, 200])
    
    def analyze(self, ticker: str) -> AnalysisResult:
        """Perform comprehensive technical analysis"""
        
        # Get historical data
        price_data = self.data_provider.get_historical_data(
            ticker, 
            self.config.get('default_period', '2y')
        )
        
        if not price_data:
            raise ValueError(f"No price data available for {ticker}")
        
        # Convert to pandas DataFrame for calculations
        df = self._prepare_dataframe(price_data)
        
        # Calculate all indicators
        indicators = self._calculate_all_indicators(df)
        
        return AnalysisResult(
            stock_code=ticker,
            timestamp=datetime.now().isoformat(),
            data={
                'technical': indicators.to_dict(),
                'latest_price': df['close'].iloc[-1],
                'indicators_calculated': True
            }
        )
    
    def _prepare_dataframe(self, price_data: List[PriceData]) -> pd.DataFrame:
        """Convert price data to DataFrame"""
        data = []
        for p in price_data:
            data.append({
                'date': p.date,
                'open': p.open,
                'high': p.high,
                'low': p.low,
                'close': p.close,
                'volume': p.volume
            })
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        return df
    
    def _calculate_all_indicators(self, df: pd.DataFrame) -> TechnicalIndicators:
        """Calculate all technical indicators"""
        
        # Calculate Moving Averages
        ma_values = {}
        for period in self.moving_averages:
            ma_values[f'ma_{period}'] = self._calculate_ma(df['close'], period)
        
        # Calculate RSI
        rsi, rsi_signal = self._calculate_rsi(df['close'])
        
        # Calculate MACD
        macd, macd_signal, macd_hist = self._calculate_macd(df['close'])
        
        # Calculate Bollinger Bands
        bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(df['close'])
        
        # Calculate Support and Resistance
        support, resistance = self._calculate_support_resistance(df)
        
        # Calculate Volume indicators
        volume_avg = self._calculate_volume_indicators(df['volume'])
        
        # Determine Trend
        trend_direction, trend_strength = self._determine_trend(df['close'], ma_values)
        
        return TechnicalIndicators(
            ma_20=ma_values.get('ma_20'),
            ma_50=ma_values.get('ma_50'),
            ma_200=ma_values.get('ma_200'),
            rsi=rsi,
            rsi_signal=rsi_signal,
            macd=macd,
            macd_signal=macd_signal,
            macd_histogram=macd_hist,
            bb_upper=bb_upper,
            bb_middle=bb_middle,
            bb_lower=bb_lower,
            bb_width=(bb_upper - bb_lower) / bb_middle if bb_middle else None,
            support_level=support,
            resistance_level=resistance,
            volume_avg_20=volume_avg,
            volume_ratio=df['volume'].iloc[-1] / volume_avg if volume_avg else None,
            trend_direction=trend_direction,
            trend_strength=trend_strength
        )
    
    def _calculate_ma(self, series: pd.Series, period: int) -> Optional[float]:
        """Calculate Moving Average"""
        if len(series) >= period:
            return series.rolling(window=period).mean().iloc[-1]
        return None
    
    def _calculate_rsi(self, series: pd.Series) -> tuple:
        """Calculate RSI"""
        if len(series) < self.rsi_period + 1:
            return None, None
        
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        # Determine RSI signal
        if current_rsi < 30:
            rsi_signal = RSISignal.OVERSOLD
        elif current_rsi > 70:
            rsi_signal = RSISignal.OVERBOUGHT
        else:
            rsi_signal = RSISignal.NEUTRAL
        
        return float(current_rsi), rsi_signal
    
    def _calculate_macd(self, series: pd.Series) -> tuple:
        """Calculate MACD"""
        if len(series) < 26:
            return None, None, None
        
        exp12 = series.ewm(span=12, adjust=False).mean()
        exp26 = series.ewm(span=26, adjust=False).mean()
        macd_line = exp12 - exp26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return (
            float(macd_line.iloc[-1]),
            float(signal_line.iloc[-1]),
            float(histogram.iloc[-1])
        )
    
    def _calculate_bollinger_bands(self, series: pd.Series, period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands"""
        if len(series) < period:
            return None, None, None
        
        middle = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return (
            float(upper.iloc[-1]),
            float(middle.iloc[-1]),
            float(lower.iloc[-1])
        )
    
    def _calculate_support_resistance(self, df: pd.DataFrame, lookback: int = 50) -> tuple:
        """Calculate support and resistance levels"""
        if len(df) < lookback:
            recent_data = df['close']
        else:
            recent_data = df['close'].tail(lookback)
        
        support = recent_data.min()
        resistance = recent_data.max()
        
        return float(support), float(resistance)
    
    def _calculate_volume_indicators(self, volume: pd.Series) -> Optional[float]:
        """Calculate volume indicators"""
        if len(volume) >= 20:
            return volume.rolling(window=20).mean().iloc[-1]
        return None
    
    def _determine_trend(self, prices: pd.Series, ma_values: dict) -> tuple:
        """Determine trend direction and strength"""
        
        # Get MA values
        ma20 = ma_values.get('ma_20')
        ma50 = ma_values.get('ma_50')
        ma200 = ma_values.get('ma_200')
        current_price = prices.iloc[-1]
        
        if not all([ma20, ma50, ma200]):
            return None, None
        
        # Check if MAs are aligned
        ma_aligned_up = ma20 > ma50 > ma200
        ma_aligned_down = ma20 < ma50 < ma200
        
        # Price relative to MAs
        price_above_all = current_price > ma20 > ma50 > ma200
        price_below_all = current_price < ma20 < ma50 < ma200
        
        # Determine trend direction
        if price_above_all and ma_aligned_up:
            trend_direction = TrendDirection.STRONG_BULLISH
            trend_strength = 90
        elif ma_aligned_up:
            trend_direction = TrendDirection.BULLISH
            trend_strength = 70
        elif price_below_all and ma_aligned_down:
            trend_direction = TrendDirection.STRONG_BEARISH
            trend_strength = 90
        elif ma_aligned_down:
            trend_direction = TrendDirection.BEARISH
            trend_strength = 70
        else:
            trend_direction = TrendDirection.SIDEWAYS
            trend_strength = 50
        
        return trend_direction, trend_strength
    
    def generate_signals(self, technical: TechnicalIndicators) -> List[Dict[str, Any]]:
        """Generate trading signals from technical indicators"""
        signals = []
        
        # RSI Signals
        if technical.rsi_signal == RSISignal.OVERSOLD:
            signals.append({
                'type': 'BUY',
                'indicator': 'RSI',
                'strength': 'MEDIUM',
                'message': 'RSI menunjukkan kondisi oversold, potential reversal'
            })
        elif technical.rsi_signal == RSISignal.OVERBOUGHT:
            signals.append({
                'type': 'SELL',
                'indicator': 'RSI',
                'strength': 'MEDIUM',
                'message': 'RSI overbought, hati-hati koreksi'
            })
        
        # MACD Signals
        if technical.macd and technical.macd_signal:
            if technical.macd > technical.macd_signal and technical.macd_histogram > 0:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'MACD',
                    'strength': 'WEAK',
                    'message': 'MACD bullish crossover'
                })
            elif technical.macd < technical.macd_signal and technical.macd_histogram < 0:
                signals.append({
                    'type': 'SELL',
                    'indicator': 'MACD',
                    'strength': 'WEAK',
                    'message': 'MACD bearish crossover'
                })
        
        # Trend Signals
        if technical.trend_direction == TrendDirection.STRONG_BULLISH:
            signals.append({
                'type': 'BUY',
                'indicator': 'TREND',
                'strength': 'STRONG',
                'message': 'Trend bullish kuat, semua moving average aligned'
            })
        elif technical.trend_direction == TrendDirection.STRONG_BEARISH:
            signals.append({
                'type': 'SELL',
                'indicator': 'TREND',
                'strength': 'STRONG',
                'message': 'Trend bearish kuat, hati-hati'
            })
        
        # Support/Resistance Signals
        current_price = technical.support_level  # This should be actual price
        if current_price and technical.support_level:
            distance_to_support = ((current_price - technical.support_level) / technical.support_level * 100)
            if distance_to_support < 2:
                signals.append({
                    'type': 'BUY',
                    'indicator': 'SUPPORT',
                    'strength': 'MEDIUM',
                    'message': 'Mendekati support level, potential bounce'
                })
        
        return signals

# main.py
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import Config
from data.yahoo_finance import YahooFinanceProvider
from analysis.fundamental import FundamentalAnalyzer
from analysis.technical import TechnicalAnalyzer
from analysis.dividend import DividendAnalyzer
from analysis.scoring import InvestmentScorer
from utils.formatter import Formatter

class WarrenAI:
    """Main application class dengan dependency injection"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.formatter = Formatter(
            currency=self.config.currency,
            locale_str=self.config.locale
        )
        
        # Initialize data provider
        self.data_provider = self._init_data_provider()
        
        # Initialize analyzers
        self.fundamental_analyzer = FundamentalAnalyzer(
            data_provider=self.data_provider,
            config=self.config
        )
        self.technical_analyzer = TechnicalAnalyzer(
            data_provider=self.data_provider,
            config=self.config
        )
        self.dividend_analyzer = DividendAnalyzer(
            data_provider=self.data_provider
        )
        self.scorer = InvestmentScorer(config=self.config)
        
        # Cache for results
        self._cache = {}
    
    def _init_data_provider(self):
        """Initialize data provider based on config"""
        if self.config.data_provider == 'yahoo':
            return YahooFinanceProvider(self.config)
        elif self.config.data_provider == 'alpha_vantage':
            # from data.alpha_vantage import AlphaVantageProvider
            # return AlphaVantageProvider(self.config)
            raise NotImplementedError("Alpha Vantage provider not yet implemented")
        elif self.config.data_provider == 'fmp':
            # from data.fmp import FMPProvider
            # return FMPProvider(self.config)
            raise NotImplementedError("FMP provider not yet implemented")
        else:
            raise ValueError(f"Unknown data provider: {self.config.data_provider}")
    
    def analyze_stock(self, ticker: str, use_cache: bool = True) -> Dict[str, Any]:
        """Comprehensive stock analysis"""
        
        # Check cache
        cache_key = f"{ticker}_{datetime.now().strftime('%Y%m%d')}"
        if use_cache and self.config.cache_enabled and cache_key in self._cache:
            return self._cache[cache_key]
        
        print(f"🔍 Analyzing {ticker}...")
        
        try:
            # Get stock metadata
            metadata = self.data_provider.get_stock_metadata(ticker)
            current_price = self.data_provider.get_current_price(ticker)
            
            # Run analyses in parallel (would use threading in production)
            print("📊 Performing fundamental analysis...")
            fund_result = self.fundamental_analyzer.analyze(ticker)
            
            print("📈 Performing technical analysis...")
            tech_result = self.technical_analyzer.analyze(ticker)
            
            print("💰 Performing dividend analysis...")
            div_result = self.dividend_analyzer.analyze(ticker)
            
            print("🎯 Calculating investment score...")
            score_result = self.scorer.calculate_score(
                fundamental=fund_result.data,
                technical=tech_result.data,
                dividend=div_result.data
            )
            
            # Generate AI summary
            summary = self._generate_ai_summary(
                metadata=metadata,
                current_price=current_price,
                fundamental=fund_result.data,
                technical=tech_result.data,
                dividend=div_result.data,
                score=score_result
            )
            
            # Generate signals
            signals = self.technical_analyzer.generate_signals(
                tech_result.data.get('technical')
            )
            
            result = {
                'metadata': metadata.to_dict(),
                'current_price': current_price,
                'fundamental': fund_result.data,
                'technical': tech_result.data,
                'dividend': div_result.data,
                'score': score_result,
                'summary': summary,
                'signals': signals,
                'analysis_date': datetime.now().isoformat()
            }
            
            # Cache result
            if self.config.cache_enabled:
                self._cache[cache_key] = result
            
            return result
            
        except Exception as e:
            error_msg = f"Error analyzing {ticker}: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'error': error_msg,
                'ticker': ticker,
                'analysis_date': datetime.now().isoformat()
            }
    
    def analyze_portfolio(self, portfolio: Dict[str, int]) -> Dict[str, Any]:
        """Analyze multiple stocks (portfolio)"""
        results = {}
        total_value = 0
        total_investment = 0
        
        for ticker, shares in portfolio.items():
            try:
                analysis = self.analyze_stock(ticker)
                current_price = analysis.get('current_price', 0)
                
                position_value = current_price * shares
                total_value += position_value
                
                # In real app, you'd have purchase price
                # total_investment += purchase_price * shares
                
                results[ticker] = {
                    'analysis': analysis,
                    'shares': shares,
                    'current_value': position_value,
                    'weight': 0  # Will calculate after total
                }
                
            except Exception as e:
                print(f"Error analyzing {ticker} in portfolio: {str(e)}")
                continue
        
        # Calculate weights
        for ticker_data in results.values():
            if total_value > 0:
                ticker_data['weight'] = (ticker_data['current_value'] / total_value) * 100
        
        return {
            'stocks': results,
            'total_value': total_value,
            'total_investment': total_investment,
            'total_return': total_value - total_investment,
            'return_percentage': ((total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
        }
    
    def _generate_ai_summary(self, metadata, current_price, fundamental, 
                           technical, dividend, score) -> str:
        """Generate AI summary of analysis"""
        
        # Use formatter for consistent formatting
        trend_formatted = self.formatter.format_trend(
            technical.get('technical', {}).get('trend_direction', '')
        )
        
        recommendation_formatted = self.formatter.format_recommendation(
            score.get('recommendation', '')
        )
        
        summary = f"""
🤖 **WARREN AI COMPREHENSIVE ANALYSIS** 🤖
{'='*60}

📋 **STOCK OVERVIEW**
• Saham: {metadata.name} ({metadata.code})
• Harga: {self.formatter.format_currency(current_price)}
• Sektor: {metadata.sector or 'N/A'}
• Industri: {metadata.industry or 'N/A'}

📊 **FUNDAMENTAL ANALYSIS**
• PER: {self.formatter.format_number(fundamental.get('fundamental', {}).get('pe_ratio'))}
• PBV: {self.formatter.format_number(fundamental.get('fundamental', {}).get('pb_ratio'))}
• ROE: {self.formatter.format_percentage(fundamental.get('fundamental', {}).get('roe'))}
• Debt/Equity: {self.formatter.format_number(fundamental.get('fundamental', {}).get('debt_to_equity'))}
• Market Cap: {self.formatter.format_currency(fundamental.get('fundamental', {}).get('market_cap'))}

📈 **TECHNICAL ANALYSIS**
• Trend: {trend_formatted}
• RSI: {self.formatter.format_number(technical.get('technical', {}).get('rsi'))} ({technical.get('technical', {}).get('rsi_signal', '')})
• Support: {self.formatter.format_currency(technical.get('technical', {}).get('support_level'))}
• Resistance: {self.formatter.format_currency(technical.get('technical', {}).get('resistance_level'))}
• MA Alignment: {technical.get('technical', {}).get('ma_alignment', 'N/A')}

💰 **DIVIDEND ANALYSIS**
• Yield: {self.formatter.format_percentage(dividend.get('dividend', {}).get('dividend_yield'))}
• Payout Ratio: {self.formatter.format_percentage(dividend.get('dividend', {}).get('payout_ratio'))}

🎯 **INVESTMENT RECOMMENDATION**
• Rekomendasi: **{recommendation_formatted}**
• Skor Total: {self.formatter.format_score(score.get('total_score', 0))}
• Confidence: {score.get('confidence', 'N/A')}
• Risiko: {score.get('risk_level', 'N/A')}
• Horizon: {score.get('time_horizon', 'N/A')}

💡 **KEY INSIGHTS:**
"""
        
        # Add strengths
        if fundamental.get('strengths'):
            summary += "✅ **Strengths:** " + " | ".join(fundamental['strengths']) + "\n"
        
        # Add weaknesses
        if fundamental.get('weaknesses'):
            summary += "⚠️ **Weaknesses:** " + " | ".join(fundamental['weaknesses']) + "\n"
        
        # Add technical signals
        technical_data = technical.get('technical', {})
        if technical_data.get('rsi_signal') == 'oversold':
            summary += "📉 **Opportunity:** RSI oversold, potential rebound\n"
        elif technical_data.get('rsi_signal') == 'overbought':
            summary += "📈 **Caution:** RSI overbought, risk of correction\n"
        
        # Add dividend insight
        div_yield = dividend.get('dividend', {}).get('dividend_yield', 0)
        if div_yield and div_yield > 0.05:
            summary += "💰 **Income:** High dividend yield for income investors\n"
        
        summary += f"""
📝 **DISCLAIMER:** 
Analisis ini bersifat edukasi dan bukan rekomendasi finansial. 
Lakukan riset mandiri dan pertimbangkan kondisi pasar terkini.
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return summary
    
    def clear_cache(self):
        """Clear analysis cache"""
        self._cache.clear()
        print("✅ Cache cleared")

# Simple CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Warren AI - Advanced Stock Analysis")
    parser.add_argument("ticker", help="Stock ticker symbol (e.g., BBRI, BMRI)")
    parser.add_argument("--config", help="Path to config file", default=None)
    
    args = parser.parse_args()
    
    # Load config if provided
    if args.config:
        config = Config.from_json(args.config)
    else:
        config = Config()
    
    # Create and run Warren AI
    app = WarrenAI(config)
    
    try:
        result = app.analyze_stock(args.ticker)
        
        print("\n" + "="*60)
        print("ANALYSIS RESULT")
        print("="*60)
        
        print(f"\n📋 {result['metadata']['name']} ({result['metadata']['code']})")
        print(f"💰 Current Price: {app.formatter.format_currency(result['current_price'])}")
        
        if 'score' in result:
            print(f"\n🎯 Recommendation: {app.formatter.format_recommendation(result['score']['recommendation'])}")
            print(f"📊 Score: {app.formatter.format_score(result['score']['total_score'])}")
        
        print("\n" + "="*60)
        print("AI SUMMARY")
        print("="*60)
        print(result['summary'])
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

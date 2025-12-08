# main.py
from core.config import Config
from data.yahoo_finance import YahooFinanceProvider
from analysis.fundamental import FundamentalAnalyzer
from analysis.technical import TechnicalAnalyzer
from analysis.scoring import InvestmentScorer
from interfaces.cli_interface import CLIInterface

class WarrenAI:
    """Main application class dengan dependency injection"""
    
    def __init__(self, config: Config):
        self.config = config
        
        # Initialize data provider
        if config.data_provider == 'yahoo':
            self.data_provider = YahooFinanceProvider()
        elif config.data_provider == 'alternative':
            # self.data_provider = AlternativeAPIProvider()
            pass
        
        # Initialize analyzers
        self.fundamental_analyzer = FundamentalAnalyzer(self.data_provider)
        self.technical_analyzer = TechnicalAnalyzer(self.data_provider)
        self.scorer = InvestmentScorer()
    
    def analyze_stock(self, ticker: str):
        """Analisis saham komprehensif"""
        # Analisis fundamental
        fund_result = self.fundamental_analyzer.analyze(ticker)
        
        # Analisis teknikal
        tech_result = self.technical_analyzer.analyze(ticker)
        
        # Hitung score
        score_result = self.scorer.calculate_score(
            fund_result, 
            tech_result
        )
        
        # Generate summary
        summary = self._generate_summary(
            fund_result, 
            tech_result, 
            score_result
        )
        
        return {
            'fundamental': fund_result,
            'technical': tech_result,
            'score': score_result,
            'summary': summary
        }
    
    def run(self):
        """Run application berdasarkan interface"""
        if self.config.interface == 'cli':
            interface = CLIInterface(self)
            interface.run()
        elif self.config.interface == 'streamlit':
            # Streamlit akan dijalankan terpisah
            pass

if __name__ == "__main__":
    config = Config(
        data_provider='yahoo',
        interface='cli',
        debug_mode=False
    )
    
    app = WarrenAI(config)
    app.run()

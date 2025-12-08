# analysis/fundamental.py
from core.base_analyzer import BaseAnalyzer, AnalysisResult
from datetime import datetime
from models.stock import StockFundamental

class FundamentalAnalyzer(BaseAnalyzer):
    """Analisis fundamental dengan OOP"""
    
    def __init__(self, data_provider):
        super().__init__(data_provider)
        self.thresholds = {
            'pe_ratio': {'good': 12, 'medium': 18},
            'pb_ratio': {'good': 1.5, 'medium': 2.5},
            'roe': {'good': 0.20, 'medium': 0.15},
            'debt_to_equity': {'good': 0.5}
        }
    
    def analyze(self, stock_code: str) -> AnalysisResult:
        if not self.validate_input(stock_code):
            raise ValueError("Invalid stock code")
        
        # Ambil data dari provider
        stock_info = self.data_provider.get_stock_info(stock_code)
        
        # Buat model
        fundamental = StockFundamental(
            code=stock_code,
            current_price=stock_info.get('currentPrice'),
            pe_ratio=stock_info.get('trailingPE'),
            pb_ratio=stock_info.get('priceToBook'),
            roe=stock_info.get('returnOnEquity'),
            # ... atribut lainnya
        )
        
        # Lakukan analisis
        score = self._calculate_score(fundamental)
        grade = self._determine_grade(score)
        
        # Return result
        return AnalysisResult(
            stock_code=stock_code,
            timestamp=datetime.now().isoformat(),
            data={
                'fundamental': fundamental.to_dict(),
                'score': score,
                'grade': grade,
                'analysis': self._generate_analysis(fundamental)
            }
        )
    
    def _calculate_score(self, fundamental: StockFundamental) -> int:
        # Logika scoring
        pass

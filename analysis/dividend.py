# analysis/dividend.py
from datetime import datetime
from typing import Dict, Any
from models.stock import DividendInfo

class DividendAnalyzer:
    """Dividend analysis"""
    
    def __init__(self, data_provider):
        self.data_provider = data_provider
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """Perform dividend analysis"""
        try:
            # Get dividend data
            dividend_data = self.data_provider.get_dividend_data(ticker)
            
            # Create dividend info object
            dividend_info = DividendInfo(
                dividend_yield=dividend_data.get('dividend_yield'),
                five_year_avg_yield=dividend_data.get('five_year_avg_yield'),
                payout_ratio=dividend_data.get('payout_ratio'),
                dividend_rate=dividend_data.get('dividend_rate')
            )
            
            # Calculate score
            score, grade = self._calculate_dividend_score(dividend_info)
            
            return {
                'dividend': dividend_info.to_dict(),
                'score': score,
                'grade': grade,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Dividend analysis failed: {str(e)}",
                'dividend': {},
                'score': 0,
                'grade': 'F'
            }
    
    def _calculate_dividend_score(self, dividend: DividendInfo) -> tuple:
        """Calculate dividend score"""
        score = 0
        
        # Yield scoring
        if dividend.dividend_yield:
            if dividend.dividend_yield > 0.05:  # 5%
                score += 3
                grade = "A"
            elif dividend.dividend_yield > 0.03:  # 3%
                score += 2
                grade = "B"
            elif dividend.dividend_yield > 0.01:  # 1%
                score += 1
                grade = "C"
            else:
                grade = "D"
        else:
            grade = "F"
        
        # Payout ratio scoring
        if dividend.payout_ratio:
            if dividend.payout_ratio < 0.5:  # Sustainable
                score += 1
            elif dividend.payout_ratio > 1.0:  # Unsustainable
                score -= 1
        
        return score, grade

# analysis/fundamental.py
from datetime import datetime
from typing import Dict, Any, List
from models.stock import FundamentalMetrics, StockMetadata

class FundamentalAnalyzer:
    """Fundamental analysis"""
    
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.thresholds = {
            'pe_ratio': {'good': 15, 'medium': 25},
            'pb_ratio': {'good': 1.5, 'medium': 3},
            'roe': {'good': 0.15, 'medium': 0.10},
            'debt_to_equity': {'good': 0.5, 'medium': 1.0}
        }
    
    def analyze(self, ticker: str) -> Dict[str, Any]:
        """Perform fundamental analysis"""
        try:
            # Get data
            fundamental_data = self.data_provider.get_fundamental_data(ticker)
            
            # Create metrics object
            metrics = FundamentalMetrics(
                pe_ratio=fundamental_data.get('pe_ratio'),
                pb_ratio=fundamental_data.get('pb_ratio'),
                roe=fundamental_data.get('roe'),
                debt_to_equity=fundamental_data.get('debt_to_equity'),
                profit_margin=fundamental_data.get('profit_margin'),
                revenue_growth=fundamental_data.get('revenue_growth'),
                earnings_growth=fundamental_data.get('earnings_growth'),
                market_cap=fundamental_data.get('market_cap'),
                current_ratio=fundamental_data.get('current_ratio'),
                quick_ratio=fundamental_data.get('quick_ratio'),
                gross_margin=fundamental_data.get('gross_margin'),
                operating_margin=fundamental_data.get('operating_margin')
            )
            
            # Calculate score
            score, strengths, weaknesses = self._calculate_score(metrics)
            
            # Determine grade
            grade = self._determine_grade(score)
            
            return {
                'metrics': metrics.to_dict(),
                'score': score,
                'grade': grade,
                'strengths': strengths,
                'weaknesses': weaknesses,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Fundamental analysis failed: {str(e)}",
                'metrics': {},
                'score': 0,
                'grade': 'F',
                'strengths': [],
                'weaknesses': []
            }
    
    def _calculate_score(self, metrics: FundamentalMetrics) -> tuple:
        """Calculate fundamental score"""
        score = 0
        strengths = []
        weaknesses = []
        
        # P/E Ratio analysis
        if metrics.pe_ratio:
            if metrics.pe_ratio < self.thresholds['pe_ratio']['good']:
                score += 2
                strengths.append(f"Low P/E ratio ({metrics.pe_ratio:.1f})")
            elif metrics.pe_ratio < self.thresholds['pe_ratio']['medium']:
                score += 1
            else:
                weaknesses.append(f"High P/E ratio ({metrics.pe_ratio:.1f})")
        
        # P/B Ratio analysis
        if metrics.pb_ratio:
            if metrics.pb_ratio < self.thresholds['pb_ratio']['good']:
                score += 2
                strengths.append(f"Low P/B ratio ({metrics.pb_ratio:.2f})")
            elif metrics.pb_ratio < self.thresholds['pb_ratio']['medium']:
                score += 1
            else:
                weaknesses.append(f"High P/B ratio ({metrics.pb_ratio:.2f})")
        
        # ROE analysis
        if metrics.roe:
            if metrics.roe > self.thresholds['roe']['good']:
                score += 2
                strengths.append(f"High ROE ({metrics.roe*100:.1f}%)")
            elif metrics.roe > self.thresholds['roe']['medium']:
                score += 1
            else:
                weaknesses.append(f"Low ROE ({metrics.roe*100:.1f}%)")
        
        # Debt analysis
        if metrics.debt_to_equity:
            if metrics.debt_to_equity < self.thresholds['debt_to_equity']['good']:
                score += 1
                strengths.append(f"Low debt-to-equity ({metrics.debt_to_equity:.2f})")
            elif metrics.debt_to_equity > self.thresholds['debt_to_equity']['medium']:
                score -= 1
                weaknesses.append(f"High debt-to-equity ({metrics.debt_to_equity:.2f})")
        
        # Profitability
        if metrics.profit_margin and metrics.profit_margin > 0.1:
            score += 1
            strengths.append(f"Good profit margin ({metrics.profit_margin*100:.1f}%)")
        
        # Growth
        if metrics.revenue_growth and metrics.revenue_growth > 0.1:
            score += 1
            strengths.append(f"Revenue growth ({metrics.revenue_growth*100:.1f}%)")
        
        return score, strengths, weaknesses
    
    def _determine_grade(self, score: int) -> str:
        """Determine fundamental grade"""
        if score >= 8:
            return "A"
        elif score >= 6:
            return "B"
        elif score >= 4:
            return "C"
        elif score >= 2:
            return "D"
        else:
            return "F"

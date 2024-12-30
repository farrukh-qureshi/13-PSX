import pandas as pd
import numpy as np
from typing import Dict, List
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CompanyMetrics:
    """Store current company metrics"""
    current_price: float
    market_cap: float
    shares_outstanding: float
    
    # Per share metrics
    eps: float
    book_value: float
    dividend_per_share: float
    
    # Financial ratios
    pe_ratio: float
    pb_ratio: float
    dividend_yield: float
    debt_to_equity: float
    current_ratio: float
    interest_coverage: float
    net_profit_margin: float
    gross_profit_margin: float
    
    # Balance sheet items
    total_assets: float
    total_liabilities: float
    equity: float
    cash: float
    debt: float

@dataclass
class HistoricalData:
    """Store historical financial data"""
    years: List[int]
    revenue: List[float]
    net_profit: List[float]
    eps: List[float]
    dividends: List[float]
    book_value: List[float]

class CompanyAnalyzer:
    def __init__(self, metrics: CompanyMetrics, historical: HistoricalData):
        self.metrics = metrics
        self.historical = historical
        self.analysis_results = {}
        self.recommendations = []
        
    def analyze_dividend_sustainability(self) -> Dict:
        """Analyze dividend sustainability"""
        payout_ratio = (self.metrics.dividend_per_share / self.metrics.eps) * 100
        
        dividend_growth = np.mean([
            (self.historical.dividends[i] / self.historical.dividends[i-1] - 1) * 100
            for i in range(1, len(self.historical.dividends))
        ])
        
        results = {
            'dividend_yield': self.metrics.dividend_yield,
            'payout_ratio': payout_ratio,
            'dividend_growth_rate': dividend_growth,
            'interest_coverage': self.metrics.interest_coverage,
            'current_ratio': self.metrics.current_ratio
        }
        
        # Dividend sustainability scoring
        score = 0
        if 0 <= payout_ratio <= 75: score += 1
        if self.metrics.current_ratio > 1.5: score += 1
        if self.metrics.interest_coverage > 3: score += 1
        if dividend_growth > 0: score += 1
        if self.metrics.debt_to_equity < 1: score += 1
        
        results['sustainability_score'] = score
        self.analysis_results['dividend'] = results
        
        # Add recommendations based on dividend analysis
        if score >= 4:
            self.recommendations.append("Strong dividend sustainability profile")
        elif score >= 3:
            self.recommendations.append("Moderate dividend sustainability")
        else:
            self.recommendations.append("Dividend sustainability concerns present")
            
        return results

    def analyze_valuation(self) -> Dict:
        """Analyze company valuation"""
        # Calculate historical averages
        avg_pe = np.mean([
            self.historical.eps[i] / self.metrics.current_price 
            for i in range(len(self.historical.eps))
        ])
        
        # Calculate growth rates
        eps_growth = np.mean([
            (self.historical.eps[i] / self.historical.eps[i-1] - 1) * 100
            for i in range(1, len(self.historical.eps))
        ])
        
        results = {
            'current_pe': self.metrics.pe_ratio,
            'historical_avg_pe': avg_pe,
            'pb_ratio': self.metrics.pb_ratio,
            'eps_growth': eps_growth,
            'price_to_sales': self.metrics.market_cap / self.historical.revenue[-1]
        }
        
        # Valuation scoring
        score = 0
        if self.metrics.pe_ratio < avg_pe: score += 1
        if self.metrics.pb_ratio < 1: score += 1
        if eps_growth > 10: score += 1
        if self.metrics.net_profit_margin > 15: score += 1
        
        results['valuation_score'] = score
        self.analysis_results['valuation'] = results
        
        # Add valuation-based recommendations
        if score >= 3:
            self.recommendations.append("Company appears undervalued")
        elif score == 2:
            self.recommendations.append("Company appears fairly valued")
        else:
            self.recommendations.append("Company may be overvalued")
            
        return results

    def analyze_financial_health(self) -> Dict:
        """Analyze financial health"""
        results = {
            'debt_to_equity': self.metrics.debt_to_equity,
            'current_ratio': self.metrics.current_ratio,
            'interest_coverage': self.metrics.interest_coverage,
            'net_profit_margin': self.metrics.net_profit_margin,
            'gross_profit_margin': self.metrics.gross_profit_margin
        }
        
        # Financial health scoring
        score = 0
        if self.metrics.debt_to_equity < 1: score += 1
        if self.metrics.current_ratio > 1.5: score += 1
        if self.metrics.interest_coverage > 3: score += 1
        if self.metrics.net_profit_margin > 15: score += 1
        if self.metrics.gross_profit_margin > 30: score += 1
        
        results['health_score'] = score
        self.analysis_results['financial_health'] = results
        
        # Add financial health recommendations
        if score >= 4:
            self.recommendations.append("Strong financial health")
        elif score >= 3:
            self.recommendations.append("Adequate financial health")
        else:
            self.recommendations.append("Financial health needs monitoring")
            
        return results

    def generate_report(self) -> Dict:
        """Generate comprehensive analysis report"""
        # Perform all analyses
        self.analyze_dividend_sustainability()
        self.analyze_valuation()
        self.analyze_financial_health()
        
        # Calculate overall score
        total_score = (
            self.analysis_results['dividend']['sustainability_score'] +
            self.analysis_results['valuation']['valuation_score'] +
            self.analysis_results['financial_health']['health_score']
        )
        
        # Generate investment recommendation
        if total_score >= 10:
            investment_rating = "Strong Buy"
        elif total_score >= 8:
            investment_rating = "Buy"
        elif total_score >= 6:
            investment_rating = "Hold"
        else:
            investment_rating = "Sell"
            
        report = {
            'company_analysis': self.analysis_results,
            'recommendations': self.recommendations,
            'investment_rating': investment_rating,
            'total_score': total_score,
            'analysis_date': datetime.now().strftime("%Y-%m-%d")
        }
        
        return report

def export_to_excel(report: Dict, filename: str):
    """Export analysis report to Excel"""
    with pd.ExcelWriter(filename) as writer:
        # Create DataFrames for each section
        metrics_df = pd.DataFrame(report['company_analysis']).transpose()
        recommendations_df = pd.DataFrame(report['recommendations'], columns=['Recommendations'])
        summary_df = pd.DataFrame({
            'Metric': ['Investment Rating', 'Total Score', 'Analysis Date'],
            'Value': [report['investment_rating'], report['total_score'], report['analysis_date']]
        })
        
        # Write to Excel
        metrics_df.to_excel(writer, sheet_name='Detailed Analysis')
        recommendations_df.to_excel(writer, sheet_name='Recommendations')
        summary_df.to_excel(writer, sheet_name='Summary')

# Example usage
if __name__ == "__main__":
    # Example data for MARI (you would replace these with actual data)
    metrics = CompanyMetrics(
        current_price=694.29,
        market_cap=833.58e9,
        shares_outstanding=1.2e9,
        eps=579.41,
        book_value=1694.74,
        dividend_per_share=232.00,
        pe_ratio=1.20,
        pb_ratio=0.25,
        dividend_yield=54.52,
        debt_to_equity=0.25,
        current_ratio=2.77,
        interest_coverage=33.83,
        net_profit_margin=43.23,
        gross_profit_margin=87.91,
        total_assets=254.6e9,
        total_liabilities=86.17e9,
        equity=168.43e9,
        cash=31.7e9,
        debt=672.38e6
    )
    
    historical = HistoricalData(
        years=[2019, 2020, 2021, 2022, 2023],
        revenue=[59.45e9, 72.03e9, 73.02e9, 95.13e9, 145.77e9],
        net_profit=[24.33e9, 30.31e9, 31.44e9, 33.06e9, 56.13e9],
        eps=[200.59, 227.23, 235.71, 247.84, 420.75],
        dividends=[6.00, 6.10, 141.00, 124.00, 147.00],
        book_value=[476.81, 698.26, 866.04, 980.92, 1262.55]
    )
    
    # Create analyzer and generate report
    analyzer = CompanyAnalyzer(metrics, historical)
    report = analyzer.generate_report()
    
    # Export to Excel
    export_to_excel(report, 'company_analysis.xlsx')

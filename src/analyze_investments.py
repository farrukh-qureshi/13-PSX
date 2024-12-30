import pandas as pd
import numpy as np

class DividendAnalyzer:
    def __init__(self, payouts: pd.DataFrame, ratios: pd.DataFrame, income_statement: pd.DataFrame):
        self.payouts = payouts
        self.ratios = ratios
        self.income_statement = income_statement

    def analyze_dividend_quality(self):
        div_data = self.payouts[self.payouts['Payout Type'] == 'Dividend']
        
        # Analyze consistency
        yearly_payouts = div_data.groupby(div_data['Year'].str[:4])['Payout %'].sum()
        consistency_score = min(len(yearly_payouts[yearly_payouts > 0]) / len(yearly_payouts) * 40, 40)
        
        # Analyze growth trend
        recent_growth = yearly_payouts.pct_change().tail(5).mean() * 100
        growth_score = min(recent_growth / 15 * 30, 30)
        
        # Analyze yield and sustainability
        current_yield = yearly_payouts.iloc[-1]
        payout_ratio = self.ratios.loc['Payout', '2023']
        sustainability_score = max(0, (70 - payout_ratio) / 70 * 30)
        
        # Analyze earnings coverage
        eps_growth = self.income_statement.loc['EPS'].pct_change().mean() * 100
        
        total_score = consistency_score + growth_score + sustainability_score
        
        return {
            'total_score': total_score,
            'consistency_years': len(yearly_payouts[yearly_payouts > 0]),
            'avg_payout': yearly_payouts.mean(),
            'growth_rate': recent_growth,
            'current_yield': current_yield,
            'payout_ratio': payout_ratio,
            'eps_growth': eps_growth
        }

    def generate_report(self):
        metrics = self.analyze_dividend_quality()
        
        recommendation = "STRONG BUY" if metrics['total_score'] >= 80 else \
                        "BUY" if metrics['total_score'] >= 65 else \
                        "HOLD" if metrics['total_score'] >= 50 else "AVOID"

        return f"""Dividend Quality Analysis
        
Overall Score: {metrics['total_score']:.1f}/100
Recommendation: {recommendation}

Key Metrics:
- Dividend Consistency: {metrics['consistency_years']} years of payments
- Current Yield: {metrics['current_yield']:.1f}%
- 5-Year Growth Rate: {metrics['growth_rate']:.1f}%
- Payout Ratio: {metrics['payout_ratio']:.1f}%
- Supporting EPS Growth: {metrics['eps_growth']:.1f}%

Analysis:
- Dividend Sustainability: {'High' if metrics['payout_ratio'] < 50 else 'Moderate' if metrics['payout_ratio'] < 70 else 'At Risk'}
- Growth Trajectory: {'Strong' if metrics['growth_rate'] > 10 else 'Moderate' if metrics['growth_rate'] > 5 else 'Weak'}
- Income Reliability: {'Excellent' if metrics['consistency_years'] > 10 else 'Good' if metrics['consistency_years'] > 5 else 'Limited'}
"""

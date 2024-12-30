import pandas as pd
import numpy as np

class StockCategorizer:
    def __init__(self, income_statement, ratios, payouts, snapshot):
        self.income_statement = income_statement
        self.ratios = ratios
        self.payouts = payouts
        self.snapshot = snapshot

    def analyze_dividend_strength(self):
        """Analyze dividend characteristics"""
        dividend_yield = float(self.snapshot['Dividend_Yield'])
        payout_ratio = self.ratios.loc['Payout', '2023']
        
        # Calculate dividend growth
        recent_dividends = self.payouts[self.payouts['Payout Type'] == 'Dividend'].head(5)
        dividend_growth = recent_dividends['Payout %'].pct_change().mean() * 100
        
        dividend_score = (
            min(dividend_yield / 5 * 40, 40) +  # Up to 40 points for yield
            min(dividend_growth / 20 * 30, 30) +  # Up to 30 points for growth
            max(0, (70 - payout_ratio) / 70 * 30)  # Up to 30 points for sustainable payout
        )
        
        return {
            'score': dividend_score,
            'yield': dividend_yield,
            'growth': dividend_growth,
            'payout_ratio': payout_ratio
        }

    def analyze_growth_strength(self):
        """Analyze growth characteristics"""
        # Calculate 5-year growth rates
        revenue_growth = self.income_statement.loc['Sales'].pct_change().mean() * 100
        profit_growth = self.income_statement.loc['PAT'].pct_change().mean() * 100
        eps_growth = self.income_statement.loc['EPS'].pct_change().mean() * 100
        
        # Get profitability metrics
        net_margin = self.ratios.loc['Net Profit Margin', '2023']
        roe = self.ratios.loc['Return on Equity', '2023']
        
        growth_score = (
            min(revenue_growth / 25 * 30, 30) +  # Up to 30 points for revenue growth
            min(profit_growth / 30 * 30, 30) +   # Up to 30 points for profit growth
            min(roe / 30 * 20, 20) +             # Up to 20 points for ROE
            min(net_margin / 30 * 20, 20)        # Up to 20 points for margin
        )
        
        return {
            'score': growth_score,
            'revenue_growth': revenue_growth,
            'profit_growth': profit_growth,
            'eps_growth': eps_growth,
            'net_margin': net_margin,
            'roe': roe
        }

    def categorize_stock(self):
        """Determine if stock is primarily dividend or growth focused"""
        dividend_metrics = self.analyze_dividend_strength()
        growth_metrics = self.analyze_growth_strength()
        
        category = "STRONG DIVIDEND STOCK" if dividend_metrics['score'] > growth_metrics['score'] else "STRONG GROWTH STOCK"
        
        report = f"""Stock Category Analysis:
        
CLASSIFICATION: {category}

Dividend Metrics (Score: {dividend_metrics['score']:.1f}/100):
- Dividend Yield: {dividend_metrics['yield']:.1f}%
- Dividend Growth Rate: {dividend_metrics['growth']:.1f}%
- Payout Ratio: {dividend_metrics['payout_ratio']:.1f}%

Growth Metrics (Score: {growth_metrics['score']:.1f}/100):
- Revenue Growth: {growth_metrics['revenue_growth']:.1f}%
- Profit Growth: {growth_metrics['profit_growth']:.1f}%
- EPS Growth: {growth_metrics['eps_growth']:.1f}%
- Net Margin: {growth_metrics['net_margin']:.1f}%
- Return on Equity: {growth_metrics['roe']:.1f}%

Primary Strength: {"Dividend payments and stability" if category == "STRONG DIVIDEND STOCK" else "Business growth and profitability"}
"""
        return report

# Load data and analyze
income_statement = pd.read_csv('financial_data/income_statement.csv', index_col='Metric')
ratios = pd.read_csv('financial_data/financial_ratios.csv', index_col='Metric')
payouts = pd.read_csv('financial_data/payouts.csv')
snapshot = pd.read_csv('financial_data/company_snapshot.csv').iloc[0]

categorizer = StockCategorizer(income_statement, ratios, payouts, snapshot)
print(categorizer.categorize_stock())
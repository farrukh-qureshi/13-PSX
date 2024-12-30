import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os

# Import analysis classes
from analyze_investments import DividendAnalyzer
from growth_or_dividend import StockCategorizer

# Import stock scrapper
from stock_scrapper import scrape_company_data

# Load data
def load_financial_data():
    try:
        payouts = pd.read_csv('financial_data/payouts.csv')
        ratios = pd.read_csv('financial_data/financial_ratios.csv', index_col='Metric')
        income_statement = pd.read_csv('financial_data/income_statement.csv', index_col='Metric')
        balance_sheet = pd.read_csv('financial_data/balance_sheet.csv', index_col='Metric')
        snapshot = pd.read_csv('financial_data/company_snapshot.csv').iloc[0]
        cash_flow = pd.read_csv('financial_data/cash_flow.csv', index_col='Metric')
        
        return {
            'payouts': payouts,
            'ratios': ratios,
            'income_statement': income_statement,
            'balance_sheet': balance_sheet,
            'snapshot': snapshot,
            'cash_flow': cash_flow
        }
    except Exception as e:
        st.error(f"Error loading financial data: {e}")
        return None

def dividend_analysis_page(data):
    st.header("Dividend Quality Analysis")
    
    # Initialize Dividend Analyzer
    analyzer = DividendAnalyzer(data['payouts'], data['ratios'], data['income_statement'])
    
    # Generate report
    report = analyzer.generate_report()
    st.markdown(report)
    
    # Visualize Dividend Metrics
    st.subheader("Dividend Metrics Visualization")
    
    # Yearly Payouts
    yearly_payouts = data['payouts'][data['payouts']['Payout Type'] == 'Dividend'].groupby(data['payouts']['Year'].str[:4])['Payout %'].sum()
    
    fig = px.line(
        x=yearly_payouts.index, 
        y=yearly_payouts.values, 
        title='Yearly Dividend Payouts',
        labels={'x': 'Year', 'y': 'Total Dividend Payout (%)'}
    )
    st.plotly_chart(fig)

def growth_analysis_page(data):
    st.header("Stock Growth Analysis")
    
    # Initialize Stock Categorizer
    categorizer = StockCategorizer(
        data['income_statement'], 
        data['ratios'], 
        data['payouts'], 
        data['snapshot']
    )
    
    # Generate report
    report = categorizer.categorize_stock()
    st.markdown(report)
    
    # Visualize Growth Metrics
    st.subheader("Growth Metrics Visualization")
    
    # Revenue and Profit Growth
    years = data['income_statement'].columns[1:]
    revenue = data['income_statement'].loc['Sales'][1:]
    profit = data['income_statement'].loc['PAT'][1:]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=revenue, name='Revenue'))
    fig.add_trace(go.Bar(x=years, y=profit, name='Profit After Tax'))
    
    fig.update_layout(
        title='Revenue and Profit Trend',
        xaxis_title='Year',
        yaxis_title='Amount',
        barmode='group'
    )
    st.plotly_chart(fig)

def company_snapshot_page(data):
    st.header("Company Snapshot")
    
    # Display key metrics from snapshot
    st.subheader("Key Financial Indicators")
    
    # Select important metrics to display
    key_metrics = {
        'Current Price': data['snapshot'].get('Current', 'N/A'),
        'Market Cap': data['snapshot'].get('Market_Cap', 'N/A'),
        'Dividend Yield': data['snapshot'].get('Dividend_Yield', 'N/A'),
        'P/E Ratio': data['snapshot'].get('PE_Ratio', 'N/A'),
        'EPS': data['snapshot'].get('EPS', 'N/A'),
        'Book Value': data['snapshot'].get('Book_Value', 'N/A')
    }
    
    # Create a DataFrame for display
    metrics_df = pd.DataFrame.from_dict(key_metrics, orient='index', columns=['Value'])
    
    # Convert 'N/A' to 0 for display
    metrics_df['Value'] = metrics_df['Value'].apply(lambda x: 0 if x == 'N/A' else x)
    
    st.table(metrics_df)
    
    # Pie chart of financial composition
    st.subheader("Financial Composition")
    
    # Calculate total debt by summing interest-bearing liabilities
    total_debt = (
        data['balance_sheet'].loc['Interest Bearing Long Term Liability'].iloc[-1] + 
        data['balance_sheet'].loc['Interest Bearing Short Term Liability'].iloc[-1]
    )
    
    composition_data = {
        'Revenue': data['income_statement'].loc['Sales'].iloc[-1],
        'Profit': data['income_statement'].loc['PAT'].iloc[-1],
        'Debt': total_debt,
        'Equity': data['balance_sheet'].loc['Shareholder Equity'].iloc[-1]
    }
    
    # Remove any zero or NaN values
    composition_data = {k: v for k, v in composition_data.items() if v > 0}
    
    fig = px.pie(
        values=list(composition_data.values()), 
        names=list(composition_data.keys()), 
        title='Financial Composition'
    )
    st.plotly_chart(fig)

def data_download_page():
    st.header("Stock Data Download")
    
    # Input for stock symbol
    symbol = st.text_input("Enter Stock Symbol (e.g., MARI)", value="MARI").upper()
    
    # Download button
    if st.button("Download Financial Data"):
        try:
            # Create financial_data directory if it doesn't exist
            if not os.path.exists('financial_data'):
                os.makedirs('financial_data')
            
            # Start scraping
            with st.spinner(f"Downloading data for {symbol}..."):
                scrape_company_data(symbol)
            
            # List downloaded files
            st.success(f"Successfully downloaded data for {symbol}")
            
            # Show list of downloaded files
            st.subheader("Downloaded Files:")
            files = os.listdir('financial_data')
            for file in files:
                st.write(file)
                
                # Optional: Show file preview
                try:
                    df = pd.read_csv(os.path.join('financial_data', file))
                    st.dataframe(df.head())
                except Exception as e:
                    st.error(f"Could not preview {file}: {e}")
        
        except Exception as e:
            st.error(f"Error downloading data: {e}")

def main():
    st.title("Financial Analysis Dashboard")
    
    # Load financial data
    data = load_financial_data()
    
    if data is None:
        st.error("Could not load financial data. Please ensure all CSV files are present.")
        return
    
    # Create sidebar navigation
    page = st.sidebar.selectbox(
        "Select Analysis", 
        [
            "Data Download",
            "Company Snapshot", 
            "Dividend Analysis", 
            "Growth Analysis"
        ]
    )
    
    # Render selected page
    if page == "Data Download":
        data_download_page()
    elif page == "Company Snapshot":
        company_snapshot_page(data)
    elif page == "Dividend Analysis":
        dividend_analysis_page(data)
    elif page == "Growth Analysis":
        growth_analysis_page(data)


if __name__ == "__main__":
    main()

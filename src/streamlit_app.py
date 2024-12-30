import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import os
import shutil

# Import analysis classes
from analyze_investments import DividendAnalyzer
from growth_or_dividend import StockCategorizer

# Import stock scrapper
from stock_scrapper import scrape_company_data

def clean_financial_data_folder():
    """Remove all files in the financial_data folder"""
    if os.path.exists('financial_data'):
        shutil.rmtree('financial_data')
    os.makedirs('financial_data')

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

def main():
    st.title("Financial Analysis Dashboard")
    
    # Initialize session state for data download
    if 'data_downloaded' not in st.session_state:
        st.session_state.data_downloaded = False
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Data Download", 
        "Company Snapshot", 
        "Dividend Analysis", 
        "Growth Analysis"
    ])
    
    # Data Download Tab
    with tab1:
        st.header("Stock Data Download")
        
        # Input for stock symbol
        symbol = st.text_input("Enter Stock Symbol (e.g., MARI)", value="MARI").upper()
        
        # Download button
        if st.button("Download Financial Data"):
            try:
                # Clean existing financial data folder
                clean_financial_data_folder()
                
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
                
                # Set flag that data has been downloaded
                st.session_state.data_downloaded = True
            
            except Exception as e:
                st.error(f"Error downloading data: {e}")
                st.session_state.data_downloaded = False
    
    # Company Snapshot Tab
    with tab2:
        if st.session_state.data_downloaded:
            # Load financial data
            data = load_financial_data()
            
            if data is None:
                st.error("Could not load financial data. Please download data first.")
                return
            
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
        else:
            st.warning("Please download financial data first in the Data Download tab.")
    
    # Dividend Analysis Tab
    with tab3:
        if st.session_state.data_downloaded:
            # Load financial data
            data = load_financial_data()
            
            if data is None:
                st.error("Could not load financial data. Please download data first.")
                return
            
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
        else:
            st.warning("Please download financial data first in the Data Download tab.")
    
    # Growth Analysis Tab
    with tab4:
        if st.session_state.data_downloaded:
            # Load financial data
            data = load_financial_data()
            
            if data is None:
                st.error("Could not load financial data. Please download data first.")
                return
            
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
        else:
            st.warning("Please download financial data first in the Data Download tab.")

if __name__ == "__main__":
    main()

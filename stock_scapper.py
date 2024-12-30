import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re

def clean_column_name(name):
    """Clean column names by removing extra spaces and newlines"""
    return re.sub(r'\s+', ' ', name).strip()

def extract_numeric(value):
    """Extract and validate numeric values"""
    if pd.isna(value) or value == '':
        return None
    # Remove commas and percentage signs
    value = str(value).replace(',', '').replace('%', '')
    numbers = re.findall(r'-?\d*\.?\d+', value)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return None
    return None

def scrape_stock_data(symbol):
    """Scrape essential financial data for any stock symbol"""
    
    if not isinstance(symbol, str) or not symbol.strip():
        raise ValueError("Stock symbol must be a non-empty string")
    
    symbol = symbol.strip().upper()
    if not re.match("^[A-Z]+$", symbol):
        raise ValueError("Stock symbol should only contain letters")

    url = f"https://sarmaaya.pk/psx/company/{symbol}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Failed to fetch data for {symbol}: {str(e)}")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    table = soup.find('div', class_='company_snapshot_content')
    if not table or not table.find('table'):
        raise ValueError(f"No data found for symbol {symbol}")
    
    table = table.find('table')
    data = {}
    
    # Updated essential columns with more financial metrics
    essential_columns = {
        'Current': 'price',
        'Volume': 'volume',
        'Price to Earnings Ratio': 'pe_ratio',
        'Earning per Share': 'eps',
        'Book Value': 'book_value',
        'Market Cap': 'market_cap',
        'Dividend': 'dividend',
        'Dividend Yield (%)': 'dividend_yield',
        'Debt to Equity': 'debt_equity_ratio',
        'Net Profit Margin': 'net_margin',
        'Gross Profit Margin': 'gross_margin',
        '52 Week High': 'high_52w',
        '52 Week Low': 'low_52w',
        'Return on Equity': 'roe',
        'Return on Assets': 'roa',
        'Current Ratio': 'current_ratio',
        'Quick Ratio': 'quick_ratio',
        'Operating Margin': 'operating_margin',
        'Beta': 'beta',
        'Shares Outstanding': 'shares_outstanding',
        'Face Value': 'face_value',
        'Free Float': 'free_float',
        'Free Float %': 'free_float_percent',
        'Change': 'change',
        'Change %': 'change_percent',
        'Times-Revenue Method': 'times_revenue'
    }

    for row in table.find_all('tr'):
        cells = row.find_all(['td', 'th'])
        for cell in cells:
            header = cell.find('strong')
            if header:
                key = clean_column_name(header.get_text())
                if key in essential_columns:
                    value = cell.get_text().split('\n')[-1].strip()
                    data[essential_columns[key]] = extract_numeric(value)
    
    # Add additional meta information
    data['symbol'] = symbol
    data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data['source_url'] = f"https://sarmaaya.pk/psx/company/{symbol}"
    
    df = pd.DataFrame([data])
    
    # Convert percentage values
    percentage_columns = ['dividend_yield', 'net_margin', 'gross_margin', 'operating_margin', 'roe', 'roa', 'change_percent', 'free_float_percent']
    for col in percentage_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x / 100 if x is not None else None)
    
    filename = f'stock_data_{symbol}_{datetime.now().strftime("%Y%m%d")}.csv'
    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")
    
    return df

if __name__ == "__main__":
    try:
        symbol = input("Enter stock symbol: ")
        data = scrape_stock_data(symbol)
        print("\nScraped Data Preview:")
        print(data.head())
    except Exception as e:
        print(f"An error occurred: {str(e)}")

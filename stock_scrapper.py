import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

def clean_value(value):
    """Convert string values like '1.26 K' or '147.00 B' to float"""
    if isinstance(value, str):
        value = value.strip()
        if value == '-' or value == '':
            return 0
        # Remove commas and percentage signs
        value = value.replace(',', '').replace('%', '')
        
        # Handle K (thousands)
        if 'K' in value:
            return float(value.replace('K', '')) * 1000
        # Handle M (millions)
        elif 'M' in value:
            return float(value.replace('M', '')) * 1000000
        # Handle B (billions)
        elif 'B' in value:
            return float(value.replace('B', '')) * 1000000000
        
        try:
            return float(value)
        except ValueError:
            return value
    return value

def scrape_company_snapshot(soup):
    """Scrape company snapshot data from the soup object"""
    logging.info("Starting to scrape company snapshot")
    try:
        snapshot_data = {}
        snapshot_table = soup.find('div', {'class': 'company_snapshot_content'})
        
        if not snapshot_table:
            logging.warning("Company snapshot table not found")
            return {}
        
        # Map of titles to keys
        fields = {
            'Current Price': 'Current',
            'Volume': 'Volume',
            'Dividend': 'Dividend',
            'Dividend Yield': 'Dividend_Yield',
            'Price to Earnings Ratio': 'PE_Ratio',
            'Earning per Share': 'EPS',
            'Book Value': 'Book_Value',
            'Price to Book': 'PB_Ratio',
            'Market Cap': 'Market_Cap',
            'Debt to Equity': 'Debt_to_Equity',
            'Net Profit Margin': 'Net_Profit_Margin',
            'Gross Profit Margin': 'Gross_Profit_Margin',
            'Current Ratio': 'Current_Ratio',
            'Shares': 'Shares',
            'FreeFloat': 'Free_Float',
            'Free Float %': 'Free_Float_Percent',
            'Equity to Asset': 'Equity_to_Asset',
            'Interest': 'Interest_Cover',
            'Beta': 'Beta',
            'Upper/Lower Cap': 'Upper_Lower_Cap',
            '52 Week High': '52W_High',
            '52 Week Low': '52W_Low',
            'High': 'High',
            'Low': 'Low'
        }
        
        # Process each field
        for title, key in fields.items():
            tag = snapshot_table.find('strong', title=lambda x: x and title in x)
            if tag and tag.find_next('br'):
                value = tag.find_next('br').next_sibling.strip()
                snapshot_data[key] = clean_value(value)
        
        return snapshot_data
    except Exception as e:
        logging.error(f"Error in scrape_company_snapshot: {str(e)}")
        logging.debug(traceback.format_exc())
        raise

def scrape_financial_data(url):
    """Scrape financial data from the given URL"""
    logging.info(f"Starting to scrape financial data from {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Create output directory if it doesn't exist
        if not os.path.exists('financial_data'):
            os.makedirs('financial_data')
        
        # Dictionary to map tab IDs to file names
        tab_mapping = {
            'nav-statement': 'income_statement.csv',
            'nav-balance': 'balance_sheet.csv',
            'nav-cash': 'cash_flow.csv',
            'nav-ratioFinance': 'financial_ratios.csv',
            'nav-equity': 'equity.csv'
        }
        
        # Process each tab
        for tab_id, filename in tab_mapping.items():
            logging.info(f"Processing tab: {tab_id}")
            tab_content = soup.find('div', {'id': tab_id})
            if not tab_content:
                logging.warning(f"Tab content not found for {tab_id}")
                continue
                
            if tab_content:
                # Find the table in the tab
                table = tab_content.find('table')
                if table:
                    # Extract headers (years)
                    headers = ['Metric'] + [th.text.strip() for th in table.find('tr').find_all('th')[1:]]
                    
                    # Extract rows
                    rows = []
                    for tr in table.find_all('tr')[1:]:  # Skip header row
                        cells = tr.find_all(['td', 'th'])
                        if cells:
                            row = [cells[0].text.strip()]  # Metric name
                            row.extend([clean_value(cell.text.strip()) for cell in cells[1:]])
                            if len(row) == len(headers):  # Only add rows that match header length
                                rows.append(row)
                    
                    # Create DataFrame and save to CSV
                    df = pd.DataFrame(rows, columns=headers)
                    output_path = os.path.join('financial_data', filename)
                    df.to_csv(output_path, index=False)
                    print(f"Saved {filename}")
    except Exception as e:
        logging.error(f"Error in scrape_financial_data: {str(e)}")
        logging.debug(traceback.format_exc())
        raise

def scrape_payout_data(url):
    """Scrape payout data from the given URL"""
    logging.info(f"Starting to scrape payout data from {url}")
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Create output directory if it doesn't exist
        if not os.path.exists('financial_data'):
            os.makedirs('financial_data')
        
        # Find the payout table
        table = soup.find('table', {'id': 'company-payouts'})
        if not table:
            logging.warning("Payout table not found")
            return
            
        if table:
            # Extract headers
            headers = [th.text.strip() for th in table.find('thead').find_all('th')]
            
            # Extract rows
            rows = []
            for tr in table.find('tbody').find_all('tr'):
                cells = tr.find_all('td')
                row = [cell.text.strip() for cell in cells]
                rows.append(row)
            
            # Create DataFrame
            df = pd.DataFrame(rows, columns=headers)
            
            # Convert numeric columns
            numeric_columns = ['Payout %', 'Face Value']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: clean_value(x) if x else 0)
            
            # Save to CSV
            output_path = os.path.join('financial_data', 'payouts.csv')
            df.to_csv(output_path, index=False)
            print("Saved payouts.csv")
    except Exception as e:
        logging.error(f"Error in scrape_payout_data: {str(e)}")
        logging.debug(traceback.format_exc())
        raise

def scrape_company_data(symbol):
    """Main function to scrape all company data"""
    logging.info(f"Starting to scrape data for company symbol: {symbol}")
    
    # Create output directory if it doesn't exist
    if not os.path.exists('financial_data'):
        os.makedirs('financial_data')
    
    base_url = "https://sarmaaya.pk"
    financial_url = f"{base_url}/ajax/widgets/all_financials.php?symbol={symbol}"
    payout_url = f"{base_url}/ajax/widgets/company_payouts.php?symbol={symbol}"
    company_url = f"{base_url}/psx/company/{symbol}"
    
    try:
        # Scrape company snapshot
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        logging.info(f"Requesting company page: {company_url}")
        response = requests.get(company_url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Get company snapshot data
        snapshot_data = scrape_company_snapshot(soup)
        if not snapshot_data:
            logging.warning("No snapshot data was retrieved")
        
        # Save snapshot data to CSV
        snapshot_df = pd.DataFrame([snapshot_data])
        snapshot_path = os.path.join('financial_data', 'company_snapshot.csv')
        snapshot_df.to_csv(snapshot_path, index=False)
        print("Saved company_snapshot.csv")
        
        # Scrape other financial data
        scrape_financial_data(financial_url)
        scrape_payout_data(payout_url)
        
        logging.info("Data scraping completed successfully!")
        
    except requests.RequestException as e:
        logging.error(f"Network error occurred: {str(e)}")
        logging.debug(traceback.format_exc())
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        logging.debug(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        symbol = input("Enter stock symbol (default: MARI): ").strip() or "MARI"
        symbol = symbol.upper()
        scrape_company_data(symbol)
    except Exception as e:
        logging.error(f"Script failed: {str(e)}")
        logging.debug(traceback.format_exc())
import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the webpage
url = 'https://sarmaaya.pk/psx/company/THCCL'

# Setting headers to mimic a browser visit
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Sending GET request to fetch the page content
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Locate the performance table
performance_table = soup.find('table', {'class': 'table table-striped table-sm-responsive table-bordered'})
data = []
columns = []

# Extracting table headers
if performance_table:
    headers = performance_table.find_all('th')
    columns = [header.text.strip() for header in headers if header.text.strip() != ""]

    # Extracting table rows
    rows = performance_table.find_all('tr')[2:]
    for row in rows:
        cols = row.find_all('td')
        data.append([col.text.strip() for col in cols])

    # Ensuring the number of columns matches the data
    max_columns = max(len(row) for row in data)
    columns = columns[:max_columns]

    # Create a DataFrame from the scraped data
    df = pd.DataFrame(data, columns=columns)

    # Save to Excel
    df.to_excel('THCCL_Performance.xlsx', index=False)
    print("Data saved to THCCL_Performance.xlsx")
else:
    print("Performance table not found on the webpage.")

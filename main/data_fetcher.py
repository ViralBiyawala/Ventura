import requests
from logging_config import logger 

# data_fetcher.py
def fetch_real_time_data(symbol):
    API_URL = f'https://api.example.com/stock/{symbol}/quote'
    response = requests.get(API_URL)
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch real-time data: {response.status_code}")
        return None

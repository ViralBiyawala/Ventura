import os
import requests
from dotenv import load_dotenv
from logs.logging_config import logger

def fetch_real_time_data(symbol):
    return None
    load_dotenv()

    API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    # url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={API_KEY}'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=1min&apikey={API_KEY}'

    try:
        r = requests.get(url)
        data = r.json()

        if 'Time Series (Daily)' in data:
            # Get the latest bar
            latest_timestamp = max(data['Time Series (Daily)'])
            latest_bar = data['Time Series (Daily)'][latest_timestamp]
            bar_dict = {
                'open': latest_bar['1. open'],
                'high': latest_bar['2. high'],
                'low': latest_bar['3. low'],
                'close': latest_bar['4. close'],
                'volume': latest_bar['5. volume'],
                'timestamp': latest_timestamp
            }
            logger.info(f"Data fetched for {symbol}: {bar_dict}")
            # logger.info(f"Successfully fetched data for {symbol}")
            return bar_dict
        else:
            logger.error(f"No data found for symbol: {symbol}")
            return None

    except Exception as e:
        logger.error(f"Failed to fetch real-time data: {str(e)}")
        return None

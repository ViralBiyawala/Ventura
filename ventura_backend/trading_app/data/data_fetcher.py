import os
import requests
from dotenv import load_dotenv
from ..logs.logging_config import logger

def fetch_real_time_data(symbol):
    return None
    load_dotenv()

    API_KEY_ID = os.getenv('ALPACA_API_KEY')
    API_SECRET_KEY = os.getenv('ALPACA_API_SECRET')
    url = f'https://data.alpaca.markets/v2/stocks/{symbol}/trades/latest?feed=iex'

    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": API_KEY_ID,
        "APCA-API-SECRET-KEY": API_SECRET_KEY
    }

    try:
        r = requests.get(url, headers=headers)
        data = r.json()

        if 'trade' in data:
            trade = data['trade']
            trade_dict = {
                'price': trade['p'],
                'size': trade['s'],
                'timestamp': trade['t'],
                'exchange': trade['x']
            }
            logger.info(f"Data fetched for {symbol}: {trade_dict}")
            return trade_dict
        else:
            logger.error(f"No data found for symbol: {symbol}")
            return None

    except Exception as e:
        logger.error(f"Failed to fetch real-time data: {str(e)}")
        return None

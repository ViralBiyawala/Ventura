import pandas as pd
import ta  # Technical Analysis Library
from logging_config import logger

# data_loader.py
def load_data(data_file):
    try:
        data = pd.read_csv(data_file, parse_dates=['Date'], index_col='Date').sort_index()
        
        data['Close'] = data['Close'].replace('[\$,]', '', regex=True).astype(float)

        # Simple Moving Average (SMA) - 200-day
        data['SMA200'] = data['Close'].rolling(window=200).mean()

        # Exponential Moving Average (EMA) - 26-day
        data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()

        # Relative Strength Index (RSI) - 14-day
        data['RSI14'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()

        # Drop NaN values from the start where moving averages can't be calculated
        data.dropna(inplace=True)
        
        return data
    except FileNotFoundError:
        logger.error(f"File {data_file} not found.")
        return None
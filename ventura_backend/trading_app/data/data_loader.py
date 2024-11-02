import pandas as pd
from ..logs.logging_config import logger
import os

# data_loader.py
def load_data(data_file):
    try:
        data_file = os.path.join(os.path.dirname(__file__), data_file)
        print(data_file)
        data = pd.read_csv(data_file, parse_dates=['Date'], index_col='Date').sort_index()
        
        data['Close'] = data['Close'].replace('[\$,]', '', regex=True).astype(float)
        data['Low'] = data['Low'].replace('[\$,]', '', regex=True).astype(float)
        data['High'] = data['High'].replace('[\$,]', '', regex=True).astype(float)
        data['Open'] = data['Open'].replace('[\$,]', '', regex=True).astype(float)
        data['Volume'] = data['Volume'].replace('[\$,]', '', regex=True).astype(float)

        # Drop NaN values from the start where moving averages can't be calculated
        data.dropna(inplace=True)
        
        return data
    except FileNotFoundError:
        logger.error(f"File {data_file} not found.")
        return None
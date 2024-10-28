import pandas as pd
from logging_config import logger

# data_loader.py
def load_data(data_file):
    try:
        data = pd.read_csv(data_file, parse_dates=True, index_col='Date')
        return data
    except FileNotFoundError:
        logger.error(f"File {data_file} not found.")
        return None
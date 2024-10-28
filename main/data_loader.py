import pandas as pd
from logging_config import logging

# data_loader.py
def load_data(data_file):
    try:
        data = pd.read_csv(data_file, parse_dates=True, index_col='Date')
        return data
    except FileNotFoundError:
        logging.error(f"File {data_file} not found.")
        return None
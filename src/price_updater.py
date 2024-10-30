from environment_creator import update_environment_with_new_data
from data.data_fetcher import fetch_real_time_data

# File: price_updater.py
def fetch_and_update_price(env, symbol):
    real_time_data = fetch_real_time_data(symbol)
    if real_time_data:
        new_price = float(real_time_data['close'])
        update_environment_with_new_data(env, new_price)
    return env.unwrapped.prices[env.unwrapped._current_tick]
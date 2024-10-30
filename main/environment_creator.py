import gymnasium as gym
from logging_config import logger
import pandas as pd

# environment_creator.py
def create_environment(env_data, window_size):
    start_index = window_size
    end_index = len(env_data)
    try:
        env = gym.make('stocks-v0', df=env_data[['Close', 'High', 'Low', 'Open']], window_size=int(window_size), frame_bound=(start_index, end_index))
        env.unwrapped.lows = pd.Series(env_data['Low'])  # Initialize lows attribute
        env.unwrapped.closes = pd.Series(env_data['Close'])  # Initialize closes attribute
        env.unwrapped.highs = pd.Series(env_data['High'])  # Initialize highs attribute
        return env
    except Exception as e:
        logger.error(f"Failed to create environment: {e}")
        return None

    
def update_environment_with_new_data(env, new_data_point):
    env.unwrapped.prices = list(env.unwrapped.prices) + [new_data_point['Close']]
    env.unwrapped._current_tick += 1
    env.unwrapped._end_tick += 1

import gymnasium as gym
from logging_config import logging

# environment_creator.py
def create_environment(data, window_size):
    start_index = window_size
    end_index = len(data)
    try:
        env = gym.make('stocks-v0', df=data, window_size=window_size, frame_bound=(start_index, end_index))
        return env
    except Exception as e:
        logging.error(f"Failed to create environment: {e}")
        return None

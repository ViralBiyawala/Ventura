import gymnasium as gym
from logging_config import logger

# environment_creator.py
def create_environment(data, window_size):
    start_index = window_size
    end_index = len(data)
    try:
        env_data = data[['Close']]
        env = gym.make('stocks-v0', df=env_data, window_size=int(window_size), frame_bound=(start_index, end_index))
        return env
    except Exception as e:
        logger.error(f"Failed to create environment: {e}")
        return None

    
def update_environment_with_new_data(env, new_data_point):
    env.unwrapped.prices = list(env.unwrapped.prices) + [new_data_point]
    env.unwrapped._current_tick += 1
    env.unwrapped._end_tick += 1

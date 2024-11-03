from .trade_executor import execute_trades
from .environment_creator import create_environment
from ..logs.logging_config import logger
from ..ai_model.model_trainer import train_model
from ..data.data_loader import load_data
import cProfile
import pstats

# main.py
def main(data_file="./APPLE_DATA.csv", total_timesteps=1000, initial_balance=100000, trade_fraction=0.7, symbol=None, window_size=14, sptd=390, user_profile=None):
    logger.info("Starting main function with parameters:")
    logger.info(f"data_file: {data_file}, total_timesteps: {total_timesteps}, initial_balance: {initial_balance}, trade_fraction: {trade_fraction}, symbol: {symbol}, window_size: {window_size}, sptd: {sptd}, user_profile: {user_profile}")
    print("Starting main function with parameters:" + f"data_file: {data_file}, total_timesteps: {total_timesteps}, initial_balance: {initial_balance}, trade_fraction: {trade_fraction}, symbol: {symbol}, window_size: {window_size}, sptd: {sptd}, user_profile: {user_profile}")
    from ..config.load_config import window_size, total_timesteps, sptd, stop_loss, take_profit
    data = load_data(data_file)
    if data is None:
        logger.error("Failed to load data.")
        return

    window_size = window_size
    env = create_environment(data, window_size)
    if env is None:
        logger.error("Failed to create environment.")
        return

    logger.info("Observation Space: %s", env.observation_space)

    model = train_model(env, total_timesteps)
    execute_trades(env, model, initial_balance, trade_fraction, symbol = symbol, report_interval="yearly", sptd=sptd, stop_loss=stop_loss, take_profit=take_profit, user_profile=user_profile)

if __name__ == "__main__":
    main()

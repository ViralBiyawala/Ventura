from trade_executor import execute_trades
from data_loader import load_data
from environment_creator import create_environment
from logging_config import logging
from model_trainer import train_model


# main.py
def main(data_file="../AAPL.csv", total_timesteps=1000, initial_balance=1000, trade_fraction=0.50, symbol="AAPL"):
    data = load_data(data_file)
    if data is None:
        return

    window_size = 10
    env = create_environment(data, window_size)
    if env is None:
        return

    logging.info("Observation Space: %s", env.observation_space)

    model = train_model(env, total_timesteps)
    execute_trades(env, model, initial_balance, trade_fraction, symbol)

if __name__ == "__main__":
    main()
import gym_anytrading
from gym_anytrading.envs import Actions
from logging_config import logging
from data_fetcher import fetch_real_time_data
import time

# trade_executor.py
def execute_trades(env, model, initial_balance, trade_fraction, symbol):
    balance = initial_balance
    balance_history = [balance]
    shares_held = 0
    action_stats = {Actions.Sell: 0, Actions.Buy: 0}
    observation, info = env.reset(seed=2024)

    step = 0
    while True:
        action, _states = model.predict(observation)
        
        # Fetch real-time price
        # real_time_data = fetch_real_time_data(symbol)
        # if real_time_data:
        #     current_price = real_time_data['latestPrice']
        # else:
        #     current_price = env.unwrapped.prices[env.unwrapped._current_tick]

        current_price = env.unwrapped.prices[env.unwrapped._current_tick]

        observation, reward, terminated, truncated, info = env.step(action)

        trade_amount = balance * trade_fraction

        if action == Actions.Buy.value:
            shares_to_buy = trade_amount / current_price
            shares_held += shares_to_buy
            balance -= trade_amount
            logging.info(f"{step}: BUY  {shares_to_buy:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        elif action == Actions.Sell.value and shares_held > 0:
            balance += shares_held * current_price
            logging.info(f"{step}: SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            shares_held = 0
        else:
            logging.info(f"{step}: HOLD | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")

        action_stats[Actions(action)] += 1
        balance_history.append(balance)

        step += 1
        if terminated or truncated:
            break

        # Sleep to simulate real-time trading
        # time.sleep(1)

    if shares_held > 0:
        balance += shares_held * current_price
        logging.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        shares_held = 0

    env.close()

    logging.info("Action stats: %s", action_stats)
    logging.info(f"Final Balance: ${balance:.2f}")
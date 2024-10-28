from gym_anytrading.envs import Actions
from logging_config import logger  # Import the logger from logging_config
from data_fetcher import fetch_real_time_data  # Import the fetch_real_time_data function from data_fetcher
import time
from environment_creator import update_environment_with_new_data  # Import the update_environment_with_new_data function from environment_creator

# trade_executor.py
def execute_trades(env, model, initial_balance, trade_fraction, symbol):
    balance = initial_balance
    balance_history = [balance]
    shares_held = 0
    action_stats = {Actions.Sell: 0, Actions.Buy: 0}
    observation, info = env.reset(seed=2024)
    shares_hold = 0
    hold_days = 0

    step = 0
    while True:
        action, _states = model.predict(observation)
        
        # Fetch real-time price
        real_time_data = fetch_real_time_data(symbol)
        if real_time_data:
            new_price  = float(real_time_data['close'])
            update_environment_with_new_data(env, new_price)
        # else:
        #     new_price = env.unwrapped.prices[env.unwrapped._current_tick]

        observation, reward, terminated, truncated, info = env.step(action)
        current_price = env.unwrapped.prices[env.unwrapped._current_tick]

        trade_amount = balance * trade_fraction

        if action == Actions.Buy.value:
            shares_to_buy = int(trade_amount / current_price)
            if shares_to_buy > 0:
                shares_held += shares_to_buy
                balance -= shares_to_buy * current_price
                logger.info(f"{step}: BUY  {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            else:
                logger.info(f"{step}: HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
        elif action == Actions.Sell.value and shares_held > 0:
            balance += shares_held * current_price
            logger.info(f"{step}: SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            shares_held = 0
            # shares_hold -= shares_held
        else:
            hold_days += 1
            shares_hold += shares_held
            logger.info(f"{step}: HOLD {shares_hold} | DAYS {hold_days} | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")

        action_stats[Actions(action)] += 1
        balance_history.append(balance)

        step += 1
        if terminated or truncated:
            break

        # Sleep to simulate real-time trading
        # time.sleep(2)

    if shares_held > 0:
        balance += shares_held * current_price
        logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        shares_held = 0

    env.close()

    logger.info("Action stats: %s", action_stats)
    logger.info(f"Final Balance: ${balance:.2f}")
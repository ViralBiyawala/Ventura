from gym_anytrading.envs import Actions
from logging_config import logger
from data_fetcher import fetch_real_time_data
from environment_creator import update_environment_with_new_data
import numpy as np
from report_generator import save_balance_history_plot, save_balance_sheet_csv
from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

def execute_trades(env, model, initial_balance, trade_fraction, symbol, stop_loss=0.95, take_profit=1.05, report_interval="daily", sptd=390, enable_long_term_investment=True):
    balance = initial_balance
    balance_history = [balance]
    shares_held = 0
    action_stats = {Actions.Sell: 0, Actions.Buy: 0}
    observation, info = env.reset(seed=2021)
    entry_price = None

    # Long-term investment setup
    long_term_fraction = 1 - trade_fraction if enable_long_term_investment else 0
    long_term_investment = initial_balance * long_term_fraction
    long_term_shares = 0
    long_term_entry_done = False

    wins = 0
    losses = 0
    peak_balance = initial_balance
    max_drawdown = 0

    # Initialize indicators
    atr = AverageTrueRange(low=env.unwrapped.lows, close=env.unwrapped.closes, high=env.unwrapped.highs, window=14)
    rsi = RSIIndicator(env.unwrapped.closes, window=14)

    while True:
        action, _states = model.predict(observation)

        # Fetch real-time price
        real_time_data = fetch_real_time_data(symbol)
        if real_time_data:
            new_price = float(real_time_data['close'])
            update_environment_with_new_data(env, new_price)

        observation, reward, terminated, truncated, info = env.step(action)
        current_price = env.unwrapped.prices[env.unwrapped._current_tick]

        # Calculate dynamic stop-loss and take-profit
        current_atr = atr.average_true_range()[env.unwrapped._current_tick]
        current_rsi = rsi.rsi()[env.unwrapped._current_tick]
        dynamic_stop_loss = stop_loss - (current_atr / current_price)
        dynamic_take_profit = take_profit + (current_atr / current_price)

        # Long-term investment setup
        if enable_long_term_investment and not long_term_entry_done:
            long_term_shares = int(long_term_investment / current_price)
            long_term_entry_done = True
            rem_balance = long_term_investment - long_term_shares * current_price
            logger.info(f"Long-term BUY {long_term_shares} shares at ${current_price:.2f} | Balance: ${rem_balance:.2f}")

        # Position sizing based on risk-adjusted returns
        trade_amount = balance * (trade_fraction - ((1 / current_rsi) * trade_fraction))

        # Implement stop-loss and take-profit checks
        if shares_held > 0:
            if current_price <= dynamic_stop_loss * entry_price:
                logger.info(f"STOP-LOSS triggered. Selling {shares_held} shares at ${current_price:.2f}")
                balance += shares_held * current_price
                shares_held = 0
                losses += 1
            elif current_price >= entry_price * dynamic_take_profit:
                logger.info(f"TAKE-PROFIT triggered. Selling {shares_held} shares at ${current_price:.2f}")
                balance += shares_held * current_price
                shares_held = 0
                wins += 1

        # Process actions
        if action == Actions.Buy.value:
            shares_to_buy = int(trade_amount / current_price) if not np.isnan(trade_amount / current_price) else 0
            if shares_to_buy > 0:
                shares_held += shares_to_buy
                balance -= shares_to_buy * current_price
                entry_price = current_price
                logger.info(f"BUY {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            else:
                logger.info(f"HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
        elif action == Actions.Sell.value and shares_held > 0:
            balance += shares_held * current_price
            if current_price > entry_price:
                wins += 1
            else:
                losses += 1
            logger.info(f"SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            shares_held = 0

        action_stats[Actions(action)] += 1

        # Update balance history and drawdown calculations
        balance_history.append(balance)
        total_balance_with_long_term = balance + (long_term_shares * current_price) if enable_long_term_investment else balance
        if total_balance_with_long_term > peak_balance:
            peak_balance = total_balance_with_long_term
        drawdown = (peak_balance - total_balance_with_long_term) / peak_balance
        if drawdown > max_drawdown:
            max_drawdown = drawdown

        if terminated or truncated:
            break

    # Final actions
    if shares_held > 0:
        balance += shares_held * current_price
        logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")

    # Sell long-term shares at the end
    if enable_long_term_investment and long_term_shares > 0:
        balance += long_term_shares * current_price
        logger.info(f"Long-term SELL {long_term_shares} shares at ${current_price:.2f} | Balance: ${balance:.2f}")

    # Calculate metrics
    balance_history = np.array(balance_history)
    daily_returns = np.diff(balance_history) / balance_history[:-1]
    total_return = (balance - initial_balance) / initial_balance
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
    win_loss_ratio = wins / losses if losses > 0 else float('inf')

    logger.info(f"Total Return: {total_return:.2%}")
    logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    logger.info(f"Max Drawdown: {max_drawdown:.2%}")
    logger.info(f"Win/Loss Ratio: {win_loss_ratio:.2f}")
    logger.info(f"Wins: {wins}, Losses: {losses}")

    logger.info("Final Balance: ${:.2f}".format(balance))
    logger.info("Action stats: %s", action_stats)

    env.close()

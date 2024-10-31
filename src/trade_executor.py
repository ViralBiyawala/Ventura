from gym_anytrading.envs import Actions
import numpy as np
from src.indicators import initialize_indicators
from src.price_updater import fetch_and_update_price
from src.levels_calculator import calculate_dynamic_levels
from src.investment_handler import handle_long_term_investment
from src.balance_updater import update_balance_history
from src.metrics_calculator import calculate_metrics
import sys

from report.report_generator import save_balance_history_plot, save_balance_sheet_csv
from logs.logging_config import logger
# File: trade_executor.py
def execute_trade_action(action, current_price, trade_amount, shares_held, balance, entry_price, wins, losses):
    if action == Actions.Buy.value and current_price > 0:
        shares_to_buy = int(trade_amount / current_price) if not np.isnan(trade_amount / current_price) else 0
        if shares_to_buy > 0:
            shares_held += shares_to_buy
            balance -= shares_to_buy * current_price
            entry_price = current_price
            logger.info(f"BUY {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        else:
            logger.info(f"HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
    elif action == Actions.Sell.value and shares_held > 0:
        if current_price > entry_price:
            wins += 1
        else:
            losses += 1
        balance += shares_held * current_price
        logger.info(f"SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        shares_held = 0
    return shares_held, balance, entry_price, wins, losses

# File: trade_executor.py
def execute_trades(env, model, initial_balance, trade_fraction, symbol, stop_loss=0.95, take_profit=1.05, report_interval="daily", sptd=390, enable_long_term_investment=True):
    balance = initial_balance
    balance_history = [balance]
    shares_held = 0
    action_stats = {Actions.Sell: 0, Actions.Buy: 0}
    observation, info = env.reset(seed=2021)
    entry_price = None

    long_term_fraction = 1 - trade_fraction if enable_long_term_investment else 0
    long_term_investment = initial_balance * long_term_fraction
    long_term_shares = 0
    long_term_entry_done = False

    wins = 0
    losses = 0
    peak_balance = initial_balance
    max_drawdown = 0

    atr, rsi = initialize_indicators(env)

    while True:
        action, _states = model.predict(observation)
        current_price = fetch_and_update_price(env, symbol)
        observation, reward, terminated, truncated, info = env.step(action)

        current_atr = atr.average_true_range()[env.unwrapped._current_tick]
        current_rsi = rsi.rsi()[env.unwrapped._current_tick]
        dynamic_stop_loss, dynamic_take_profit = calculate_dynamic_levels(current_price, current_atr, stop_loss, take_profit)

        long_term_shares, long_term_entry_done = handle_long_term_investment(enable_long_term_investment, long_term_entry_done, long_term_investment, current_price, long_term_shares)

        trade_amount = balance * (trade_fraction - ((1 / current_rsi) * trade_fraction))

        if shares_held > 0 and entry_price is not None:
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

        shares_held, balance, entry_price, wins, losses = execute_trade_action(action, current_price, trade_amount, shares_held, balance, entry_price, wins, losses)
        action_stats[Actions(action)] += 1

        balance_history = update_balance_history(balance_history, balance)
        total_balance_with_long_term = balance + (long_term_shares * current_price) if enable_long_term_investment else balance
        if total_balance_with_long_term > peak_balance:
            peak_balance = total_balance_with_long_term
        drawdown = (peak_balance - total_balance_with_long_term) / peak_balance
        if drawdown > max_drawdown:
            max_drawdown = drawdown

        if terminated or truncated:
            break

    if shares_held > 0:
        balance += shares_held * current_price
        logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")

    if enable_long_term_investment and long_term_shares > 0:
        balance += long_term_shares * current_price
        logger.info(f"Long-term SELL {long_term_shares} shares at ${current_price:.2f} | Balance: ${balance:.2f}")

    total_return, sharpe_ratio, win_loss_ratio = calculate_metrics(balance_history, initial_balance, balance, wins, losses)

    logger.info(f"Total Return: {total_return:.2%}")
    logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    logger.info(f"Max Drawdown: {max_drawdown:.2%}")
    logger.info(f"Win/Loss Ratio: {win_loss_ratio:.2f}")
    logger.info(f"Wins: {wins}, Losses: {losses}")

    logger.info("Final Balance: ${:.2f}".format(balance))
    logger.info("Action stats: %s", action_stats)

    env.close()

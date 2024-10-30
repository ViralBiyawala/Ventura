# from gym_anytrading.envs import Actions
# from logging_config import logger
# from data_fetcher import fetch_real_time_data
# from environment_creator import update_environment_with_new_data
# import time
# import numpy as np
# from report_generator import save_balance_history_plot, save_balance_sheet_csv

# def execute_trades(env, model, initial_balance, trade_fraction, symbol, stop_loss=0.85, take_profit=1.05, report_interval="daily", sptd=390):
#     balance = initial_balance
#     balance_history = [balance]
#     shares_held = 0
#     action_stats = {Actions.Sell: 0, Actions.Buy: 0}
#     observation, info = env.reset(seed=2024)
#     liabilities = 0
#     entry_price = None  # To track the price at which the position was entered

#     # Long-term investment setup
#     long_term_fraction = 1 - trade_fraction
#     long_term_investment = initial_balance * long_term_fraction
#     long_term_shares = 0
#     long_term_entry_price = None
#     long_term_entry_done = False

#     step = 0
#     report_step = 0  # To track when to generate reports
#     wins = 0
#     losses = 0
#     peak_balance = initial_balance
#     max_drawdown = 0

#     while True:
#         action, _states = model.predict(observation)

#         # Fetch real-time price
#         real_time_data = fetch_real_time_data(symbol)
#         if real_time_data:
#             new_price = float(real_time_data['close'])
#             update_environment_with_new_data(env, new_price)

#         observation, reward, terminated, truncated, info = env.step(action)
#         current_price = env.unwrapped.prices[env.unwrapped._current_tick]

#         # Long-term investment setup
#         if not long_term_entry_done:
#             long_term_shares = int(long_term_investment / current_price)
#             long_term_entry_price = current_price
#             long_term_entry_done = True
#             rem_balance = long_term_investment - long_term_shares * current_price
#             logger.info(f"Long-term BUY {long_term_shares} shares at ${current_price:.2f} | Balance: ${rem_balance:.2f}")

#         trade_amount = balance * trade_fraction

#         # Implement stop-loss and take-profit checks
#         if shares_held > 0:
#             if current_price <= entry_price * stop_loss:
#                 logger.info(f"{step}: STOP-LOSS triggered. Selling {shares_held} shares at ${current_price:.2f}")
#                 balance += shares_held * current_price
#                 shares_held = 0
#                 losses += 1
#             elif current_price >= entry_price * take_profit:
#                 logger.info(f"{step}: TAKE-PROFIT triggered. Selling {shares_held} shares at ${current_price:.2f}")
#                 balance += shares_held * current_price
#                 shares_held = 0
#                 wins += 1

#         # Process actions
#         if action == Actions.Buy.value:
#             shares_to_buy = int(trade_amount / current_price)
#             if shares_to_buy > 0:
#                 shares_held += shares_to_buy
#                 balance -= shares_to_buy * current_price
#                 entry_price = current_price  # Set the entry price for the position
#                 if step % 10 == 0:
#                     logger.info(f"{step}: BUY {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
#             else:
#                 if step % 10 == 0:
#                     logger.info(f"{step}: HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
#         elif action == Actions.Sell.value and shares_held > 0:
#             balance += shares_held * current_price
#             if current_price > entry_price:
#                 wins += 1
#             else:
#                 losses += 1
#             if step % 10 == 0:
#                 logger.info(f"{step}: SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
#             shares_held = 0

#         action_stats[Actions(action)] += 1

#         # Update balance history and drawdown calculations less frequently
#         if step % 10 == 0:
#             balance_history.append(balance)
#             total_balance_with_long_term = balance + (long_term_shares * current_price)  # Include long-term investment in drawdown calculations
#             if total_balance_with_long_term > peak_balance:
#                 peak_balance = total_balance_with_long_term
#             drawdown = (peak_balance - total_balance_with_long_term) / peak_balance
#             if drawdown > max_drawdown:
#                 max_drawdown = drawdown

#         step += 1
#         report_step += 1

#         if terminated or truncated:
#             break

#     if shares_held > 0:
#         balance += shares_held * current_price
#         logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
#         shares_held = 0

#     # Sell long-term shares at the end
#     if long_term_shares > 0:
#         balance += long_term_shares * current_price
#         logger.info(f"Long-term SELL {long_term_shares} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
#         long_term_shares = 0

#     # Calculate metrics
#     balance_history = np.array(balance_history)
#     daily_returns = np.diff(balance_history) / balance_history[:-1]
#     total_return = (balance - initial_balance) / initial_balance
#     sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)  # Assuming 252 trading days in a year
#     win_loss_ratio = wins / losses if losses > 0 else float('inf')

#     logger.info(f"Total Return: {total_return:.2%}")
#     logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
#     logger.info(f"Max Drawdown: {max_drawdown:.2%}")
#     logger.info(f"Win/Loss Ratio: {win_loss_ratio:.2f}")
#     logger.info(f"Wins: {wins}, Losses: {losses}")

#     logger.info("With Risk Management - Final Balance: ${:.2f}".format(balance))
#     logger.info("With Risk Management - Action stats: %s", action_stats)

#     env.close()

from gym_anytrading.envs import Actions
from logging_config import logger
from data_fetcher import fetch_real_time_data
from environment_creator import update_environment_with_new_data
import time
import numpy as np
from report_generator import save_balance_history_plot, save_balance_sheet_csv

def execute_trades(env, model, initial_balance, trade_fraction, symbol, stop_loss=0.90, take_profit=1.10, report_interval="daily", sptd=390):
    balance = initial_balance
    balance_history = [balance]
    shares_held = 0
    action_stats = {Actions.Sell: 0, Actions.Buy: 0}
    observation, info = env.reset(seed=2024)
    liabilities = 0
    entry_price = None

    # Long-term investment setup
    long_term_fraction = 1 - trade_fraction
    long_term_investment = initial_balance * long_term_fraction
    long_term_shares = 0
    long_term_entry_price = None
    long_term_entry_done = False

    step = 0
    report_step = 0
    wins = 0
    losses = 0
    peak_balance = initial_balance
    max_drawdown = 0

    while True:
        action, _states = model.predict(observation)

        # Fetch real-time price
        real_time_data = fetch_real_time_data(symbol)
        if real_time_data:
            new_price = float(real_time_data['close'])
            update_environment_with_new_data(env, new_price)

        observation, reward, terminated, truncated, info = env.step(action)
        current_price = env.unwrapped.prices[env.unwrapped._current_tick]

        # Long-term investment setup
        if not long_term_entry_done:
            long_term_shares = int(long_term_investment / current_price)
            long_term_entry_price = current_price
            long_term_entry_done = True
            rem_balance = long_term_investment - long_term_shares * current_price
            logger.info(f"Long-term BUY {long_term_shares} shares at ${current_price:.2f} | Balance: ${rem_balance:.2f}")

        trade_amount = balance * trade_fraction

        # Implement stop-loss and take-profit checks
        if shares_held > 0:
            if current_price <= entry_price * stop_loss:
                logger.info(f"{step}: STOP-LOSS triggered. Selling {shares_held} shares at ${current_price:.2f}")
                balance += shares_held * current_price
                shares_held = 0
                losses += 1
            elif current_price >= entry_price * take_profit:
                logger.info(f"{step}: TAKE-PROFIT triggered. Selling {shares_held} shares at ${current_price:.2f}")
                balance += shares_held * current_price
                shares_held = 0
                wins += 1

        # Process actions
        if action == Actions.Buy.value:
            shares_to_buy = int(trade_amount / current_price)
            if shares_to_buy > 0:
                shares_held += shares_to_buy
                balance -= shares_to_buy * current_price
                entry_price = current_price
                if step % 10 == 0:
                    logger.info(f"{step}: BUY {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            else:
                if step % 10 == 0:
                    logger.info(f"{step}: HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
        elif action == Actions.Sell.value and shares_held > 0:
            balance += shares_held * current_price
            if current_price > entry_price:
                wins += 1
            else:
                losses += 1
            if step % 10 == 0:
                logger.info(f"{step}: SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            shares_held = 0

        action_stats[Actions(action)] += 1

        # Update balance history and drawdown calculations
        if step % 10 == 0:
            balance_history.append(balance)
            total_balance_with_long_term = balance + (long_term_shares * current_price)
            if total_balance_with_long_term > peak_balance:
                peak_balance = total_balance_with_long_term
            drawdown = (peak_balance - total_balance_with_long_term) / peak_balance
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        step += 1
        report_step += 1

        if terminated or truncated:
            break

    # Final actions
    if shares_held > 0:
        balance += shares_held * current_price
        logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        shares_held = 0

    # Sell long-term shares at the end
    if long_term_shares > 0:
        balance += long_term_shares * current_price
        logger.info(f"Long-term SELL {long_term_shares} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        long_term_shares = 0

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

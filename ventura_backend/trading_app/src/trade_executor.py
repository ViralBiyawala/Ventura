from gym_anytrading.envs import Actions
import numpy as np
from .indicators import initialize_indicators
from .price_updater import fetch_and_update_price
from .levels_calculator import calculate_dynamic_levels
from .investment_handler import handle_long_term_investment
from .balance_updater import update_balance_history
from .metrics_calculator import calculate_metrics
import sys
import time

from ..report.report_generator import save_balance_history_plot, save_balance_sheet_csv
from ..logs.logging_config import logger
from ..models import Trade, UserProfile, Portfolio

# File: trade_executor.py
def execute_trade_action(action, current_price, trade_amount, shares_held, balance, entry_price, wins, losses, user_profile, symbol=None):
    if action == Actions.Buy.value and current_price > 0:
        shares_to_buy = int(trade_amount / current_price) if not np.isnan(trade_amount / current_price) else 0
        if shares_to_buy > 0:
            shares_held += shares_to_buy
            balance -= (shares_to_buy * current_price)
            entry_price = current_price
            logger.info(f"BUY {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            # Store the trade action in the database
            Trade.objects.create(
                user_profile=user_profile,
                symbol=symbol,
                trade_type="buy",
                current_price=float(current_price),
                quantity=shares_to_buy
            )
            # Update portfolio balance
            portfolio = Portfolio.objects.get(user_profile=user_profile)
            portfolio.market_value -= (shares_to_buy * current_price)
            portfolio.save()
            # assert balance == portfolio.market_value, f"Balance mismatch after BUY: Logged balance = {balance}, Portfolio balance = {portfolio.market_value}"
        else:
            logger.info(f"HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
    elif action == Actions.Sell.value and shares_held > 0:
        if current_price > entry_price:
            wins += 1
        else:
            losses += 1
        balance += (shares_held * current_price)
        logger.info(f"SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        # Store the trade action in the database
        Trade.objects.create(
            user_profile=user_profile,
            symbol=symbol,
            trade_type="sell",
            current_price=float(current_price),
            quantity=shares_held
        )
        # Update portfolio balance
        portfolio = Portfolio.objects.get(user_profile=user_profile)
        portfolio.market_value += (shares_held * current_price)
        portfolio.save()
        # assert balance == portfolio.market_value, f"Balance mismatch after SELL: Logged balance = {balance}, Portfolio balance = {portfolio.market_value}"
        shares_held = 0        
    return shares_held, balance, entry_price, wins, losses

# File: trade_executor.py
def execute_trades(env, model, initial_balance, trade_fraction, symbol, stop_loss=0.95, take_profit=1.05, report_interval="daily", sptd=390, enable_long_term_investment=True, user_profile=None):
    balance = initial_balance
    balance_history = [balance]
    shares_held = 0
    action_stats = {Actions.Sell: 0, Actions.Buy: 0}
    observation, info = env.reset(seed=2021)
    entry_price = None

    portfolio = Portfolio.objects.get(user_profile=user_profile)
    portfolio.market_value += balance  # Correctly add the new investment amount
    portfolio.save()

    long_term_fraction = 1 - trade_fraction if enable_long_term_investment else 0
    long_term_investment = balance * long_term_fraction
    long_term_shares = 0
    rem_balance = 0
    long_term_entry_done = False

    balance -= long_term_investment  # Deduct the long-term investment amount from the balance

    wins = 0
    losses = 0
    peak_balance = balance
    max_drawdown = 0
    trade_amount = balance * (trade_fraction)

    atr, rsi = initialize_indicators(env)

    while True:
        action, _states = model.predict(observation)
        current_price = fetch_and_update_price(env, symbol)
        observation, reward, terminated, truncated, info = env.step(action)

        current_atr = atr.average_true_range()[env.unwrapped._current_tick]
        current_rsi = rsi.rsi()[env.unwrapped._current_tick]
        dynamic_stop_loss, dynamic_take_profit = calculate_dynamic_levels(current_price, current_atr, stop_loss, take_profit)

        long_term_shares, long_term_entry_done, rem_balance = handle_long_term_investment(enable_long_term_investment, long_term_entry_done, long_term_investment, current_price, long_term_shares, user_profile, symbol, rem_balance)

        trade_amount = balance * (0.9)  # Rebalance the trade amount after each trade and keep 10% as buffer

        if shares_held > 0 and entry_price is not None:
            if current_price <= dynamic_stop_loss * entry_price:
                logger.info(f"STOP-LOSS triggered. Selling {shares_held} shares at ${current_price:.2f}")
                balance += (shares_held * current_price)
                losses += 1
                # Update portfolio balance
                portfolio = Portfolio.objects.get(user_profile=user_profile)
                portfolio.market_value += (shares_held * current_price)
                portfolio.save()
                # assert balance == portfolio.market_value, f"Balance mismatch after STOP-LOSS: Logged balance = {balance}, Portfolio balance = {portfolio.market_value}"
                shares_held = 0
            elif current_price >= entry_price * dynamic_take_profit:
                logger.info(f"TAKE-PROFIT triggered. Selling {shares_held} shares at ${current_price:.2f}")
                balance += (shares_held * current_price)
                wins += 1
                # Update portfolio balance
                portfolio = Portfolio.objects.get(user_profile=user_profile)
                portfolio.market_value += (shares_held * current_price)
                portfolio.save()
                # assert balance == portfolio.market_value, f"Balance mismatch after TAKE-PROFIT: Logged balance = {balance}, Portfolio balance = {portfolio.market_value}"
                shares_held = 0

        shares_held, balance, entry_price, wins, losses = execute_trade_action(action, current_price, trade_amount, shares_held, balance, entry_price, wins, losses, user_profile, symbol)
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

        # time.sleep(30) # Sleep for 30 seconds before fetching the next price

    if shares_held > 0:
        balance += (shares_held * current_price)
        logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        portfolio = Portfolio.objects.get(user_profile=user_profile)
        portfolio.market_value += (shares_held * current_price)
        portfolio.save()
        # assert balance == portfolio.market_value, f"Balance mismatch after final SELL: Logged balance = {balance}, Portfolio balance = {portfolio.market_value}"

    if enable_long_term_investment and long_term_shares > 0:
        balance += (long_term_shares * current_price)
        balance += rem_balance
        logger.info(f"Long-term SELL {long_term_shares} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
        portfolio = Portfolio.objects.get(user_profile=user_profile)
        portfolio.market_value += (long_term_shares * current_price)
        portfolio.save()
        # assert balance == portfolio.market_value, f"Balance mismatch after long-term SELL: Logged balance = {balance}, Portfolio balance = {portfolio.market_value}"


    total_return, sharpe_ratio, win_loss_ratio = calculate_metrics(balance_history, initial_balance, balance, wins, losses)

    logger.info(f"Total Return: {total_return:.2%}")
    logger.info(f"Sharpe Ratio: {sharpe_ratio:.2f}")
    logger.info(f"Max Drawdown: {max_drawdown:.2%}")
    logger.info(f"Win/Loss Ratio: {win_loss_ratio:.2f}")
    logger.info(f"Wins: {wins}, Losses: {losses}")

    logger.info("Final Balance: ${:.2f}".format(balance))
    logger.info("Action stats: %s", action_stats)

    env.close()

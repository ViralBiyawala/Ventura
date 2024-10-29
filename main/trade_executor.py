from gym_anytrading.envs import Actions
from logging_config import logger
from data_fetcher import fetch_real_time_data
from environment_creator import update_environment_with_new_data
import time
from report_generator import save_balance_history_plot, save_balance_sheet_csv

def execute_trades(env, model, initial_balance, trade_fraction, symbol, stop_loss=0.85, take_profit=1.05, report_interval="daily", sptd=390):
    def run_simulation(use_risk_management):
        balance = initial_balance
        balance_history = [balance]
        shares_held = 0
        action_stats = {Actions.Sell: 0, Actions.Buy: 0}
        observation, info = env.reset(seed=2024)
        liabilities = 0
        entry_price = None  # To track the price at which the position was entered

        step = 0
        report_step = 0  # To track when to generate reports
        while True:
            action, _states = model.predict(observation)

            # Fetch real-time price
            real_time_data = fetch_real_time_data(symbol)
            if real_time_data:
                new_price = float(real_time_data['close'])
                update_environment_with_new_data(env, new_price)

            observation, reward, terminated, truncated, info = env.step(action)
            current_price = env.unwrapped.prices[env.unwrapped._current_tick]

            trade_amount = balance * trade_fraction

            # Implement stop-loss and take-profit checks
            if use_risk_management and shares_held > 0:
                if current_price <= entry_price * stop_loss:
                    logger.info(f"{step}: STOP-LOSS triggered. Selling {shares_held} shares at ${current_price:.2f}")
                    balance += shares_held * current_price
                    shares_held = 0
                elif current_price >= entry_price * take_profit:
                    logger.info(f"{step}: TAKE-PROFIT triggered. Selling {shares_held} shares at ${current_price:.2f}")
                    balance += shares_held * current_price
                    shares_held = 0

            # Process actions
            if action == Actions.Buy.value:
                shares_to_buy = int(trade_amount / current_price)
                if shares_to_buy > 0:
                    shares_held += shares_to_buy
                    balance -= shares_to_buy * current_price
                    entry_price = current_price  # Set the entry price for the position
                    logger.info(f"{step}: BUY {shares_to_buy} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
                else:
                    logger.info(f"{step}: HOLD (Insufficient funds to buy shares) | Current price: ${current_price:.2f} | Balance: ${balance:.2f}")
            elif action == Actions.Sell.value and shares_held > 0:
                balance += shares_held * current_price
                logger.info(f"{step}: SELL {shares_held} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
                shares_held = 0

            action_stats[Actions(action)] += 1
            balance_history.append(balance)

            step += 1
            report_step += 1

            # Generate balance report and balance sheet at intervals (daily or weekly)
            if report_interval == "daily" and report_step >= sptd:  # Assuming 390 steps per trading day
                # save_balance_report(balance_history, action_stats, report_type="daily")
                save_balance_sheet_csv(balance, shares_held, current_price, liabilities, initial_balance=initial_balance * trade_fraction, report_type="daily")
                # save_balance_history_plot(balance_history, report_type="daily")
                report_step = 0
            elif report_interval == "weekly" and report_step >= (sptd * 5):  # Assuming 5 trading days per week
                # save_balance_report(balance_history, action_stats, report_type="weekly")
                save_balance_sheet_csv(balance, shares_held, current_price, liabilities, initial_balance=initial_balance*trade_fraction, report_type="weekly")
                # save_balance_history_plot(balance_history, report_type="weekly")
                report_step = 0
            elif report_interval == "yearly" and report_step >= (sptd * 5 * 12):  # Assuming 5 trading days per week
                # save_balance_report(balance_history, action_stats, report_type="weekly")
                save_balance_sheet_csv(balance, shares_held, current_price, liabilities, initial_balance=initial_balance*trade_fraction, report_type="yearly")
                # save_balance_history_plot(balance_history, report_type="yearly")
                report_step = 0

            if terminated or truncated:
                break

        if shares_held > 0:
            balance += shares_held * current_price
            logger.info(f"Final SELL {shares_held:.2f} shares at ${current_price:.2f} | Balance: ${balance:.2f}")
            shares_held = 0

        return balance, balance_history, action_stats

    # Run simulation with risk management
    balance_with_risk, balance_history_with_risk, action_stats_with_risk = run_simulation(use_risk_management=True)
    logger.info("With Risk Management - Final Balance: ${:.2f}".format(balance_with_risk))
    logger.info("With Risk Management - Action stats: %s", action_stats_with_risk)

    env.close()

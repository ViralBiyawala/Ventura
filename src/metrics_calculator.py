import numpy as np

# File: metrics_calculator.py
def calculate_metrics(balance_history, initial_balance, balance, wins, losses):
    balance_history = np.array(balance_history)
    daily_returns = np.diff(balance_history) / balance_history[:-1]
    total_return = (balance - initial_balance) / initial_balance
    sharpe_ratio = np.mean(daily_returns) / np.std(daily_returns) * np.sqrt(252)
    win_loss_ratio = wins / losses if losses > 0 else float('inf')
    return total_return, sharpe_ratio, win_loss_ratio

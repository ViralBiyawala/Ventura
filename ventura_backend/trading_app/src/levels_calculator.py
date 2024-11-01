# File: levels_calculator.py
def calculate_dynamic_levels(current_price, current_atr, stop_loss, take_profit):
    dynamic_stop_loss = stop_loss - (current_atr / current_price)
    dynamic_take_profit = take_profit + (current_atr / current_price)
    return dynamic_stop_loss, dynamic_take_profit
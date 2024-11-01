from ta.volatility import AverageTrueRange
from ta.momentum import RSIIndicator

# File: indicators.py
def initialize_indicators(env):
    atr = AverageTrueRange(low=env.unwrapped.lows, close=env.unwrapped.closes, high=env.unwrapped.highs, window=14)
    rsi = RSIIndicator(env.unwrapped.closes, window=14)
    return atr, rsi
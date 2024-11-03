from ..logs.logging_config import logger
from ..models import Trade, Portfolio

# File: investment_handler.py
def handle_long_term_investment(enable_long_term_investment, long_term_entry_done, long_term_investment, current_price, long_term_shares, user_profile, symbol, rem_balance):
    if enable_long_term_investment and long_term_entry_done == False:
        long_term_shares = int(long_term_investment / current_price)
        long_term_entry_done = True
        rem_balance = long_term_investment - (long_term_shares * current_price)
        logger.info(f"Long-term BUY {long_term_shares} shares at ${current_price:.2f} | Balance: ${rem_balance:.2f}")
        
        # Store the trade action in the database
        Trade.objects.create(
            user_profile=user_profile,
            symbol=symbol,
            trade_type="buy",
            current_price=float(current_price),
            quantity=long_term_shares
        )

        # Update portfolio balance
        portfolio = Portfolio.objects.get(user_profile=user_profile)
        portfolio.market_value -= (long_term_shares * current_price)
        portfolio.save()
    return long_term_shares, long_term_entry_done, rem_balance

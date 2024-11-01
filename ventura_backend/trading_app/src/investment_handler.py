from ..logs.logging_config import logger

# File: investment_handler.py
def handle_long_term_investment(enable_long_term_investment, long_term_entry_done, long_term_investment, current_price, long_term_shares):
    if enable_long_term_investment and long_term_entry_done == False:
        long_term_shares = int(long_term_investment / current_price)
        long_term_entry_done = True
        rem_balance = long_term_investment - long_term_shares * current_price
        logger.info(f"Long-term BUY {long_term_shares} shares at ${current_price:.2f} | Balance: ${rem_balance:.2f}")
    return long_term_shares, long_term_entry_done

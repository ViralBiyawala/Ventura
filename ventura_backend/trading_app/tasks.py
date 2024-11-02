from celery import shared_task
from .src.main import main as start_trading
from .models import UserProfile
from .logs.logging_config import logger

@shared_task()
def start_trading_task(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, user_profile_id):
    logger.info(f"Task started with parameters: data_file={data_file}, total_timesteps={total_timesteps}, initial_balance={initial_balance}, trade_fraction={trade_fraction}, symbol={symbol}, window_size={window_size}, sptd={sptd}, user_profile_id={user_profile_id}")
    
    # Ensure the user profile exists
    try:
        user_profile = UserProfile.objects.get(id=user_profile_id)
    except UserProfile.DoesNotExist:
        logger.error(f"UserProfile with id {user_profile_id} does not exist.")
        return

    # Call the execute_trades function
    try:
        logger.info("Calling execute_trades function.")
        start_trading(data_file, total_timesteps, initial_balance, trade_fraction, symbol, window_size, sptd, user_profile)
        logger.info("Task completed.")
    except Exception as e:
        logger.error(f"Error executing trades: {e}")

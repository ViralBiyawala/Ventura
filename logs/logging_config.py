import logging
import logging.handlers
import os

# Create a logs directory if it doesn't exist
log_directory = '..\logs\logs'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging
log_file = os.path.join(log_directory, 'simulation_api.log')
handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10**256, backupCount=5)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(handler)

import logging

# logging_config.py
# Configure logging to write to a file
logging.basicConfig(filename='simulation.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

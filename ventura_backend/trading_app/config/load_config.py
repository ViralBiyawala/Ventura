import yaml
import os

# Get the absolute path to the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the config.yaml file
config_path = os.path.join(current_dir, 'config.yaml')

# Load the config.yaml file
with open(config_path, 'r') as file:
    config = yaml.safe_load(file)

# Access parameters
window_size = config['environment']['window_size']
total_timesteps = config['environment']['total_timesteps']
sptd = config['environment']['sptd']

stop_loss = config['risk_management']['stop_loss']
take_profit = config['risk_management']['take_profit']

learning_rate = config['model']['learning_rate']
policy = config['model']['policy']

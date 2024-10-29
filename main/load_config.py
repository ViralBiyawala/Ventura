import yaml

# Load the config.yaml file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Access parameters
window_size = config['environment']['window_size']
total_timesteps = config['environment']['total_timesteps']
sptd = config['environment']['sptd']

stop_loss = config['risk_management']['stop_loss']
take_profit = config['risk_management']['take_profit']

learning_rate = config['model']['learning_rate']
policy = config['model']['policy']

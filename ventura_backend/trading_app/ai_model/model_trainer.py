from stable_baselines3 import PPO, A2C, DDPG, SAC

# model_trainer.py
def train_model(env, total_timesteps, algorithm='PPO', save_path='trained_model'):
    from ..config.load_config import learning_rate, policy
    
    algorithms = {
        'PPO': PPO,
        'A2C': A2C
    }
    
    if algorithm not in algorithms:
        raise ValueError(f"Unsupported algorithm: {algorithm}. Choose from {list(algorithms.keys())}")
    
    model_class = algorithms[algorithm]
    model = model_class(policy, env, verbose=0)
    model.learn(total_timesteps=total_timesteps)
    
    # Save the trained model
    model.save(save_path)
    
    return model

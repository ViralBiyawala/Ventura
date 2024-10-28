
from stable_baselines3 import PPO


# model_trainer.py
def train_model(env, total_timesteps):
    from load_config import learning_rate, policy
    model = PPO(policy, env, verbose=0)
    model.learn(total_timesteps=total_timesteps)
    return model

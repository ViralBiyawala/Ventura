
from stable_baselines3 import PPO

# model_trainer.py
def train_model(env, total_timesteps):
    model = PPO('MlpPolicy', env, verbose=0)
    model.learn(total_timesteps=total_timesteps)
    return model

import gymnasium as gym
from gymnasium.envs.registration import register
from gymnasium.utils.env_checker import check_env

register(
    id="pokemon-blue-gym-v1",
    entry_point="learning.pokemon_world_env:PokemonWorldEnv",
)

def Train():
    env = gym.make("pokemon-blue-gym-v1")

    # Reset environment to start a new episode
    observation, info = env.reset()

    print("Checking environment...")
    check_env(env.unwrapped)  
    print("Environment looks good!")

    print(f"Starting observation: {observation}")

    episode_over = False
    total_reward = 0

    while not episode_over:
        # Choose an action: 0 = push cart left, 1 = push cart right
        action = env.action_space.sample()  # Random action for now - real agents will be smarter!

        # Take the action and see what happens
        observation, reward, terminated, truncated, info = env.step(action)

        total_reward += reward
        episode_over = terminated or truncated

    print(f"Episode finished! Total reward: {total_reward}")
    env.close()
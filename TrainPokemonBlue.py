
import os
import threading
import gymnasium as gym
import memory_maps.pokemon_red_blue as mm


from learning import pokemon_gymnasium

from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from flask import Flask, jsonify, render_template

app = Flask(__name__)
env = pokemon_gymnasium.GetGym()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/state")
def state():
    latest_state = mm.read_game_state(env.unwrapped.pyboy)
    latest_state["current_reward"] = env.unwrapped.total_reward
    return jsonify(latest_state)

def start_webserver():
    app.run(port=5000)

flask_thread = threading.Thread(target=start_webserver, daemon=True)
flask_thread.start()

if __name__ == "__main__":
    models_dir = "models/PPO"
    logdir = "logs"

    if not os.path.exists("models"):
        os.makedirs("models")
    if not os.path.exists(logdir):
        os.makedirs(logdir)
    if not os.path.exists(models_dir):        
        os.makedirs(models_dir)

    run = 0
    while run < 10:
    
        run += 1
        print(f"Starting run {run}")

        env = pokemon_gymnasium.GetGym()

        checkpoint_callback = CheckpointCallback(
            save_freq=10000,
            save_path=models_dir,
            name_prefix="ppo_model"
        )
        
        model_output_path = os.path.join(models_dir, "ppo_final_model.zip")

        if os.path.exists(model_output_path):
            model = PPO.load(
                model_output_path,
                env,
                verbose=1,
                tensorboard_log=logdir,
                device="auto"
            )
        else:
            model = PPO(
                "MlpPolicy",
                env,
                verbose=1,
                tensorboard_log=logdir,
                device="auto"
            )

        model.learn(total_timesteps=1_000_000, callback=checkpoint_callback)

        model.save(model_output_path)

        env.close()



import os
import threading
import gymnasium as gym
import memory_maps.pokemon_red_blue as mm


from learning import pokemon_gymnasium
from learning.callbacks import StateCheckpointCallback

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import SubprocVecEnv


from flask import Flask, jsonify, render_template

app = Flask(__name__)
checkpoint_callback = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/template/environment")
def environment_template():
    return render_template("environment.html")

@app.route("/template/party")
def party_template():
    return render_template("party.html")

@app.route("/state")
def state():
    if not checkpoint_callback == None:
        checkpoint_callback.latest_states
        return jsonify(checkpoint_callback.latest_states)
    return jsonify([])

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

    environments = 8
    env =  SubprocVecEnv([ pokemon_gymnasium.MakeGym(seed=i) for i in range(environments) ])

    checkpoint_callback = StateCheckpointCallback(
        save_freq=10000,
        save_path=models_dir,
        name_prefix="ppo_model",
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
            n_steps=2048,
            batch_size=64,
            device="auto"
        )

    model.learn(total_timesteps=1_000_000, callback=checkpoint_callback)

    model.save(model_output_path)

    env.close()


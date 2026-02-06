import threading
import Emulator
import memory_maps.pokemon_red_blue as mm

from controllers import RandomController
from flask import Flask, jsonify, render_template

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
    global latest_state
    return jsonify([latest_state])

def start_webserver():
    app.run(port=5000)

def emulate():
    global latest_state

    pyboy = Emulator.emulate("roms/Pokemon - Blue Version.gb", 3, False)    
    Emulator.load_specific_state(pyboy, "reset")
    while True:
        #key = RandomController.PickControl()
        #Emulator.press_button(pyboy, key)
        pyboy.tick()
        latest_state = mm.read_game_state(pyboy)

runThread = threading.Thread(target=emulate, daemon=True)
runThread.start()

app.run(port=5000)
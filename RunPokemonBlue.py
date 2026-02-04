import threading
import Emulator
import memory_maps.pokemon_red_blue as mm

from controllers import RandomController
from flask import Flask, jsonify, render_template

app = Flask(__name__)
latest_state = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/state")
def state():
    return jsonify(latest_state)

def emulate():
    global latest_state

    pyboy = Emulator.emulate("roms/Pokemon - Blue Version.gb", 3, False)    
    while True:
        #key = RandomController.PickControl()
        #Emulator.press_button(pyboy, key)
        pyboy.tick()
        latest_state = mm.read_game_state(pyboy)

runThread = threading.Thread(target=emulate, daemon=True)
runThread.start()

app.run(port=5000)
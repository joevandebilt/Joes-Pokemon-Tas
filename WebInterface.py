
from flask import Flask, jsonify, render_template
import memory_maps.pokemon_red_blue as mm

app = Flask(__name__)
pyboy = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/state")
def state():
    global pyboy
    latest_state = mm.read_game_state(pyboy)
    return jsonify(latest_state)

def start_webserver(pyboy_pointer):
    global pyboy
    pyboy = pyboy_pointer
    app.run(port=5000)
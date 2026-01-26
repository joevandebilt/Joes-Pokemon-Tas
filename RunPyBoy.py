from pyboy import PyBoy
from pyboy.utils import WindowEvent
from random import randrange
from flask import Flask, jsonify
import threading
import time
import asyncio


app = Flask(__name__)

POKEMON_CHAR_MAP = {
    0x80: "A", 0x81: "B", 0x82: "C", 0x83: "D", 0x84: "E",
    0x85: "F", 0x86: "G", 0x87: "H", 0x88: "I", 0x89: "J",
    0x8A: "K", 0x8B: "L", 0x8C: "M", 0x8D: "N", 0x8E: "O",
    0x8F: "P", 0x90: "Q", 0x91: "R", 0x92: "S", 0x93: "T",
    0x94: "U", 0x95: "V", 0x96: "W", 0x97: "X", 0x98: "Y",
    0x99: "Z",
    0x7F: " ",   # space
}

def emulate():
    
    pyboy = PyBoy("Pokemon - Blue Version.gb")
    pyboy.set_emulation_speed(0)    #No speed limit

    #Press A once every 60 frames
    while pyboy.tick():
            
            match randrange(8):
                case 0:
                    press = WindowEvent.PRESS_BUTTON_A
                    release = WindowEvent.RELEASE_BUTTON_A
                case 1:
                    press = WindowEvent.PRESS_BUTTON_B
                    release = WindowEvent.RELEASE_BUTTON_B
                case 2:
                    press = WindowEvent.PRESS_BUTTON_START
                    release = WindowEvent.RELEASE_BUTTON_START
                case 3:
                    press = WindowEvent.PRESS_BUTTON_SELECT
                    release = WindowEvent.RELEASE_BUTTON_SELECT
                case 4:
                    press = WindowEvent.PRESS_ARROW_UP
                    release = WindowEvent.RELEASE_ARROW_UP
                case 5:
                    press = WindowEvent.PRESS_ARROW_DOWN
                    release = WindowEvent.RELEASE_ARROW_DOWN
                case 6:
                    press = WindowEvent.PRESS_ARROW_LEFT
                    release = WindowEvent.RELEASE_ARROW_LEFT
                case 7:
                    press = WindowEvent.PRESS_ARROW_RIGHT
                    release = WindowEvent.RELEASE_ARROW_RIGHT
                

            pyboy.send_input(press)
            for _ in range(5):
                pyboy.tick()
            pyboy.send_input(release)
            monitor(pyboy)

    pyboy.stop()

@app.route("/state")
def state():
    return jsonify(latest_state)

def monitor(pyboy):
    global latest_state
    latest_state = read_game_state(pyboy)

def read_game_state(pyboy):
    return {
        "map": pyboy.memory[0xD35E],
        "x": pyboy.memory[0xD361],
        "y": pyboy.memory[0xD362],
        "player_name": read_pokemon_string(pyboy, 0xD158, 4),
        "in_battle": pyboy.memory[0xD057] != 0,
        "party_count": pyboy.memory[0xD163],
        "pokemon": [
            {
                "species": pyboy.memory[0xD164], #decimal version of hex ID, needs mapping
                "level": pyboy.memory[0xD18C],
                "hp": read_u16(pyboy, 0xD16C, 2),
                "max_hp": read_u16(pyboy, 0xD18D, 2),
                "exp": read_u24(pyboy, 0xD179)
            }
        ]
    }

def read_pokemon_string(pyboy, start_addr, max_len=16):
    chars = []

    for i in range(max_len):
        byte = pyboy.memory[start_addr + i]

        if byte == 0x50:  # String terminator
            break

        chars.append(POKEMON_CHAR_MAP.get(byte, "?"))

    return "".join(chars)

def read_u16(pyboy, addr):
    return int.from_bytes(
        bytes(pyboy.memory[addr:addr+2]),
        "little"
    )

def read_u24(pyboy, addr):
    b = pyboy.memory[addr:addr+3]
    return b[0] + (b[1] << 8) + (b[2] << 16)

t1 = threading.Thread(target=emulate, daemon=True)
t1.start()

app.run(port=5000)
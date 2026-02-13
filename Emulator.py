import os
import shutil
import threading
import datetime as dt

from pyboy import PyBoy
from pyboy.utils import WindowEvent
from pathlib import Path
from random import randint

from learning.actions import GameboyAction

PyBoyButton = {
    "A": WindowEvent.PRESS_BUTTON_A,
    "B": WindowEvent.PRESS_BUTTON_B,
    "UP": WindowEvent.PRESS_ARROW_UP,
    "DOWN": WindowEvent.PRESS_ARROW_DOWN,
    "LEFT": WindowEvent.PRESS_ARROW_LEFT,
    "RIGHT": WindowEvent.PRESS_ARROW_RIGHT,
    "START": WindowEvent.PRESS_BUTTON_START,
    "SELECT": WindowEvent.PRESS_BUTTON_SELECT,
    GameboyAction.A: WindowEvent.PRESS_BUTTON_A,
    GameboyAction.B: WindowEvent.PRESS_BUTTON_B,
    GameboyAction.UP: WindowEvent.PRESS_ARROW_UP,
    GameboyAction.DOWN: WindowEvent.PRESS_ARROW_DOWN,
    GameboyAction.LEFT: WindowEvent.PRESS_ARROW_LEFT,
    GameboyAction.RIGHT: WindowEvent.PRESS_ARROW_RIGHT,
    GameboyAction.START: WindowEvent.PRESS_BUTTON_START,
    GameboyAction.SELECT: WindowEvent.PRESS_BUTTON_SELECT
}

def emulate(romPath, speed=2, useQuickSaves=True, headless=False):
    window = "SDL2"
    if headless:
        window = "null"

    seed = randint(0, 9999)
    workingRomPath = f"{romPath}_{seed}.gb"
    
    if os.path.exists(romPath) and not os.path.exists(workingRomPath):
        shutil.copyfile(romPath, workingRomPath)

    pyboy = PyBoy(workingRomPath, sound_volume=0, sound_emulated=False, window=window)
    pyboy.set_emulation_speed(speed)    #No speed limit

    if useQuickSaves:
        quick_load(pyboy)

        saveThread = threading.Thread(target=save_thread, args=(pyboy,), daemon=True)
        saveThread.start()

    return pyboy

def save_thread(pyboy):
    last_save_time = dt.datetime.now()
    while True:
        now = dt.datetime.now()
        if (now - last_save_time).total_seconds() > 60:
            quick_save(pyboy)
            last_save_time = now
            print("Game state saved at ", now.strftime("%Y-%m-%d %H:%M:%S"))
    

def quick_save(pyboy):
    with open("save_states/quick_state.state", "wb") as f:
        pyboy.save_state(f)

def quick_load(pyboy):
    load_specific_state(pyboy, "quick_state")

def load_specific_state(pyboy, stateName):
    filepath = f"save_states/{stateName}.state"
    if not os.path.exists(filepath):
        return
    
    with open(filepath, "rb") as f:
        pyboy.load_state(f)

def press_button(pyboy, button, render=False):
    pyboy.send_input(button)
    pyboy.tick(30, render)
    pyboy.send_input(button + 8)  # RELEASE 
    pyboy.tick(30, render)

def switch_off(pyboy):
    romPath = pyboy.gamerom
    ramPath = romPath+'.ram'
    pyboy.stop()
    if os.path.exists(romPath):
        os.remove(romPath)
    if os.path.exists(ramPath):
        os.remove(ramPath)
    

    
    
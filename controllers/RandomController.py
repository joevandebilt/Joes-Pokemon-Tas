from pyboy.utils import WindowEvent
from random import randrange

def PickControl():
    match randrange(8):
        case 0:
            return WindowEvent.PRESS_BUTTON_A
        case 1:
            return WindowEvent.PRESS_BUTTON_B
        case 2:
            return WindowEvent.PRESS_BUTTON_START
        case 3:
            return WindowEvent.PRESS_BUTTON_SELECT
        case 4:
            return WindowEvent.PRESS_ARROW_UP
        case 5:
            return WindowEvent.PRESS_ARROW_DOWN
        case 6:
            return WindowEvent.PRESS_ARROW_LEFT
        case 7:
            return WindowEvent.PRESS_ARROW_RIGHT
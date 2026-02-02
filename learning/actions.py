from enum import Enum

class GameboyAction(Enum):
    NO_OP = 0
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4
    A = 5
    B = 6
    START = 7
    SELECT = 8
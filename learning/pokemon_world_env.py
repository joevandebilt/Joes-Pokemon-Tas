import gymnasium as gym
from gymnasium import spaces
from learning.actions import GameboyAction

import Emulator as Emulator
import memory_maps.pokemon_red_blue as mm
import numpy as np

class PokemonWorldEnv(gym.Env):

    metadata = {"render_modes": ["human"], "render_fps": 30 }
    pyboy = None

    def __init__(self, render_mode=None):

        self.pyboy = Emulator.emulate("roms/Pokemon - Blue Version.gb", 0, False)

        self.render_mode = render_mode

        self.action_space = spaces.Discrete(len(GameboyAction))
               
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(6,),
            dtype=np.int32
        )

        self.steps_taken = 0
    
    def _get_obs(self):
        world_state = mm.read_game_state(self.pyboy)

        return np.array([
            world_state["in_battle"],
            world_state["x"],
            world_state["y"],
            world_state["map"],
            world_state["party_count"],
            world_state["pokemon"][0]["level"],
            world_state["pokemon"][1]["level"],
            world_state["pokemon"][2]["level"],
            world_state["pokemon"][3]["level"],
            world_state["pokemon"][4]["level"],
            world_state["pokemon"][5]["level"]
        ], dtype=np.int32)
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        Emulator.load_specific_state(self.pyboy, "reset")

        #Additional info to return for debugging or whatever
        info = {}

        if self.render_mode == "human":
            self.render()

        return self._get_obs(), info
    
    def perform_action(self, action: GameboyAction):
        if action == GameboyAction.NO_OP:
            return
        else:
            button = Emulator.PyBoyButton.get(action)
            Emulator.press_button(self.pyboy, button)
    
    def step(self, action):
        action_enum = GameboyAction(action)
        self.perform_action(action_enum)

        self.steps_taken += 1

        obs = self._get_obs()

        reward = self.calulate_reward(obs)
        terminated = False

        info = {}

        if (self.render_mode == "human"):
            self.render()

        truncate = False
        if self.steps_taken > 100000:
            truncate = True

        return obs, reward, terminated, truncate, info
    
    def render(self):
        return

    # REWARDS
    def calulate_reward(self, obs):
        reward = 0

        reward += self.new_tile_reward(obs)
        reward += self.level_up_reward(obs)

        return reward


    def new_tile_reward(self, obs):
        reward = 0

        current_tile = (obs[1], obs[2], obs[3])  # x, y, map

        if not hasattr(self, "visited_tiles"):
            self.visited_tiles = set()

        if current_tile not in self.visited_tiles:
            self.visited_tiles.add(current_tile)
            reward += 1  # Reward for visiting a new tile

        return reward
    
    def level_up_reward(self, obs):
        reward = 0

        current_level = obs[5]  # First Pokemon's level

        if not hasattr(self, "last_level"):
            self.last_level = current_level

        if current_level > self.last_level:
            reward += (current_level - self.last_level) * 10  # Reward for leveling up
            self.last_level = current_level

        return reward
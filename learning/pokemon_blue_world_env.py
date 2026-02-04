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

        self.pyboy = Emulator.emulate("roms/Pokemon - Blue Version.gb", 0, False, False)

        self.render_mode = render_mode

        self.action_space = spaces.Discrete(len(GameboyAction))
               
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(14,),
            dtype=np.int32
        )

        self.steps_taken = 0

        self.total_reward = 0
    
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
            world_state["pokemon"][5]["level"],
            world_state["events"]["oaks_parcel"],
            world_state["events"]["pokedex"],
            world_state["events"]["brock"],
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
        self.total_reward += reward

        info = {}

        if (self.render_mode == "human"):
            self.render()

        terminated = obs[13] == 1
        truncate = False

        return obs, reward, terminated, truncate, info
    
    def render(self):
        return
    
    def close(self):
        self.pyboy.stop()        

    # REWARDS
    def calulate_reward(self, obs):
        reward = 0

        reward += self.new_map_reward(obs)
        reward += self.new_tile_reward(obs)
        reward += self.level_up_reward(obs)
        reward += self.oaks_parcel_collected(obs)
        reward += self.pokedex_collected(obs)
        reward += self.first_badge_collected(obs)

        reward -= self.standing_still(obs)

        return reward


    #1 reward for new tile
    def new_tile_reward(self, obs):
        reward = 0

        current_tile = (obs[1], obs[2], obs[3])  # x, y, map

        if not hasattr(self, "visited_tiles"):
            self.visited_tiles = set()

        if current_tile not in self.visited_tiles:
            self.visited_tiles.add(current_tile)
            reward += 0.01  # Reward for visiting a new tile

        return reward
    
    def new_map_reward(self, obs):
        reward = 0

        current_map = obs[3]

        if not hasattr(self, "visited_maps"):
            self.visited_maps = set()

        if current_map not in self.visited_maps:
            self.visited_maps.add(current_map)
            reward += 1  # Reward for visiting a new map

        return reward

    
    #10 reward for pokemon level up
    def level_up_reward(self, obs):
        reward = 0

        indexes = [5, 6, 7, 8, 9, 10]

        current_levels = obs[indexes] # Pokemon levels        

        if not hasattr(self, "last_levels"):
            self.last_levels = current_levels

        if np.any(current_levels > self.last_levels):
            reward += 10  # Reward for leveling up
            self.last_levels = current_levels

        return reward
    
    #1000 reward for collecting oaks parcel
    def oaks_parcel_collected(self, obs):
        if obs[11] == 1:
            return 1000
        return 0
        
    #1000 reward for collecting pokedex
    def pokedex_collected(self, obs):
        if obs[12] == 1:
            return 2000
        return 0
        
    #10000 reward for collecting oaks parcel
    def first_badge_collected(self, obs):
        if obs[13] == 1:
            return 10000
        return 0
    
    def standing_still(self, obs):
        reward = 0
        
        current_tile = (obs[1], obs[2], obs[3])  # x, y, map

        if not hasattr(self, "last_places"):
            self.last_places = []
        
        if (len(self.last_places) > 3):
            counts = self.last_places.count(current_tile)
            reward = counts * 0.001
            self.last_places.pop(0)

        self.last_places.append(current_tile)

        return reward

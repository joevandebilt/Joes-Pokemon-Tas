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

        self.pyboy = Emulator.emulate("roms/Pokemon - Blue Version.gb", 0, False, True)
        
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(len(GameboyAction))
               
        self.observation_space = spaces.Box(
            low=0,
            high=2_147_483_647,
            shape=(9,),
            dtype=np.int32
        )

        self.steps_taken = 0

        self.total_reward = 0
    
    def _get_obs(self):
        world_state = mm.read_game_state(self.pyboy)

        obs = np.array([
            world_state["in_battle"],
            world_state["x"],
            world_state["y"],
            world_state["map"],
            #world_state["party_count"],
            (
                world_state["pokemon"][0]["exp"]+
                world_state["pokemon"][1]["exp"]+
                world_state["pokemon"][2]["exp"]+
                world_state["pokemon"][3]["exp"]+
                world_state["pokemon"][4]["exp"]+
                world_state["pokemon"][5]["exp"]
            ),
            world_state["events"]["allow_starter"],
            world_state["events"]["oaks_parcel"],
            world_state["events"]["pokedex"],
            world_state["events"]["brock"],
        ], dtype=np.int32)

        return obs, world_state
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        Emulator.load_specific_state(self.pyboy, "reset")

        #clear reward trackers
        reward_attr = [
            "visited_tiles",
            "visited_maps",
            "last_levels",
            "party_size",
            "milestone_starter",
            "milestone_parcel",
            "milestone_pokedex",
            "milestone_badge",
            "last_places",
            "gained_exp",
            "in_battle"
        ]

        for attr in reward_attr:
            if hasattr(self, attr):
                delattr(self, attr)


        #Additional info to return for debugging or whatever
        info = {}

        if self.render_mode == "human":
            self.render()

        obs, world_state = self._get_obs()

        return obs, info
    
    def perform_action(self, action: GameboyAction):
        button = Emulator.PyBoyButton.get(action)
        Emulator.press_button(self.pyboy, button)
    
    def step(self, action):
        action_enum = GameboyAction(action)
        self.perform_action(action_enum)

        self.steps_taken += 1

        obs, world_state = self._get_obs()

        reward = self.calulate_reward(obs, world_state)
        self.total_reward += reward

        #world_state["total_reward"] = self.total_reward

        info = {
            "game_state": world_state,
        }

        if (self.render_mode == "human"):
            self.render()

        terminated = world_state["events"]["brock"]
        truncate = False

        return obs, reward, terminated, truncate, info
    
    def render(self):
        return
    
    def close(self):
        Emulator.switch_off(self.pyboy)

    # REWARDS
    def calulate_reward(self, obs, world_state):
        reward = 0

        reward += self.new_map_reward(obs, world_state)
        reward += self.new_tile_reward(obs, world_state)
        reward += self.level_up_reward(obs, world_state)
        reward += self.choose_starter(obs, world_state)
        reward += self.oaks_parcel_collected(obs, world_state)
        reward += self.pokedex_collected(obs, world_state)
        reward += self.first_badge_collected(obs, world_state)

        reward -= self.punish_standing_still(obs, world_state)
        reward -= self.punish_ran_away(obs, world_state)

        return reward


    #1 reward for new tile
    def new_tile_reward(self, obs, world_state):
        reward = 0

        current_tile = (world_state["map"], world_state["x"], world_state["y"])  # m, x, y

        if not hasattr(self, "visited_tiles"):
            self.visited_tiles = set()

        if current_tile not in self.visited_tiles:
            self.visited_tiles.add(current_tile)
            reward += 1  # Reward for visiting a new tile

        return reward
    
    #3 reward for visiting a new map
    def new_map_reward(self, obs, world_state):
        reward = 0

        current_map = world_state["map"]

        if not hasattr(self, "visited_maps"):
            self.visited_maps = set()
            self.last_map = None

        if not self.last_map == None and not self.last_map == current_map:
            link = (self.last_map, current_map)
            if link not in self.visited_maps:
                self.visited_maps.add(link)
                reward += 3  

        self.last_map = current_map

        return reward

    
    #3 reward for pokemon level up
    def level_up_reward(self, obs, world_state):
        reward = 0

        current_exp = (
                world_state["pokemon"][0]["exp"],
                world_state["pokemon"][1]["exp"],
                world_state["pokemon"][2]["exp"],
                world_state["pokemon"][3]["exp"],
                world_state["pokemon"][4]["exp"],
                world_state["pokemon"][5]["exp"]
        ) # Pokemon levels        

        if not hasattr(self, "last_levels"):
            self.last_exp = current_exp
            self.gained_exp = False

        if np.any(current_exp > self.last_exp):
            reward += 3  # Reward for leveling up
            self.last_exp = current_exp
            self.gained_exp = True
        else:
            self.gained_exp = False
            
        return reward
    
    #3 reward for catching a new pokemon
    def catch_pokemon_reward(self, obs, world_state):
        reward = 0

        if not hasattr(self, "party_size"):
            self.party_size = world_state["party_size"]

        if world_state["party_size"] > self.party_size:
            reward = 3

        self.party_size = world_state["party_size"]

        return reward


    #5 reward for getting past the autowalk section
    def choose_starter(self, obs, world_state):
        reward = 0
        if not hasattr(self, "milestone_starter"):
            self.milestone_starter = world_state["events"]["allow_starter"]

        if world_state["events"]["allow_starter"] == True and not self.milestone_starter:
            reward = 5
        
        self.milestone_starter = world_state["events"]["allow_starter"]

        return reward

    #5 reward for collecting oaks parcel
    def oaks_parcel_collected(self, obs, world_state):
        reward = 0
        if not hasattr(self, "milestone_parcel"):
            self.milestone_parcel = world_state["events"]["oaks_parcel"]

        if world_state["events"]["oaks_parcel"] == True and not self.milestone_parcel:
            reward = 5
            self.visited_tiles = set()
            self.visited_maps = set()
        
        self.milestone_pokedex = world_state["events"]["oaks_parcel"]

        return reward
        
    #10 reward for collecting pokedex
    def pokedex_collected(self, obs, world_state):
        reward = 0
        if not hasattr(self, "milestone_pokedex"):
            self.milestone_pokedex = world_state["events"]["pokedex"]

        if world_state["events"]["pokedex"] == True and not self.milestone_pokedex:
            reward = 10
        
        self.milestone_pokedex = world_state["events"]["pokedex"]

        return reward
        
    #10000 reward for winning first badge
    def first_badge_collected(self, obs, world_state):
        reward = 0
        if not hasattr(self, "milestone_badge"):
            self.milestone_badge = world_state["events"]["brock"]

        if world_state["events"]["brock"] == True and not self.milestone_badge:
            reward = 10000
        
        self.milestone_pokedex = world_state["events"]["brock"]
        return reward
    
    def punish_standing_still(self, obs, world_state):
        punish = 0
        memory_size = 20

        if not world_state["in_battle"] and not world_state["in_dialog"]:
            current_tile = (world_state["map"], world_state["x"], world_state["y"])   # map, x, y

            if not hasattr(self, "last_places"):
                self.last_places = []

            if (len(self.last_places) > memory_size):
                counts = self.last_places.count(current_tile)
                if counts > (memory_size / 2):
                    punish = 0.01
                self.last_places.pop(0)

            self.last_places.append(current_tile)

        return punish
    
    def punish_ran_away(self, obs, world_state):
        punish = 0

        if not hasattr(self, "in_battle"):
            self.in_battle = world_state["in_battle"]

        if self.in_battle and not world_state["in_battle"] and not self.gained_exp:
            punish = 1

        self.in_battle = world_state["in_battle"]
            
        return punish

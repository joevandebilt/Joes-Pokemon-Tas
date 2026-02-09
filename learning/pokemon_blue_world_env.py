import gymnasium as gym
from gymnasium import spaces
from learning.actions import GameboyAction
from memory_maps.static_data.pokemon_data import MAP_NAMES

import Emulator as Emulator
import memory_maps.pokemon_red_blue as mm
import numpy as np

class PokemonWorldEnv(gym.Env):

    metadata = {"render_modes": ["human"], "render_fps": 30 }
    
    def __init__(self, render_mode=None):

        self.pyboy = Emulator.emulate("roms/Pokemon - Blue Version.gb", 0, False, False)
        
        self.render_mode = render_mode

        self.action_space = spaces.Discrete(len(GameboyAction))
               
        self.observation_space = spaces.Box(
            low=np.array([0,0,0,0,0,0,0,0]),
            high=np.array([255,255,255,1,1,11,600,2000]),
            shape=(8,),
            dtype=np.int32
        )

        self._reset_reward_state()        
    
    def _get_world_state(self):
        return mm.read_game_state(self.pyboy)

    def _get_obs(self, world_state):
        return np.array([
            world_state["map"],                             #255
            world_state["x"],                               #255
            world_state["y"],                               #255
            world_state["in_battle"],                       #1
            world_state["in_dialog"],                       #1
            self.get_total_milestones(world_state),         #11
            self.get_total_levels(world_state),             #600
            self.get_total_health_remaining(world_state),   #600
        ], dtype=np.int32)
    
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        np.random.seed(seed)

        Emulator.load_specific_state(self.pyboy, "reset")

        #clear reward trackers
        self._reset_reward_state()

        #Additional info to return for debugging or whatever
        info = {}

        if self.render_mode == "human":
            self.render()

        world_state = self._get_world_state()
        obs = self._get_obs(world_state)

        return obs, info
    
    def _reset_reward_state(self):
        self.visited_tiles = set()
        self.visited_maps = set()
        self.last_places = []
        self.last_map = None
        self.pre_battle_exp = None
        self.in_battle = False
        self.in_trainer_battle = False
        self.damage_dealt = 0
        self.health_remaining = 0
        self.last_levels = None
        self.party_size = 0
        self.milestone_starter = False
        self.milestone_parcel = False
        self.milestone_pokedex = False
        self.milestone_badges = 0     
        self.reward_events = []
        self.steps_taken = 0
        self.total_reward = 0

    def perform_action(self, action: GameboyAction):
        button = Emulator.PyBoyButton.get(action)
        Emulator.press_button(self.pyboy, button)
    
    def step(self, action):
        action_enum = GameboyAction(action)
        self.perform_action(action_enum)

        self.steps_taken += 1

        world_state = self._get_world_state()
        obs = self._get_obs(world_state)

        reward = self.calulate_reward(world_state)
        self.total_reward += reward

        info = {
            "game_state": world_state
        }

        if (self.render_mode == "human"):
            self.render()

        terminated = world_state["events"]["brock"]
        truncate = self.steps_taken > 1_000_000

        return obs, reward, terminated, truncate, info
    
    def render(self):
        return
    
    def close(self):
        Emulator.switch_off(self.pyboy)

    def get_total_milestones(self, world_state):
        milestones = np.array([
            world_state["events"]["allow_starter"],
            world_state["events"]["oaks_parcel"],
            world_state["events"]["pokedex"],
        ], dtype=bool)
        return milestones.sum() + self.get_badge_count(world_state)

    def get_total_levels(self, world_state):
        return (
            world_state["pokemon"][0]["level"]+
            world_state["pokemon"][1]["level"]+
            world_state["pokemon"][2]["level"]+
            world_state["pokemon"][3]["level"]+
            world_state["pokemon"][4]["level"]+
            world_state["pokemon"][5]["level"]
        )
    
    def get_total_exp(self, world_state):
        return (
                world_state["pokemon"][0]["exp"] +
                world_state["pokemon"][1]["exp"] +
                world_state["pokemon"][2]["exp"] +
                world_state["pokemon"][3]["exp"] +
                world_state["pokemon"][4]["exp"] +
                world_state["pokemon"][5]["exp"]
        )

    def get_total_health_remaining(self, world_state):
        return (
            world_state["pokemon"][0]["hp"]+
            world_state["pokemon"][1]["hp"]+
            world_state["pokemon"][2]["hp"]+
            world_state["pokemon"][3]["hp"]+
            world_state["pokemon"][4]["hp"]+
            world_state["pokemon"][5]["hp"]
        )

    def get_badge_count(self, world_state):
        badges = np.array([
            world_state["events"]["brock"],
            world_state["events"]["misty"],
            world_state["events"]["surge"],
            world_state["events"]["erika"],
            world_state["events"]["koga"],
            world_state["events"]["sabrina"],
            world_state["events"]["blaine"],
            world_state["events"]["giovanni"]
        ], dtype=bool)
        return badges.sum()

    # REWARDS
    def calulate_reward(self, world_state):
        reward = 0

        reward += self.new_map_reward(world_state)
        reward += self.new_tile_reward(world_state)        
        reward += self.trainer_battle_reward(world_state)
        reward += self.dealt_damage_reward(world_state)
        reward += self.catch_pokemon_reward(world_state)
        reward += self.level_up_reward(world_state)
        reward += self.choose_starter(world_state)
        reward += self.oaks_parcel_collected(world_state)
        reward += self.pokedex_collected(world_state)
        reward += self.badges_collected(world_state)
        reward += self.healed_when_needed(world_state)

        reward -= self.punish_standing_still(world_state)
        reward -= self.punish_ran_away(world_state)

        return reward


    def log_reward(self, rwd, msg):
        log = {
            "reward": rwd, 
            "message": msg,
            "steps": self.steps_taken
        }
        self.reward_events.append(log)
        

    #1 reward for new tile
    def new_tile_reward(self, world_state):
        reward = 0

        current_tile = (world_state["map"], world_state["x"], world_state["y"])  # m, x, y

        if current_tile not in self.visited_tiles:
            self.visited_tiles.add(current_tile)
            reward += 0.01  # Reward for visiting a new tile

        return reward
    
    def new_map_reward(self, world_state):
        reward = 0

        current_map = world_state["map"]

        if not self.last_map == None and not self.last_map == current_map:
            link = (self.last_map, current_map)
            if link not in self.visited_maps:
                self.visited_maps.add(link)
                reward += 0.03
                self.log_reward(reward, f"Found connection between {MAP_NAMES.get(self.last_map)} and {MAP_NAMES.get(current_map)}")

        self.last_map = current_map

        return reward

    def trainer_battle_reward(self, world_state): 
        reward = 0
        in_trainer_battle = world_state["in_trainer_battle"]

        if not self.in_trainer_battle and in_trainer_battle:
            reward = 0.02
            self.log_reward(reward, f"Started Trainer Battle")
        elif  self.in_trainer_battle and not in_trainer_battle:
            reward = 0.05
            self.log_reward(reward, f"Finished Trainer Battle")

        self.in_trainer_battle = in_trainer_battle

        return reward
    
    def dealt_damage_reward(self, world_state):
        reward = 0

        if world_state["in_battle"]:
            damage_dealt = world_state["damage_dealt"]
            if damage_dealt > 0 and not self.damage_dealt == damage_dealt:
                reward = 0.02
                self.damage_dealt = damage_dealt
                self.log_reward(reward, f"Dealt {damage_dealt}hp damage in battle")

        return reward
    
    #3 reward for pokemon level up
    def level_up_reward(self, world_state):
        reward = 0

        current_levels = self.get_total_levels(world_state)

        if self.last_levels == None:
            self.last_levels = current_levels

        if current_levels > self.last_levels:
            reward = 0.05
            self.log_reward(reward, f"Earned another level")
            
        self.last_levels = current_levels

        return reward
    
    #3 reward for catching a new pokemon
    def catch_pokemon_reward(self, world_state):
        reward = 0

        party_size = world_state["party_count"]
        if party_size > self.party_size:
            reward = 0.03
            self.log_reward(reward, f"Increased Partysize to {party_size}")

        self.party_size = party_size

        return reward

    def healed_when_needed(self, world_state):
        reward = 0
        health_remaining = self.get_total_health_remaining(world_state)

        if health_remaining > self.health_remaining:
            amount_healed = health_remaining - self.health_remaining
            reward = (amount_healed) * 0.001
            self.log_reward(reward, f"Healed {amount_healed} hp")

        self.health_remaining = health_remaining

        return reward

    #5 reward for getting past the autowalk section
    def choose_starter(self, world_state):
        reward = 0

        if world_state["events"]["allow_starter"] == True and not self.milestone_starter:
            reward = 0.5
            self.log_reward(reward, f"Followed professor oak to his lab")
        
        self.milestone_starter = world_state["events"]["allow_starter"]

        return reward

    #5 reward for collecting oaks parcel
    def oaks_parcel_collected(self, world_state):
        reward = 0

        if world_state["events"]["oaks_parcel"] == True and not self.milestone_parcel:
            reward = 0.5
            self.visited_tiles = set()
            self.visited_maps = set()
            self.log_reward(reward, f"Picked up Oak's Parcel")
        
        self.milestone_parcel = world_state["events"]["oaks_parcel"]

        return reward
        
    #10 reward for collecting pokedex
    def pokedex_collected(self, world_state):
        reward = 0

        if world_state["events"]["pokedex"] == True and not self.milestone_pokedex:
            reward = 1
            self.log_reward(reward, f"Collected the Pokedex")
        
        self.milestone_pokedex = world_state["events"]["pokedex"]

        return reward
        
    #10000 reward for winning first badge
    def badges_collected(self, world_state):
        reward = 0

        badges_collected = self.get_badge_count(world_state)
        if badges_collected > self.milestone_badges:
            reward = badges_collected * 10
            self.log_reward(reward, f"Collected {badges_collected} badge(s)")
        
        self.milestone_badges = badges_collected
        return reward
    
    def punish_standing_still(self, world_state):
        punish = 0
        memory_size = 20

        if not world_state["in_battle"] and not world_state["in_dialog"]:
            current_tile = (world_state["map"], world_state["x"], world_state["y"])   # map, x, y

            if (len(self.last_places) > memory_size):
                counts = self.last_places.count(current_tile)
                if counts > (memory_size / 2):
                    punish = 0.01
                self.last_places.pop(0)

            self.last_places.append(current_tile)

        return punish
    
    def punish_ran_away(self, world_state):
        punish = 0
       
        current_exp = self.get_total_exp(world_state)
        if not self.in_battle and world_state["in_battle"]:
            #battle started     
            self.pre_battle_exp = current_exp
        elif self.in_battle and not world_state["in_battle"]:
            #battle ended            
            if self.pre_battle_exp == current_exp:
                punish = 0.02
                self.log_reward(punish*-1, f"Battle ended with 0 EXP Gained ({self.pre_battle_exp}->{current_exp})")

        self.in_battle = world_state["in_battle"]
            
        return punish

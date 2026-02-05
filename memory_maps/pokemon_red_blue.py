from memory_maps.static_data.pokemon_data import POKEMON_CHAR_MAP, POKEMON_ID_TO_NAME, POKEMON_MOVES

def read_game_state(pyboy):
    data = {
        "map": pyboy.memory[0xD35E],    #https://glitchcity.wiki/wiki/List_of_maps_by_index_number_(Generation_I)
        "x": pyboy.memory[0xD361],
        "y": pyboy.memory[0xD362],
        "player_name": read_pokemon_string(pyboy, 0xD158, 4),
        "player_id": pyboy.memory[0xD359],
        "in_battle": pyboy.memory[0xD057] != 0,
        "in_dialog": pyboy.memory[0xD730] != 0,
        "events":{
            "oaks_parcel": (pyboy.memory[0xD60D] != 0) or ((pyboy.memory[0xD74E] & 0x01) != 0),
            "pokedex": (pyboy.memory[0xD74E] & 0x01) != 0,
            "town_map": pyboy.memory[0xD5F3] != 0,
            "brock": pyboy.memory[0xD755] != 0,
            "misty": pyboy.memory[0xD75E] != 0,
            "surge": pyboy.memory[0xD773] != 0,
            "erika": pyboy.memory[0xD77C] != 0,
            "koga": pyboy.memory[0xD792] != 0,
            "sabrina": pyboy.memory[0xD7B3] != 0,
            "blaine": pyboy.memory[0xD79A] != 0,
            "giovanni": pyboy.memory[0xD751] != 0,
            "snorlax_celadon": pyboy.memory[0xD7E0] != 0,
            "snorlax_vermillion": pyboy.memory[0xD7D8] != 0,
            "articuno": pyboy.memory[0xD782] != 0,
            "zapdos": pyboy.memory[0xD7D4] != 0,
            "moltres": pyboy.memory[0xD7EE] != 0,
            "mewtwo": pyboy.memory[0xD85F] != 0,
            "ss_anne": pyboy.memory[0xD803] != 0
        },
        "party_count": pyboy.memory[0xD163],
        "pokemon": [
            {
                "species": read_species(pyboy, 0xD164),
                "name": read_pokemon_string(pyboy, 0xD2B5, 10),
                "level": pyboy.memory[0xD18C],
                "hp": read_u16(pyboy, 0xD16C),
                "max_hp": read_u16(pyboy, 0xD18D),
                "exp": read_exp(pyboy, 0xD179),
                "next_level_exp": 0,
                "moves": [
                    { "move": read_move(pyboy, 0xD173), "pp": pyboy.memory[0xD188] },
                    { "move": read_move(pyboy, 0xD174), "pp": pyboy.memory[0xD189] },
                    { "move": read_move(pyboy, 0xD175), "pp": pyboy.memory[0xD18A] },
                    { "move": read_move(pyboy, 0xD176), "pp": pyboy.memory[0xD18B] }
                ]
            },
            {
                "species": read_species(pyboy, 0xD165),
                "level": pyboy.memory[0xD1B8],
                "hp": read_u16(pyboy, 0xD198),
                "max_hp": read_u16(pyboy, 0xD1B9),
                "exp": read_exp(pyboy, 0xD1A5),
                "next_level_exp": 0,
                "moves": [
                    { "move": read_move(pyboy, 0xD19F), "pp": pyboy.memory[0xD1B4] },
                    { "move": read_move(pyboy, 0xD1A0), "pp": pyboy.memory[0xD1B5] },
                    { "move": read_move(pyboy, 0xD1A1), "pp": pyboy.memory[0xD1B6] },
                    { "move": read_move(pyboy, 0xD1A2), "pp": pyboy.memory[0xD1B7] }
                ]
            },
            {
                "species": read_species(pyboy, 0xD166),
                "level": pyboy.memory[0xD1E4],
                "hp": read_u16(pyboy, 0xD1C4),
                "max_hp": read_u16(pyboy, 0xD1E5),
                "exp": read_exp(pyboy, 0xD1D1),
                "next_level_exp": 0,
                "moves": [
                    { "move": read_move(pyboy, 0xD1CB), "pp": pyboy.memory[0xD1E0] },
                    { "move": read_move(pyboy, 0xD1CC), "pp": pyboy.memory[0xD1E1] },
                    { "move": read_move(pyboy, 0xD1CD), "pp": pyboy.memory[0xD1E2] },
                    { "move": read_move(pyboy, 0xD1CE), "pp": pyboy.memory[0xD1E3] }
                ]
            },
            {
                "species": read_species(pyboy, 0xD167),
                "level": pyboy.memory[0xD210],
                "hp": read_u16(pyboy, 0xD1F0),
                "max_hp": read_u16(pyboy, 0xD211),
                "exp": read_exp(pyboy, 0xD1FD),
                "next_level_exp": 0,
                "moves": [
                    { "move": read_move(pyboy, 0xD1F7), "pp": pyboy.memory[0xD20C] },
                    { "move": read_move(pyboy, 0xD1F8), "pp": pyboy.memory[0xD20D] },
                    { "move": read_move(pyboy, 0xD1F9), "pp": pyboy.memory[0xD20E] },
                    { "move": read_move(pyboy, 0xD1FA), "pp": pyboy.memory[0xD20F] }
                ]
            },
            {
                "species": read_species(pyboy, 0xD168),
                "level": pyboy.memory[0xD23C],
                "hp": read_u16(pyboy, 0xD21C),
                "max_hp": read_u16(pyboy, 0xD23D),
                "exp": read_exp(pyboy, 0xD229),
                "next_level_exp": 0,
                "moves": [
                    { "move": read_move(pyboy, 0xD223), "pp": pyboy.memory[0xD238] },
                    { "move": read_move(pyboy, 0xD224), "pp": pyboy.memory[0xD239] },
                    { "move": read_move(pyboy, 0xD225), "pp": pyboy.memory[0xD23A] },
                    { "move": read_move(pyboy, 0xD226), "pp": pyboy.memory[0xD23B] }
                ]
            },
            {
                "species": read_species(pyboy, 0xD169),
                "level": pyboy.memory[0xD268],
                "hp": read_u16(pyboy, 0xD248),
                "max_hp": read_u16(pyboy, 0xD269),
                "exp": read_exp(pyboy, 0xD255),
                "next_level_exp": 0,
                "moves": [
                    { "move": read_move(pyboy, 0xD24F), "pp": pyboy.memory[0xD264] },
                    { "move": read_move(pyboy, 0xD250), "pp": pyboy.memory[0xD265] },
                    { "move": read_move(pyboy, 0xD251), "pp": pyboy.memory[0xD266] },
                    { "move": read_move(pyboy, 0xD252), "pp": pyboy.memory[0xD267] }
                ]
            }
        ]
    }
    for pokemon in data["pokemon"]:
        if (pokemon["species"] == "Unknown"):
            continue
        elif (pokemon["level"] == 100):
            pokemon["next_level_exp"] = pokemon["exp"]
        else:
            pokemon["next_level_exp"] = exp_for_level(pokemon["level"], pokemon["species"].get("growth", "medium_fast"))
            
    return data

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
        "big"
    )

def read_species(pyboy, addr):
    return POKEMON_ID_TO_NAME.get(pyboy.memory[addr], "Unknown")

def read_exp(pyboy, addr):    
    return int.from_bytes(
        bytes(pyboy.memory[addr:addr+3]),
        "big"
    )

def exp_for_level(level, growth="medium_fast"):
    """
    Returns total EXP needed to reach a given level.
    Level = 1..100
    Growth: "medium_fast", "medium_slow", "fast", "slow"
    """
    if growth == "medium_fast":
        return level ** 3
    elif growth == "medium_slow":
        return int((6/5) * level**3 - 15 * level**2 + 100 * level - 140)
    elif growth == "fast":
        return int(0.8 * level**3)
    elif growth == "slow":
        return int(1.25 * level**3)
    else:
        raise ValueError("Unknown growth rate")

def read_move(pyboy, addr):
    move_id = pyboy.memory[addr]
    move_name = POKEMON_MOVES.get(move_id, "UNKNOWN MOVE")
    return {"id": move_id, "name": move_name}

def is_save_loaded(pyboy):
    return pyboy.memory[0xD163] != 0
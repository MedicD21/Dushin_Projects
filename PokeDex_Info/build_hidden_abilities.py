#!/usr/bin/env python3
"""
Fetch hidden abilities for all Pokemon from PokéAPI and add to pokemon_data.json
"""

import json
import requests
from pathlib import Path
import time

DATA_PATH = Path(__file__).parent / "data" / "pokemon_data.json"
POKEAPI_BASE = "https://pokeapi.co/api/v2"


def get_pokemon_hidden_ability(pokemon_name: str) -> str | None:
    """Fetch hidden ability for a Pokemon from PokéAPI"""
    try:
        response = requests.get(
            f"{POKEAPI_BASE}/pokemon/{pokemon_name.lower()}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            # Find the hidden ability
            for ability in data.get("abilities", []):
                if ability.get("is_hidden"):
                    return ability["ability"]["name"]
        return None
    except Exception as e:
        print(f"Error fetching hidden ability for {pokemon_name}: {e}")
        return None


def add_hidden_abilities_to_pokemon():
    """Add hidden abilities to all Pokemon in pokemon_data.json"""
    
    # Load existing data
    with open(DATA_PATH, 'r') as f:
        pokemon_data = json.load(f)
    
    print(f"Processing {len(pokemon_data)} Pokemon to add hidden abilities...")
    
    hidden_count = 0
    
    for idx, pokemon in enumerate(pokemon_data):
        pokemon_name = pokemon.get("name", "")
        normal_abilities = pokemon.get("abilities", [])
        
        # Skip if abilities_info already exists with hidden ability
        if "abilities_info" in pokemon and pokemon["abilities_info"].get("hidden"):
            print(f"[{idx+1}/{len(pokemon_data)}] {pokemon_name} - Already has hidden ability info")
            continue
        
        print(f"[{idx+1}/{len(pokemon_data)}] Fetching hidden ability for {pokemon_name}...", end=" ")
        
        hidden_ability = get_pokemon_hidden_ability(pokemon_name)
        
        if hidden_ability:
            print(f"Found: {hidden_ability}")
            hidden_count += 1
        else:
            print("None")
        
        # Structure abilities with normal and hidden
        pokemon["abilities_info"] = {
            "normal": normal_abilities,
            "hidden": hidden_ability
        }
        
        # Be nice to the API
        time.sleep(0.1)
    
    # Save updated data
    with open(DATA_PATH, 'w') as f:
        json.dump(pokemon_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nSuccessfully added hidden abilities!")
    print(f"Pokemon with hidden abilities: {hidden_count}/{len(pokemon_data)}")
    print(f"Saved to {DATA_PATH}")


if __name__ == "__main__":
    add_hidden_abilities_to_pokemon()

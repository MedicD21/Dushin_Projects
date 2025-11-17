#!/usr/bin/env python3
"""
Script to add moves data to pokemon_data.json by fetching from PokéAPI
"""

import json
import requests
from pathlib import Path
import time

DATA_PATH = Path(__file__).parent / "data" / "pokemon_data.json"
POKEAPI_BASE = "https://pokeapi.co/api/v2"


def get_pokemon_moves(pokemon_name: str) -> list[str]:
    """Fetch moves for a Pokemon from PokéAPI"""
    try:
        response = requests.get(
            f"{POKEAPI_BASE}/pokemon/{pokemon_name.lower()}",
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            moves = [move["move"]["name"] for move in data.get("moves", [])]
            return moves
        else:
            return []
    except Exception as e:
        print(f"Error fetching moves for {pokemon_name}: {e}")
        return []


def add_moves_to_pokemon():
    """Add moves field to all Pokemon in pokemon_data.json"""
    
    # Load existing data
    with open(DATA_PATH, 'r') as f:
        pokemon_data = json.load(f)
    
    print(f"Processing {len(pokemon_data)} Pokemon...")
    
    for idx, pokemon in enumerate(pokemon_data):
        # Skip if moves already exist
        if "moves" in pokemon and pokemon["moves"]:
            print(f"[{idx+1}/{len(pokemon_data)}] {pokemon['name']} - Already has moves")
            continue
        
        pokemon_name = pokemon.get("name", "").lower().replace(" ", "-")
        print(f"[{idx+1}/{len(pokemon_data)}] Fetching moves for {pokemon['name']}...", end=" ")
        
        moves = get_pokemon_moves(pokemon_name)
        pokemon["moves"] = moves
        
        print(f"Found {len(moves)} moves")
        
        # Be nice to the API - small delay
        time.sleep(0.1)
    
    # Save updated data
    with open(DATA_PATH, 'w') as f:
        json.dump(pokemon_data, f, indent=2)
    
    print(f"\nSuccessfully added moves to all Pokemon!")
    print(f"Saved to {DATA_PATH}")


if __name__ == "__main__":
    add_moves_to_pokemon()

#!/usr/bin/env python3
"""
Enhance pokemon_data.json with hidden abilities and evolution data.
This script enriches the Pokemon data with additional fields needed for the UI.
"""

import json
from pathlib import Path

# Hidden ability data - mapping of Pokemon to their hidden ability
HIDDEN_ABILITIES = {
    "Bulbasaur": "Chlorophyll",
    "Ivysaur": "Chlorophyll",
    "Venusaur": "Chlorophyll",
    "Charmander": "Blaze",
    "Charmeleon": "Blaze",
    "Charizard": "Blaze",
    "Squirtle": "Torrent",
    "Wartortle": "Torrent",
    "Blastoise": "Torrent",
    # Add more as needed
}

# Evolution data - mapping of Pokemon to their evolutions
EVOLUTION_DATA = {
    "Bulbasaur": {
        "name": "Bulbasaur",
        "evolutions": [
            {
                "name": "Ivysaur",
                "method": "Level 16",
                "sprite": "ivysaur"
            },
            {
                "name": "Venusaur",
                "method": "Level 32 (from Ivysaur)",
                "sprite": "venusaur"
            }
        ]
    },
    "Ivysaur": {
        "name": "Ivysaur",
        "evolutions": [
            {
                "name": "Venusaur",
                "method": "Level 32",
                "sprite": "venusaur"
            }
        ]
    },
    "Charmander": {
        "name": "Charmander",
        "evolutions": [
            {
                "name": "Charmeleon",
                "method": "Level 16",
                "sprite": "charmeleon"
            },
            {
                "name": "Charizard",
                "method": "Level 36 (from Charmeleon)",
                "sprite": "charizard"
            }
        ]
    },
    "Squirtle": {
        "name": "Squirtle",
        "evolutions": [
            {
                "name": "Wartortle",
                "method": "Level 16",
                "sprite": "wartortle"
            },
            {
                "name": "Blastoise",
                "method": "Level 36 (from Wartortle)",
                "sprite": "blastoise"
            }
        ]
    },
    # This is just a starter template - in production would have all 1025+ Pokemon
}

def enhance_pokemon_data():
    """Enhance pokemon_data.json with hidden abilities and evolution data."""
    data_path = Path('data/pokemon_data.json')
    
    with open(data_path) as f:
        pokemon_list = json.load(f)
    
    # Enhance each Pokemon
    for pokemon in pokemon_list:
        name = pokemon.get('name', '')
        
        # Structure abilities with normal and hidden
        abilities = pokemon.get('abilities', [])
        hidden = HIDDEN_ABILITIES.get(name)
        
        pokemon['abilities_info'] = {
            'normal': abilities,
            'hidden': hidden
        }
        
        # Add evolution data if available
        if name in EVOLUTION_DATA:
            pokemon['evolution'] = EVOLUTION_DATA[name]
        else:
            pokemon['evolution'] = {
                'name': name,
                'evolutions': []
            }
    
    # Write back
    with open(data_path, 'w') as f:
        json.dump(pokemon_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced {len(pokemon_list)} Pokemon")

if __name__ == '__main__':
    enhance_pokemon_data()

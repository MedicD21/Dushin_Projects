#!/usr/bin/env python3
"""
Build complete evolution chain data for all Pokemon.
Scrapes PokéAPI and adds evolution data to pokemon_data.json.
"""

import json
import requests
from pathlib import Path
from typing import Dict, List, Optional

# Evolution method mapping
EVOLUTION_METHODS = {
    "level-up": "Level {param}",
    "trade": "Trade",
    "use-item": "Use {item}",
    "shed": "Shed (Nincada only)",
    "spin": "Spin around holding {item}",
    "tower-of-darkness": "Complete Tower of Darkness",
    "tower-of-waters": "Complete Tower of Waters",
    "three-critical-hits": "Land 3 critical hits in one battle",
    "other": "Special condition"
}

def get_evolution_details(pokemon_name: str) -> Optional[Dict]:
    """Fetch evolution chain for a Pokemon from PokéAPI."""
    try:
        # Get Pokemon details
        response = requests.get(
            f"https://pokeapi.co/api/v2/pokemon-species/{pokemon_name.lower()}",
            timeout=5
        )
        if response.status_code != 200:
            return None
        
        species_data = response.json()
        evolution_chain_url = species_data.get('evolution_chain', {}).get('url')
        
        if not evolution_chain_url:
            return None
        
        # Get evolution chain
        chain_response = requests.get(evolution_chain_url, timeout=5)
        if chain_response.status_code != 200:
            return None
        
        chain_data = chain_response.json()
        
        # Build evolution chain
        evolution_chain = build_evolution_chain(chain_data['chain'])
        
        return evolution_chain
    except Exception as e:
        print(f"  ⚠️  Error fetching {pokemon_name}: {e}")
        return None

def build_evolution_chain(chain_node: Dict, parent_name: Optional[str] = None) -> Dict:
    """Recursively build evolution chain from PokéAPI chain node."""
    species_name = chain_node['species']['name'].title()
    
    evolutions = []
    
    # Process all evolutions from this node
    for evolves_to in chain_node.get('evolves_to', []):
        evolution_details = evolves_to['evolution_details']
        
        if not evolution_details:
            # If no details, assume level-up evolution
            evolution_details = [{}]
        
        for detail in evolution_details:
            method = format_evolution_method(detail)
            evolved_name = evolves_to['species']['name'].title()
            
            evolutions.append({
                'name': evolved_name,
                'method': method,
                'sprite': evolves_to['species']['name'].lower()
            })
        
        # Recursively get further evolutions
        further_evolutions = build_evolution_chain(evolves_to, species_name)
        if further_evolutions and further_evolutions.get('evolutions'):
            evolutions.extend(further_evolutions['evolutions'])
    
    return {
        'name': species_name,
        'evolutions': evolutions
    }

def format_evolution_method(detail: Dict) -> str:
    """Format evolution method from PokéAPI detail object."""
    
    # Level up
    if detail.get('trigger', {}).get('name') == 'level-up':
        level = detail.get('min_level')
        if level:
            # Add condition info if available
            happiness = detail.get('min_happiness')
            if happiness:
                return f"Level {level} (high friendship)"
            
            time_of_day = detail.get('time_of_day')
            if time_of_day:
                return f"Level {level} ({time_of_day.title()})"
            
            known_move = detail.get('known_move')
            if known_move:
                move_name = known_move['name'].replace('-', ' ').title()
                return f"Level {level} (knowing {move_name})"
            
            known_type = detail.get('known_type')
            if known_type:
                type_name = known_type['name'].title()
                return f"Level {level} (knowing {type_name} move)"
            
            return f"Level {level}"
        
        # Fallback
        return "Level up"
    
    # Trade
    elif detail.get('trigger', {}).get('name') == 'trade':
        held_item = detail.get('held_item')
        if held_item:
            item_name = held_item['name'].replace('-', ' ').title()
            return f"Trade (holding {item_name})"
        trade_species = detail.get('trade_species')
        if trade_species:
            species_name = trade_species['name'].title()
            return f"Trade for {species_name}"
        return "Trade"
    
    # Item use
    elif detail.get('trigger', {}).get('name') == 'use-item':
        item = detail.get('item')
        if item:
            item_name = item['name'].replace('-', ' ').title()
            return f"Use {item_name}"
        return "Use item"
    
    # Special evolutions
    elif detail.get('trigger', {}).get('name') == 'shed':
        return "Shed (Nincada → Ninjask + Shedinja)"
    
    # Beauty stat
    elif 'beauty' in str(detail):
        return "Max Beauty stat"
    
    # Other
    else:
        trigger = detail.get('trigger', {}).get('name', 'Special condition')
        return trigger.replace('-', ' ').title()

def enhance_pokemon_data():
    """Add evolution data to pokemon_data.json."""
    data_path = Path('data/pokemon_data.json')
    
    with open(data_path) as f:
        pokemon_list = json.load(f)
    
    print("🔄 Adding evolution data to Pokemon...")
    
    for i, pokemon in enumerate(pokemon_list):
        pokemon_name = pokemon.get('name', '')
        
        if (i + 1) % 100 == 0:
            print(f"  Processing {i + 1}/{len(pokemon_list)}: {pokemon_name}")
        
        # Skip if already has evolution data
        if 'evolution' in pokemon:
            continue
        
        # Fetch evolution data
        evolution_data = get_evolution_details(pokemon_name)
        
        if evolution_data:
            pokemon['evolution'] = evolution_data
        else:
            # Add empty evolution for Pokemon with no evolutions
            pokemon['evolution'] = {
                'name': pokemon_name,
                'evolutions': []
            }
    
    # Write back
    with open(data_path, 'w') as f:
        json.dump(pokemon_list, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced {len(pokemon_list)} Pokemon with evolution data!")

if __name__ == '__main__':
    print("📊 Building evolution data for all Pokemon...")
    print("   This will take a minute to fetch from PokéAPI...")
    enhance_pokemon_data()

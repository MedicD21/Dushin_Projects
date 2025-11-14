#!/usr/bin/env python3
"""
Region Name Fixer
Quick utility to fix region names in pokemon_data.json to use simplified format
"""

import sys
import os
import json

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from config import PokeDataUtils, DATA_FILES


def simplify_region_name(region_name):
    """Convert region names to simplified format"""
    if not region_name:
        return region_name

    # Mapping of complex region names to simplified ones
    region_mappings = {
        "Kanto (Let's Go)": "Kanto",
        "Kanto (FRLG)": "Kanto",
        "Johto (HGSS)": "Johto",
        "Johto (GSC)": "Johto",
        "Hoenn (ORAS)": "Hoenn",
        "Hoenn (RSE)": "Hoenn",
        "Sinnoh (BDSP)": "Sinnoh",
        "Sinnoh (Pt)": "Sinnoh",
        "Sinnoh (DP)": "Sinnoh",
        "Unova (B2W2)": "Unova",
        "Unova (BW)": "Unova",
        "Kalos (Central)": "Kalos",
        "Kalos (Coastal)": "Kalos",
        "Kalos (Mountain)": "Kalos",
        "Alola (SM)": "Alola",
        "Alola (USUM)": "Alola",
        "Galar (Base)": "Galar",
        "Galar (Isle of Armor)": "Galar",
        "Galar (Crown Tundra)": "Galar",
        "Paldea (SV)": "Paldea",
        "Paldea (Teal Mask)": "Paldea",
        "Paldea (Indigo Disk)": "Paldea",
        "Hisui (PLA)": "Hisui",
    }

    return region_mappings.get(region_name, region_name)


def fix_region_names():
    """Fix all region names in pokemon_data.json"""
    print("🔧 Fixing region names in pokemon_data.json...")

    # Load existing data
    utils = PokeDataUtils()
    pokemon_data = utils.load_json_data(DATA_FILES["pokemon"])

    if not pokemon_data:
        print("❌ Could not load pokemon data")
        return

    print(f"📊 Processing {len(pokemon_data)} Pokemon...")

    # Create backup
    backup_file = DATA_FILES["pokemon"].replace(
        ".json", "_backup_before_region_fix.json"
    )
    utils.save_json_data(pokemon_data, backup_file)
    print(f"💾 Backup created: {backup_file}")

    # Fix region names
    fixed_count = 0
    for pokemon in pokemon_data:
        if "game_appearances" in pokemon:
            for game, game_data in pokemon["game_appearances"].items():
                if "region" in game_data:
                    old_region = game_data["region"]
                    new_region = simplify_region_name(old_region)
                    if old_region != new_region:
                        game_data["region"] = new_region
                        fixed_count += 1

    # Save fixed data
    utils.save_json_data(pokemon_data, DATA_FILES["pokemon"])

    print(f"✅ Fixed {fixed_count} region name entries")
    print(f"💾 Updated data saved to: {DATA_FILES['pokemon']}")
    print("🎉 Region name fix completed!")


if __name__ == "__main__":
    fix_region_names()

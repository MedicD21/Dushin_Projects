import json
from tqdm import tqdm
from pathlib import Path
from .client import get

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "pokemon_abilities.json"
BASE_URL = "https://pokeapi.co/api/v2/ability/"

B_ABILITY = 307

NEW_A_START = 10001
NEW_A_END = 10060 #change PRN for new abilities 

def grab_ability():
    
    ability_list = []
    exist_data = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r') as file:
            exist_data = json.load(file)
            
    exist_ids = { entry["id"] for entry in exist_data}
    
    def fetch_range(start, end, tag="Fetching"):
        for ability_id in tqdm(range(start, end + 1), desc=tag):
            
            if ability_id in exist_ids:
                tqdm.write(f"⚠️  Ability {ability_id} already exists. Skipping...")
                continue
            
            url = BASE_URL + str(ability_id)
            data = get(url)
            
            if data is None:
                tqdm.write(f"⚠️  No data for ability {ability_id}")
                continue
            
            #gets ability name and if in a main series game
            ability_name = data["name"]
            tqdm.write(f"⌛Getting {ability_name} info...")
            main_series = data["is_main_series"]
            
            #------Gets english ability effect description-----#
            effect_text = None
            for effect in data["effect_entries"]:
                if effect["language"]["name"] == "en":
                    effect_text = effect["effect"]
                    break
                    
            #------Gets English Ability flavor description for each game-----#    
            flavor_entries = []
            for item in data["flavor_text_entries"]:
                if item['language']['name'] == 'en':
                    flavor_text = item['flavor_text']               
                    version_group = item['version_group']['name'].lower()
                    flavor_entries.append({
                        "flavor_text": flavor_text,
                        "in_game": version_group
                        })
            
            #-----Generation Ability was introduced-----#        
            gen = data['generation']['name'].lower()
            
            #-----Changes to the effect and what game that took place-----#
            eff_changes = []
            for efc in data['effect_changes']:
                for entry in efc['effect_entries']:
                    if entry['language']['name'] == 'en':
                        eff_C_text = entry['effect']
                        vg = efc['version_group']['name'].lower()
                        eff_changes.append({
                            "effect_changes": eff_C_text,
                            "in_game_change": vg,
                        })
            
            #-----Gets all pokemon who have ability and what slot it is in-----#            
            pkmn = []
            for p in data['pokemon']:
                name = p['pokemon']['name']
                is_hidden = p['is_hidden']
                slot = p['slot']
                pkmn.append({
                    "is_hidden": is_hidden,
                    "pokemon": name,
                    "slot": slot,
                    })                 
                        
            ability_list.append({
                "id": ability_id,
                "name": ability_name,
                "generation": gen,
                "is_main_series": main_series,
                "effect": effect_text,  # single EN effect text
                "flavor_texts": flavor_entries, # list of flavor text per game
                "effect_changes": eff_changes, # list of effect changes per game
                "pokemon_with_ability": pkmn, # list of pkmn with, if hidden and slot
                })
            
    fetch_range(1, B_ABILITY, "First Wave")
    tqdm.write("🌀 First Wave Complete...")
    
    fetch_range(NEW_A_START, NEW_A_END, "Alt Abilities being fetched") 
    tqdm.write("🐸 Alt Abilities Complete...")
    
    out_list = exist_data + ability_list
    out_list = sorted(out_list, key=lambda x: x["id"]) #sorts by id
    
    with open(OUTPUT_FILE, 'w') as file:
        json.dump(out_list, file, indent=4)
    
    tqdm.write("✅ All Abilities fetched and saved! ✅")
        
if __name__ == "__main__":
    grab_ability()
    
    
    
    
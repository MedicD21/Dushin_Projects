import requests
import json
import os
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[2]
DATA_RAW = ROOT / "data" / "raw"

def grab_name(): # Grabs Pokemon names from PokeAPI
    
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    fn = DATA_RAW / "pokemon_names.json"
    base_url = "https://pokeapi.co/api/v2/pokemon/"
    count = 1
    p_name = []
    MAX_POKEMON = 1025
    
    while count < 4:
        time.sleep(.1) # to avoid hitting API rate limits
        response = requests.get(f"{base_url}{count}")
        if response.status_code == 200:
            data = response.json()
            name = data['name'] # gets pokemon name from dict key
            p_name.append({"id": count, "name": name})
            print(f"{name} added to {fn}")

        else:
            print("Bad Url")
        count += 1

    try:
        with open(fn, 'w') as file:
            json.dump(p_name, file, indent=4,) #writes to json 
    except OSError as e:
        print(f"Error writing to {fn}: {e}")
    return p_name
        
if __name__ == "__main__":
    grab_name()
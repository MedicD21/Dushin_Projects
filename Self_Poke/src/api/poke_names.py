import json
from tqdm import tqdm
from pathlib import Path
from .client import get

#creates path to output file
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "pokemon_names.json"
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
BASE_PKMN = 1025
VARIANT_START = 10001
VARIANT_END   = 10303  
#=====================
def grab_names(): 
    
    pkmn_list = [] 
    existing_data = []
    if OUTPUT_FILE.exists(): #checks if file exists
        with open(OUTPUT_FILE, "r") as file:
            existing_data = json.load(file)
    
    #creates set of existing ids to avoid duplicates        
    existing_ids = { entry["id"] for entry in existing_data} 
    
    # Fetching function with progress bar
    def fetch_range(start, end, tag="Fetching"):
        for pokemon_id in tqdm(range(start, end + 1), desc=tag):
            
            if pokemon_id in existing_ids:
                continue

            url = BASE_URL + str(pokemon_id)
            data = get(url)

            if data is None:
                continue

            name = data["name"]
            tqdm.write(f"Fetched: ID {pokemon_id}, Name: {name}")

            pkmn_list.append({
                "id": pokemon_id,
                "name": name
            })

    # Fetch base Pokémon
    fetch_range(1, BASE_PKMN, "Base Pokémon")
    tqdm.write("Base Pokémon fetch complete.")

    # Fetch variant Pokémon
    fetch_range(VARIANT_START, VARIANT_END, "Variant Pokémon")
    tqdm.write("Variant Pokémon fetch complete.")
        
    out_list = existing_data + pkmn_list
        
    with open(OUTPUT_FILE, "w") as file: #writes to json 
        json.dump(out_list, file, indent=4) #dumps the list into json

if __name__ == "__main__":
    grab_names()
    
       
    

    
    
    
    
    
    
    
    
    
  
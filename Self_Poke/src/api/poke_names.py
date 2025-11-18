import json
import time
from pathlib import Path
from api.client import get

#creates path to output file
ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "pokemon_names.json"
BASE_URL = "https://pokeapi.co/api/v2/pokemon/"
MAX_PKMN = 1025

def grab_names(): 
    
    pkmn_list = [] #creates list
    
    for pokemon_id in range(1, MAX_PKMN + 1): #loop through pokemon starting at 1
        
        url = BASE_URL + str(pokemon_id) #adds 1 to base url
        data = get(url) #runs client get to look at pokeapi data
        
        if data is None: 
            continue
        
        name = data["name"] #variable name created from finding name on pokeapi
        
        pkmn_list.append({
            "id": pokemon_id, 
            "name": name
        }) #addes variable id and name pulled to the list
        
    with open(OUTPUT_FILE, "w") as file: #writes to json 
        json.dump(pkmn_list, file, indent=4) #dumps the list into json

if __name__ == "__main__":
    grab_names()
    
       
    

    
    
    
    
    
    
    
    
    
  
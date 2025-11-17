import requests
import time
from libpath 

def grab_name(): # Grabs Pokemon names from PokeAPI
    
    base_url = "https://pokeapi.co/api/v2/"
    count = 1
    p_name = []
    MAX_POKEMON = 1025
    
    while count < 4:
        time.sleep(.5) # to avoid hitting API rate limits
        response = requests.get(f"{base_url}")
        if response.status_code == 200:
            
            data = response.json()
            name = data['name'] # gets pokemon name from dict key
            p_name.append({"id": count, "name": name})
            print(f"{name} added to {fn}")

        else:
            
            print("Bad Url: Retry")
            
            
        count += 1
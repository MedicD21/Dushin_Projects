import json
from tqdm import tqdm
from pathlib import Path
from .client import get

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw"
DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = DATA_DIR / "pokemon_abilities.json"
BASE_URL = "https://pokeapi.co/api/v2/item/"

def grab_item():
    
    item_list = []
    exist_data = []
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r') as file:
            exist_data = json.load(file)
    
    exist_ids = { entry["id"] for entry in exist_data}
    
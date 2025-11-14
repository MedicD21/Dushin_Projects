# Pokemon Data Collection System - Output Locations

## Where Scrapers Save Their Data

All scrapers now save their data to the `data/` directory to keep everything organized.

### Output Files by Scraper:

#### 1. Basic Pokemon Scraper (`scrapers/pokemon_info.py`)

- **Output**: `data/pokemon_data.json`
- **Contains**: Basic Pokemon info (name, number, types, abilities, base stats)
- **Format**: Array of Pokemon objects with core information

#### 2. Comprehensive Pokemon Scraper (`scrapers/comprehensive_scraper.py`)

- **Output**: `data/pokemon_data.json` (updates existing file)
- **Contains**: Enhanced Pokemon data including:
  - Physical info (height, weight, species)
  - Regional Pokedex numbers
  - Game appearances
  - Evolution information
  - Location data
- **Format**: Updates existing Pokemon objects with additional fields

#### 3. Game Dex Scraper (`scrapers/game_dex_scraper_v3.py`)

- **Output**: `data/pokemon_data.json` (updates existing file)
- **Contains**: Regional dex numbers and game appearances
- **Format**: Adds `game_appearances` field to existing Pokemon data

#### 4. Abilities Scraper (`scrapers/abilities_scraper.py`)

- **Output**:
  - `data/abilities_data.json` (structured data)
  - `data/abilities_data.txt` (human-readable text)
- **Contains**: Detailed ability information, descriptions, and which Pokemon have each ability
- **Format**: Array of ability objects with descriptions and Pokemon lists

### Data Directory Structure:

```
data/
├── pokemon_data.json      # Main Pokemon dataset (updated by multiple scrapers)
├── pokemon_games.json     # Game information by generation
├── abilities_data.json    # Abilities database
├── abilities_data.txt     # Human-readable abilities list
├── moves_data.json        # (Future: moves database)
├── locations_data.json    # (Future: location data)
└── items_data.json        # (Future: items database)
```

### How Data Updates Work:

1. **Basic Scraper**: Creates the initial `pokemon_data.json` file
2. **Other Scrapers**: Load existing `pokemon_data.json` and add new fields
3. **All Changes**: Are saved back to the same file, preserving existing data

### Example Data Structure:

After running multiple scrapers, a Pokemon entry looks like:

```json
{
  "number": "#0001",
  "name": "Bulbasaur",
  "types": ["Grass", "Poison"],
  "abilities": ["Overgrow", "Chlorophyll"],
  "base_stats": {
    "hp": 45,
    "attack": 49,
    "defense": 49,
    "sp_attack": 65,
    "sp_defense": 65,
    "speed": 45
  },
  "physical_info": {
    "species": "Seed Pokémon",
    "height_meters": 0.7,
    "weight_kilograms": 6.9
  },
  "game_appearances": {
    "Red": { "dex_number": 1, "available": true, "region": "Kanto (RBY)" },
    "Blue": { "dex_number": 1, "available": true, "region": "Kanto (RBY)" },
    "Yellow": { "dex_number": 1, "available": true, "region": "Kanto (RBY)" }
  },
  "evolution_info": {
    "has_evolution_data": true,
    "evolution_text": ["Evolves into Ivysaur at level 16"]
  }
}
```

### Running Scrapers:

To run any scraper and see where it saves data:

```bash
# Make sure you're in the project directory and venv is activated
cd /Users/dustinschaaf/Desktop/Dushin_Projects/PokeDex_Info
source venv/bin/activate

# Run individual scrapers
python scrapers/pokemon_info.py          # → data/pokemon_data.json
python scrapers/comprehensive_scraper.py # → data/pokemon_data.json (enhanced)
python scrapers/abilities_scraper.py     # → data/abilities_data.json & .txt

# Or use the main orchestrator
python main.py
```

### Checking Output:

After running scrapers, check the data directory:

```bash
ls -la data/
cat data/pokemon_data.json | jq length  # Count Pokemon entries
head -20 data/abilities_data.txt         # Preview abilities text file
```

All scrapers include progress output showing what they're doing and confirm where they save the data when complete.

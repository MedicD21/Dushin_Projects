# Pokemon Data Collection System

A comprehensive Python-based system for scraping and organizing Pokemon data from Serebii.net.

## Project Structure

```
PokeDex_Info/
├── main.py                     # Main orchestrator script
├── requirements.txt            # Python dependencies
├── data/                       # Data storage
│   ├── pokemon_data.json      # Main Pokemon dataset
│   ├── pokemon_games.json     # Pokemon games information
│   ├── abilities_data.json    # Abilities database
│   └── moves_data.json        # Moves database
├── scrapers/                   # Specialized scrapers
│   ├── pokemon_info.py        # Basic Pokemon info scraper
│   ├── comprehensive_scraper.py # Detailed Pokemon data scraper
│   ├── game_dex_scraper_v3.py # Game-specific dex numbers
│   └── abilities_scraper.py   # Abilities scraper
├── utils/                      # Shared utilities
│   ├── config.py              # Configuration and utilities
│   └── grab_info.py           # Data access functions
└── README.md                   # This file
```

## Features

### Data Collection

- **Basic Pokemon Info**: National dex number, name, types, abilities, base stats
- **Physical Information**: Height, weight, species category
- **Regional Pokedex Numbers**: Dex numbers across all games and regions
- **Game Appearances**: Which games each Pokemon appears in
- **Evolution Data**: Evolution chains and requirements
- **Location Data**: Where to find Pokemon in each game
- **Abilities Database**: Detailed ability information
- **Moves Database**: Move sets and learning methods

### Scrapers Available

1. **Basic Scraper** (`pokemon_info.py`)

   - Scrapes fundamental Pokemon data from Serebii's main Pokedex
   - Collects: National #, name, types, abilities, base stats (HP, Att, Def, SpA, SpD, Speed)

2. **Comprehensive Scraper** (`comprehensive_scraper.py`)

   - Collects detailed information from individual Pokemon pages
   - Adds: Physical stats, species info, regional dex numbers, game appearances
   - Parses complex HTML structures and concatenated data

3. **Game Dex Scraper** (`game_dex_scraper_v3.py`)

   - Focuses specifically on regional Pokedex numbers
   - Maps regional entries to specific games (e.g., "Kanto (RBY)" → Red/Blue/Yellow)
   - Handles DLC areas and special regions

4. **Abilities Scraper** (`abilities_scraper.py`)
   - Scrapes detailed ability information
   - Collects descriptions, effects, and Pokemon that have each ability

### Utilities

- **Configuration System** (`utils/config.py`)

  - Centralized settings and URL management
  - Data file path management
  - Common parsing utilities
  - Request handling with rate limiting

- **Data Access Functions** (`utils/grab_info.py`)
  - Easy access to Pokemon data
  - Game information queries
  - Data filtering and search functions

## Usage

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main orchestrator
python main.py
```

### Running Individual Scrapers

```bash
# Basic Pokemon data
python scrapers/pokemon_info.py

# Comprehensive data collection
python scrapers/comprehensive_scraper.py

# Game-specific dex numbers
python scrapers/game_dex_scraper_v3.py
```

### Using Data Access Functions

```python
from utils.grab_info import pk_names, get_pokemon_by_name, get_all_games

# Get all Pokemon names
pokemon_names = pk_names()

# Get specific Pokemon data
bulbasaur = get_pokemon_by_name("Bulbasaur")

# Get all games
games = get_all_games()
```

## Data Structure

### Pokemon Data Format

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
    "Red": { "dex_number": 1, "available": true },
    "Blue": { "dex_number": 1, "available": true }
  }
}
```

### Games Data Format

```json
{
  "generation": 1,
  "region": "Kanto",
  "games": ["Red", "Blue", "Yellow"],
  "release_year": 1996,
  "platform": "Game Boy"
}
```

## Regional Dex Mapping

The system automatically maps regional Pokedex entries to specific games:

- **Kanto (RBY)** → Red, Blue, Yellow
- **Kanto (Let's Go)** → Let's Go Pikachu, Let's Go Eevee
- **Johto (GSC)** → Gold, Silver, Crystal
- **Johto (HGSS)** → HeartGold, SoulSilver
- **Central Kalos** → X, Y
- **Isle of Armor** → Sword, Shield (DLC)
- **Blueberry** → Scarlet, Violet (DLC)
- **Lumiose** → Legends Z-A
- And many more...

## Development

### Adding New Scrapers

1. Create new scraper in `scrapers/` directory
2. Import and add to `main.py` orchestrator
3. Follow existing patterns for data structure
4. Use utilities from `utils/config.py` for consistency

### Data Management

- Automatic backups before major operations
- Data validation and integrity checking
- Export tools for analysis
- Duplicate detection and cleanup

## Notes

- Scrapers include respectful delays (0.5s between requests)
- Error handling for network issues and parsing errors
- Progress saving for long-running operations
- Comprehensive logging and status reporting

## Contributing

When contributing:

1. Follow the established directory structure
2. Use the shared utilities for consistency
3. Include error handling and progress reporting
4. Test scrapers on small datasets first
5. Document any new data fields or structures

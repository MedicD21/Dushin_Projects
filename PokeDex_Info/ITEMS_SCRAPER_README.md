# Items Scraper Documentation

## Overview

The `items_scraper.py` module scrapes comprehensive item data from Serebii ItemDex and exports it to organized JSON files.

## Website Structure Analysis

### Serebii ItemDex Structure

The Serebii ItemDex (`https://www.serebii.net/itemdex/`) is organized with:

1. **Main Page** (`/itemdex/`): Contains dropdown menus and links to category pages
2. **Category Pages**: Organized lists of items by type

   - `/itemdex/list/pokeball.shtml` - Poké Balls (38 items)
   - `/itemdex/list/recovery.shtml` - Recovery items (43 items)
   - `/itemdex/list/holditem.shtml` - Hold Items (256+ items)
   - `/itemdex/list/evolutionary.shtml` - Evolutionary Items (122+ items)
   - `/itemdex/list/keyitem.shtml` - Key Items (279+ items)
   - `/itemdex/list/fossil.shtml` - Fossils & Others (237+ items)
   - `/itemdex/list/vitamins.shtml` - Stat Items (143+ items)
   - `/itemdex/list/mail.shtml` - Mail (46 items)
   - `/itemdex/list/berry.shtml` - Berries (85+ items)

3. **Individual Item Pages**: Each item has a detailed page at `/itemdex/{item-name}.shtml`

### Data Structure Extracted

Each item page contains the following data in HTML tables:

- **Item Name**: Header or title
- **Sprites**: Item sprite images
- **Item Type**: Category classification
- **Japanese Name**: Original Japanese name
- **Price Information**:
  - Purchase Price
  - Sell Price
- **In-Depth Effect**: Description of what the item does
- **Flavor Text**: Game-specific descriptions (per game version)
- **Attainable In**: List of games where the item appears
- **Locations**: Where to find the item in-game (game-specific)
- **Shopping Details**: Where items can be purchased (game-specific)

## Scraper Implementation

### Class: `ItemDexScraper`

**Methods:**

- `fetch_page(url)`: Fetches and parses a page using BeautifulSoup
- `extract_item_from_page(item_url, item_name, category)`: Extracts all data from an individual item page
- `scrape_category(category_name, category_url)`: Scrapes all items in a category
- `scrape_all()`: Orchestrates scraping of all categories
- `save_to_json(items, filename)`: Saves items to a single JSON file with metadata
- `save_by_category()`: Saves items organized by category into separate JSON files

### Output Format

#### Main File: `data/items_data.json`

```json
{
  "metadata": {
    "total_items": 1000+,
    "categories": [
      "Poké Balls",
      "Recovery",
      "Hold Item",
      ...
    ],
    "scrape_date": "2025-11-16 10:30:00"
  },
  "items": [
    {
      "name": "Beast Ball",
      "category": "Poké Balls",
      "url": "/itemdex/beastball.shtml",
      "effect": "This special Poké Ball is used for catching Ultra Beasts...",
      "price": {
        "purchase": 0,
        "sell": 0
      },
      "games": ["Sun", "Moon", "Ultra Sun", "Ultra Moon", "Sword", "Shield", "Scarlet", "Violet"],
      "flavor_text": {
        "Sun": "A special Poké Ball designed to catch Ultra Beasts. It has a...",
        "Sword": "A somewhat different Poké Ball that has a low success rate..."
      },
      "locations": {
        "Sun": "Route 2, Route 8, Route 13, Aether Paradise, Seafolk Village",
        "Sword": "Stow-on-Side, Wyndon Stadium"
      },
      "japanese_name": "ウルトラボール"
    },
    ...
  ]
}
```

#### Category Files: `data/items_by_category/{category_name}.json`

Each category gets its own file with the same structure but only items from that category.

## Running the Scraper

### From Command Line

```bash
python3 scrapers/items_scraper.py
```

### From Main Menu

```bash
python3 main.py
```

Then select option **8** to run the items scraper.

### Integration in Main Menu

The items scraper is integrated into `main.py` with the following options:

- **Option 8**: Run items scraper
- **Option 9**: Run all scrapers (includes items)

## Data Collection Strategy

The scraper uses a multi-step approach:

1. **Category Discovery**: Identifies category pages from the main ItemDex page
2. **Item Discovery**: Finds all items within each category
3. **Detail Extraction**: Scrapes individual item pages for comprehensive data
4. **Data Organization**: Sorts and structures the data
5. **File Output**: Saves to both comprehensive and category-specific files

### Rate Limiting

- 0.2 second delay between item page requests (respectful scraping)
- Prevents overwhelming the server

## Performance Notes

- **Scope**: 1,000+ items across 9 categories
- **Scraping Time**: ~10-15 minutes for complete dataset (due to individual page scraping)
- **File Size**: ~2-3 MB for comprehensive JSON
- **Category-Specific Files**: ~200-400 KB each

## Error Handling

The scraper handles:

- Network timeouts
- Missing or malformed pages
- Incomplete data extraction
- Invalid item names/URLs

## Future Enhancements

Potential improvements:

- Add item evolution items tracking
- Extract held item effects (stat boosts, etc.)
- Add breeding item information
- Link items to Pokémon that use them
- Extract item generation introduction data
- Add item artwork/sprite data

## Dependencies

- `requests`: HTTP requests
- `BeautifulSoup4`: HTML parsing
- `json`: JSON file operations
- `sys`, `os`: System/path operations
- `time`: Rate limiting

## Notes

- The scraper respects Serebii's server by adding delays between requests
- All data is extracted from publicly available HTML
- The scraper adapts to the actual HTML structure found, not hardcoded selectors
- Duplicate items (appearing in multiple tables) are automatically deduplicated

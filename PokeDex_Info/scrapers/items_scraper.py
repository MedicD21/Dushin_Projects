#!/usr/bin/env python3
"""
Serebii ItemDex Scraper
Extracts all items from Serebii ItemDex with detailed information
"""

import sys
import os
import json
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
from pathlib import Path
from tqdm import tqdm

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from config import PokeDataUtils, DATA_FILES

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
}

# Category list pages on Serebii (based on what we found)
CATEGORY_PAGES = {
    'Poké Balls': '/itemdex/list/pokeball.shtml',
    'Recovery': '/itemdex/list/recovery.shtml',
    'Hold Item': '/itemdex/list/holditem.shtml',
    'Evolutionary Items': '/itemdex/list/evolutionary.shtml',
    'Key Items': '/itemdex/list/keyitem.shtml',
    'Fossils & Others': '/itemdex/list/fossil.shtml',
    'Stat Items': '/itemdex/list/vitamins.shtml',
    'Mail': '/itemdex/list/mail.shtml',
    'Berries': '/itemdex/list/berry.shtml',
}


class ItemDexScraper:
    """Scrapes items from Serebii ItemDex"""

    # Map shorthand game codes to full game names (for compatibility with pokemon_games.json)
    GAME_CODE_MAP = {
        # Gen 1
        'RGBY': ['Red', 'Blue', 'Yellow'],
        # Gen 2
        'GS': ['Gold', 'Silver'],
        'C': ['Crystal'],
        # Gen 3
        'RS': ['Ruby', 'Sapphire'],
        'E': ['Emerald'],
        'FRLG': ['FireRed', 'LeafGreen'],
        # Gen 4
        'DP': ['Diamond', 'Pearl'],
        'Pt': ['Platinum'],
        'HG': ['HeartGold'],
        'SS': ['SoulSilver'],
        # Gen 5
        'B': ['Black'],
        'W': ['White'],
        'B2': ['Black 2'],
        'W2': ['White 2'],
        # Gen 6
        'X': ['X'],
        'Y': ['Y'],
        'ΩR': ['Omega Ruby'],
        'αS': ['Alpha Sapphire'],
        # Gen 7
        'S': ['Sun'],
        'M': ['Moon'],
        'US': ['Ultra Sun'],
        'UM': ['Ultra Moon'],
        'LGP': ['Let\'s Go Pikachu'],
        'LGE': ['Let\'s Go Eevee'],
        # Gen 8
        'SW': ['Sword'],
        'SH': ['Shield'],
        'BDSP': ['Brilliant Diamond', 'Shining Pearl'],
        'PLA': ['Legends Arceus'],
        # Gen 9
        # Scarlet and Violet don't have shorthand in the scrapes
    }

    def __init__(self):
        self.utils = PokeDataUtils()
        self.session = requests.Session()
        self.base_url = "https://www.serebii.net"
        self.items = {}
        self.items_by_category = {}


    def fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch and parse a page"""
        try:
            response = self.session.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
        return None

    def extract_item_from_page(self, item_url: str, item_name: str, category: str) -> Dict:
        """Extract detailed information from an individual item page"""
        full_url = f"{self.base_url}{item_url}"
        soup = self.fetch_page(full_url)

        if not soup:
            return self._create_empty_item(item_name, category, item_url)

        item_data = {
            'name': item_name,
            'category': category,
            'url': item_url,
            'effect': '',
            'held_item_effects': [],  # NEW: stat boosts and special effects
            'price': {'purchase': 0, 'sell': 0},
            'games': [],
            'flavor_text': {},
            'locations': {},
            'japanese_name': '',
            'generation_introduced': None,  # NEW: when item was added
            'evolution_info': {  # NEW: which Pokemon evolve with this item
                'pokemon': [],
                'method': ''
            },
            'breeding_info': '',  # NEW: breeding-related information
            'pokemon_usage': []  # NEW: Pokemon that use/hold this item
        }

        tables = soup.find_all('table')
        page_text = soup.get_text().lower()

        for table in tables:
            rows = table.find_all('tr')

            # Look for specific sections in the table
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue

                first_cell = cells[0].get_text().strip()

                # Japanese Name and Item Type
                if 'Japanese Name' in first_cell and len(cells) > 1:
                    jp_text = cells[1].get_text().strip()
                    if jp_text:
                        item_data['japanese_name'] = jp_text.split('\n')[0]

                # Price information
                if 'Purchase Price' in first_cell and len(cells) > 1:
                    try:
                        price_text = cells[1].get_text().strip()
                        price_val = ''.join(c for c in price_text if c.isdigit())
                        if price_val:
                            item_data['price']['purchase'] = int(price_val)
                    except:
                        pass

                if 'Sell Price' in first_cell and len(cells) > 1:
                    try:
                        price_text = cells[1].get_text().strip()
                        price_val = ''.join(c for c in price_text if c.isdigit())
                        if price_val:
                            item_data['price']['sell'] = int(price_val)
                    except:
                        pass

                # In-Depth Effect
                if 'In-Depth Effect' in first_cell or 'In-Game Description' in first_cell:
                    if i + 1 < len(rows):
                        effect_text = rows[i + 1].get_text().strip()
                        item_data['effect'] = effect_text[:500]

                # Flavor Text (game-specific descriptions)
                # Format: Each row has [Game1, Game2, FlavorText] or [Game, FlavorText]
                if 'Flavour Text' in first_cell or 'Flavor Text' in first_cell:
                    j = i + 1
                    while j < len(rows) and j < i + 20:
                        flavor_cells = rows[j].find_all(['td', 'th'])
                        if len(flavor_cells) >= 2:
                            # Get all cell texts
                            cell_texts = [cell.get_text().strip() for cell in flavor_cells]
                            
                            # Last cell is always the flavor text description
                            flavor_text_content = cell_texts[-1]
                            
                            # First 1-2 cells are game names
                            game_names = cell_texts[:-1]
                            
                            # Store with each game name as key
                            if flavor_text_content and len(flavor_text_content) > 10:  # Ensure it's actual text
                                for game_name in game_names:
                                    if game_name and game_name not in ['Flavour Text', 'Flavor Text']:
                                        item_data['flavor_text'][game_name] = flavor_text_content[:300]
                        j += 1

                # Games available (Attainable In section)
                # Format: Row 1 = game abbrevs, Row 2 = Yes confirmations, Row 3 = more games, etc.
                if 'Attainable In' in first_cell:
                    j = i + 1
                    games_found = set()
                    while j < len(rows) and j < i + 8:
                        games_row = rows[j]
                        games_cells = games_row.find_all(['td', 'th'])
                        if games_cells:
                            games_text = [cell.get_text().strip() for cell in games_cells]
                            
                            # Filter: only add game abbreviations, not "Yes" or empty values
                            # Valid game codes: 1-5 chars, no spaces, not "Yes"
                            for game_code in games_text:
                                if game_code and game_code != 'Yes' and 0 < len(game_code) <= 5:
                                    # Exclude common non-game text
                                    if not any(skip in game_code for skip in ['Attainable', 'Text']):
                                        games_found.add(game_code)
                        j += 1
                    
                    # Convert shorthand codes to full game names
                    if games_found:
                        full_game_names = self._convert_game_codes_to_names(games_found)
                        item_data['games'].extend(full_game_names)

        # Extract additional data from page content
        item_data['generation_introduced'] = self._extract_generation(page_text)
        item_data['held_item_effects'] = self._extract_held_item_effects(soup, item_name)
        item_data['evolution_info'] = self._extract_evolution_info(soup, item_name)
        item_data['breeding_info'] = self._extract_breeding_info(soup)
        item_data['pokemon_usage'] = self._extract_pokemon_usage(item_name)

        return item_data

    def _convert_game_codes_to_names(self, game_codes: set) -> List[str]:
        """Convert game shorthand codes to full game names for consistency with pokemon_games.json"""
        full_names = set()
        unmatched_codes = []
        
        for code in game_codes:
            if code in self.GAME_CODE_MAP:
                full_names.update(self.GAME_CODE_MAP[code])
            else:
                # Handle any special cases (like Scarlet, Violet which don't have shorthand)
                # These might be passed through directly
                unmatched_codes.append(code)
        
        # Add any unmatched codes directly (for future-proofing)
        full_names.update(unmatched_codes)
        
        return sorted(list(full_names))

    def _create_empty_item(self, name: str, category: str, url: str) -> Dict:
        """Create an empty item template"""
        return {
            'name': name,
            'category': category,
            'url': url,
            'effect': '',
            'held_item_effects': [],
            'price': {'purchase': 0, 'sell': 0},
            'games': [],
            'flavor_text': {},
            'locations': {},
            'japanese_name': '',
            'generation_introduced': None,
            'evolution_info': {'pokemon': [], 'method': ''},
            'breeding_info': '',
            'pokemon_usage': []
        }

    def _extract_generation(self, page_text: str) -> Optional[int]:
        """Extract which generation item was introduced in"""
        gen_mapping = {
            'generation i': 1, 'gen i': 1, 'gen 1': 1,
            'generation ii': 2, 'gen ii': 2, 'gen 2': 2,
            'generation iii': 3, 'gen iii': 3, 'gen 3': 3,
            'generation iv': 4, 'gen iv': 4, 'gen 4': 4,
            'generation v': 5, 'gen v': 5, 'gen 5': 5,
            'generation vi': 6, 'gen vi': 6, 'gen 6': 6,
            'generation vii': 7, 'gen vii': 7, 'gen 7': 7,
            'generation viii': 8, 'gen viii': 8, 'gen 8': 8,
            'generation ix': 9, 'gen ix': 9, 'gen 9': 9,
        }

        for gen_text, gen_num in gen_mapping.items():
            if gen_text in page_text:
                return gen_num

        return None

    def _extract_held_item_effects(self, soup: BeautifulSoup, item_name: str) -> List[str]:
        """Extract held item effects and stat boosts"""
        effects = []
        page_text = soup.get_text()

        # Look for common held item effect patterns
        effect_patterns = [
            'raises', 'boosts', 'increases', 'multiplies', 'doubles',
            'reduces', 'decreases', 'resistance', 'immunity', 'prevents',
            'damage', 'accuracy', 'evasion', 'speed', 'critical',
            '+10%', '+20%', '+50%', '1.5x', '2x',
        ]

        paragraphs = soup.find_all(['p', 'div'])
        for para in paragraphs:
            text = para.get_text().strip()
            if any(pattern in text.lower() for pattern in effect_patterns) and len(text) > 20 and len(text) < 300:
                if text not in effects:
                    effects.append(text)

        return effects[:5]  # Return first 5 effects

    def _extract_evolution_info(self, soup: BeautifulSoup, item_name: str) -> Dict:
        """Extract evolution items and which Pokemon they evolve"""
        evolution_info = {'pokemon': [], 'method': ''}

        page_text = soup.get_text()
        
        # Check if this is an evolution item
        if 'evolution' in page_text.lower() or 'evolve' in page_text.lower():
            evolution_info['method'] = 'Evolution Item'

            # Try to find Pokemon names that use this item for evolution
            # Common Pokemon names (simplified list - you can expand)
            pokemon_list = [
                'Pikachu', 'Raichu', 'Nidoran', 'Nidoking', 'Nidoqueen',
                'Cleffa', 'Clefairy', 'Clefable', 'Vulpix', 'Ninetales',
                'Jigglypuff', 'Wigglytuff', 'Oddish', 'Gloom', 'Vileplume',
                'Paras', 'Parasect', 'Venonat', 'Venomoth', 'Diglett',
                'Dugtrio', 'Meowth', 'Persian', 'Psyduck', 'Golduck',
                'Mankey', 'Primeape', 'Growlithe', 'Arcanine', 'Poliwag',
                'Poliwrath', 'Poliwag', 'Abra', 'Kadabra', 'Alakazam',
                'Machop', 'Machoke', 'Machamp', 'Bellsprout', 'Weepinbell',
                'Victreebel', 'Tentacool', 'Tentacruel', 'Slowpoke', 'Slowbro',
                'Seel', 'Dewgong', 'Shellder', 'Cloyster', 'Gastly',
                'Haunter', 'Gengar', 'Onix', 'Steelix', 'Drowzee', 'Hypno',
                'Krabby', 'Kingler', 'Voltorb', 'Electrode', 'Exeggcute',
                'Exeggutor', 'Cubone', 'Marowak', 'Hitmonlee', 'Hitmonchan',
                'Lickitung', 'Lickilicky', 'Koffing', 'Weezing', 'Rhyhorn',
                'Rhydon', 'Rhyperior', 'Chansey', 'Blissey', 'Tangela',
                'Tangrowth', 'Kangaskhan', 'Horsea', 'Seadra', 'Kingdra',
                'Goldeen', 'Seaking', 'Staryu', 'Starmie', 'Mr. Mime',
                'Jynx', 'Electabuzz', 'Electivire', 'Magby', 'Magnemite',
                'Magneton', 'Magnezone', 'Farfetch\'d', 'Doduo', 'Dodrio',
                'Seel', 'Dewgong', 'Grimer', 'Muk', 'Shellder', 'Cloyster',
                'Gastly', 'Haunter', 'Gengar', 'Onix', 'Drowzee', 'Hypno',
                'Krabby', 'Kingler', 'Exeggcute', 'Exeggutor', 'Cubone',
                'Marowak', 'Hitmonlee', 'Hitmonchan', 'Lickitung', 'Koffing',
                'Weezing', 'Rhyhorn', 'Rhydon', 'Chansey', 'Tangela',
                'Kangaskhan', 'Horsea', 'Seadra', 'Goldeen', 'Seaking',
                'Staryu', 'Starmie', 'Mr. Mime', 'Jynx', 'Electabuzz',
                'Magnemite', 'Magneton', 'Farfetch\'d', 'Doduo', 'Dodrio',
                'Seel', 'Grimer', 'Muk', 'Shellder', 'Gastly', 'Haunter',
                'Gengar', 'Onix', 'Drowzee', 'Krabby', 'Kingler', 'Voltorb',
                'Electrode', 'Exeggcute', 'Cubone', 'Hitmonlee', 'Hitmonchan',
                'Lickitung', 'Rhyhorn', 'Chansey', 'Tangela', 'Kangaskhan',
                'Horsea', 'Goldeen', 'Staryu', 'Starmie', 'Mr. Mime', 'Jynx',
                'Electabuzz', 'Magnemite', 'Magneton', 'Doduo', 'Seel',
            ]

            for pokemon in pokemon_list:
                if pokemon.lower() in page_text.lower():
                    evolution_info['pokemon'].append(pokemon)

        return evolution_info

    def _extract_breeding_info(self, soup: BeautifulSoup) -> str:
        """Extract breeding-related information"""
        page_text = soup.get_text().lower()

        breeding_keywords = [
            'breeding', 'egg', 'hatch', 'incubate', 'fertility',
            'parent', 'offspring', 'breed', 'breedable'
        ]

        if any(keyword in page_text for keyword in breeding_keywords):
            # Find relevant text sections
            paragraphs = soup.find_all(['p', 'div'])
            for para in paragraphs:
                text = para.get_text().strip()
                if any(keyword in text.lower() for keyword in breeding_keywords) and len(text) > 30:
                    return text[:200]

        return ""

    def _extract_pokemon_usage(self, item_name: str) -> List[str]:
        """Extract Pokemon that use or hold this item"""
        # This would require cross-referencing with Pokemon data
        # For now, we'll implement a basic version
        pokemon_usage = []

        # Known common mappings (can be expanded with Pokemon data)
        usage_mappings = {
            'Assault Vest': ['Pokémon that value special defense'],
            'Choice Band': ['Physical attacking Pokémon'],
            'Choice Scarf': ['Fast Pokémon needing speed'],
            'Destiny Knot': ['Breeding'],
            'Focus Sash': ['Fragile sweepers'],
            'Life Orb': ['Sweepers and attackers'],
            'Leftovers': ['Walls and bulky Pokémon'],
            'Trick Room': ['Slow Pokémon'],
        }

        if item_name in usage_mappings:
            pokemon_usage = usage_mappings[item_name]

        return pokemon_usage

    def scrape_category(self, category_name: str, category_url: str) -> List[Dict]:
        """Scrape all items in a category"""
        print(f"\n📂 Scraping {category_name}...")
        full_url = f"{self.base_url}{category_url}"
        soup = self.fetch_page(full_url)

        if not soup:
            print(f"  ❌ Failed to fetch {category_name}")
            return []

        items = []
        tables = soup.find_all('table')
        item_links_found = []

        # Find the main items table (usually table 1, the big one with all items)
        for table in tables[1:]:
            rows = table.find_all('tr')

            # Skip header and separator rows
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                if not cells or len(cells) < 3:
                    continue

                # Item link is usually in one of the first 3 cells
                item_link = None
                item_name = ''

                for cell in cells[:3]:
                    link = cell.find('a', href=True)
                    if link and '/itemdex/' in link['href'] and not 'list' in link['href']:
                        item_link = link['href']
                        item_name = link.get_text().strip()
                        break

                # If no link found in cells, get text from cell
                if not item_name:
                    for cell in cells:
                        text = cell.get_text().strip()
                        # Valid item names are 2-100 chars and don't contain headers
                        if text and 2 < len(text) < 100 and '====' not in text:
                            item_name = text
                            break

                if item_link and item_name:
                    # Skip empty or separator rows
                    if not item_name or '====' in item_name:
                        continue

                    item_links_found.append((item_name, item_link))

        # Scrape each item with progress bar
        with tqdm(total=len(item_links_found), desc=f"  {category_name}", ncols=80, unit="items") as pbar:
            for item_name, item_link in item_links_found:
                item_data = self.extract_item_from_page(item_link, item_name, category_name)
                items.append(item_data)
                pbar.update(1)
                
                # Rate limiting
                time.sleep(0.2)

        if items:
            print(f"  ✅ Found {len(items)} items in {category_name}")
        return items

    def scrape_all(self) -> tuple:
        """Scrape all item categories"""
        print("="*60)
        print("🔄 Starting ItemDex Scraper")
        print(f"📊 Categories to scrape: {len(CATEGORY_PAGES)}")
        print("="*60)

        all_items = []
        categories_dict = {}

        with tqdm(total=len(CATEGORY_PAGES), desc="Overall Progress", ncols=80, unit="categories") as cat_pbar:
            for category_name, category_url in CATEGORY_PAGES.items():
                items = self.scrape_category(category_name, category_url)
                all_items.extend(items)
                categories_dict[category_name] = items
                self.items_by_category[category_name] = items
                cat_pbar.update(1)

        self.items = {item['name'].lower().replace(' ', '_'): item for item in all_items}

        print("\n" + "="*60)
        print(f"✅ Total items scraped: {len(all_items)}")
        print("="*60)

        return all_items, categories_dict

    def save_to_json(self, items: List[Dict], filename: str = 'items_data.json') -> str:
        """Save items to JSON file"""
        filepath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'items', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # Sort items by name
        sorted_items = sorted(items, key=lambda x: x['name'].lower())

        # Create structure with metadata
        data = {
            'metadata': {
                'total_items': len(sorted_items),
                'categories': sorted(list(set(item['category'] for item in sorted_items))),
                'scrape_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'version': '2.0',
                'new_fields': ['generation_introduced', 'evolution_info', 'breeding_info', 'pokemon_usage', 'held_item_effects']
            },
            'items': sorted_items
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Saved {len(sorted_items)} items to {filepath}")
        return filepath

    def save_by_category(self) -> str:
        """Save items organized by category"""
        category_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'items', 'by_category')
        os.makedirs(category_dir, exist_ok=True)

        print("\n📁 Saving items by category...")

        for category_name, items in self.items_by_category.items():
            # Create filename from category name
            safe_name = category_name.lower().replace(' ', '_').replace('&', 'and')
            filepath = os.path.join(category_dir, f'{safe_name}.json')

            sorted_items = sorted(items, key=lambda x: x['name'].lower())

            category_data = {
                'metadata': {
                    'category': category_name,
                    'total_items': len(sorted_items),
                    'scrape_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'version': '2.0'
                },
                'items': sorted_items
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)

            print(f"  ✓ {category_name:<30} {len(items):>4} items")

        print(f"\n✅ Saved category files to {category_dir}")
        return category_dir


def main():
    """Main execution"""
    scraper = ItemDexScraper()

    # Scrape all items
    all_items, categories = scraper.scrape_all()

    if all_items:
        # Save comprehensive file
        scraper.save_to_json(all_items)

        # Save by category
        scraper.save_by_category()

        print("\n" + "="*60)
        print("🎉 ItemDex Scraper completed successfully!")
        print("="*60)
    else:
        print("❌ No items were scraped. Please check the website structure.")


if __name__ == '__main__':
    main()

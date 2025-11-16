import requests
import os
import json
from pathlib import Path

# Game icon indices from pokeos
# Icons 0-34, 36-41, 59, 69 are available
ICON_INDICES = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 
                20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 37, 38, 
                39, 40, 41, 59, 69}

URL_BASE = "https://assets.pokeos.com/games/icons/"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

def fetch_and_save_game_icons(icons_dir="icons"):
    """Fetch game icons from pokeos and save them locally"""
    # Create icons directory if it doesn't exist
    icon_path = Path(__file__).parent / icons_dir
    icon_path.mkdir(exist_ok=True)
    
    game_icons_map = {}
    successful = 0
    failed = 0
    
    print(f"\n{'='*60}")
    print(f"🎮 Downloading Game Icons")
    print(f"{'='*60}\n")
    
    for num in sorted(ICON_INDICES):
        icon_url = f"{URL_BASE}{num}.png"
        icon_filename = f"game_icon_{num}.png"
        icon_filepath = icon_path / icon_filename
        
        try:
            response = requests.get(icon_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                # Save the image file
                with open(icon_filepath, 'wb') as f:
                    f.write(response.content)
                
                # Store in mapping
                game_icons_map[icon_filename] = icon_url
                print(f"✅ Downloaded {icon_filename} ({len(response.content)} bytes)")
                successful += 1
            else:
                print(f"❌ Failed to download icon {num} - Status: {response.status_code}")
                failed += 1
        except Exception as e:
            print(f"❌ Error downloading icon {num}: {e}")
            failed += 1
    
    # Save mapping JSON file
    json_filepath = Path(__file__).parent / "game_icons.json"
    with open(json_filepath, 'w', encoding='utf-8') as f:
        json.dump(game_icons_map, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"📊 RESULTS:")
    print(f"   ✅ Successful: {successful}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Icons saved to: {icon_path}")
    print(f"   📄 Mapping saved to: {json_filepath}")
    print(f"{'='*60}\n")
    
    return game_icons_map

if __name__ == '__main__':
    fetch_and_save_game_icons()  
    
    
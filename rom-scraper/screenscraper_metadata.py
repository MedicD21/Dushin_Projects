#!/usr/bin/env python3
"""
ScreenScraper Metadata Fetcher
Fetches game metadata, artwork, and information from ScreenScraper.fr
"""

import os
import sys
import requests
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Optional, List
import xml.etree.ElementTree as ET


class ScreenScraperAPI:
    """Handles fetching game metadata from ScreenScraper.fr"""

    BASE_URL = "https://www.screenscraper.fr/api2"

    # System ID mapping (ScreenScraper system IDs)
    SYSTEM_IDS = {
        'nes': 3,
        'snes': 4,
        'n64': 14,
        'gamecube': 13,
        'wii': 16,
        'wiiu': 18,
        'switch': 225,
        'gb': 9,
        'gbc': 10,
        'gba': 12,
        'nds': 15,
        '3ds': 17,
        'genesis': 1,
        'megadrive': 1,
        'sega32x': 19,
        'segacd': 20,
        'saturn': 22,
        'dreamcast': 23,
        'mastersystem': 2,
        'gamegear': 21,
        'psx': 57,
        'ps2': 58,
        'ps3': 59,
        'psp': 61,
        'psvita': 62,
        'arcade': 75,
        'mame': 75,
        'fba': 75,
        'atari2600': 26,
        'atari7800': 43,
        'lynx': 28,
        'jaguar': 27,
        'neogeo': 142,
        'pcengine': 31,
        'turbografx16': 31,
        'wonderswan': 45,
        'wonderswancolor': 46,
    }

    def __init__(self, dev_user: str, dev_password: str, user: str = None, password: str = None):
        """
        Initialize ScreenScraper API client

        Args:
            dev_user: Developer username
            dev_password: Developer password
            user: User account username (optional)
            password: User account password (optional)
        """
        self.dev_user = dev_user
        self.dev_password = dev_password
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.rate_limit_delay = 1.0  # Delay between requests (seconds)
        self.last_request_time = 0

    def _wait_for_rate_limit(self):
        """Implement rate limiting to be nice to ScreenScraper servers"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _build_auth_params(self) -> Dict:
        """Build authentication parameters for API requests"""
        params = {
            'devid': self.dev_user,
            'devpassword': self.dev_password,
            'softname': 'ROM_Scraper/1.0',
        }

        if self.user and self.password:
            params['ssid'] = self.user
            params['sspassword'] = self.password

        return params

    def get_rom_hash(self, rom_path: str) -> Dict[str, str]:
        """
        Calculate ROM file hashes for matching

        Args:
            rom_path: Path to ROM file

        Returns:
            Dictionary with md5, sha1, and crc hashes
        """
        try:
            md5_hash = hashlib.md5()
            sha1_hash = hashlib.sha1()

            with open(rom_path, 'rb') as f:
                # Read file in chunks to handle large files
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
                    sha1_hash.update(chunk)

            return {
                'md5': md5_hash.hexdigest(),
                'sha1': sha1_hash.hexdigest(),
                'size': os.path.getsize(rom_path)
            }

        except Exception as e:
            print(f"Error calculating hash for {rom_path}: {e}")
            return {}

    def search_game(self, system: str, rom_name: str = None, rom_path: str = None) -> Optional[Dict]:
        """
        Search for game metadata

        Args:
            system: System/platform name (e.g., 'snes', 'nes', 'gba')
            rom_name: ROM filename (optional)
            rom_path: Path to ROM file for hash matching (optional, more accurate)

        Returns:
            Game metadata dictionary or None
        """
        self._wait_for_rate_limit()

        # Get system ID
        system_id = self.SYSTEM_IDS.get(system.lower())
        if system_id is None:
            print(f"Unknown system: {system}")
            print(f"Available systems: {', '.join(self.SYSTEM_IDS.keys())}")
            return None

        params = self._build_auth_params()
        params['systemeid'] = system_id
        params['output'] = 'json'

        # Use ROM hash for most accurate matching
        if rom_path and os.path.exists(rom_path):
            print(f"Calculating hash for: {rom_path}")
            hashes = self.get_rom_hash(rom_path)
            if hashes:
                params['md5'] = hashes['md5']
                params['sha1'] = hashes['sha1']
                params['romtaille'] = hashes['size']

        # Fallback to name-based search
        elif rom_name:
            params['romnom'] = rom_name

        else:
            print("Error: Either rom_name or rom_path must be provided")
            return None

        url = f"{self.BASE_URL}/jeuInfos.php"

        try:
            print(f"Searching ScreenScraper for: {rom_name or rom_path}")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()

            # Check for errors
            if 'response' in data:
                if data['response'].get('erreur'):
                    print(f"ScreenScraper error: {data['response']['erreur']}")
                    return None

            # Return game data
            if 'response' in data and 'jeu' in data['response']:
                print("✓ Game found!")
                return data['response']['jeu']
            else:
                print("Game not found in ScreenScraper database")
                return None

        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return None

    def download_media(self, media_url: str, output_path: str) -> bool:
        """
        Download media file (artwork, screenshot, etc.)

        Args:
            media_url: URL of media to download
            output_path: Where to save the file

        Returns:
            True if successful, False otherwise
        """
        self._wait_for_rate_limit()

        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            print(f"Downloading: {output_path.name}")
            response = self.session.get(media_url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"✓ Saved: {output_path}")
            return True

        except Exception as e:
            print(f"Error downloading media: {e}")
            return False

    def scrape_game_complete(self, system: str, rom_path: str, output_dir: str) -> Dict:
        """
        Complete scrape: fetch metadata and download all media

        Args:
            system: System/platform name
            rom_path: Path to ROM file
            output_dir: Directory to save metadata and media

        Returns:
            Dictionary with scraping results
        """
        rom_path = Path(rom_path)
        output_dir = Path(output_dir)

        # Create folder structure compatible with EmulationStation/RetroArch
        system_dir = output_dir / system
        roms_dir = system_dir / "roms"
        media_dir = system_dir / "media"
        images_dir = media_dir / "images"
        videos_dir = media_dir / "videos"
        metadata_dir = system_dir / "metadata"

        for directory in [roms_dir, images_dir, videos_dir, metadata_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        # Search for game
        game_data = self.search_game(system, rom_path=str(rom_path))

        if not game_data:
            return {'success': False, 'error': 'Game not found'}

        # Extract game info
        game_name = game_data.get('noms', [{}])[0].get('text', 'Unknown')
        game_id = game_data.get('id', 'unknown')

        print(f"\nGame: {game_name}")
        print(f"ID: {game_id}")

        results = {
            'success': True,
            'game_name': game_name,
            'game_id': game_id,
            'metadata': {},
            'media': {}
        }

        # Save metadata JSON
        metadata_file = metadata_dir / f"{rom_path.stem}.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Saved metadata: {metadata_file}")
        results['metadata']['json'] = str(metadata_file)

        # Download media files
        medias = game_data.get('medias', [])

        # Priority media types
        media_types = {
            'box-2D': 'boxart',
            'box-3D': 'boxart-3d',
            'screenmarquee': 'marquee',
            'sstitle': 'title',
            'ss': 'screenshot',
            'fanart': 'fanart',
            'video': 'video',
            'video-normalized': 'video-normalized'
        }

        for media in medias:
            media_type = media.get('type')
            media_url = media.get('url')

            if media_type in media_types and media_url:
                # Determine output directory and filename
                if media_type.startswith('video'):
                    output_subdir = videos_dir
                    ext = '.mp4'
                else:
                    output_subdir = images_dir
                    ext = Path(media_url).suffix or '.png'

                friendly_name = media_types[media_type]
                output_file = output_subdir / f"{rom_path.stem}-{friendly_name}{ext}"

                if self.download_media(media_url, output_file):
                    results['media'][friendly_name] = str(output_file)

        # Generate gamelist.xml entry (for EmulationStation)
        self._generate_gamelist_entry(system_dir, rom_path, game_data, results)

        return results

    def _generate_gamelist_entry(self, system_dir: Path, rom_path: Path,
                                 game_data: Dict, scrape_results: Dict):
        """Generate/update gamelist.xml for EmulationStation compatibility"""
        gamelist_file = system_dir / "gamelist.xml"

        # Parse existing gamelist or create new one
        if gamelist_file.exists():
            tree = ET.parse(gamelist_file)
            root = tree.getroot()
        else:
            root = ET.Element("gameList")
            tree = ET.ElementTree(root)

        # Check if game already exists
        existing_game = None
        for game in root.findall('game'):
            path_elem = game.find('path')
            if path_elem is not None and path_elem.text == f"./roms/{rom_path.name}":
                existing_game = game
                break

        # Create or update game entry
        if existing_game is None:
            game_elem = ET.SubElement(root, "game")
        else:
            game_elem = existing_game

        # Update game info
        self._set_xml_element(game_elem, 'path', f"./roms/{rom_path.name}")
        self._set_xml_element(game_elem, 'name', scrape_results['game_name'])

        # Add additional metadata
        if 'descriptions' in game_data and game_data['descriptions']:
            desc = game_data['descriptions'][0].get('text', '')
            self._set_xml_element(game_elem, 'desc', desc)

        if 'dates' in game_data and game_data['dates']:
            release_date = game_data['dates'][0].get('text', '')
            self._set_xml_element(game_elem, 'releasedate', release_date)

        if 'editeur' in game_data:
            self._set_xml_element(game_elem, 'publisher', game_data['editeur'].get('text', ''))

        if 'developpeur' in game_data:
            self._set_xml_element(game_elem, 'developer', game_data['developpeur'].get('text', ''))

        if 'genres' in game_data and game_data['genres']:
            genre = game_data['genres'][0].get('text', '')
            self._set_xml_element(game_elem, 'genre', genre)

        if 'joueurs' in game_data:
            self._set_xml_element(game_elem, 'players', game_data['joueurs'].get('text', ''))

        # Add media paths
        for media_type, media_path in scrape_results['media'].items():
            media_path = Path(media_path)
            relative_path = f"./media/{media_path.parent.name}/{media_path.name}"

            if 'video' in media_type:
                self._set_xml_element(game_elem, 'video', relative_path)
            elif media_type == 'boxart':
                self._set_xml_element(game_elem, 'image', relative_path)
            elif media_type == 'marquee':
                self._set_xml_element(game_elem, 'marquee', relative_path)

        # Write gamelist.xml
        self._indent_xml(root)
        tree.write(gamelist_file, encoding='utf-8', xml_declaration=True)
        print(f"✓ Updated gamelist.xml: {gamelist_file}")

    def _set_xml_element(self, parent: ET.Element, tag: str, text: str):
        """Set or update an XML element"""
        elem = parent.find(tag)
        if elem is None:
            elem = ET.SubElement(parent, tag)
        elem.text = text

    def _indent_xml(self, elem: ET.Element, level: int = 0):
        """Add pretty-printing to XML"""
        indent = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent


def main():
    """Main entry point"""
    print("=== ScreenScraper Metadata Fetcher ===\n")

    # Get credentials
    dev_user = input("Enter dev username (default: MedicD21): ").strip() or "MedicD21"
    dev_password = input("Enter dev password (default: ZMAcfblO1jB): ").strip() or "ZMAcfblO1jB"
    user = input("Enter user account (default: MedicD21): ").strip() or "MedicD21"
    password = input("Enter user password (default: Desmond87): ").strip() or "Desmond87"

    # Initialize API client
    scraper = ScreenScraperAPI(dev_user, dev_password, user, password)

    # Get output directory
    output_dir = input("\nEnter path to save metadata and media: ").strip()
    if not output_dir:
        print("Error: Output directory is required")
        return

    while True:
        print("\n--- Options ---")
        print("1. Scrape single ROM file")
        print("2. Scrape all ROMs in a directory")
        print("3. Search by ROM name (no download)")
        print("4. List available systems")
        print("5. Exit")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == "1":
            system = input("Enter system (e.g., snes, nes, gba): ").strip()
            rom_path = input("Enter path to ROM file: ").strip()

            if os.path.exists(rom_path):
                results = scraper.scrape_game_complete(system, rom_path, output_dir)
                print(f"\nResults: {json.dumps(results, indent=2)}")
            else:
                print(f"Error: ROM file not found: {rom_path}")

        elif choice == "2":
            system = input("Enter system (e.g., snes, nes, gba): ").strip()
            roms_dir = input("Enter path to ROMs directory: ").strip()

            if os.path.isdir(roms_dir):
                rom_files = []
                for ext in ['*.zip', '*.gba', '*.gbc', '*.gb', '*.nes', '*.snes', '*.sfc', '*.bin', '*.iso']:
                    rom_files.extend(Path(roms_dir).glob(ext))

                print(f"\nFound {len(rom_files)} ROM files")

                for idx, rom_file in enumerate(rom_files, 1):
                    print(f"\n[{idx}/{len(rom_files)}] Processing: {rom_file.name}")
                    scraper.scrape_game_complete(system, str(rom_file), output_dir)
                    time.sleep(1)  # Be nice to the API

                print("\n✓ Batch scraping complete!")
            else:
                print(f"Error: Directory not found: {roms_dir}")

        elif choice == "3":
            system = input("Enter system (e.g., snes, nes, gba): ").strip()
            rom_name = input("Enter ROM name: ").strip()

            game_data = scraper.search_game(system, rom_name=rom_name)
            if game_data:
                print(f"\nGame Data:\n{json.dumps(game_data, indent=2)}")

        elif choice == "4":
            print("\nAvailable Systems:")
            for system_name, system_id in sorted(scraper.SYSTEM_IDS.items()):
                print(f"  {system_name}: {system_id}")

        elif choice == "5":
            print("Exiting...")
            break

        else:
            print("Invalid choice")


if __name__ == "__main__":
    main()

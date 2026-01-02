#!/usr/bin/env python3
"""
Archive.org ROM Downloader
Downloads ROM files from Internet Archive collections
"""

import os
import sys
import requests
import json
from pathlib import Path
from typing import List, Dict
import time


class ArchiveRomDownloader:
    """Handles searching and downloading ROMs from Archive.org"""

    BASE_URL = "https://archive.org"
    SEARCH_URL = f"{BASE_URL}/advancedsearch.php"

    # Common ROM collections on Archive.org
    COMMON_COLLECTIONS = [
        "no-intro-rom-sets",
        "mame-merged",
        "redump.org",
        "tosec",
        "mame_chd_game_boy_advance",
        "mame_chd_nintendo_ds",
        "mame_chd_playstation",
        "mame_chd_sega_dreamcast"
    ]

    # Complete ROM sets - Known identifiers for full system sets
    COMPLETE_SETS = {
        'gba': {
            'name': 'Game Boy Advance',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Game Boy Advance',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro GBA set (verified dumps)'
                }
            ]
        },
        'gbc': {
            'name': 'Game Boy Color',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Game Boy Color',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro GBC set (verified dumps)'
                }
            ]
        },
        'gb': {
            'name': 'Game Boy',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Game Boy',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro GB set (verified dumps)'
                }
            ]
        },
        'nes': {
            'name': 'Nintendo Entertainment System',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Nintendo Entertainment System',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro NES set (verified dumps)'
                }
            ]
        },
        'snes': {
            'name': 'Super Nintendo',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Super Nintendo Entertainment System',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro SNES set (verified dumps)'
                }
            ]
        },
        'n64': {
            'name': 'Nintendo 64',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Nintendo 64',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro N64 set (verified dumps)'
                }
            ]
        },
        'nds': {
            'name': 'Nintendo DS',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Nintendo - Nintendo DS',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro DS set (verified dumps)'
                }
            ]
        },
        'genesis': {
            'name': 'Sega Genesis / Mega Drive',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Sega - Mega Drive - Genesis',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro Genesis/MD set (verified dumps)'
                }
            ]
        },
        'mastersystem': {
            'name': 'Sega Master System',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Sega - Master System - Mark III',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro SMS set (verified dumps)'
                }
            ]
        },
        'gamegear': {
            'name': 'Sega Game Gear',
            'sets': [
                {
                    'id': 'no-intro_romsets',
                    'search': 'Sega - Game Gear',
                    'collection': 'no-intro-rom-sets',
                    'type': 'No-Intro',
                    'description': 'Complete No-Intro Game Gear set (verified dumps)'
                }
            ]
        },
        'psx': {
            'name': 'Sony PlayStation',
            'sets': [
                {
                    'id': 'redump',
                    'search': 'Sony - PlayStation',
                    'collection': 'redump.org',
                    'type': 'Redump',
                    'description': 'Complete Redump PSX set (verified dumps)'
                }
            ]
        },
        'ps2': {
            'name': 'Sony PlayStation 2',
            'sets': [
                {
                    'id': 'redump',
                    'search': 'Sony - PlayStation 2',
                    'collection': 'redump.org',
                    'type': 'Redump',
                    'description': 'Complete Redump PS2 set (verified dumps)'
                }
            ]
        },
        'dreamcast': {
            'name': 'Sega Dreamcast',
            'sets': [
                {
                    'id': 'redump',
                    'search': 'Sega - Dreamcast',
                    'collection': 'redump.org',
                    'type': 'Redump',
                    'description': 'Complete Redump Dreamcast set (verified dumps)'
                }
            ]
        },
        'saturn': {
            'name': 'Sega Saturn',
            'sets': [
                {
                    'id': 'redump',
                    'search': 'Sega - Saturn',
                    'collection': 'redump.org',
                    'type': 'Redump',
                    'description': 'Complete Redump Saturn set (verified dumps)'
                }
            ]
        },
        'arcade': {
            'name': 'Arcade (MAME)',
            'sets': [
                {
                    'id': 'mame-merged',
                    'search': 'MAME',
                    'collection': 'mame-merged',
                    'type': 'MAME Merged',
                    'description': 'Complete MAME ROM set (merged)'
                }
            ]
        }
    }

    def __init__(self, download_path: str = None):
        """
        Initialize the downloader

        Args:
            download_path: Base path where ROMs will be downloaded
        """
        if download_path is None:
            download_path = input("Enter the path where you want to save ROMs: ").strip()

        self.download_path = Path(download_path)
        self.download_path.mkdir(parents=True, exist_ok=True)
        print(f"ROMs will be saved to: {self.download_path}")

    def search_roms(self, query: str, collection: str = None, rows: int = 50) -> List[Dict]:
        """
        Search for ROMs on Archive.org

        Args:
            query: Search query string
            collection: Specific collection to search in (optional)
            rows: Number of results to return

        Returns:
            List of search results
        """
        params = {
            "q": query,
            "fl[]": ["identifier", "title", "description", "downloads", "item_size"],
            "rows": rows,
            "page": 1,
            "output": "json"
        }

        if collection:
            params["q"] += f" AND collection:{collection}"

        try:
            print(f"Searching Archive.org for: {query}")
            response = requests.get(self.SEARCH_URL, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            docs = data.get("response", {}).get("docs", [])

            print(f"Found {len(docs)} results")
            return docs

        except Exception as e:
            print(f"Error searching Archive.org: {e}")
            return []

    def get_item_files(self, identifier: str) -> List[Dict]:
        """
        Get list of files for a specific Archive.org item

        Args:
            identifier: Archive.org item identifier

        Returns:
            List of files in the item
        """
        url = f"{self.BASE_URL}/metadata/{identifier}"

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()
            files = data.get("files", [])

            # Filter for ROM files (common extensions)
            rom_extensions = ['.zip', '.7z', '.rar', '.iso', '.bin', '.cue',
                            '.gba', '.gbc', '.gb', '.nes', '.snes', '.sfc',
                            '.n64', '.z64', '.md', '.smd', '.gen', '.psx',
                            '.nds', '.3ds', '.cia']

            rom_files = [
                f for f in files
                if any(f.get('name', '').lower().endswith(ext) for ext in rom_extensions)
            ]

            return rom_files

        except Exception as e:
            print(f"Error getting files for {identifier}: {e}")
            return []

    def download_file(self, identifier: str, filename: str, system: str = "roms") -> bool:
        """
        Download a specific file from Archive.org

        Args:
            identifier: Archive.org item identifier
            filename: Name of the file to download
            system: System/platform name for folder organization

        Returns:
            True if successful, False otherwise
        """
        url = f"{self.BASE_URL}/download/{identifier}/{filename}"

        # Create system-specific folder
        system_path = self.download_path / system
        system_path.mkdir(parents=True, exist_ok=True)

        output_file = system_path / filename

        # Skip if file already exists
        if output_file.exists():
            print(f"File already exists: {output_file}")
            return True

        try:
            print(f"Downloading: {filename}")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0

            with open(output_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)

                        # Progress indicator
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\rProgress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')

            print(f"\n✓ Downloaded: {output_file}")
            return True

        except Exception as e:
            print(f"\n✗ Error downloading {filename}: {e}")
            if output_file.exists():
                output_file.unlink()  # Remove partial download
            return False

    def download_rom_set(self, identifier: str, system: str = None):
        """
        Download an entire ROM set from Archive.org

        Args:
            identifier: Archive.org item identifier
            system: System/platform name (auto-detected if not provided)
        """
        print(f"\nProcessing item: {identifier}")

        files = self.get_item_files(identifier)

        if not files:
            print("No ROM files found in this item")
            return

        print(f"Found {len(files)} ROM file(s)")

        # Auto-detect system if not provided
        if system is None:
            system = identifier.replace("-", "_")

        for idx, file_info in enumerate(files, 1):
            filename = file_info.get('name')
            print(f"\n[{idx}/{len(files)}] Processing: {filename}")
            self.download_file(identifier, filename, system)
            time.sleep(0.5)  # Be nice to Archive.org servers

    def browse_complete_sets(self):
        """Browse and select complete ROM sets for download"""
        print("\n" + "=" * 60)
        print("           COMPLETE ROM SETS")
        print("=" * 60)
        print("\nAvailable complete ROM sets:")
        print()

        systems = sorted(self.COMPLETE_SETS.keys())

        for idx, system_key in enumerate(systems, 1):
            system_info = self.COMPLETE_SETS[system_key]
            print(f"{idx:2d}. {system_info['name']} ({system_key})")
            for set_info in system_info['sets']:
                print(f"    └─ {set_info['type']}: {set_info['description']}")

        print("\n" + "-" * 60)
        choice = input("\nEnter system number to download (or 0 to cancel): ").strip()

        if not choice.isdigit() or int(choice) == 0:
            return

        choice_idx = int(choice)
        if choice_idx < 1 or choice_idx > len(systems):
            print("Invalid choice")
            return

        # Get selected system
        selected_system = systems[choice_idx - 1]
        system_info = self.COMPLETE_SETS[selected_system]

        print(f"\nSelected: {system_info['name']}")
        print()

        # Show available sets for this system
        sets = system_info['sets']
        if len(sets) == 1:
            selected_set = sets[0]
        else:
            print("Available sets:")
            for idx, set_info in enumerate(sets, 1):
                print(f"{idx}. {set_info['type']}: {set_info['description']}")

            set_choice = input("\nEnter set number: ").strip()
            if not set_choice.isdigit() or int(set_choice) < 1 or int(set_choice) > len(sets):
                print("Invalid choice")
                return
            selected_set = sets[int(set_choice) - 1]

        # Search for the complete set
        print(f"\nSearching for {selected_set['type']} set...")
        print(f"Query: {selected_set['search']}")
        print(f"Collection: {selected_set['collection']}")
        print()

        results = self.search_roms(
            selected_set['search'],
            selected_set['collection'],
            rows=20
        )

        if not results:
            print("❌ No results found. The set may not be available on Archive.org")
            print("Try searching manually or check Archive.org directly")
            return

        # Display results
        print("\n" + "=" * 60)
        print("Found the following items:")
        print("-" * 60)

        for idx, item in enumerate(results, 1):
            title = item.get('title', 'Untitled')
            identifier = item.get('identifier', 'unknown')
            size = item.get('item_size', 'Unknown')
            downloads = item.get('downloads', 'Unknown')

            print(f"\n{idx}. {title}")
            print(f"   ID: {identifier}")
            print(f"   Size: {size}")
            print(f"   Downloads: {downloads}")

        print("\n" + "=" * 60)

        # Let user choose which result to download
        download_choice = input("\nEnter number to download (or 0 to cancel): ").strip()

        if not download_choice.isdigit() or int(download_choice) == 0:
            return

        download_idx = int(download_choice)
        if download_idx < 1 or download_idx > len(results):
            print("Invalid choice")
            return

        selected_item = results[download_idx - 1]

        # Confirm download
        print(f"\n⚠️  You are about to download a COMPLETE ROM SET!")
        print(f"System: {system_info['name']}")
        print(f"Item: {selected_item.get('title')}")
        print(f"Size: {selected_item.get('item_size', 'Unknown')}")
        print(f"\nThis may take a long time and use significant disk space.")

        confirm = input("\nProceed with download? (yes/no): ").strip().lower()

        if confirm not in ['yes', 'y']:
            print("Download cancelled")
            return

        # Download the complete set
        print(f"\n🚀 Starting download of complete {system_info['name']} set...")
        self.download_rom_set(selected_item['identifier'], selected_system)
        print(f"\n✓ Complete set download finished!")
        print(f"Location: {self.download_path / selected_system}")

    def search_complete_set(self, system: str) -> List[Dict]:
        """
        Search for a complete ROM set for a specific system

        Args:
            system: System key (e.g., 'gba', 'snes', 'nes')

        Returns:
            List of matching Archive.org items
        """
        if system not in self.COMPLETE_SETS:
            print(f"❌ Unknown system: {system}")
            print(f"Available systems: {', '.join(sorted(self.COMPLETE_SETS.keys()))}")
            return []

        system_info = self.COMPLETE_SETS[system]
        print(f"Searching for complete {system_info['name']} sets...")

        all_results = []
        for set_info in system_info['sets']:
            results = self.search_roms(
                set_info['search'],
                set_info['collection'],
                rows=10
            )
            all_results.extend(results)

        return all_results

    def interactive_search(self):
        """Interactive search and download interface"""
        print("\n=== Archive.org ROM Downloader ===\n")

        while True:
            print("\n" + "=" * 60)
            print("Options:")
            print("=" * 60)
            print("1. 🎮 Browse Complete ROM Sets (No-Intro, Redump, etc.)")
            print("2. 🔍 Search for ROMs")
            print("3. 📥 Download by Archive.org identifier")
            print("4. 📚 List common ROM collections")
            print("5. 🚪 Exit")
            print("=" * 60)

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                # NEW: Browse complete sets
                self.browse_complete_sets()

            elif choice == "2":
                query = input("Enter search query: ").strip()
                collection = input("Enter collection name (or press Enter to search all): ").strip()

                results = self.search_roms(query, collection if collection else None)

                if results:
                    print("\nSearch Results:")
                    for idx, item in enumerate(results, 1):
                        print(f"\n{idx}. {item.get('title', 'Untitled')}")
                        print(f"   ID: {item.get('identifier')}")
                        print(f"   Size: {item.get('item_size', 'Unknown')}")
                        print(f"   Downloads: {item.get('downloads', 'Unknown')}")

                    download_choice = input("\nEnter number to download (or 0 to cancel): ").strip()
                    if download_choice.isdigit() and 0 < int(download_choice) <= len(results):
                        selected = results[int(download_choice) - 1]
                        system = input("Enter system name (e.g., snes, nes, gba): ").strip()
                        self.download_rom_set(selected['identifier'], system)

            elif choice == "3":
                identifier = input("Enter Archive.org identifier: ").strip()
                system = input("Enter system name (e.g., snes, nes, gba): ").strip()
                self.download_rom_set(identifier, system)

            elif choice == "4":
                print("\nCommon ROM Collections on Archive.org:")
                for idx, collection in enumerate(self.COMMON_COLLECTIONS, 1):
                    print(f"{idx}. {collection}")
                print("\nYou can search within these collections using option 2")

            elif choice == "5":
                print("Exiting...")
                break

            else:
                print("Invalid choice. Please try again.")


def main():
    """Main entry point"""
    downloader = ArchiveRomDownloader()
    downloader.interactive_search()


if __name__ == "__main__":
    main()

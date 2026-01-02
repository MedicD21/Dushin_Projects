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

    def interactive_search(self):
        """Interactive search and download interface"""
        print("\n=== Archive.org ROM Downloader ===\n")

        while True:
            print("\nOptions:")
            print("1. Search for ROMs")
            print("2. Download by Archive.org identifier")
            print("3. List common ROM collections")
            print("4. Exit")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == "1":
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

            elif choice == "2":
                identifier = input("Enter Archive.org identifier: ").strip()
                system = input("Enter system name (e.g., snes, nes, gba): ").strip()
                self.download_rom_set(identifier, system)

            elif choice == "3":
                print("\nCommon ROM Collections on Archive.org:")
                for idx, collection in enumerate(self.COMMON_COLLECTIONS, 1):
                    print(f"{idx}. {collection}")
                print("\nYou can search within these collections using option 1")

            elif choice == "4":
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

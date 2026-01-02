#!/usr/bin/env python3
"""
Myrient ROM Downloader
Downloads complete ROM sets from myrient.erista.me
"""

import os
import sys
import requests
import re
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urljoin, unquote
import time
from html.parser import HTMLParser


class DirectoryParser(HTMLParser):
    """Parse HTML directory listings to extract file links"""

    def __init__(self):
        super().__init__()
        self.files = []
        self.in_link = False
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr, value in attrs:
                if attr == 'href':
                    self.current_href = value
                    self.in_link = True

    def handle_data(self, data):
        if self.in_link and self.current_href:
            # Only include actual files (not parent directory or directories)
            if not self.current_href.startswith('?') and not self.current_href == '../':
                if not self.current_href.endswith('/'):  # Not a directory
                    self.files.append({
                        'href': self.current_href,
                        'name': data.strip()
                    })

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_link = False
            self.current_href = None


class ROMFilter:
    """Utilities for filtering and prioritizing ROM files"""

    # Region priority: prefer USA/EN first, then World, skip others
    REGION_PRIORITY = {
        'USA': 1,
        'En': 1,
        'World': 2,
        'Europe': 3,
        'Japan': 99,  # Skip
        'Korea': 99,  # Skip
        'China': 99,  # Skip
    }

    @staticmethod
    def extract_game_title(filename: str) -> str:
        """
        Extract base game title from ROM filename

        Example: "Pokemon - Fire Red (USA).gba" -> "Pokemon - Fire Red"
        """
        # Remove file extension
        name = Path(filename).stem

        # Remove region tags (USA), (Europe), (World), etc.
        name = re.sub(r'\s*\([^)]*\)', '', name)

        # Remove revision tags [!], [b1], etc.
        name = re.sub(r'\s*\[[^\]]*\]', '', name)

        # Clean up extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    @staticmethod
    def get_region_priority(filename: str) -> int:
        """
        Get priority score for ROM based on region
        Lower = higher priority

        Returns 99 for regions to skip
        """
        # Check for region tags in filename
        for region, priority in ROMFilter.REGION_PRIORITY.items():
            # Case insensitive search for region in parentheses
            if re.search(rf'\({region}\)', filename, re.IGNORECASE):
                return priority
            # Also check for [Region] format
            if re.search(rf'\[{region}\]', filename, re.IGNORECASE):
                return priority

        # If no recognized region found, skip it
        return 99

    @staticmethod
    def should_download(filename: str, existing_titles: Set[str]) -> Tuple[bool, int, str]:
        """
        Determine if a ROM should be downloaded

        Args:
            filename: ROM filename to check
            existing_titles: Set of game titles already downloaded/queued

        Returns:
            Tuple of (should_download, priority, title)
        """
        title = ROMFilter.extract_game_title(filename)
        priority = ROMFilter.get_region_priority(filename)

        # Skip if region priority is too low (99 = skip)
        if priority >= 99:
            return (False, priority, title)

        # Skip if we already have this title
        if title in existing_titles:
            return (False, priority, title)

        return (True, priority, title)


class MyrientRomDownloader:
    """Handles downloading complete ROM sets from myrient.erista.me"""

    BASE_URL = "https://myrient.erista.me/files"

    # System mappings for myrient.erista.me
    # Format: system_key -> (collection_path, display_name)
    SYSTEMS = {
        'gba': {
            'name': 'Game Boy Advance',
            'paths': [
                'T-En Collection/Nintendo - Game Boy Advance [T-En] Collection',
                'No-Intro/Nintendo - Game Boy Advance',
            ]
        },
        'gbc': {
            'name': 'Game Boy Color',
            'paths': [
                'T-En Collection/Nintendo - Game Boy Color [T-En] Collection',
                'No-Intro/Nintendo - Game Boy Color',
            ]
        },
        'gb': {
            'name': 'Game Boy',
            'paths': [
                'T-En Collection/Nintendo - Game Boy [T-En] Collection',
                'No-Intro/Nintendo - Game Boy',
            ]
        },
        'nes': {
            'name': 'Nintendo Entertainment System',
            'paths': [
                'T-En Collection/Nintendo - Nintendo Entertainment System [T-En] Collection',
                'No-Intro/Nintendo - Nintendo Entertainment System',
            ]
        },
        'snes': {
            'name': 'Super Nintendo',
            'paths': [
                'T-En Collection/Nintendo - Super Nintendo Entertainment System [T-En] Collection',
                'No-Intro/Nintendo - Super Nintendo Entertainment System',
            ]
        },
        'n64': {
            'name': 'Nintendo 64',
            'paths': [
                'T-En Collection/Nintendo - Nintendo 64 [T-En] Collection',
                'No-Intro/Nintendo - Nintendo 64',
            ]
        },
        'nds': {
            'name': 'Nintendo DS',
            'paths': [
                'T-En Collection/Nintendo - Nintendo DS [T-En] Collection',
                'No-Intro/Nintendo - Nintendo DS (Decrypted)',
            ]
        },
        'genesis': {
            'name': 'Sega Genesis / Mega Drive',
            'paths': [
                'T-En Collection/Sega - Mega Drive - Genesis [T-En] Collection',
                'No-Intro/Sega - Mega Drive - Genesis',
            ]
        },
        'mastersystem': {
            'name': 'Sega Master System',
            'paths': [
                'No-Intro/Sega - Master System - Mark III',
            ]
        },
        'gamegear': {
            'name': 'Sega Game Gear',
            'paths': [
                'T-En Collection/Sega - Game Gear [T-En] Collection',
                'No-Intro/Sega - Game Gear',
            ]
        },
        'psx': {
            'name': 'Sony PlayStation',
            'paths': [
                'Redump/Sony - PlayStation',
            ]
        },
        'ps2': {
            'name': 'Sony PlayStation 2',
            'paths': [
                'Redump/Sony - PlayStation 2',
            ]
        },
        'dreamcast': {
            'name': 'Sega Dreamcast',
            'paths': [
                'Redump/Sega - Dreamcast',
            ]
        },
        'saturn': {
            'name': 'Sega Saturn',
            'paths': [
                'Redump/Sega - Saturn',
            ]
        },
        'gamecube': {
            'name': 'Nintendo GameCube',
            'paths': [
                'Redump/Nintendo - GameCube - NR',
            ]
        },
        'wii': {
            'name': 'Nintendo Wii',
            'paths': [
                'Redump/Nintendo - Wii - NR',
            ]
        },
        '3ds': {
            'name': 'Nintendo 3DS',
            'paths': [
                'No-Intro/Nintendo - Nintendo 3DS (Decrypted)',
            ]
        },
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
        self.session = requests.Session()

    def get_directory_listing(self, url: str) -> List[Dict]:
        """
        Parse directory listing from myrient to get file list

        Args:
            url: URL of the directory to list

        Returns:
            List of file dictionaries with 'name' and 'href'
        """
        try:
            print(f"Fetching directory listing from: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            parser = DirectoryParser()
            parser.feed(response.text)

            # Filter for ROM files
            rom_extensions = ['.zip', '.7z', '.rar', '.iso', '.bin', '.cue',
                            '.gba', '.gbc', '.gb', '.nes', '.sfc', '.smc',
                            '.n64', '.z64', '.md', '.smd', '.gen', '.nds',
                            '.3ds', '.cia', '.chd']

            rom_files = [
                f for f in parser.files
                if any(f['href'].lower().endswith(ext) for ext in rom_extensions)
            ]

            print(f"Found {len(rom_files)} ROM files")
            return rom_files

        except Exception as e:
            print(f"Error fetching directory listing: {e}")
            return []

    def download_file(self, url: str, output_path: Path, filename: str = None) -> bool:
        """
        Download a file from myrient

        Args:
            url: URL of the file to download
            output_path: Directory to save the file
            filename: Optional filename override

        Returns:
            True if successful, False otherwise
        """
        if filename is None:
            filename = unquote(url.split('/')[-1])

        output_file = output_path / filename

        # Skip if already exists
        if output_file.exists():
            print(f"  ⏭️  Skipping (already exists): {filename}")
            return True

        try:
            print(f"  ⬇️  Downloading: {filename}")
            response = self.session.get(url, stream=True, timeout=120)
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
                            mb_downloaded = downloaded / (1024 * 1024)
                            mb_total = total_size / (1024 * 1024)
                            print(f"\r     Progress: {progress:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')

            print(f"\n  ✓ Downloaded: {filename}")
            return True

        except Exception as e:
            print(f"\n  ✗ Error downloading {filename}: {e}")
            if output_file.exists():
                output_file.unlink()  # Remove partial download
            return False

    def unzip_file(self, zip_path: Path, extract_to: Path) -> bool:
        """
        Extract a zip file and remove the zip after extraction

        Args:
            zip_path: Path to zip file
            extract_to: Directory to extract to

        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"  📦 Extracting: {zip_path.name}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)

            # Remove zip file after extraction
            zip_path.unlink()
            print(f"  ✓ Extracted and removed zip")
            return True

        except Exception as e:
            print(f"  ✗ Error extracting {zip_path.name}: {e}")
            return False

    def get_existing_titles(self, system_dir: Path) -> Set[str]:
        """
        Get set of game titles already in destination folder

        Args:
            system_dir: System directory to scan

        Returns:
            Set of extracted game titles
        """
        existing_titles = set()

        if not system_dir.exists():
            return existing_titles

        for file_path in system_dir.iterdir():
            if file_path.is_file():
                title = ROMFilter.extract_game_title(file_path.name)
                existing_titles.add(title)

        return existing_titles

    def download_complete_set(self, system: str, collection_choice: int = 0) -> bool:
        """
        Download complete ROM set for a system with smart filtering

        Args:
            system: System key (e.g., 'gba', 'snes')
            collection_choice: Which collection path to use (default: 0 = first/preferred)

        Returns:
            True if successful, False otherwise
        """
        if system not in self.SYSTEMS:
            print(f"❌ Unknown system: {system}")
            print(f"Available systems: {', '.join(sorted(self.SYSTEMS.keys()))}")
            return False

        system_info = self.SYSTEMS[system]
        paths = system_info['paths']

        if collection_choice >= len(paths):
            collection_choice = 0

        collection_path = paths[collection_choice]
        url = f"{self.BASE_URL}/{collection_path}/"

        print(f"\n{'='*60}")
        print(f"System: {system_info['name']}")
        print(f"Collection: {collection_path.split('/')[0]}")
        print(f"URL: {url}")
        print(f"{'='*60}\n")

        # Get file listing
        files = self.get_directory_listing(url)

        if not files:
            print("❌ No ROM files found at this URL")
            return False

        # Create system directory
        system_dir = self.download_path / system
        system_dir.mkdir(parents=True, exist_ok=True)

        # Get existing titles to avoid duplicates
        existing_titles = self.get_existing_titles(system_dir)
        print(f"📁 Found {len(existing_titles)} existing games in destination")

        # Filter files by region priority
        print(f"\n🔍 Filtering {len(files)} files...")
        print(f"   Priority: USA/EN > World > Europe (skipping Japan, Korea, etc.)")
        print()

        files_to_download = []
        skipped_count = 0
        duplicate_count = 0

        for file_info in files:
            filename = file_info['name']
            should_dl, priority, title = ROMFilter.should_download(filename, existing_titles)

            if should_dl:
                files_to_download.append((file_info, priority, title))
                existing_titles.add(title)  # Mark as queued to avoid duplicates in batch
            else:
                if priority >= 99:
                    skipped_count += 1
                else:
                    duplicate_count += 1

        # Sort by priority (lower = higher priority)
        files_to_download.sort(key=lambda x: x[1])

        print(f"✓ Filter Results:")
        print(f"  • Will download: {len(files_to_download)} files")
        print(f"  • Skipped (wrong region): {skipped_count} files")
        print(f"  • Skipped (duplicate): {duplicate_count} files")

        if not files_to_download:
            print("\n✓ No new files to download!")
            return True

        # Confirm download
        print(f"\nThis will download to: {system_dir}/")
        confirm = input("\nProceed with download? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Download cancelled")
            return False

        # Download filtered files
        print(f"\n🚀 Starting download of {len(files_to_download)} files...\n")

        success_count = 0
        fail_count = 0
        extracted_count = 0

        for idx, (file_info, priority, title) in enumerate(files_to_download, 1):
            filename = file_info['name']
            print(f"[{idx}/{len(files_to_download)}] {title}")
            print(f"  File: {filename}")

            file_url = urljoin(url, file_info['href'])

            if self.download_file(file_url, system_dir, filename):
                success_count += 1

                # Unzip if it's a zip file
                downloaded_file = system_dir / filename
                if downloaded_file.suffix.lower() == '.zip':
                    if self.unzip_file(downloaded_file, system_dir):
                        extracted_count += 1

            else:
                fail_count += 1

            # Small delay to be nice to the server
            time.sleep(0.3)

        # Summary
        print(f"\n{'='*60}")
        print(f"✓ Download Complete!")
        print(f"{'='*60}")
        print(f"Successfully downloaded: {success_count} files")
        print(f"Extracted from zip: {extracted_count} files")
        if fail_count > 0:
            print(f"Failed downloads: {fail_count} files")
        print(f"Location: {system_dir}")
        print(f"{'='*60}\n")

        return True

    def browse_systems(self):
        """Interactive system browser"""
        print("\n" + "=" * 60)
        print("           MYRIENT ROM DOWNLOADER")
        print("           Complete ROM Sets")
        print("=" * 60)
        print("\nAvailable Systems:\n")

        systems = sorted(self.SYSTEMS.keys())

        for idx, system_key in enumerate(systems, 1):
            system_info = self.SYSTEMS[system_key]
            collections = [path.split('/')[0] for path in system_info['paths']]
            collections_str = ', '.join(set(collections))
            print(f"{idx:2d}. {system_info['name']} ({system_key})")
            print(f"    Collections: {collections_str}")

        print("\n" + "-" * 60)
        choice = input("\nEnter system number to download (or 0 to cancel): ").strip()

        if not choice.isdigit() or int(choice) == 0:
            return

        choice_idx = int(choice)
        if choice_idx < 1 or choice_idx > len(systems):
            print("Invalid choice")
            return

        selected_system = systems[choice_idx - 1]
        system_info = self.SYSTEMS[selected_system]

        # If multiple collections available, let user choose
        if len(system_info['paths']) > 1:
            print(f"\nAvailable collections for {system_info['name']}:")
            for idx, path in enumerate(system_info['paths'], 1):
                collection = path.split('/')[0]
                print(f"{idx}. {collection}")

            coll_choice = input("\nSelect collection (or press Enter for first): ").strip()
            if coll_choice.isdigit():
                coll_idx = int(coll_choice) - 1
            else:
                coll_idx = 0
        else:
            coll_idx = 0

        # Download the complete set
        self.download_complete_set(selected_system, coll_idx)

    def interactive_menu(self):
        """Main interactive menu"""
        print("\n=== Myrient ROM Downloader ===")
        print("Source: myrient.erista.me\n")

        while True:
            print("\n" + "=" * 60)
            print("Options:")
            print("=" * 60)
            print("1. 🎮 Browse and Download Complete ROM Sets")
            print("2. 📋 List All Available Systems")
            print("3. 🚪 Exit")
            print("=" * 60)

            choice = input("\nEnter your choice (1-3): ").strip()

            if choice == "1":
                self.browse_systems()

            elif choice == "2":
                print("\nAvailable Systems:")
                for system_key in sorted(self.SYSTEMS.keys()):
                    system_info = self.SYSTEMS[system_key]
                    print(f"  {system_key:15s} - {system_info['name']}")

            elif choice == "3":
                print("\nThank you for using Myrient ROM Downloader!")
                break

            else:
                print("Invalid choice. Please try again.")


def main():
    """Main entry point"""
    downloader = MyrientRomDownloader()
    downloader.interactive_menu()


if __name__ == "__main__":
    main()

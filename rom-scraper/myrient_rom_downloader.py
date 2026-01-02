#!/usr/bin/env python3
"""
Myrient ROM Downloader
Downloads complete ROM sets from myrient.erista.me
"""

import argparse
import json
import os
import sys
import requests
import re
import zipfile
import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from urllib.parse import urljoin, unquote
import time
from html.parser import HTMLParser
import xml.etree.ElementTree as ET


def load_config() -> Dict:
    """Load configuration from config.json if it exists."""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: could not read config.json ({e})")
    return {}


def pick_download_directory(initial: Optional[str] = None) -> Optional[str]:
    """Open a folder picker dialog and return the selected path."""
    # Try tkinter first
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        try:
            selected = filedialog.askdirectory(
                initialdir=initial or os.getcwd(),
                title="Select download folder",
            )
        finally:
            root.destroy()

        if selected:
            return selected
        return None
    except Exception as e:
        print(f"Tkinter folder picker unavailable ({e})")

    # Fallback: Try Windows COM-based folder picker (better for external drives)
    if sys.platform == 'win32':
        try:
            import subprocess
            print("Using Windows folder picker...")
            print("TIP: Navigate INTO a folder (double-click) before clicking OK")

            # PowerShell script using Shell.Application with flags to show all folders
            # BIF_RETURNONLYFSDIRS (0x0001) + BIF_NEWDIALOGSTYLE (0x0040) = 0x0041
            ps_script = """
            $shell = New-Object -ComObject Shell.Application
            $folder = $shell.BrowseForFolder(0, 'Select download folder for ROMs (navigate into a folder, then click OK)', 0x0041, 0)
            if ($folder) {
                $folderPath = $folder.Self.Path
                Write-Output $folderPath
            }
            """

            result = subprocess.run(
                ['powershell', '-NoProfile', '-Command', ps_script],
                capture_output=True,
                text=True,
                timeout=120
            )

            selected = result.stdout.strip()
            if selected:
                # Handle special paths and verify
                if os.path.exists(selected):
                    return selected
                print(f"Selected path doesn't exist or isn't accessible: {selected}")
        except Exception as e:
            print(f"Windows folder picker also unavailable ({e})")

    print("Folder picker unavailable; falling back to manual entry.")
    return None


def resolve_download_path(cli_path: Optional[str], use_picker: bool = False) -> str:
    """
    Decide which download path to use, preferring CLI, env var, then config.

    This keeps the script non-interactive when a path is already provided.
    """
    if cli_path:
        return cli_path

    # Check environment variable
    env_path = os.getenv("MYRIENT_DOWNLOAD_PATH")
    if env_path:
        return env_path

    # Check config file
    config = load_config()
    config_path = config.get("paths", {}).get("default_download_path")
    if config_path:
        return config_path

    # Try folder picker if requested
    if use_picker:
        picked = pick_download_directory()
        if picked:
            return picked
        print("No folder selected; falling back to manual entry.\n")

    # Show available drives to help user
    if sys.platform == 'win32':
        import string
        available_drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                try:
                    # Get volume label if available
                    import subprocess
                    result = subprocess.run(
                        ['cmd', '/c', 'vol', f'{letter}:'],
                        capture_output=True,
                        text=True,
                        timeout=2
                    )
                    volume_name = "Unknown"
                    for line in result.stdout.split('\n'):
                        if 'Volume in drive' in line:
                            parts = line.split('is')
                            if len(parts) > 1:
                                volume_name = parts[1].strip()
                    available_drives.append(f"{drive} ({volume_name})")
                except:
                    available_drives.append(drive)

        if available_drives:
            print("\nAvailable drives:")
            for drive in available_drives:
                print(f"  {drive}")
            print()

    download_path = input("Enter the path where you want to save ROMs (e.g., E:\\ROMS): ").strip()
    if not download_path:
        download_path = "./downloaded_roms"
        print(f"No path entered. Defaulting to: {download_path}")
    return download_path


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


class ScreenScraperIntegration:
    """Simplified ScreenScraper integration for fetching media"""

    BASE_URL = "https://www.screenscraper.fr/api2"

    SYSTEM_IDS = {
        'nes': 3, 'snes': 4, 'n64': 14, 'gb': 9, 'gbc': 10, 'gba': 12,
        'nds': 15, '3ds': 17, 'genesis': 1, 'mastersystem': 2,
        'gamegear': 21, 'psx': 57, 'ps2': 58, 'dreamcast': 23,
        'saturn': 22, 'gamecube': 13, 'wii': 16
    }

    def __init__(self, dev_user: str, dev_password: str, user: str = None, password: str = None):
        self.dev_user = dev_user
        self.dev_password = dev_password
        self.user = user
        self.password = password
        self.session = requests.Session()
        self.last_request_time = 0
        self.rate_limit_delay = 1.5

    def _wait_for_rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()

    def _build_auth_params(self) -> Dict:
        params = {
            'devid': self.dev_user,
            'devpassword': self.dev_password,
            'softname': 'MyrientROMDownloader/1.0',
        }
        if self.user and self.password:
            params['ssid'] = self.user
            params['sspassword'] = self.password
        return params

    def get_rom_hash(self, rom_path: str) -> Dict[str, str]:
        try:
            md5_hash = hashlib.md5()
            sha1_hash = hashlib.sha1()
            with open(rom_path, 'rb') as f:
                while chunk := f.read(8192):
                    md5_hash.update(chunk)
                    sha1_hash.update(chunk)
            return {
                'md5': md5_hash.hexdigest(),
                'sha1': sha1_hash.hexdigest(),
                'size': os.path.getsize(rom_path)
            }
        except Exception:
            return {}

    def search_and_download_media(self, system: str, rom_path: Path) -> Optional[Dict]:
        """Search for game and download box art and media to game folder"""
        self._wait_for_rate_limit()

        system_id = self.SYSTEM_IDS.get(system.lower())
        if not system_id:
            return None

        params = self._build_auth_params()
        params['systemeid'] = system_id
        params['output'] = 'json'

        # Calculate ROM hash for accurate matching
        hashes = self.get_rom_hash(str(rom_path))
        if hashes:
            params['md5'] = hashes['md5']
            params['sha1'] = hashes['sha1']
            params['romtaille'] = hashes['size']

        url = f"{self.BASE_URL}/jeuInfos.php"

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if 'response' not in data or 'jeu' not in data['response']:
                return None

            game_data = data['response']['jeu']
            game_name = game_data.get('noms', [{}])[0].get('text', 'Unknown')

            print(f"  📋 Found: {game_name}")

            # Create game folder
            game_folder = rom_path.parent / rom_path.stem
            game_folder.mkdir(exist_ok=True)

            # Move ROM into game folder
            new_rom_path = game_folder / rom_path.name
            if rom_path.exists() and not new_rom_path.exists():
                rom_path.rename(new_rom_path)

            # Save metadata JSON
            metadata_file = game_folder / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, indent=2, ensure_ascii=False)

            # Download box art (2D box)
            boxart_path = None
            medias = game_data.get('medias', [])
            for media in medias:
                media_type = media.get('type')
                media_url = media.get('url')

                if media_type == 'box-2D' and media_url:
                    ext = Path(media_url).suffix or '.png'
                    boxart_path = game_folder / f"boxart{ext}"

                    if not boxart_path.exists():
                        self._download_file(media_url, boxart_path)
                    break

            return {
                'game_name': game_name,
                'rom_path': new_rom_path,
                'boxart_path': boxart_path,
                'metadata': game_data
            }

        except Exception as e:
            print(f"  ⚠️  ScreenScraper error: {e}")
            return None

    def _download_file(self, url: str, output_path: Path):
        """Download a media file"""
        try:
            response = self.session.get(url, stream=True, timeout=30)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"  🖼️  Downloaded boxart: {output_path.name}")
        except Exception as e:
            print(f"  ⚠️  Failed to download media: {e}")


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

    def __init__(self, download_path: str = None, use_picker: bool = False, enable_screenscraper: bool = True):
        """
        Initialize the downloader

        Args:
            download_path: Base path where ROMs will be downloaded
            use_picker: When True, opens a folder picker if no CLI path is given
            enable_screenscraper: When True, downloads media from ScreenScraper
        """
        download_path = resolve_download_path(download_path, use_picker=use_picker)

        self.download_path = Path(download_path).expanduser()
        self.download_path.mkdir(parents=True, exist_ok=True)
        print(f"ROMs will be saved to: {self.download_path}")
        self.session = requests.Session()

        # Initialize ScreenScraper if enabled
        self.screenscraper = None
        if enable_screenscraper:
            config = load_config()
            ss_config = config.get('screenscraper', {})
            if ss_config.get('dev_user') and ss_config.get('dev_password'):
                self.screenscraper = ScreenScraperIntegration(
                    dev_user=ss_config['dev_user'],
                    dev_password=ss_config['dev_password'],
                    user=ss_config.get('user'),
                    password=ss_config.get('password')
                )
                print("✓ ScreenScraper media downloading enabled")
            else:
                print("⚠️  ScreenScraper credentials not found in config.json")

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

    def download_complete_set(self, system: str, collection_choice: int = 0, auto_confirm: bool = False) -> bool:
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

        # Create system subdirectory
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

        # Confirm download (skip if auto_confirm is True)
        if not auto_confirm:
            print(f"\nThis will download to: {system_dir}/")
            confirm = input("\nProceed with download? (yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("Download cancelled")
                return False
        else:
            print(f"\n✓ Auto-confirmed download to: {system_dir}/")

        # Download filtered files
        print(f"\n🚀 Starting download of {len(files_to_download)} files...\n")

        success_count = 0
        fail_count = 0
        extracted_count = 0
        media_count = 0
        games_info = []

        for idx, (file_info, priority, title) in enumerate(files_to_download, 1):
            filename = file_info['name']
            print(f"[{idx}/{len(files_to_download)}] {title}")
            print(f"  File: {filename}")

            file_url = urljoin(url, file_info['href'])

            if self.download_file(file_url, system_dir, filename):
                success_count += 1

                downloaded_file = system_dir / filename
                rom_file_for_scraper = downloaded_file

                # Unzip if it's a zip file
                if downloaded_file.suffix.lower() == '.zip':
                    if self.unzip_file(downloaded_file, system_dir):
                        extracted_count += 1
                        # Find the extracted ROM file for ScreenScraper
                        rom_extensions = ['.gba', '.gbc', '.gb', '.nes', '.sfc', '.smc',
                                         '.n64', '.z64', '.md', '.smd', '.gen', '.nds', '.3ds']
                        for extracted_file in system_dir.iterdir():
                            if extracted_file.suffix.lower() in rom_extensions and extracted_file.stem == downloaded_file.stem:
                                rom_file_for_scraper = extracted_file
                                break

                # Fetch media from ScreenScraper
                if self.screenscraper and rom_file_for_scraper.exists():
                    print(f"  🔍 Fetching media from ScreenScraper...")
                    game_info = self.screenscraper.search_and_download_media(system, rom_file_for_scraper)
                    if game_info:
                        media_count += 1
                        games_info.append(game_info)

            else:
                fail_count += 1

            # Small delay to be nice to the server
            time.sleep(0.3)

        # Create master gamelist.xml
        if games_info:
            self._create_gamelist_xml(system_dir, system, games_info)

        # Summary
        print(f"\n{'='*60}")
        print(f"✓ Download Complete!")
        print(f"{'='*60}")
        print(f"Successfully downloaded: {success_count} files")
        print(f"Extracted from zip: {extracted_count} files")
        if media_count > 0:
            print(f"Downloaded media/boxart: {media_count} files")
        if fail_count > 0:
            print(f"Failed downloads: {fail_count} files")
        print(f"Location: {system_dir}")
        print(f"{'='*60}\n")

        return True

    def _create_gamelist_xml(self, system_dir: Path, system: str, games_info: List[Dict]):
        """Create master gamelist.xml for EmulationStation compatibility"""
        gamelist_file = system_dir / "gamelist.xml"

        root = ET.Element("gameList")

        for game_info in games_info:
            game_elem = ET.SubElement(root, "game")

            # Add game metadata
            rom_path = game_info['rom_path']
            game_folder = rom_path.parent

            ET.SubElement(game_elem, "path").text = f"./{game_folder.name}/{rom_path.name}"
            ET.SubElement(game_elem, "name").text = game_info['game_name']

            # Add metadata from ScreenScraper
            metadata = game_info['metadata']

            if 'descriptions' in metadata and metadata['descriptions']:
                desc = metadata['descriptions'][0].get('text', '')
                ET.SubElement(game_elem, "desc").text = desc

            if 'dates' in metadata and metadata['dates']:
                release_date = metadata['dates'][0].get('text', '')
                ET.SubElement(game_elem, "releasedate").text = release_date

            if 'editeur' in metadata:
                publisher = metadata['editeur'].get('text', '')
                ET.SubElement(game_elem, "publisher").text = publisher

            if 'developpeur' in metadata:
                developer = metadata['developpeur'].get('text', '')
                ET.SubElement(game_elem, "developer").text = developer

            if 'genres' in metadata and metadata['genres']:
                genre = metadata['genres'][0].get('text', '')
                ET.SubElement(game_elem, "genre").text = genre

            if 'joueurs' in metadata:
                players = metadata['joueurs'].get('text', '')
                ET.SubElement(game_elem, "players").text = players

            # Add media paths
            if game_info['boxart_path']:
                boxart_rel_path = f"./{game_folder.name}/{game_info['boxart_path'].name}"
                ET.SubElement(game_elem, "image").text = boxart_rel_path

        # Pretty print XML
        self._indent_xml(root)
        tree = ET.ElementTree(root)
        tree.write(gamelist_file, encoding='utf-8', xml_declaration=True)
        print(f"\n✓ Created master gamelist.xml: {gamelist_file}")

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

    def download_custom_systems(self):
        """Download ROMs from user-selected systems"""
        systems = sorted(self.SYSTEMS.keys())
        selected_systems = []

        print("\n" + "=" * 60)
        print("           CUSTOM MULTI-PLATFORM DOWNLOAD")
        print("=" * 60)
        print("\nAvailable Systems:\n")

        for idx, system_key in enumerate(systems, 1):
            system_info = self.SYSTEMS[system_key]
            print(f"{idx:2d}. {system_info['name']} ({system_key})")

        print("\n" + "-" * 60)
        print("Select systems to download (one at a time)")
        print("Enter '0' or 'done' when finished selecting")
        print("-" * 60)

        while True:
            choice = input("\nEnter system number (or 0/done to finish): ").strip().lower()

            if choice in ['0', 'done', '']:
                break

            if not choice.isdigit():
                print("Invalid input. Please enter a number.")
                continue

            choice_idx = int(choice)
            if choice_idx < 1 or choice_idx > len(systems):
                print("Invalid choice. Please try again.")
                continue

            selected_system = systems[choice_idx - 1]
            if selected_system in selected_systems:
                print(f"✓ {self.SYSTEMS[selected_system]['name']} is already selected")
            else:
                selected_systems.append(selected_system)
                print(f"✓ Added: {self.SYSTEMS[selected_system]['name']}")
                print(f"   Total selected: {len(selected_systems)} systems")

        if not selected_systems:
            print("\nNo systems selected. Cancelled.")
            return

        # Confirm selection
        print("\n" + "=" * 60)
        print("Selected Systems:")
        for system_key in selected_systems:
            print(f"  • {self.SYSTEMS[system_key]['name']} ({system_key})")

        print("\n" + "=" * 60)
        confirm = input(f"\nProceed with downloading {len(selected_systems)} systems? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Download cancelled")
            return

        print("\n🚀 Starting custom multi-platform download...\n")

        total_success = 0
        total_failed = 0
        completed_systems = []
        failed_systems = []

        for idx, system_key in enumerate(selected_systems, 1):
            system_info = self.SYSTEMS[system_key]
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(selected_systems)}] Processing: {system_info['name']}")
            print(f"{'='*60}\n")

            try:
                if self.download_complete_set(system_key, collection_choice=0, auto_confirm=True):
                    completed_systems.append(system_key)
                    total_success += 1
                else:
                    failed_systems.append(system_key)
                    total_failed += 1
            except Exception as e:
                print(f"❌ Error downloading {system_key}: {e}")
                failed_systems.append(system_key)
                total_failed += 1

            # Delay between systems
            if idx < len(selected_systems):
                print(f"\n⏱️  Waiting 5 seconds before next system...")
                time.sleep(5)

        # Final summary
        print("\n" + "=" * 60)
        print("           CUSTOM DOWNLOAD COMPLETE!")
        print("=" * 60)
        print(f"Successfully completed: {total_success} systems")
        if completed_systems:
            print("  ✓ " + ", ".join(completed_systems))

        if total_failed > 0:
            print(f"\nFailed: {total_failed} systems")
            print("  ✗ " + ", ".join(failed_systems))

        print(f"\nAll ROMs saved to: {self.download_path}")
        print("=" * 60 + "\n")

    def download_all_systems(self):
        """Download ROMs from all available systems automatically"""
        systems = sorted(self.SYSTEMS.keys())

        print("\n" + "=" * 60)
        print("           AUTO-DOWNLOAD ALL SYSTEMS")
        print("=" * 60)
        print(f"\nThis will download ROMs from all {len(systems)} systems:")
        for system_key in systems:
            system_info = self.SYSTEMS[system_key]
            print(f"  • {system_info['name']} ({system_key})")

        print("\n" + "=" * 60)
        confirm = input("\nProceed with downloading all systems? (yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("Auto-download cancelled")
            return

        print("\n🚀 Starting auto-download for all systems...\n")

        total_success = 0
        total_failed = 0
        completed_systems = []
        failed_systems = []

        for idx, system_key in enumerate(systems, 1):
            system_info = self.SYSTEMS[system_key]
            print(f"\n{'='*60}")
            print(f"[{idx}/{len(systems)}] Processing: {system_info['name']}")
            print(f"{'='*60}\n")

            try:
                # Download first collection for each system (auto-confirm)
                if self.download_complete_set(system_key, collection_choice=0, auto_confirm=True):
                    completed_systems.append(system_key)
                    total_success += 1
                else:
                    failed_systems.append(system_key)
                    total_failed += 1
            except Exception as e:
                print(f"❌ Error downloading {system_key}: {e}")
                failed_systems.append(system_key)
                total_failed += 1

            # Delay between systems
            if idx < len(systems):
                print(f"\n⏱️  Waiting 5 seconds before next system...")
                time.sleep(5)

        # Final summary
        print("\n" + "=" * 60)
        print("           AUTO-DOWNLOAD COMPLETE!")
        print("=" * 60)
        print(f"Successfully completed: {total_success} systems")
        if completed_systems:
            print("  ✓ " + ", ".join(completed_systems))

        if total_failed > 0:
            print(f"\nFailed: {total_failed} systems")
            print("  ✗ " + ", ".join(failed_systems))

        print(f"\nAll ROMs saved to: {self.download_path}")
        print("=" * 60 + "\n")

    def interactive_menu(self):
        """Main interactive menu"""
        print("\n=== Myrient ROM Downloader ===")
        print("Source: myrient.erista.me\n")

        while True:
            print("\n" + "=" * 60)
            print("Options:")
            print("=" * 60)
            print("1. 🎮 Browse and Download Complete ROM Sets")
            print("2. 🤖 Auto-Download ALL Systems")
            print("3. 🎯 Custom Multi-Platform Download")
            print("4. 📋 List All Available Systems")
            print("5. 🚪 Exit")
            print("=" * 60)

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == "1":
                self.browse_systems()

            elif choice == "2":
                self.download_all_systems()

            elif choice == "3":
                self.download_custom_systems()

            elif choice == "4":
                print("\nAvailable Systems:")
                for system_key in sorted(self.SYSTEMS.keys()):
                    system_info = self.SYSTEMS[system_key]
                    print(f"  {system_key:15s} - {system_info['name']}")

            elif choice == "5":
                print("\nThank you for using Myrient ROM Downloader!")
                break

            else:
                print("Invalid choice. Please try again.")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Download complete ROM sets from myrient.erista.me"
    )
    parser.add_argument(
        "-p",
        "--path",
        dest="download_path",
        help="Download directory (defaults to MYRIENT_DOWNLOAD_PATH or config.json paths.default_download_path)",
    )
    parser.add_argument(
        "--pick-path",
        action="store_true",
        help="Open a folder picker to choose the download directory",
    )
    return parser.parse_args()


def main():
    """Main entry point"""
    args = parse_args()
    # If no path provided via CLI, default to using picker
    use_picker = args.pick_path or (args.download_path is None)
    downloader = MyrientRomDownloader(
        download_path=args.download_path,
        use_picker=use_picker,
    )
    downloader.interactive_menu()


if __name__ == "__main__":
    main()

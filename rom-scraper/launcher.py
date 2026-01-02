#!/usr/bin/env python3
"""
ROM Scraper Launcher
Unified interface for both ROM downloading and metadata scraping
"""

import os
import sys
import json
from pathlib import Path


def load_config():
    """Load configuration from config.json"""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}


def main():
    """Main launcher interface"""
    print("=" * 60)
    print("           ROM SCRAPER TOOLKIT")
    print("=" * 60)
    print()
    print("A complete solution for ROM management:")
    print("  • Download Complete ROM Sets from Myrient")
    print("  • Fetch metadata from ScreenScraper.fr")
    print("  • Generate EmulationStation-compatible structures")
    print()
    print("=" * 60)
    print()

    while True:
        print("\n--- Main Menu ---")
        print()
        print("1. Myrient ROM Downloader")
        print("   └─ Download complete ROM sets (No-Intro, Redump, etc.)")
        print()
        print("2. ScreenScraper Metadata Fetcher")
        print("   └─ Fetch game info, artwork, and videos")
        print()
        print("3. View Configuration")
        print("   └─ Display current settings and credentials")
        print()
        print("4. Quick Start Guide")
        print("   └─ Show recommended workflow")
        print()
        print("5. Exit")
        print()
        print("-" * 60)

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            print("\nLaunching Myrient ROM Downloader...")
            print("-" * 60)
            os.system(f"python3 {Path(__file__).parent / 'myrient_rom_downloader.py'}")

        elif choice == "2":
            print("\nLaunching ScreenScraper Metadata Fetcher...")
            print("-" * 60)
            os.system(f"python3 {Path(__file__).parent / 'screenscraper_metadata.py'}")

        elif choice == "3":
            config = load_config()
            print("\n--- Current Configuration ---")
            print(json.dumps(config, indent=2))
            print("\nTo modify, edit: config.json")

        elif choice == "4":
            print("\n" + "=" * 60)
            print("           QUICK START GUIDE")
            print("=" * 60)
            print()
            print("Recommended Workflow:")
            print()
            print("Step 1: Download Complete ROM Set")
            print("  • Choose option 1 (Myrient Downloader)")
            print("  • Select your system (GBA, SNES, NES, etc.)")
            print("  • Choose collection (T-En, No-Intro, Redump)")
            print("  • Specify where to save")
            print()
            print("Step 2: Fetch Metadata")
            print("  • Choose option 2 (ScreenScraper Fetcher)")
            print("  • Use 'Scrape all ROMs in directory' option")
            print("  • Point it to your downloaded ROMs folder")
            print()
            print("Step 3: Use with Emulators")
            print("  • Copy the generated folder to your device")
            print("  • Compatible with EmulationStation, RetroArch, Anbernic")
            print("  • Includes gamelist.xml, artwork, and videos")
            print()
            print("Example:")
            print("  1. Download GBA complete set → ./roms/gba/")
            print("  2. Scrape metadata → ./game_data/gba/")
            print("  3. Copy game_data/gba/ to your EmulationStation")
            print()
            print("For detailed instructions, see README.md")
            print("=" * 60)

        elif choice == "5":
            print("\nThank you for using ROM Scraper Toolkit!")
            print("Happy gaming! 🎮")
            break

        else:
            print("\n❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)

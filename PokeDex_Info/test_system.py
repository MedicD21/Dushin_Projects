#!/usr/bin/env python3
"""
Quick test of the organized Pokemon data collection system
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))


def test_project_structure():
    """Test that all directories and key files exist"""
    print("Testing project structure...")

    # Check directories
    dirs = ["data", "scrapers", "utils"]
    for directory in dirs:
        if os.path.exists(directory):
            print(f"  ✓ {directory}/ directory exists")
        else:
            print(f"  ✗ {directory}/ directory missing")

    # Check key files
    files = [
        "data/pokemon_data.json",
        "data/pokemon_games.json",
        "utils/config.py",
        "utils/grab_info.py",
        "scrapers/comprehensive_scraper.py",
        "main.py",
        "README.md",
    ]

    for file_path in files:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path} exists")
        else:
            print(f"  ✗ {file_path} missing")


def test_utilities():
    """Test the utility modules"""
    print("\nTesting utilities...")

    try:
        from config import PokeDataUtils, DATA_FILES

        print("  ✓ Config module imports successfully")

        utils = PokeDataUtils()
        print("  ✓ PokeDataUtils instantiated")

        # Test data loading
        pokemon_data = utils.load_json_data(DATA_FILES["pokemon"])
        if pokemon_data:
            print(f"  ✓ Pokemon data loaded: {len(pokemon_data)} entries")
        else:
            print("  ○ No Pokemon data found (expected if not scraped yet)")

    except ImportError as e:
        print(f"  ✗ Config import failed: {e}")
    except Exception as e:
        print(f"  ✗ Config test failed: {e}")

    try:
        from grab_info import pk_names

        names = pk_names()
        if names:
            print(f"  ✓ Grab_info module works: {len(names)} Pokemon names")
        else:
            print("  ○ No Pokemon names found (expected if not scraped yet)")
    except ImportError as e:
        print(f"  ✗ Grab_info import failed: {e}")
    except Exception as e:
        print(f"  ✗ Grab_info test failed: {e}")


def test_scrapers():
    """Test that scrapers can be imported"""
    print("\nTesting scrapers...")

    scraper_files = [
        "scrapers/comprehensive_scraper.py",
        "scrapers/game_dex_scraper.py",
        "scrapers/pokemon_info.py",
        "scrapers/abilities_scraper.py",
    ]

    for scraper_file in scraper_files:
        if os.path.exists(scraper_file):
            print(f"  ✓ {scraper_file} exists")
        else:
            print(f"  ✗ {scraper_file} missing")


def show_current_data_status():
    """Show what data we currently have"""
    print("\nCurrent data status:")

    try:
        from config import PokeDataUtils, DATA_FILES

        utils = PokeDataUtils()

        for data_type, file_path in DATA_FILES.items():
            if os.path.exists(file_path):
                data = utils.load_json_data(file_path)
                if isinstance(data, list):
                    count = len(data)
                elif isinstance(data, dict):
                    count = len(data.keys())
                else:
                    count = 0
                print(f"  {data_type.title()}: {count} entries")
            else:
                print(f"  {data_type.title()}: No data file")

    except Exception as e:
        print(f"  Error checking data: {e}")


def main():
    print("=== Pokemon Data Collection System Test ===")

    test_project_structure()
    test_utilities()
    test_scrapers()
    show_current_data_status()

    print("\n=== Test Complete ===")
    print("If all tests passed, you can run 'python main.py' to start the system.")


if __name__ == "__main__":
    main()

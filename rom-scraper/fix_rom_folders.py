#!/usr/bin/env python3
"""
Script to fix ROM folder structure.

Converts from old structure:
  system/
    Game1/
      Game1.nes
      boxart.png
      metadata.json
    Game2/
      Game2.nes
      boxart.png
      metadata.json

To new structure:
  system/
    gamelist.xml
    media/
      Game1-boxart.png
      Game1-metadata.json
      Game2-boxart.png
      Game2-metadata.json
    Game1.nes
    Game2.nes
"""

import argparse
import shutil
from pathlib import Path
from typing import List


def is_rom_file(filepath: Path) -> bool:
    """Check if file is a ROM file"""
    rom_extensions = [
        '.zip', '.7z', '.rar', '.iso', '.bin', '.cue',
        '.gba', '.gbc', '.gb', '.nes', '.sfc', '.smc',
        '.n64', '.z64', '.md', '.smd', '.gen', '.nds',
        '.3ds', '.cia', '.chd', '.pbp'
    ]
    return filepath.suffix.lower() in rom_extensions


def fix_system_folder(system_dir: Path, dry_run: bool = False) -> dict:
    """
    Fix a system folder by moving ROMs out of subdirectories and
    organizing media files into a media/ folder.

    Returns:
        dict with statistics about the operation
    """
    if not system_dir.is_dir():
        print(f"❌ Not a directory: {system_dir}")
        return {'error': 'not_a_directory'}

    stats = {
        'roms_moved': 0,
        'media_moved': 0,
        'folders_removed': 0,
        'errors': []
    }

    # Create media directory
    media_dir = system_dir / "media"
    if not dry_run:
        media_dir.mkdir(exist_ok=True)

    # Find all subdirectories (potential game folders)
    subdirs = [d for d in system_dir.iterdir() if d.is_dir() and d.name != 'media']

    if not subdirs:
        print(f"ℹ️  No game folders found in {system_dir.name}")
        return stats

    print(f"\n{'='*60}")
    print(f"Processing: {system_dir.name}")
    print(f"{'='*60}")
    print(f"Found {len(subdirs)} potential game folders")

    for game_folder in subdirs:
        print(f"\n📁 Processing: {game_folder.name}")

        # Find files in this folder
        files = list(game_folder.iterdir())
        rom_files = [f for f in files if f.is_file() and is_rom_file(f)]
        metadata_files = [f for f in files if f.is_file() and f.name.endswith('-metadata.json') or f.name == 'metadata.json']
        boxart_files = [f for f in files if f.is_file() and ('boxart' in f.name.lower() or f.suffix.lower() in ['.png', '.jpg', '.jpeg'])]

        # Move ROM file(s) to system directory
        for rom_file in rom_files:
            new_rom_path = system_dir / rom_file.name

            if new_rom_path.exists():
                print(f"  ⚠️  ROM already exists: {rom_file.name} (skipping)")
                stats['errors'].append(f"{game_folder.name}: ROM already exists")
            else:
                if dry_run:
                    print(f"  [DRY RUN] Would move ROM: {rom_file.name} -> {system_dir.name}/")
                else:
                    shutil.move(str(rom_file), str(new_rom_path))
                    print(f"  ✓ Moved ROM: {rom_file.name}")
                stats['roms_moved'] += 1

        # Move metadata to media folder
        for metadata_file in metadata_files:
            # Use ROM basename for metadata filename
            if rom_files:
                rom_basename = rom_files[0].stem
                new_metadata_name = f"{rom_basename}-metadata.json"
            else:
                new_metadata_name = f"{game_folder.name}-metadata.json"

            new_metadata_path = media_dir / new_metadata_name

            if dry_run:
                print(f"  [DRY RUN] Would move metadata: {metadata_file.name} -> media/{new_metadata_name}")
            else:
                shutil.move(str(metadata_file), str(new_metadata_path))
                print(f"  ✓ Moved metadata: {new_metadata_name}")
            stats['media_moved'] += 1

        # Move boxart to media folder
        for boxart_file in boxart_files:
            # Skip if it's the metadata file (already moved)
            if boxart_file in metadata_files:
                continue

            # Use ROM basename for boxart filename
            if rom_files:
                rom_basename = rom_files[0].stem
                new_boxart_name = f"{rom_basename}-boxart{boxart_file.suffix}"
            else:
                new_boxart_name = f"{game_folder.name}-boxart{boxart_file.suffix}"

            new_boxart_path = media_dir / new_boxart_name

            if dry_run:
                print(f"  [DRY RUN] Would move boxart: {boxart_file.name} -> media/{new_boxart_name}")
            else:
                shutil.move(str(boxart_file), str(new_boxart_path))
                print(f"  ✓ Moved boxart: {new_boxart_name}")
            stats['media_moved'] += 1

        # Remove empty game folder
        try:
            remaining_files = list(game_folder.iterdir())
            if not remaining_files:
                if dry_run:
                    print(f"  [DRY RUN] Would remove empty folder: {game_folder.name}")
                else:
                    game_folder.rmdir()
                    print(f"  ✓ Removed empty folder: {game_folder.name}")
                stats['folders_removed'] += 1
            else:
                print(f"  ⚠️  Folder not empty, keeping: {game_folder.name}")
                print(f"     Remaining files: {[f.name for f in remaining_files]}")
                stats['errors'].append(f"{game_folder.name}: folder not empty")
        except Exception as e:
            print(f"  ❌ Error removing folder: {e}")
            stats['errors'].append(f"{game_folder.name}: {str(e)}")

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Fix ROM folder structure by moving ROMs out of subdirectories"
    )
    parser.add_argument(
        "base_path",
        type=str,
        help="Base path containing system folders (e.g., C:\\Users\\DScha\\Desktop\\ROM_PY_Downloads)"
    )
    parser.add_argument(
        "--system",
        type=str,
        help="Specific system folder to fix (e.g., 'nes', 'gba'). If not specified, will process all systems."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually making changes"
    )

    args = parser.parse_args()

    base_path = Path(args.base_path)

    if not base_path.exists():
        print(f"❌ Path does not exist: {base_path}")
        return

    print("\n" + "="*60)
    print("           ROM FOLDER STRUCTURE FIX")
    print("="*60)
    if args.dry_run:
        print("⚠️  DRY RUN MODE - No changes will be made")
    print(f"Base path: {base_path}")
    print("="*60)

    # Determine which systems to process
    if args.system:
        system_dirs = [base_path / args.system]
    else:
        # Process all subdirectories as potential system folders
        system_dirs = [d for d in base_path.iterdir() if d.is_dir()]

    if not system_dirs:
        print("❌ No system folders found")
        return

    total_stats = {
        'roms_moved': 0,
        'media_moved': 0,
        'folders_removed': 0,
        'errors': []
    }

    # Process each system
    for system_dir in system_dirs:
        stats = fix_system_folder(system_dir, dry_run=args.dry_run)

        # Aggregate stats
        total_stats['roms_moved'] += stats.get('roms_moved', 0)
        total_stats['media_moved'] += stats.get('media_moved', 0)
        total_stats['folders_removed'] += stats.get('folders_removed', 0)
        total_stats['errors'].extend(stats.get('errors', []))

    # Final summary
    print("\n" + "="*60)
    print("           SUMMARY")
    print("="*60)
    print(f"ROMs moved: {total_stats['roms_moved']}")
    print(f"Media files moved: {total_stats['media_moved']}")
    print(f"Folders removed: {total_stats['folders_removed']}")

    if total_stats['errors']:
        print(f"\nErrors/Warnings: {len(total_stats['errors'])}")
        for error in total_stats['errors'][:10]:  # Show first 10 errors
            print(f"  • {error}")
        if len(total_stats['errors']) > 10:
            print(f"  ... and {len(total_stats['errors']) - 10} more")

    if args.dry_run:
        print("\n⚠️  This was a dry run. Run without --dry-run to make actual changes.")
    else:
        print(f"\n✓ Complete! Fixed folder structure in: {base_path}")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()

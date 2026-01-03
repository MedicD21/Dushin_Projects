#!/usr/bin/env python3
"""
ROM Name Cleaner

Cleans up ROM filenames by removing:
- Region codes (USA), (Europe), (Japan), etc.
- Version info (Rev 1), (v1.1), etc.
- Tags like [!], [h1], [a1], [b1], [t1], etc.
- Extra parentheses and brackets
- Multiple spaces

Usage:
    python clean_rom_names.py
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


def pick_folder() -> Optional[str]:
    """Open a folder picker dialog and return the selected path."""
    # Try tkinter first
    try:
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)

        selected = filedialog.askdirectory(
            title="Select folder containing ROMs to clean"
        )

        root.destroy()

        if selected:
            return selected
        return None
    except Exception as e:
        print(f"Tkinter folder picker unavailable ({e})")

    # Fallback: Windows PowerShell folder picker
    if sys.platform == 'win32':
        try:
            import subprocess
            print("Using Windows folder picker...")

            ps_script = """
            $shell = New-Object -ComObject Shell.Application
            $folder = $shell.BrowseForFolder(0, 'Select folder containing ROMs to clean', 0x0041, 0)
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
            if selected and os.path.exists(selected):
                return selected
        except Exception as e:
            print(f"Windows folder picker also unavailable ({e})")

    return None


class ROMNameCleaner:
    """Clean ROM filenames by removing region codes, tags, and other metadata"""

    # ROM file extensions to process
    ROM_EXTENSIONS = {
        '.zip', '.7z', '.rar', '.iso', '.bin', '.cue',
        '.gba', '.gbc', '.gb', '.nes', '.sfc', '.smc',
        '.n64', '.z64', '.md', '.smd', '.gen', '.nds',
        '.3ds', '.cia', '.chd', '.pbp', '.cso'
    }

    def __init__(self, directory: Path, recursive: bool = True):
        """
        Initialize ROM name cleaner

        Args:
            directory: Directory containing ROMs
            recursive: If True, process subdirectories
        """
        self.directory = directory
        self.recursive = recursive

    def is_rom_file(self, filepath: Path) -> bool:
        """Check if file is a ROM file"""
        return filepath.suffix.lower() in self.ROM_EXTENSIONS

    def clean_name(self, filename: str) -> str:
        """
        Clean a ROM filename

        Args:
            filename: Original filename (with extension)

        Returns:
            Cleaned filename
        """
        # Separate name and extension
        filepath = Path(filename)
        name = filepath.stem
        ext = filepath.suffix

        # Remove common patterns
        patterns_to_remove = [
            # Region codes
            r'\s*\(USA\)',
            r'\s*\(US\)',
            r'\s*\(Europe\)',
            r'\s*\(EU\)',
            r'\s*\(World\)',
            r'\s*\(Japan\)',
            r'\s*\(JP\)',
            r'\s*\(Asia\)',
            r'\s*\(Korea\)',
            r'\s*\(Australia\)',
            r'\s*\(Germany\)',
            r'\s*\(France\)',
            r'\s*\(Spain\)',
            r'\s*\(Italy\)',
            r'\s*\(Brazil\)',
            r'\s*\(En\)',
            r'\s*\(En,Fr,De,Es,It\)',
            r'\s*\(En,Fr,De\)',

            # Multi-region variants
            r'\s*\(USA,\s*Europe\)',
            r'\s*\(Japan,\s*USA\)',

            # Version info
            r'\s*\(Rev\s*\d+\)',
            r'\s*\(Rev\s*[A-Z]\)',
            r'\s*\(v\d+\.\d+\)',
            r'\s*\(Version\s*\d+\)',

            # Tags and labels
            r'\s*\[!\]',          # Verified good dump
            r'\s*\[a\d*\]',       # Alternate
            r'\s*\[b\d*\]',       # Bad dump
            r'\s*\[h\d*C?\]',     # Hack
            r'\s*\[o\d*\]',       # Overdump
            r'\s*\[t\d*\]',       # Trained
            r'\s*\[f\d*\]',       # Fixed
            r'\s*\[T-\w+\]',      # Translation
            r'\s*\[T\+\w+\]',     # Translation
            r'\s*\[p\d*\]',       # Pirate
            r'\s*\[x\]',          # Bad checksum
            r'\s*\[C\]',          # Checksum
            r'\s*\[BF\]',         # Bung Fix

            # Additional info
            r'\s*\(Disc\s*\d+\)',
            r'\s*\(Disk\s*\d+\)',
            r'\s*\(Side\s*[AB]\)',
            r'\s*\(Unl\)',        # Unlicensed
            r'\s*\(Beta\)',
            r'\s*\(Proto\)',
            r'\s*\(Sample\)',
            r'\s*\(Demo\)',
            r'\s*\(Promo\)',

            # Misc
            r'\s*\(M\d+\)',       # Mapper info
            r'\s*\(PRG\d+\)',
            r'\s*\(CHR\d+\)',
        ]

        # Apply all patterns
        for pattern in patterns_to_remove:
            name = re.sub(pattern, '', name, flags=re.IGNORECASE)

        # Remove any remaining empty parentheses or brackets
        name = re.sub(r'\s*\(\s*\)', '', name)
        name = re.sub(r'\s*\[\s*\]', '', name)
        name = re.sub(r'\s*\{\s*\}', '', name)

        # Clean up multiple spaces
        name = ' '.join(name.split())

        # Remove trailing/leading spaces
        name = name.strip()

        # Handle edge case: if name is empty after cleaning, use original
        if not name:
            name = filepath.stem

        return name + ext

    def preview_changes(self) -> List[Tuple[Path, str, str]]:
        """
        Preview what files would be renamed

        Returns:
            List of tuples: (file_path, old_name, new_name)
        """
        changes = []

        if self.recursive:
            files = self.directory.rglob('*')
        else:
            files = self.directory.glob('*')

        for filepath in files:
            if not filepath.is_file() or not self.is_rom_file(filepath):
                continue

            old_name = filepath.name
            new_name = self.clean_name(old_name)

            if old_name != new_name:
                changes.append((filepath, old_name, new_name))

        return changes

    def rename_files(self, dry_run: bool = False) -> dict:
        """
        Rename ROM files

        Args:
            dry_run: If True, don't actually rename files

        Returns:
            Statistics about the operation
        """
        stats = {
            'total_files': 0,
            'renamed': 0,
            'skipped': 0,
            'errors': 0
        }

        changes = self.preview_changes()
        stats['total_files'] = len(changes)

        for filepath, old_name, new_name in changes:
            try:
                new_path = filepath.parent / new_name

                # Check if target already exists
                if new_path.exists() and new_path != filepath:
                    print(f"  ⚠️  Skipping (target exists): {old_name}")
                    stats['skipped'] += 1
                    continue

                if dry_run:
                    print(f"  [DRY RUN] Would rename:")
                    print(f"    FROM: {old_name}")
                    print(f"    TO:   {new_name}")
                else:
                    filepath.rename(new_path)
                    print(f"  ✓ Renamed:")
                    print(f"    FROM: {old_name}")
                    print(f"    TO:   {new_name}")

                stats['renamed'] += 1

            except Exception as e:
                print(f"  ❌ Error renaming {old_name}: {e}")
                stats['errors'] += 1

        return stats


def main():
    print("\n" + "="*60)
    print("           ROM NAME CLEANER")
    print("="*60)
    print("\nThis tool removes region codes, tags, and version info")
    print("from ROM filenames to make them cleaner.\n")

    # Pick folder
    folder_path = pick_folder()

    if not folder_path:
        print("❌ No folder selected. Exiting.")
        return

    directory = Path(folder_path)

    if not directory.exists():
        print(f"❌ Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"❌ Not a directory: {directory}")
        return

    print(f"\n📁 Selected folder: {directory}\n")

    # Ask for recursive processing
    recursive_input = input("Process subdirectories recursively? (yes/no) [yes]: ").strip().lower()
    recursive = recursive_input in ['', 'yes', 'y']

    # Initialize cleaner
    cleaner = ROMNameCleaner(directory, recursive=recursive)

    # Preview changes
    print(f"\n{'='*60}")
    print("PREVIEW CHANGES")
    print(f"{'='*60}\n")

    changes = cleaner.preview_changes()

    if not changes:
        print("✓ No ROM files need renaming!")
        print("\nAll ROM filenames are already clean.\n")
        return

    print(f"Found {len(changes)} files to rename:\n")

    # Show first 20 changes as preview
    for idx, (filepath, old_name, new_name) in enumerate(changes[:20], 1):
        print(f"{idx:3d}. {old_name}")
        print(f"     → {new_name}\n")

    if len(changes) > 20:
        print(f"... and {len(changes) - 20} more files\n")

    # Confirm
    print(f"{'='*60}")
    confirm = input(f"\nProceed with renaming {len(changes)} files? (yes/no): ").strip().lower()

    if confirm not in ['yes', 'y']:
        print("\n❌ Operation cancelled.\n")
        return

    # Perform renaming
    print(f"\n{'='*60}")
    print("RENAMING FILES")
    print(f"{'='*60}\n")

    stats = cleaner.rename_files(dry_run=False)

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total files processed: {stats['total_files']}")
    print(f"Successfully renamed: {stats['renamed']}")
    print(f"Skipped: {stats['skipped']}")
    print(f"Errors: {stats['errors']}")
    print(f"{'='*60}\n")

    if stats['renamed'] > 0:
        print(f"✓ Complete! Renamed {stats['renamed']} ROM files in: {directory}\n")
    else:
        print("No files were renamed.\n")


if __name__ == "__main__":
    main()

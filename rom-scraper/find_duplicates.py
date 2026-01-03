#!/usr/bin/env python3
"""
ROM Duplicate Finder

Scans a directory for duplicate ROM files based on:
1. File hash (MD5) - finds exact duplicates
2. Game title extraction - finds different versions of same game
3. File size - quick pre-filter for potential duplicates

Usage:
    python find_duplicates.py <directory_path> [options]
"""

import argparse
import hashlib
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class DuplicateFinder:
    """Find duplicate ROM files in a directory"""

    # ROM file extensions to scan
    ROM_EXTENSIONS = {
        '.zip', '.7z', '.rar', '.iso', '.bin', '.cue',
        '.gba', '.gbc', '.gb', '.nes', '.sfc', '.smc',
        '.n64', '.z64', '.md', '.smd', '.gen', '.nds',
        '.3ds', '.cia', '.chd', '.pbp', '.cso'
    }

    def __init__(self, directory: Path, recursive: bool = True):
        """
        Initialize duplicate finder

        Args:
            directory: Directory to scan
            recursive: If True, scan subdirectories recursively
        """
        self.directory = directory
        self.recursive = recursive
        self.files_by_hash: Dict[str, List[Path]] = defaultdict(list)
        self.files_by_size: Dict[int, List[Path]] = defaultdict(list)
        self.files_by_title: Dict[str, List[Path]] = defaultdict(list)

    def is_rom_file(self, filepath: Path) -> bool:
        """Check if file is a ROM file"""
        return filepath.suffix.lower() in self.ROM_EXTENSIONS

    def calculate_hash(self, filepath: Path, algorithm: str = 'md5') -> str:
        """
        Calculate file hash

        Args:
            filepath: Path to file
            algorithm: Hash algorithm ('md5', 'sha1', 'sha256')

        Returns:
            Hex digest of file hash
        """
        if algorithm == 'md5':
            hasher = hashlib.md5()
        elif algorithm == 'sha1':
            hasher = hashlib.sha1()
        elif algorithm == 'sha256':
            hasher = hashlib.sha256()
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")

        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            print(f"  ⚠️  Error hashing {filepath.name}: {e}")
            return ""

    def extract_game_title(self, filename: str) -> str:
        """
        Extract clean game title from ROM filename

        Removes region codes, version info, etc.
        Example: "Super Mario Bros. (USA) (Rev 1).nes" -> "Super Mario Bros."
        """
        # Remove extension
        name = Path(filename).stem

        # Remove common patterns in parentheses and brackets
        patterns = [
            r'\s*\([^)]*\)',  # (USA), (Europe), (v1.1), etc.
            r'\s*\[[^\]]*\]',  # [!], [h1], [a1], etc.
            r'\s*\{[^}]*\}',   # {Other info}
        ]

        for pattern in patterns:
            name = re.sub(pattern, '', name)

        # Clean up extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    def scan_directory(self) -> Dict[str, int]:
        """
        Scan directory for ROM files

        Returns:
            Statistics about the scan
        """
        print(f"\n{'='*60}")
        print(f"Scanning: {self.directory}")
        print(f"{'='*60}")

        if self.recursive:
            files = self.directory.rglob('*')
        else:
            files = self.directory.glob('*')

        rom_files = [f for f in files if f.is_file() and self.is_rom_file(f)]

        stats = {
            'total_files': len(rom_files),
            'total_size': 0,
            'processed': 0,
            'errors': 0
        }

        print(f"Found {len(rom_files)} ROM files to analyze\n")

        for idx, filepath in enumerate(rom_files, 1):
            try:
                # Show progress
                if idx % 10 == 0 or idx == len(rom_files):
                    print(f"  Processing: {idx}/{len(rom_files)} files...", end='\r')

                # Get file size
                file_size = filepath.stat().st_size
                stats['total_size'] += file_size

                # Calculate hash
                file_hash = self.calculate_hash(filepath)
                if not file_hash:
                    stats['errors'] += 1
                    continue

                # Extract title
                title = self.extract_game_title(filepath.name)

                # Store in indices
                self.files_by_hash[file_hash].append(filepath)
                self.files_by_size[file_size].append(filepath)
                self.files_by_title[title.lower()].append(filepath)

                stats['processed'] += 1

            except Exception as e:
                print(f"\n  ⚠️  Error processing {filepath.name}: {e}")
                stats['errors'] += 1

        print(f"\n  Processing: {stats['processed']}/{len(rom_files)} files... Done!")
        return stats

    def find_exact_duplicates(self) -> Dict[str, List[Path]]:
        """
        Find exact duplicate files (same hash)

        Returns:
            Dictionary of hash -> list of duplicate files
        """
        return {
            hash_val: files
            for hash_val, files in self.files_by_hash.items()
            if len(files) > 1
        }

    def find_size_duplicates(self) -> Dict[int, List[Path]]:
        """
        Find files with same size (potential duplicates)

        Returns:
            Dictionary of size -> list of files
        """
        return {
            size: files
            for size, files in self.files_by_size.items()
            if len(files) > 1
        }

    def find_title_duplicates(self) -> Dict[str, List[Path]]:
        """
        Find files with same game title (different versions)

        Returns:
            Dictionary of title -> list of files
        """
        return {
            title: files
            for title, files in self.files_by_title.items()
            if len(files) > 1
        }


def format_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def print_duplicates(duplicates: Dict, title: str, show_hash: bool = False):
    """Print duplicate files in a formatted way"""
    if not duplicates:
        print(f"\n✓ No {title.lower()} found!")
        return

    print(f"\n{'='*60}")
    print(f"{title.upper()}")
    print(f"{'='*60}")
    print(f"Found {len(duplicates)} groups with duplicates\n")

    total_wasted = 0
    file_count = 0

    for idx, (key, files) in enumerate(sorted(duplicates.items()), 1):
        print(f"\n[Group {idx}] {len(files)} duplicate files:")

        if show_hash:
            print(f"  Hash: {key}")

        # Calculate wasted space (size of duplicates, keeping 1 original)
        file_size = files[0].stat().st_size
        wasted = file_size * (len(files) - 1)
        total_wasted += wasted

        print(f"  Size: {format_size(file_size)} each")
        print(f"  Wasted space: {format_size(wasted)}")
        print(f"  Files:")

        for file in sorted(files):
            # Show relative path from scan directory
            rel_path = file.relative_to(file.parents[0]) if file.is_absolute() else file
            print(f"    • {file.parent.name}/{file.name}")
            file_count += 1

    print(f"\n{'='*60}")
    print(f"Total duplicate groups: {len(duplicates)}")
    print(f"Total duplicate files: {file_count}")
    print(f"Total wasted space: {format_size(total_wasted)}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Find duplicate ROM files in a directory"
    )
    parser.add_argument(
        "directory",
        type=str,
        help="Directory to scan for duplicates"
    )
    parser.add_argument(
        "--type",
        choices=['exact', 'size', 'title', 'all'],
        default='exact',
        help="Type of duplicates to find (default: exact)"
    )
    parser.add_argument(
        "--no-recursive",
        action="store_true",
        help="Don't scan subdirectories recursively"
    )
    parser.add_argument(
        "--hash",
        choices=['md5', 'sha1', 'sha256'],
        default='md5',
        help="Hash algorithm to use (default: md5)"
    )
    parser.add_argument(
        "--export",
        type=str,
        help="Export results to a text file"
    )

    args = parser.parse_args()

    directory = Path(args.directory)

    if not directory.exists():
        print(f"❌ Directory does not exist: {directory}")
        return

    if not directory.is_dir():
        print(f"❌ Not a directory: {directory}")
        return

    print("\n" + "="*60)
    print("           ROM DUPLICATE FINDER")
    print("="*60)

    # Initialize finder
    finder = DuplicateFinder(
        directory=directory,
        recursive=not args.no_recursive
    )

    # Scan directory
    stats = finder.scan_directory()

    # Print scan statistics
    print(f"\n{'='*60}")
    print("SCAN STATISTICS")
    print(f"{'='*60}")
    print(f"Total ROM files found: {stats['total_files']}")
    print(f"Successfully processed: {stats['processed']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total size: {format_size(stats['total_size'])}")
    print(f"{'='*60}")

    # Find and display duplicates based on type
    if args.type in ['exact', 'all']:
        exact_dupes = finder.find_exact_duplicates()
        print_duplicates(exact_dupes, "Exact Duplicates (Same Hash)", show_hash=True)

    if args.type in ['size', 'all']:
        size_dupes = finder.find_size_duplicates()
        print_duplicates(size_dupes, "Size Duplicates (Same File Size)")

    if args.type in ['title', 'all']:
        title_dupes = finder.find_title_duplicates()
        print_duplicates(title_dupes, "Title Duplicates (Same Game, Different Versions)")

    # Export to file if requested
    if args.export:
        export_path = Path(args.export)
        with open(export_path, 'w', encoding='utf-8') as f:
            f.write("ROM DUPLICATE FINDER REPORT\n")
            f.write("="*60 + "\n\n")
            f.write(f"Scan directory: {directory}\n")
            f.write(f"Total files: {stats['total_files']}\n")
            f.write(f"Total size: {format_size(stats['total_size'])}\n\n")

            if args.type in ['exact', 'all']:
                exact_dupes = finder.find_exact_duplicates()
                f.write("\nEXACT DUPLICATES\n")
                f.write("="*60 + "\n")
                for idx, (hash_val, files) in enumerate(sorted(exact_dupes.items()), 1):
                    f.write(f"\nGroup {idx}: {hash_val}\n")
                    for file in sorted(files):
                        f.write(f"  {file}\n")

        print(f"\n✓ Results exported to: {export_path}")

    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()

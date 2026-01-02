# ROM Scraper Project

A comprehensive ROM management toolkit that downloads complete ROM sets from Myrient.erista.me and fetches detailed game metadata from ScreenScraper.fr.

## Features

- **🎮 Complete ROM Set Downloads**: Download entire verified ROM collections from Myrient
- **📦 Multiple Collections**: No-Intro, Redump, T-En (English Translation) collections
- **🔍 ScreenScraper Integration**: Fetch game information, artwork, screenshots, and videos
- **🖥️ EmulationStation Compatible**: Generates proper folder structures and gamelist.xml
- **🎯 17+ Systems Supported**: Nintendo, Sega, Sony, and more
- **⚡ Fast & Reliable**: Direct downloads from myrient.erista.me
- **🔄 Batch Processing**: Scrape entire ROM directories at once
- **🎨 Hash-based Matching**: Accurate game identification using ROM file hashes

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection
- ScreenScraper.fr account (free)

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure credentials (optional):
   - Edit `config.json` with your ScreenScraper credentials
   - Or enter them interactively when running the scripts

## Usage

### 1. Myrient ROM Downloader

Download complete ROM sets from myrient.erista.me:

```bash
python myrient_rom_downloader.py
```

**What is Myrient?**
Myrient (myrient.erista.me) is a reliable ROM preservation site hosting complete, verified ROM collections including:
- **No-Intro**: Verified cartridge-based ROM sets
- **Redump**: Verified disc-based ROM sets
- **T-En Collection**: English translation patches pre-applied

**Features:**
- 🎮 **17+ Complete System Sets**: Full libraries for GBA, SNES, NES, Genesis, PlayStation, and more
- ⚡ **Direct Downloads**: Fast, reliable downloads from myrient servers
- 📦 **Multiple Collections**: Choose between No-Intro, Redump, or T-En versions
- 📊 **Progress Tracking**: See download progress for each file
- ⏭️ **Smart Skip**: Automatically skips already downloaded files
- 🗂️ **Auto Organization**: Saves to system-specific folders

**How to Use:**

**Step 1: Launch the Downloader**
```bash
python myrient_rom_downloader.py
# You'll be asked where to save ROMs
```

**Setting the download folder (3 ways):**
- CLI flag (no prompt): `python myrient_rom_downloader.py --path "D:/ROMs"`
- Folder picker dialog: `python myrient_rom_downloader.py --pick-path`
- Config/env: set `paths.default_download_path` in `config.json` or set `MYRIENT_DOWNLOAD_PATH`

**Step 2: Browse Systems**
```
Choose option 1: Browse and Download Complete ROM Sets

You'll see a list like:
 1. Game Boy (gb)
    Collections: T-En Collection, No-Intro
 2. Game Boy Advance (gba)
    Collections: T-En Collection, No-Intro
 3. Game Boy Color (gbc)
    Collections: T-En Collection, No-Intro
 ...and more
```

**Step 3: Select System & Collection**
```
Enter system number: 2 (for GBA)

Available collections for Game Boy Advance:
1. T-En Collection
2. No-Intro

Select collection: 1 (for T-En with English patches)
```

**Step 4: Confirm & Download**
```
⚠️  Found 1,234 files in complete set
This will download to: /your/path/gba/

Proceed with download? (yes/no): yes

🚀 Starting download...
[1/1234] Pokemon - Fire Red (USA).gba
  ⬇️  Downloading...
  Progress: 100% (4.5/4.5 MB)
  ✓ Downloaded
```

**Available Complete Sets:**
- **Nintendo Handhelds**: GB, GBC, GBA, NDS, 3DS
- **Nintendo Consoles**: NES, SNES, N64, GameCube, Wii
- **Sega**: Genesis/Mega Drive, Master System, Game Gear, Saturn, Dreamcast
- **Sony**: PlayStation (PSX), PlayStation 2 (PS2)

**Collection Types:**
- **T-En Collection**: Games with English translation patches pre-applied (best for international users)
- **No-Intro**: Complete verified cartridge ROM sets
- **Redump**: Complete verified disc ROM sets (PSX, PS2, Dreamcast, etc.)

**Smart Filtering Features:**

The downloader includes intelligent filtering to save time and space:

1. **Region Priority**: Automatically prioritizes English versions
   - First choice: USA/EN versions
   - Second choice: World versions
   - Third choice: Europe versions
   - Skips: Japan, Korea, China versions

2. **Duplicate Detection**: Only downloads each game once
   - Checks existing files in destination folder
   - Compares game titles (ignoring region tags)
   - Skips duplicates automatically

3. **Automatic Unzipping**:
   - Extracts ZIP files after download
   - Removes ZIP files to save space
   - Organizes ROMs in clean folders

**Example Filter Output:**
```
🔍 Filtering 2,847 files...
   Priority: USA/EN > World > Europe (skipping Japan, Korea, etc.)

✓ Filter Results:
  • Will download: 847 files (USA/EN versions)
  • Skipped (wrong region): 1,832 files (Japan, Korea, etc.)
  • Skipped (duplicate): 168 files (already have)
```

This means instead of downloading 2,847 files, you only download 847 English versions!

### 2. ScreenScraper Metadata Fetcher

Fetch game metadata, artwork, and media:

```bash
python screenscraper_metadata.py
```

The script will:
1. Ask for your ScreenScraper credentials (defaults provided in config.json)
2. Ask where to save metadata and media
3. Present an interactive menu with options to:
   - Scrape a single ROM file
   - Scrape all ROMs in a directory
   - Search by ROM name
   - List available systems

**Features:**
- Hash-based game matching for accuracy
- Downloads box art, screenshots, videos, and more
- Generates EmulationStation-compatible gamelist.xml
- Creates organized folder structure
- Batch processing for entire ROM collections
- Rate limiting to respect ScreenScraper API

**Folder Structure Created:**
```
[output_dir]/
└── [system]/
    ├── roms/                   # Place your ROM files here
    ├── media/
    │   ├── images/            # Box art, screenshots, etc.
    │   └── videos/            # Game videos
    ├── metadata/              # JSON metadata files
    └── gamelist.xml           # EmulationStation game list
```

**Example Workflow:**
```
1. Choose "Scrape all ROMs in a directory"
2. Enter system: "gba"
3. Enter ROMs directory: "/path/to/gba/roms"
4. Script will process each ROM and download metadata
```

### 3. Complete Workflow Example

**Step 1: Download ROMs**
```bash
python archive_rom_downloader.py
# Search for "Pokemon" in "no-intro-rom-sets"
# Download to: ./roms
# Choose system: gba
```

**Step 2: Fetch Metadata**
```bash
python screenscraper_metadata.py
# Enter credentials (or use defaults)
# Save to: ./game_data
# Choose "Scrape all ROMs in a directory"
# System: gba
# ROMs directory: ./roms/gba
```

**Result:**
```
./game_data/gba/
├── roms/                      # Copy your ROMs here for EmulationStation
├── media/
│   ├── images/
│   │   ├── pokemon-ruby-boxart.png
│   │   ├── pokemon-ruby-screenshot.png
│   │   └── ...
│   └── videos/
│       └── pokemon-ruby-video.mp4
├── metadata/
│   └── pokemon-ruby.json
└── gamelist.xml
```

## Supported Systems

The ScreenScraper integration supports 40+ systems including:

- **Nintendo**: NES, SNES, N64, GameCube, Wii, Wii U, Switch
- **Nintendo Handhelds**: GB, GBC, GBA, DS, 3DS
- **Sega**: Genesis/Mega Drive, Master System, Game Gear, Saturn, Dreamcast
- **Sony**: PlayStation, PS2, PS3, PSP, PS Vita
- **Arcade**: MAME, FBA, Neo Geo
- **Atari**: 2600, 7800, Lynx, Jaguar
- **Others**: PC Engine, WonderSwan, and more

See the full list in the script or run option 4 in the metadata fetcher.

## EmulationStation / RetroArch / Anbernic Integration

The folder structure is compatible with:

### EmulationStation
1. Copy the generated system folder to your ES-DE or EmulationStation installation
2. The gamelist.xml will be automatically recognized
3. Media files are properly linked in the XML

### RetroArch
1. Use the ROMs from the `roms/` folder
2. Import the metadata as needed
3. Box art can be used with RetroArch's thumbnail system

### Anbernic Devices
1. Copy the system folder to your SD card's appropriate location
2. Most Anbernic devices use EmulationStation-based frontends
3. The folder structure is compatible with ArkOS, JELOS, and similar CFWs

## Configuration

Edit `config.json` to customize:

- **Credentials**: ScreenScraper login information
- **Paths**: Default download and metadata directories
- **Settings**: Rate limiting, media preferences
- **Systems**: Add or modify system definitions

## Tips and Best Practices

1. **ScreenScraper API Limits**:
   - Free accounts have rate limits
   - The script includes automatic rate limiting (1 second delay)
   - Consider registering for a premium account for heavy usage

2. **ROM Matching**:
   - Hash-based matching (using ROM files) is most accurate
   - Name-based matching works but may be less precise
   - Use No-Intro or Redump ROM sets for best results

3. **Storage**:
   - Plan for adequate storage space
   - Videos can be large (50-200MB per game)
   - Use `download_videos: false` in config if space is limited

4. **Legal Considerations**:
   - Only download ROMs you legally own
   - Respect copyright laws in your jurisdiction
   - Archive.org and ScreenScraper have their own terms of service

## Troubleshooting

**"Game not found in ScreenScraper database"**
- Try using the ROM file hash instead of name
- Check if your ROM is from a verified set (No-Intro, Redump)
- Verify the system name is correct

**Download fails from Archive.org**
- Check your internet connection
- The item may have restricted access
- Try a different search query or collection

**Rate limit errors from ScreenScraper**
- Increase `rate_limit_delay` in config.json
- Wait a few minutes before retrying
- Consider upgrading to a premium account

## Credentials

Default credentials (configured in config.json):
- **ScreenScraper Dev Account**: MedicD21 / ZMAcfblO1jB
- **ScreenScraper User Account**: MedicD21 / Desmond87

You can change these by editing config.json or entering new ones interactively.

## License

This project is for personal use. Respect the terms of service of Archive.org and ScreenScraper.fr.

## Support

For issues or questions:
1. Check the troubleshooting section
2. Verify your credentials are correct
3. Ensure you have the latest version of the scripts
4. Check ScreenScraper.fr status page for API availability

## Changelog

### Version 1.0
- Initial release
- Archive.org ROM downloader
- ScreenScraper metadata fetcher
- EmulationStation gamelist.xml generation
- Support for 40+ systems
- Batch processing capabilities

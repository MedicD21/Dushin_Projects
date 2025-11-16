# 📋 Items Scraper - Files Reference

## Created Files

### 1. Core Scraper

**File**: `scrapers/items_scraper.py` (319 lines)

- **Purpose**: Main items scraper for Serebii ItemDex
- **Classes**: ItemDexScraper
- **Methods**: fetch_page, extract_item_from_page, scrape_category, scrape_all, save_to_json, save_by_category
- **Dependencies**: requests, BeautifulSoup4, json, os, time
- **Output**:
  - `data/items_data.json` (comprehensive file)
  - `data/items_by_category/*.json` (category-specific files)

### 2. Quick Test Version

**File**: `scrapers/items_scraper_test.py` (59 lines)

- **Purpose**: Fast test to verify scraper functionality
- **Scope**: 2 categories (Poké Balls, Recovery) = 81 items
- **Time**: ~1 minute
- **Output**: Console display only

### 3. Documentation Files

#### a. Technical Documentation

**File**: `ITEMS_SCRAPER_README.md` (5.4 KB)

- Website structure analysis
- Data extraction methodology
- Output format specification
- Performance notes
- Dependencies listing

#### b. User Guide

**File**: `ITEMS_SCRAPER_SETUP.md` (6.6 KB)

- Quick start instructions
- How to run (3 methods)
- Full data coverage info
- Features & capabilities
- Usage examples

#### c. Project Status

**File**: `ITEMS_SCRAPER_COMPLETE.md` (8.0 KB)

- Deliverables summary
- Architecture overview
- Integration points
- Performance metrics
- Customization guide

#### d. This File

**File**: `FILES_REFERENCE.md`

- Overview of all created/modified files
- File purposes and locations

---

## Modified Files

### main.py

**Changes**:

- Line 208: Added menu option "8. Run items scraper"
- Line 156-164: Added items scraper handler in run_scraper() method
- Line 435: Added choice == "8" handler to call items scraper
- Line 431-439: Items scraper included in "run all" option (choice 9)

**No breaking changes** - only additions to existing menu system

---

## Directory Structure

```
PokeDex_Info/
├── scrapers/
│   ├── items_scraper.py          ← NEW (main scraper)
│   ├── items_scraper_test.py     ← NEW (quick test)
│   ├── pokemon_info.py           (existing)
│   ├── moves_scraper.py          (existing)
│   ├── abilities_scraper.py      (existing)
│   ├── excel_importer.py         (existing)
│   └── ...
├── data/
│   ├── pokemon_data.json         (existing)
│   ├── moves_data_*.json         (existing)
│   ├── items_data.json           ← CREATED BY SCRAPER
│   └── items_by_category/        ← CREATED BY SCRAPER
│       ├── poke_balls.json
│       ├── recovery.json
│       ├── hold_item.json
│       ├── evolutionary_items.json
│       ├── key_items.json
│       ├── fossils_others.json
│       ├── stat_items.json
│       ├── mail.json
│       └── berries.json
├── main.py                       ← MODIFIED (menu integration)
├── ITEMS_SCRAPER_README.md       ← NEW (technical docs)
├── ITEMS_SCRAPER_SETUP.md        ← NEW (user guide)
├── ITEMS_SCRAPER_COMPLETE.md     ← NEW (project status)
└── FILES_REFERENCE.md            ← NEW (this file)
```

---

## Quick Reference

### Run Items Scraper

**Test Version** (Recommended first)

```bash
python3 scrapers/items_scraper_test.py
```

**Full Scraper**

```bash
python3 scrapers/items_scraper.py
```

**Via Main Menu**

```bash
python3 main.py
# Then select:
# 8 - Run items scraper (alone)
# 9 - Run all scrapers (includes items)
```

---

## File Dependencies

### items_scraper.py requires:

- ✅ Python 3.6+
- ✅ requests library
- ✅ beautifulsoup4 library
- ✅ utils/config.py (for PokeDataUtils)
- ✅ Internet connection

### items_scraper_test.py requires:

- ✅ Python 3.6+
- ✅ scrapers/items_scraper.py module
- ✅ requests & beautifulsoup4 libraries
- ✅ Internet connection

### main.py integration requires:

- ✅ scrapers/items_scraper.py in scrapers/ directory
- ✅ Python subprocess module (standard library)

---

## Data Files Created by Scraper

### Primary Output

**File**: `data/items_data.json`

- **Size**: ~2-3 MB
- **Format**: JSON with metadata
- **Contents**: All 1,000+ items sorted alphabetically
- **Structure**:
  ```json
  {
    "metadata": {...},
    "items": [...]
  }
  ```

### Category-Specific Outputs

**Directory**: `data/items_by_category/`

- **Files**: 9 JSON files (one per category)
- **Naming**: {category_name_lowercase}.json
- **Size**: ~200-400 KB each
- **Purpose**: Organized by category for easier access

---

## Troubleshooting

### If scraper doesn't run:

1. Check Python 3 is installed: `python3 --version`
2. Check dependencies: `pip list | grep requests beautifulsoup4`
3. Check file exists: `ls scrapers/items_scraper.py`
4. Try quick test first: `python3 scrapers/items_scraper_test.py`

### If main menu option doesn't appear:

1. Verify main.py was modified correctly
2. Check for syntax errors: `python3 -m py_compile main.py`
3. Try running main.py: `python3 main.py`

### If scraper hangs/times out:

1. Check internet connection
2. Run quick test instead: `python3 scrapers/items_scraper_test.py`
3. Serebii might be slow - try again later
4. Rate limiting can be adjusted in items_scraper.py

---

## Verification Checklist

- [x] items_scraper.py exists and is 319 lines
- [x] items_scraper_test.py exists and is 59 lines
- [x] 3 documentation files created
- [x] main.py modified with items scraper option
- [x] Menu option 8 references items scraper
- [x] Menu option 9 includes items in "run all"
- [x] Quick test runs successfully
- [x] Full scraper tested and working
- [x] Output format verified
- [x] Documentation complete

---

## Support & Customization

### To modify scraper:

1. Edit `scrapers/items_scraper.py`
2. Main configuration: `CATEGORY_PAGES` dict (line ~20)
3. Rate limiting: `time.sleep()` calls
4. Output paths: `save_to_json()` and `save_by_category()` methods

### To add more categories:

1. Find category URL on Serebii ItemDex
2. Add to `CATEGORY_PAGES` dict:
   ```python
   'Category Name': '/itemdex/list/categoryslug.shtml',
   ```
3. Scraper will automatically process new category

### To extract more data:

1. Find table in item detail page
2. Add extraction logic in `extract_item_from_page()`
3. Add field to returned item dict

---

## Integration with Project

The items scraper integrates seamlessly with existing project structure:

- ✅ Uses same config utilities (`utils/config.py`)
- ✅ Follows same coding patterns as other scrapers
- ✅ Outputs to same `data/` directory
- ✅ Integrated into main.py menu system
- ✅ Works with existing project tools

---

**All files are ready to use! Start with the quick test: `python3 scrapers/items_scraper_test.py`**

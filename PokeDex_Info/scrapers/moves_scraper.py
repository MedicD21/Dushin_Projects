#!/usr/bin/env python3
"""
Pokemon Moves Scraper
Scrapes comprehensive move data from Serebii.net including move details and Pokemon that learn them.
"""

import sys
import os
import json
import time
import re
from typing import Dict, List, Any, Optional

# Add project paths
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from config import PokeDataUtils, DATA_FILES, BASE_URLS


class MovesDataScraper:
    """Scrapes Pokemon moves data from Serebii"""

    def __init__(self, generation: int = 9):
        self.utils = PokeDataUtils()
        self.moves_data = []
        self.generation = generation

        # Generation-specific configuration
        self.gen_config = self._get_generation_config(generation)
        self.base_url = self.gen_config["url"]

        # Move categories mapping
        self.move_categories = {
            "Physical": "Physical",
            "Special": "Special",
            "Status": "Status",
            "Other": "Status",  # Fallback
        }

    def _get_generation_config(self, generation: int) -> Dict[str, Any]:
        """Get generation-specific configuration"""
        configs = {
            4: {
                "url": "https://www.serebii.net/attackdex-dp/",
                "games": ["Diamond", "Pearl", "Platinum"],
                "filename": "moves_data_gen4.json",
                "has_za_data": False,
            },
            5: {
                "url": "https://www.serebii.net/attackdex-bw/",
                "games": ["Black", "White", "Black 2", "White 2"],
                "filename": "moves_data_gen5.json",
                "has_za_data": False,
            },
            6: {
                "url": "https://www.serebii.net/attackdex-xy/",
                "games": ["X", "Y", "Omega Ruby", "Alpha Sapphire"],
                "filename": "moves_data_gen6.json",
                "has_za_data": False,
            },
            7: {
                "url": "https://www.serebii.net/attackdex-sm/",
                "games": ["Sun", "Moon", "Ultra Sun", "Ultra Moon"],
                "filename": "moves_data_gen7.json",
                "has_za_data": False,
            },
            8: {
                "url": "https://www.serebii.net/attackdex-swsh/",
                "games": ["Sword", "Shield", "Legends: Arceus"],
                "filename": "moves_data_gen8.json",
                "has_za_data": False,
            },
            9: {
                "url": "https://www.serebii.net/attackdex-sv/",
                "games": ["Scarlet", "Violet", "Legends: Z-A"],
                "filename": "moves_data_gen9.json",
                "has_za_data": True,
            },
        }

        if generation not in configs:
            raise ValueError(
                f"Generation {generation} not supported. Supported generations: {list(configs.keys())}"
            )

        return configs[generation]

    def scrape_moves_list(self) -> List[str]:
        """Get list of all moves from the main attack dex page"""
        print("Fetching moves list from Serebii...")

        try:
            soup = self.utils.safe_request(self.base_url)
            if not soup:
                return []

            move_links = []

            # Find all select dropdowns that contain move options
            select_elements = soup.find_all("select")
            for select in select_elements:
                options = select.find_all("option")
                for option in options:
                    value = option.get("value", "")
                    # Look for options with attackdex-sv URLs
                    if value and "/attackdex-sv/" in value and value.endswith(".shtml"):
                        # Extract move filename from the full path
                        # e.g., "/attackdex-sv/thunderbolt.shtml" -> "thunderbolt"
                        move_filename = value.split("/attackdex-sv/")[-1].replace(
                            ".shtml", ""
                        )
                        if move_filename and move_filename not in move_links:
                            move_links.append(move_filename)

            # Filter out any remaining non-move entries
            filtered_moves = []
            skip_patterns = [
                "index",
                "nav",
                "menu",
                "generation",
                "pokemon",
                "games",
                "archive",
                "privacy",
                "discord",
                "home",
            ]

            for move in move_links:
                # Skip if it contains navigation patterns or is too short/long
                if (
                    not any(pattern in move.lower() for pattern in skip_patterns)
                    and 2 <= len(move) <= 50
                    and move.replace("-", "").replace("_", "").isalnum()
                ):
                    filtered_moves.append(move)

            print(f"Found {len(filtered_moves)} moves to scrape")
            return filtered_moves

        except Exception as e:
            print(f"Error fetching moves list: {e}")
            return []

    def scrape_move_data(self, move_filename: str) -> Optional[Dict[str, Any]]:
        """Scrape detailed data for a specific move"""
        move_url = f"{self.base_url}{move_filename}.shtml"

        try:
            soup = self.utils.safe_request(move_url)
            if not soup:
                return None

            # Comprehensive move data structure matching Serebii layout
            move_data = {
                "name": "",
                "battle_type": "",
                "category": "",
                "power_points": None,
                "base_power": None,
                "accuracy": None,
                "battle_effect": "",
                "secondary_effect": "",
                "effect_rate": "",
                "base_critical_hit_rate": "",
                "speed_priority": 0,
                "pokemon_hit_in_battle": "",
                "physical_contact": False,
                "sound_type": False,
                "punch_move": False,
                "biting_move": False,
                "snatchable": False,
                "slicing_move": False,
                "bullet_type": False,
                "wind_move": False,
                "powder_move": False,
                "metronome": False,
                "affected_by_gravity": False,
                "defrosts_when_used": False,
                "reflected_by_magic_coat": False,
                "blocked_by_protect": False,
                "copyable_by_mirror_move": False,
                "z_move_power": "",
                "z_move_effect": "",
                "learned_by": [],  # Pokemon that can learn this move
            }

            # Add Pokemon Legends Z-A data structure only for supported generations
            if self.gen_config["has_za_data"]:
                move_data["pokemon_legends_za_data"] = {
                    "cooldown": "",
                    "base_power_za": "",
                    "distance": "",
                    "effect_rate_za": "",
                    "effect_duration": "",
                    "frame_data": "",
                    "base_critical_hit_rate_za": "",
                }

            # Extract move name from page title
            title = soup.find("title")
            if title:
                title_text = title.get_text()
                if " - " in title_text:
                    move_data["name"] = title_text.split(" - ")[0].strip()

            # Find the main move details table
            tables = soup.find_all("table", class_="dextable")

            for table in tables:
                rows = table.find_all("tr")

                # Parse structured table data
                for i, row in enumerate(rows):
                    cells = row.find_all(["td", "th"])

                    # Look for header patterns and extract data
                    for j, cell in enumerate(cells):
                        cell_text = cell.get_text().strip()

                        # Battle Type (from image src)
                        if "Battle Type" in cell_text and j + 1 < len(rows):
                            next_row = rows[i + 1]
                            type_cells = next_row.find_all("td")
                            if len(type_cells) > 1:
                                type_img = type_cells[1].find("img")
                                if type_img and type_img.get("src"):
                                    src = type_img.get("src")
                                    # Extract type from path like "/pokedx-bw/type/grass.gif"
                                    if "/type/" in src:
                                        move_data["battle_type"] = (
                                            src.split("/type/")[1]
                                            .replace(".gif", "")
                                            .replace(".png", "")
                                            .title()
                                        )

                        # Category (from image src)
                        elif "Category" in cell_text and j == 2 and i + 1 < len(rows):
                            next_row = rows[i + 1]
                            cat_cells = next_row.find_all("td")
                            if len(cat_cells) > 2:
                                cat_img = cat_cells[2].find("img")
                                if cat_img and cat_img.get("src"):
                                    src = cat_img.get("src")
                                    if "/type/" in src:
                                        move_data["category"] = (
                                            src.split("/type/")[1]
                                            .replace(".gif", "")
                                            .replace(".png", "")
                                            .title()
                                        )

                        # Power Points, Base Power, Accuracy (numeric values)
                        elif "Power Points" in cell_text and i + 1 < len(rows):
                            next_row = rows[i + 1]
                            value_cells = next_row.find_all("td")
                            if len(value_cells) >= 3:
                                # Power Points
                                pp_text = value_cells[0].get_text().strip()
                                if pp_text.isdigit():
                                    move_data["power_points"] = int(pp_text)
                                # Base Power
                                power_text = value_cells[1].get_text().strip()
                                if power_text.isdigit():
                                    move_data["base_power"] = int(power_text)
                                # Accuracy
                                acc_text = value_cells[2].get_text().strip()
                                if acc_text.isdigit():
                                    move_data["accuracy"] = int(acc_text)

                        # Battle Effect
                        elif "Battle Effect:" in cell_text:
                            if i + 1 < len(rows):
                                effect_row = rows[i + 1]
                                effect_cell = effect_row.find("td", class_="fooinfo")
                                if effect_cell:
                                    move_data["battle_effect"] = (
                                        effect_cell.get_text().strip()
                                    )

                        # Secondary Effect and Effect Rate
                        elif "Secondary Effect:" in cell_text:
                            if i + 1 < len(rows):
                                effect_row = rows[i + 1]
                                effect_cells = effect_row.find_all("td")
                                if len(effect_cells) >= 2:
                                    # Secondary Effect
                                    sec_effect = (
                                        effect_cells[0].get_text().strip()
                                        if effect_cells[0].get("class")
                                        and "fooinfo" in effect_cells[0].get("class")
                                        else effect_cells[1].get_text().strip()
                                    )
                                    move_data["secondary_effect"] = sec_effect
                                    # Effect Rate
                                    if len(effect_cells) >= 3:
                                        rate_text = effect_cells[-1].get_text().strip()
                                        move_data["effect_rate"] = rate_text

                        # Critical Hit Rate, Speed Priority, Pokemon Hit in Battle
                        elif "Base Critical Hit Rate" in cell_text and i + 1 < len(
                            rows
                        ):
                            next_row = rows[i + 1]
                            crit_cells = next_row.find_all("td")
                            if len(crit_cells) >= 3:
                                move_data["base_critical_hit_rate"] = (
                                    crit_cells[0].get_text().strip()
                                )
                                priority_text = crit_cells[1].get_text().strip()
                                if priority_text.lstrip("-").isdigit():
                                    move_data["speed_priority"] = int(priority_text)
                                move_data["pokemon_hit_in_battle"] = (
                                    crit_cells[2].get_text().strip()
                                )

                        # Move attribute flags (Physical Contact, Sound-Type, etc.)
                        elif "Physical Contact" in cell_text:
                            # Find the corresponding values row
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                attr_cells = values_row.find_all("td")
                                if len(attr_cells) >= 5:
                                    move_data["physical_contact"] = (
                                        attr_cells[0].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["sound_type"] = (
                                        attr_cells[1].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["punch_move"] = (
                                        attr_cells[2].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["biting_move"] = (
                                        attr_cells[3].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["snatchable"] = (
                                        attr_cells[4].get_text().strip().lower()
                                        == "yes"
                                    )

                        # Second row of attributes
                        elif "Slicing Move" in cell_text:
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                attr_cells = values_row.find_all("td")
                                if len(attr_cells) >= 5:
                                    move_data["slicing_move"] = (
                                        attr_cells[0].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["bullet_type"] = (
                                        attr_cells[1].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["wind_move"] = (
                                        attr_cells[2].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["powder_move"] = (
                                        attr_cells[3].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["metronome"] = (
                                        attr_cells[4].get_text().strip().lower()
                                        == "yes"
                                    )

                        # Third row of attributes
                        elif "Affected by Gravity" in cell_text:
                            if i + 1 < len(rows):
                                values_row = rows[i + 1]
                                attr_cells = values_row.find_all("td")
                                if len(attr_cells) >= 5:
                                    move_data["affected_by_gravity"] = (
                                        attr_cells[0].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["defrosts_when_used"] = (
                                        attr_cells[1].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["reflected_by_magic_coat"] = (
                                        attr_cells[2].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["blocked_by_protect"] = (
                                        attr_cells[3].get_text().strip().lower()
                                        == "yes"
                                    )
                                    move_data["copyable_by_mirror_move"] = (
                                        attr_cells[4].get_text().strip().lower()
                                        == "yes"
                                    )

                        # Pokémon Legends: Z-A Data section (only for supported generations)
                        elif self.gen_config["has_za_data"] and (
                            "Pokémon Legends: Z-A Data" in cell_text
                            or "Pokemon Legends: Z-A Data" in cell_text
                        ):
                            # Look for the Z-A data table that follows
                            za_table_found = False
                            for remaining_row in rows[i:]:
                                za_cells = remaining_row.find_all("td")
                                if len(za_cells) >= 3:
                                    # Check for Cooldown | Base Power | Distance headers
                                    if any(
                                        "Cooldown" in cell.get_text()
                                        for cell in za_cells
                                    ):
                                        # Next row should have the values
                                        next_idx = rows.index(remaining_row) + 1
                                        if next_idx < len(rows):
                                            value_row = rows[next_idx]
                                            value_cells = value_row.find_all("td")
                                            if len(value_cells) >= 3:
                                                move_data["pokemon_legends_za_data"][
                                                    "cooldown"
                                                ] = (value_cells[0].get_text().strip())
                                                move_data["pokemon_legends_za_data"][
                                                    "base_power_za"
                                                ] = (value_cells[1].get_text().strip())
                                                move_data["pokemon_legends_za_data"][
                                                    "distance"
                                                ] = (value_cells[2].get_text().strip())

                                    # Check for Effect Rate | Effect Duration | Frame Data headers
                                    elif any(
                                        "Effect Rate" in cell.get_text()
                                        for cell in za_cells
                                    ):
                                        next_idx = rows.index(remaining_row) + 1
                                        if next_idx < len(rows):
                                            value_row = rows[next_idx]
                                            value_cells = value_row.find_all("td")
                                            if len(value_cells) >= 3:
                                                move_data["pokemon_legends_za_data"][
                                                    "effect_rate_za"
                                                ] = (value_cells[0].get_text().strip())
                                                move_data["pokemon_legends_za_data"][
                                                    "effect_duration"
                                                ] = (value_cells[1].get_text().strip())
                                                frame_text = (
                                                    value_cells[2]
                                                    .get_text()
                                                    .strip()
                                                    .replace("\r", "")
                                                    .replace("\t", " ")
                                                )
                                                move_data["pokemon_legends_za_data"][
                                                    "frame_data"
                                                ] = " ".join(frame_text.split())

                                    # Check for Base Critical Hit Rate (single column in Z-A section)
                                    elif (
                                        any(
                                            "Base Critical Hit Rate" in cell.get_text()
                                            for cell in za_cells
                                        )
                                        and len(za_cells) == 1
                                    ):
                                        next_idx = rows.index(remaining_row) + 1
                                        if next_idx < len(rows):
                                            value_row = rows[next_idx]
                                            value_cells = value_row.find_all("td")
                                            if len(value_cells) >= 1:
                                                move_data["pokemon_legends_za_data"][
                                                    "base_critical_hit_rate_za"
                                                ] = (value_cells[0].get_text().strip())

            # Extract Pokemon that learn this move
            move_data["learned_by"] = self.extract_pokemon_learners(soup)

            # Set fallback name if not found
            if not move_data["name"]:
                move_data["name"] = move_filename.replace("-", " ").title()

            return move_data

        except Exception as e:
            print(f"Error scraping move {move_filename}: {e}")
            return None

    def extract_pokemon_learners(self, soup) -> List[Dict[str, Any]]:
        """Extract which Pokemon can learn this move and how"""
        learners = []

        try:
            # Look for specific learning method sections
            learning_methods = {
                "Level Up": "Level Up",
                "Move Reminder": "Move Reminder",
                "Breeding": "Breeding",
                "Z-A Data": "Z-A Level Up",
            }

            # Find all tables with Pokemon learning data
            tables = soup.find_all("table", class_="dextable")

            for table in tables:
                # Determine learning method from nearby headers
                current_method = "Level Up"  # default

                # Look for method headers before this table
                prev_elements = []
                current_elem = table
                for _ in range(10):  # Look back at previous 10 elements
                    current_elem = current_elem.find_previous_sibling()
                    if current_elem:
                        prev_elements.append(
                            current_elem.get_text().strip()
                            if current_elem.get_text
                            else ""
                        )
                    else:
                        break

                # Check for learning method indicators
                prev_text = " ".join(prev_elements).lower()
                if "move reminder" in prev_text:
                    current_method = "Move Reminder"
                elif "breeding" in prev_text:
                    current_method = "Breeding"
                elif "z-a" in prev_text:
                    current_method = "Z-A Level Up"

                # Parse table rows
                rows = table.find_all("tr")
                for row in rows:
                    cells = row.find_all("td", class_="fooinfo")

                    if len(cells) >= 3:  # Need at least dex#, pic, name columns
                        try:
                            # Extract dex number (first cell with #0XXX format)
                            dex_cell = cells[0]
                            dex_text = dex_cell.get_text().strip()

                            if dex_text.startswith("#") and len(dex_text) >= 5:
                                dex_number = dex_text[
                                    1:
                                ]  # Remove # and keep 4-digit format (0270)

                                # Extract Pokemon name and form (usually 3rd cell with link)
                                pokemon_name = ""
                                pokemon_form = "Normal"
                                if len(cells) >= 3:
                                    name_cell = cells[2]  # Usually the name column
                                    name_link = name_cell.find("a")
                                    if name_link:
                                        pokemon_name = name_link.get_text().strip()
                                    else:
                                        pokemon_name = name_cell.get_text().strip()

                                # Check for form variants by looking at the image in the 2nd cell
                                if len(cells) >= 2:
                                    pic_cell = cells[1]  # Usually the picture column
                                    img_tag = pic_cell.find("img")
                                    if img_tag and img_tag.get("src"):
                                        img_src = img_tag.get("src")
                                        # Check for form indicators in image filename
                                        if "-h.png" in img_src or "-h/" in img_src:
                                            pokemon_form = "Hisuian"
                                        elif "-a.png" in img_src or "-a/" in img_src:
                                            pokemon_form = "Alolan"
                                        elif "-g.png" in img_src or "-g/" in img_src:
                                            pokemon_form = "Galarian"
                                        elif "-p.png" in img_src or "-p/" in img_src:
                                            pokemon_form = "Paldean"
                                        elif "-mega" in img_src.lower():
                                            pokemon_form = "Mega"
                                        elif "-gmax" in img_src.lower():
                                            pokemon_form = "Gigantamax"

                                # Extract level (last cell with "Lv. X" format)
                                learn_level = None
                                level_text = ""
                                if len(cells) >= 4:
                                    # Level is usually in the last cell
                                    level_cell = cells[-1]
                                    level_text = level_cell.get_text().strip()

                                    if level_text.startswith("Lv. "):
                                        try:
                                            learn_level = int(
                                                level_text.replace("Lv. ", "")
                                            )
                                        except ValueError:
                                            learn_level = None

                                # Create learner entry
                                learner_data = {
                                    "dex_number": dex_number,  # Keep 4-digit format like "0270"
                                    "name": pokemon_name,
                                    "form": pokemon_form,
                                    "method": current_method,
                                }

                                if learn_level is not None:
                                    learner_data["level"] = learn_level

                                # Only add if we have valid dex number and name
                                if dex_number and pokemon_name and len(dex_number) == 4:
                                    learners.append(learner_data)

                        except (ValueError, IndexError, AttributeError) as e:
                            continue

        except Exception as e:
            print(f"Error extracting Pokemon learners: {e}")

        # Remove duplicates while preserving order (include form in deduplication)
        seen = set()
        unique_learners = []
        for learner in learners:
            key = (
                learner["dex_number"],
                learner["form"],
                learner["method"],
                learner.get("level"),
            )
            if key not in seen:
                seen.add(key)
                unique_learners.append(learner)

        return unique_learners

    def scrape_all_moves(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Scrape all moves data"""
        print("=== Pokemon Moves Scraper ===")
        print("Fetching comprehensive moves data from Serebii.net")
        print()

        # Get list of moves
        move_files = self.scrape_moves_list()
        if not move_files:
            print("No moves found to scrape!")
            return []

        if limit:
            move_files = move_files[:limit]
            print(f"Limiting to first {limit} moves for testing")

        print(f"Scraping {len(move_files)} moves...")
        print()

        moves_data = []

        for i, move_file in enumerate(move_files, 1):
            print(f"[{i:3d}/{len(move_files)}] Scraping {move_file}...")

            move_data = self.scrape_move_data(move_file)
            if move_data:
                # Skip moves that no Pokemon can learn (not usable in Gen 9)
                learners_count = len(move_data["learned_by"])
                if learners_count == 0:
                    print(
                        f"  ⚠ {move_data['name']} - {move_data['battle_type']} type, no Pokemon can learn it (skipping - not usable in Gen 9)"
                    )
                else:
                    moves_data.append(move_data)
                    print(
                        f"  ✓ {move_data['name']} - {move_data['battle_type']} type, {learners_count} Pokemon can learn it"
                    )
            else:
                print(f"  ✗ Failed to scrape {move_file}")

            # Rate limiting
            time.sleep(0.5)

            # Progress update every 25 moves
            if i % 25 == 0:
                print(f"\n--- Progress: {i}/{len(move_files)} moves completed ---\n")

        total_scraped = len(move_files)
        usable_moves = len(moves_data)
        skipped_moves = total_scraped - usable_moves

        print(f"\n✅ Scraping complete! Collected {usable_moves} usable Gen 9 moves")
        if skipped_moves > 0:
            print(
                f"   ⚠ Skipped {skipped_moves} moves (no Pokemon can learn them in Gen 9)"
            )
        return moves_data

    def save_moves_data(self, moves_data: List[Dict[str, Any]]):
        """Save moves data to JSON file"""
        # Use generation-specific filename
        output_file = f"data/{self.gen_config['filename']}"

        # Create backup if file exists
        if os.path.exists(output_file):
            backup_file = output_file.replace(".json", "_backup.json")
            os.rename(output_file, backup_file)
            print(f"Created backup: {backup_file}")

        # Create structured data with metadata
        structured_data = {
            "metadata": {
                "generation": self.generation,
                "games": self.gen_config["games"],
                "source": f"Serebii.net AttackDex-Gen{self.generation}",
                "scraped_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_moves": len(moves_data),
            },
            "moves": moves_data,
        }

        # Save new data
        self.utils.save_json_data(structured_data, output_file)
        print(f"✅ Saved {len(moves_data)} Gen 9 moves to {output_file}")

        # Print summary stats
        types_count = {}
        categories_count = {}
        total_learners = 0

        for move in moves_data:
            # Count by type
            move_type = move.get("battle_type", "Unknown")
            types_count[move_type] = types_count.get(move_type, 0) + 1

            # Count by category
            category = move.get("category", "Unknown")
            categories_count[category] = categories_count.get(category, 0) + 1

            # Count total Pokemon-move relationships
            total_learners += len(move.get("learned_by", []))

        print(f"\n📊 Moves Data Summary:")
        print(f"   Total Moves: {len(moves_data)}")
        print(f"   Total Pokemon-Move Relationships: {total_learners}")
        print(f"   Move Types: {len(types_count)}")
        print(f"   Move Categories: {len(categories_count)}")


def main():
    """Main execution function"""
    print("=== Pokémon Moves Data Scraper ===")
    print("Available generations:")
    print("4 - Generation 4 (Diamond/Pearl/Platinum/HeartGold/SoulSilver)")
    print("5 - Generation 5 (Black/White/Black2/White2)")
    print("6 - Generation 6 (X/Y/Omega Ruby/Alpha Sapphire)")
    print("7 - Generation 7 (Sun/Moon/Ultra Sun/Ultra Moon)")
    print(
        "8 - Generation 8 (Sword/Shield/Brilliant Diamond/Shining Pearl/Legends Arceus)"
    )
    print("9 - Generation 9 (Scarlet/Violet/Legends Z-A)")

    while True:
        try:
            generation = int(
                input("\nWhich generation would you like to scrape? (4-9): ")
            )
            if 4 <= generation <= 9:
                break
            else:
                print("Please enter a number between 4 and 9.")
        except ValueError:
            print("Please enter a valid number.")

    scraper = MovesDataScraper(generation)

    # Ask user for scraping options
    print(f"\nPokemon Moves Scraper - Generation {generation}")
    print("1. Scrape all moves (full dataset)")
    print("2. Scrape first 50 moves (testing)")
    print("3. Scrape first 10 moves (quick test)")

    choice = input("Choose option (1-3): ").strip()

    limit = None
    if choice == "2":
        limit = 50
    elif choice == "3":
        limit = 10
    elif choice != "1":
        print("Invalid choice, defaulting to full scrape")

    # Scrape moves data
    moves_data = scraper.scrape_all_moves(limit=limit)

    if moves_data:
        # Save data
        scraper.save_moves_data(moves_data)
        print(f"\n🎉 Generation {generation} moves scraping completed successfully!")
        print(f"Data saved to: data/{scraper.gen_config['filename']}")
    else:
        print("❌ No moves data collected")


if __name__ == "__main__":
    main()

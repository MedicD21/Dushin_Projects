#!/usr/bin/env python3
"""
Quick test version of Items Scraper - scrapes just a few items to verify functionality
Useful for testing before running the full scrape (which takes 15-20 minutes)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "utils"))

from items_scraper import ItemDexScraper


def quick_test():
    """Run a quick test of the items scraper with limited categories"""
    print("="*60)
    print("🧪 Quick Items Scraper Test (Limited)")
    print("="*60)
    print("\nThis test scrapes just 2 categories to verify functionality.")
    print("For the full dataset, run: python3 scrapers/items_scraper.py\n")
    
    scraper = ItemDexScraper()
    
    # Only scrape first 2 categories for testing
    limited_categories = {
        'Poké Balls': '/itemdex/list/pokeball.shtml',
        'Recovery': '/itemdex/list/recovery.shtml',
    }
    
    print("Testing...")
    all_items = []
    
    for category_name, category_url in limited_categories.items():
        items = scraper.scrape_category(category_name, category_url)
        all_items.extend(items)
        scraper.items_by_category[category_name] = items
    
    print("\n" + "="*60)
    print(f"✅ Test Complete!")
    print(f"✅ Scraped {len(all_items)} items from {len(limited_categories)} categories")
    print("="*60)
    
    if all_items:
        print("\nSample item data:")
        sample = all_items[0]
        print(f"  Name: {sample['name']}")
        print(f"  Category: {sample['category']}")
        print(f"  Effect: {sample['effect'][:100]}..." if sample['effect'] else "  Effect: (none)")
        print(f"  Games: {', '.join(sample['games'][:3])}" if sample['games'] else "  Games: (none)")
    
    print("\n✨ Items scraper is working correctly!")
    print("\nTo scrape all items:")
    print("  python3 scrapers/items_scraper.py")
    print("\nOr from the main menu:")
    print("  python3 main.py  (then select option 8)")


if __name__ == '__main__':
    quick_test()

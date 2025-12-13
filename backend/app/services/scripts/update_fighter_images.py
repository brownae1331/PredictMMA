#!/usr/bin/env python3
"""
Script to update fighter image URLs using ESPN scraper.

Usage:
    python update_fighter_images.py [--skip-existing] [--limit N] [--start-from N]

Examples:
    # Update all fighters
    python update_fighter_images.py

    # Skip fighters that already have image URLs
    python update_fighter_images.py --skip-existing

    # Update only first 10 fighters
    python update_fighter_images.py --limit 10

    # Start from fighter 100
    python update_fighter_images.py --start-from 100
"""

import argparse
import sys
import time
from contextlib import contextmanager
from typing import Optional

from app.db.database import sessionLocal
from app.db.models.models import Fighter
from app.services.scrapers.espn_fighter_image_scraper import ESPNFighterImageScraper


@contextmanager
def session_scope():
    """Database session context manager."""
    db = sessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def update_fighter_images(skip_existing: bool = False, limit: Optional[int] = None, start_from: int = 0):
    """Update image URLs for all fighters in the database."""
    print("=" * 60)
    print("Updating Fighter Image URLs from ESPN")
    print("=" * 60)
    
    scraper = ESPNFighterImageScraper()
    
    with session_scope() as db:
        # Query all fighters
        query = db.query(Fighter)
        
        if skip_existing:
            query = query.filter(Fighter.image_url.is_(None))
            print("Skipping fighters that already have image URLs")
        
        fighters = query.all()
        
        if start_from > 0:
            fighters = fighters[start_from:]
            print(f"Starting from fighter #{start_from + 1}")
        
        if limit:
            fighters = fighters[:limit]
            print(f"Limiting to {limit} fighters")
        
        total_fighters = len(fighters)
        print(f"Found {total_fighters} fighters to process")
        print()
        
        updated = 0
        skipped = 0
        failed = 0
        
        for i, fighter in enumerate(fighters, 1):
            try:
                # Skip if already has image URL and not forcing update
                if skip_existing and fighter.image_url:
                    skipped += 1
                    continue
                
                print(f"[{i}/{total_fighters}] Processing: {fighter.name}", end=" ... ")
                
                # Get image URL from ESPN
                image_url = scraper.get_fighter_image(fighter.name)
                
                # Check if we got a valid URL (not the default no-photo URL)
                if image_url and image_url != scraper.DEFAULT_NO_PHOTO_URL:
                    fighter.image_url = image_url
                    updated += 1
                    print(f"✅ Updated: {image_url[:50]}...")
                else:
                    # Still save the default URL so we know we tried
                    if not fighter.image_url:
                        fighter.image_url = scraper.DEFAULT_NO_PHOTO_URL
                        updated += 1
                    print(f"⚠️  No image found (using default)")
                
                # Commit every fighter to save progress
                db.commit()
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.5)
                
            except Exception as e:
                failed += 1
                print(f"❌ Error: {e}")
                db.rollback()
                continue
        
        print()
        print("=" * 60)
        print(f"✅ Image update complete:")
        print(f"   - Updated: {updated}")
        print(f"   - Skipped: {skipped}")
        print(f"   - Failed: {failed}")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Update fighter image URLs using ESPN scraper"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip fighters that already have image URLs"
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit the number of fighters to process"
    )
    parser.add_argument(
        "--start-from",
        type=int,
        default=0,
        help="Start processing from fighter at this index (0-based)"
    )
    
    args = parser.parse_args()
    
    try:
        update_fighter_images(
            skip_existing=args.skip_existing,
            limit=args.limit,
            start_from=args.start_from
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()


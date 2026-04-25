"""
main.py — Daily AI/ML news digest pipeline.

Runs the full pipeline in order:
  1. Fetch articles from all RSS feeds
  2. Remove duplicates (seen within the last 7 days)
  3. Score and select the top 5 with source diversity
  4. Render a markdown digest file in digests/

Run locally:
    python src/main.py

Called automatically by GitHub Actions every day at 7am UTC.
"""

import sys
import os

# Allow running as `python src/main.py` from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    RSS_FEEDS,
    SEEN_ARTICLES_FILE,
    DEDUP_WINDOW_DAYS,
    TOP_N,
    MAX_PER_SOURCE,
    DIGESTS_DIR,
)
from src.fetcher import fetch_all_feeds
from src.deduplicator import get_new_articles
from src.scorer import select_top
from src.renderer import render_digest


def run():
    print("=" * 50)
    print("  Daily AI/ML News Digest")
    print("=" * 50)

    # Step 1: Fetch
    print("\n[1/4] Fetching RSS feeds...")
    articles = fetch_all_feeds(RSS_FEEDS)
    print(f"  Total fetched: {len(articles)}")

    # Step 2: Deduplicate
    print("\n[2/4] Deduplicating...")
    new_articles = get_new_articles(articles, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS)
    print(f"  New articles:  {len(new_articles)}")

    if not new_articles:
        print("\nNothing new today. Exiting.")
        return

    # Step 3: Score and select
    print(f"\n[3/4] Selecting top {TOP_N}...")
    top = select_top(new_articles, TOP_N, MAX_PER_SOURCE)

    if not top:
        print("\nNo articles passed scoring. Exiting.")
        return

    # Step 4: Render
    print("\n[4/4] Rendering digest...")
    path = render_digest(top, DIGESTS_DIR)

    print(f"\nDone! Digest saved to: {path}")
    print("=" * 50)


if __name__ == "__main__":
    run()

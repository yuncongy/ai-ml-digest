"""
main.py — Weekly AI/ML news digest pipeline.

Every day (via GitHub Actions):
  1. Fetch new articles from RSS feeds
  2. Deduplicate against seen_articles.json
  3. Add new articles to weekly_pool.json

On SEND_DAY (configured in config.py):
  4. Pick the top N articles from the pool
  5. Send an HTML email via Gmail
  6. Clear the pool for the next week

Run locally:
    python src/main.py

Called automatically by GitHub Actions every day at 7 AM UTC.
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import (
    ENABLED,
    SEND_DAY,
    RSS_FEEDS,
    SEEN_ARTICLES_FILE,
    WEEKLY_POOL_FILE,
    DEDUP_WINDOW_DAYS,
    TOP_N,
    MAX_PER_SOURCE,
    EMAIL_TO,
    EMAIL_FROM,
    EMAIL_SUBJECT,
)
from src.fetcher import fetch_all_feeds
from src.deduplicator import get_new_articles
from src.scorer import select_top
from src.emailer import send_email


# ─── Weekly pool helpers ──────────────────────────────────────────────────────

def _load_pool_raw(filepath: str) -> list[dict]:
    """Load the pool as raw dicts (published stored as ISO string)."""
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r") as f:
        return json.load(f)


def _save_pool_raw(pool: list[dict], filepath: str) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(pool, f, indent=2, default=str)


def add_to_pool(new_articles: list[dict], filepath: str) -> int:
    """Append new articles to the weekly pool. Returns number added."""
    pool = _load_pool_raw(filepath)
    existing_urls = {a["url"] for a in pool}
    added = 0
    for article in new_articles:
        if article["url"] not in existing_urls:
            a = dict(article)
            a["published"] = article["published"].isoformat()
            pool.append(a)
            added += 1
    _save_pool_raw(pool, filepath)
    print(f"  [pool] Added {added} article(s). Pool size: {len(pool)}")
    return added


def load_pool(filepath: str) -> list[dict]:
    """Load the pool with published converted back to datetime objects."""
    raw = _load_pool_raw(filepath)
    for a in raw:
        a["published"] = datetime.fromisoformat(a["published"])
    return raw


def clear_pool(filepath: str) -> None:
    _save_pool_raw([], filepath)
    print("  [pool] Pool cleared for next week.")


# ─── Main pipeline ────────────────────────────────────────────────────────────

def run():
    print("=" * 50)
    print("  Weekly AI/ML News Digest")
    print("=" * 50)

    if not ENABLED:
        print("\nService is DISABLED. Set ENABLED = True in config.py to re-enable.")
        return

    today = datetime.now(timezone.utc).strftime("%A").lower()  # e.g. "monday"
    is_send_day = today == SEND_DAY.lower()

    print(f"\n  Today: {today.capitalize()}  |  Send day: {SEND_DAY.capitalize()}")

    # Step 1: Fetch
    print("\n[1/3] Fetching RSS feeds...")
    articles = fetch_all_feeds(RSS_FEEDS)
    print(f"  Fetched: {len(articles)}")

    # Step 2: Deduplicate
    print("\n[2/3] Deduplicating...")
    new_articles = get_new_articles(articles, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS)

    # Step 3: Add to weekly pool
    print("\n[3/3] Updating weekly pool...")
    if new_articles:
        add_to_pool(new_articles, WEEKLY_POOL_FILE)
    else:
        print("  [pool] No new articles to add.")

    # ── Send day logic ────────────────────────────────────────────────────────
    if not is_send_day:
        print(f"\nNot send day yet. Articles are accumulating in the pool.")
        print("=" * 50)
        return

    print(f"\n--- It's {SEND_DAY.capitalize()}! Preparing weekly email ---")

    pool = load_pool(WEEKLY_POOL_FILE)
    if not pool:
        print("Pool is empty — nothing to send this week.")
        print("=" * 50)
        return

    top = select_top(pool, TOP_N, MAX_PER_SOURCE)
    if not top:
        print("No articles passed scoring — nothing to send.")
        print("=" * 50)
        return

    print(f"\nSending email with {len(top)} articles to {EMAIL_TO}...")
    send_email(top, EMAIL_TO, EMAIL_FROM, EMAIL_SUBJECT)

    clear_pool(WEEKLY_POOL_FILE)

    print(f"\nDone! Weekly digest sent to {EMAIL_TO}")
    print("=" * 50)


if __name__ == "__main__":
    run()

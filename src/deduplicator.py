"""
deduplicator.py — Track seen article URLs so we never include the same
article twice within the deduplication window.

Storage format (seen_articles.json):
    {
        "https://example.com/article": "2026-04-24T10:00:00+00:00",
        ...
    }

Each key is an article URL; the value is the ISO-8601 UTC timestamp of
when that URL was first seen. Entries older than DEDUP_WINDOW_DAYS are
removed automatically on each run.
"""

import json
import os
from datetime import datetime, timedelta, timezone


# ─── Load / save ──────────────────────────────────────────────────────────────

def load_seen(filepath: str) -> dict[str, str]:
    """
    Load the seen-articles store from disk.

    Returns an empty dict if the file does not exist yet.
    """
    if not os.path.exists(filepath):
        return {}
    with open(filepath, "r") as f:
        return json.load(f)


def save_seen(seen: dict[str, str], filepath: str) -> None:
    """Write the seen-articles store back to disk."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(seen, f, indent=2)


# ─── Expire old entries ───────────────────────────────────────────────────────

def expire_old(seen: dict[str, str], window_days: int) -> dict[str, str]:
    """
    Remove any entries that were first seen more than `window_days` ago.

    Returns a new dict with only the still-valid entries.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    fresh = {}

    for url, timestamp_str in seen.items():
        first_seen = datetime.fromisoformat(timestamp_str)
        if first_seen >= cutoff:
            fresh[url] = timestamp_str

    removed = len(seen) - len(fresh)
    if removed:
        print(f"  [dedup] Expired {removed} old article(s) from store")

    return fresh


# ─── Filter and record ────────────────────────────────────────────────────────

def filter_new(
    articles: list[dict],
    seen: dict[str, str],
) -> tuple[list[dict], dict[str, str]]:
    """
    Split `articles` into new (not yet seen) and already-seen.

    Also records each new article's URL in `seen` with the current timestamp
    so it won't appear in future digests.

    Returns:
        new_articles : list of article dicts that are new
        updated_seen : the seen dict with new URLs added
    """
    now = datetime.now(timezone.utc).isoformat()
    new_articles = []

    for article in articles:
        url = article["url"]
        if url in seen:
            continue                          # already sent before
        new_articles.append(article)
        seen[url] = now                       # mark as seen right now

    print(
        f"  [dedup] {len(new_articles)} new / "
        f"{len(articles) - len(new_articles)} already seen"
    )
    return new_articles, seen


# ─── Convenience wrapper ──────────────────────────────────────────────────────

def get_new_articles(
    articles: list[dict],
    filepath: str,
    window_days: int,
) -> list[dict]:
    """
    Full dedup pipeline in one call:
      1. Load the seen store
      2. Expire old entries
      3. Filter out already-seen articles
      4. Save the updated store

    Returns the list of articles that are new (never seen before).
    """
    seen = load_seen(filepath)
    seen = expire_old(seen, window_days)
    new_articles, seen = filter_new(articles, seen)
    save_seen(seen, filepath)
    return new_articles


# ─── Quick smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from config import RSS_FEEDS, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS
    from src.fetcher import fetch_all_feeds

    print("Fetching feeds...\n")
    articles = fetch_all_feeds(RSS_FEEDS)

    print(f"\nRunning deduplication (window = {DEDUP_WINDOW_DAYS} days)...")
    new_articles = get_new_articles(articles, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS)

    print(f"\nNew articles after dedup: {len(new_articles)}")
    for a in new_articles[:3]:
        print(f"  - {a['source']}: {a['title']}")

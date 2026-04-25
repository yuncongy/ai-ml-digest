"""
fetcher.py — Fetch and parse RSS feeds into a normalized article list.

Each article is returned as a plain dict with these keys:
    title     : str   — headline
    url       : str   — link to the full article
    source    : str   — human-readable feed name (from config)
    published : datetime (UTC) — when the article was published
    excerpt   : str   — short plain-text summary (up to 300 chars)
"""

import html
import re
from datetime import datetime, timezone

import feedparser


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _strip_html(text: str) -> str:
    """Remove HTML tags and decode HTML entities from a string."""
    text = re.sub(r"<[^>]+>", "", text)
    return html.unescape(text).strip()


def _parse_published(entry) -> datetime:
    """
    Extract the published datetime from a feedparser entry.
    Falls back to the current time if the field is missing or unparseable.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


# ─── Core functions ───────────────────────────────────────────────────────────

def fetch_feed(source: dict) -> list[dict]:
    """
    Fetch and parse a single RSS feed.

    Args:
        source: a dict with 'name' and 'url' keys (from config.RSS_FEEDS)

    Returns:
        A list of normalized article dicts.
    """
    feed = feedparser.parse(source["url"])
    articles = []

    for entry in feed.entries:
        title = entry.get("title", "").strip()
        url = entry.get("link", "").strip()

        # Skip entries that are missing the two most important fields
        if not title or not url:
            continue

        raw_summary = entry.get("summary", "") or entry.get("description", "")
        excerpt = _strip_html(raw_summary)[:300]

        articles.append(
            {
                "title": title,
                "url": url,
                "source": source["name"],
                "published": _parse_published(entry),
                "excerpt": excerpt,
            }
        )

    return articles


def fetch_all_feeds(feeds: list[dict]) -> list[dict]:
    """
    Fetch every feed in the list and combine results into one article list.

    Failed feeds are skipped with a printed warning so one bad feed
    does not abort the whole run.

    Args:
        feeds: list of source dicts (config.RSS_FEEDS)

    Returns:
        Combined list of article dicts from all feeds.
    """
    all_articles = []

    for source in feeds:
        try:
            articles = fetch_feed(source)
            print(f"  [ok] {source['name']}: {len(articles)} articles fetched")
            all_articles.extend(articles)
        except Exception as exc:
            print(f"  [skip] {source['name']}: {exc}")

    return all_articles


# ─── Quick smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")          # make sure project root is on the path
    from config import RSS_FEEDS

    print("Fetching feeds...\n")
    articles = fetch_all_feeds(RSS_FEEDS)

    print(f"\nTotal articles fetched: {len(articles)}")
    print("\n--- First 3 articles ---")
    for article in articles[:3]:
        print(f"\nTitle  : {article['title']}")
        print(f"Source : {article['source']}")
        print(f"URL    : {article['url']}")
        print(f"Date   : {article['published']}")
        print(f"Excerpt: {article['excerpt'][:120]}...")

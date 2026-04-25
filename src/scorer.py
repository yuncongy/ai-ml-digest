"""
scorer.py — Rank articles and select the top N for the digest.

Scoring strategy (no LLM needed):
  1. Sort all articles by published date, newest first.
  2. Walk the sorted list and pick articles greedily, skipping any source
     that has already contributed MAX_PER_SOURCE articles to the selection.
  3. Stop once TOP_N articles are chosen.

This guarantees recency while preventing one high-volume source (e.g. ArXiv)
from crowding out everything else.
"""

from collections import defaultdict


def select_top(
    articles: list[dict],
    top_n: int,
    max_per_source: int,
) -> list[dict]:
    """
    Return the top `top_n` articles ranked by recency with source diversity.

    Args:
        articles      : list of article dicts (must have 'published' and 'source')
        top_n         : how many articles to return
        max_per_source: max articles allowed from any single source

    Returns:
        Ordered list of up to `top_n` article dicts, newest first.
    """
    # Sort newest-first so we always prefer the most recent articles
    sorted_articles = sorted(articles, key=lambda a: a["published"], reverse=True)

    selected = []
    source_counts = defaultdict(int)   # track how many picks each source has

    for article in sorted_articles:
        if len(selected) >= top_n:
            break

        source = article["source"]
        if source_counts[source] >= max_per_source:
            continue                   # this source already has its quota

        selected.append(article)
        source_counts[source] += 1

    print(f"  [scorer] Selected {len(selected)} articles from {len(source_counts)} sources")
    return selected


# ─── Quick smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from config import RSS_FEEDS, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS, TOP_N, MAX_PER_SOURCE
    from src.fetcher import fetch_all_feeds
    from src.deduplicator import get_new_articles

    print("Fetching feeds...\n")
    articles = fetch_all_feeds(RSS_FEEDS)

    print(f"\nDeduplicating...")
    new_articles = get_new_articles(articles, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS)

    print(f"\nSelecting top {TOP_N} (max {MAX_PER_SOURCE} per source)...")
    top = select_top(new_articles, TOP_N, MAX_PER_SOURCE)

    print(f"\n--- Top {len(top)} articles ---")
    for i, a in enumerate(top, 1):
        print(f"\n{i}. [{a['source']}] {a['title']}")
        print(f"   {a['url']}")
        print(f"   Published: {a['published']}")

"""
renderer.py — Render the selected articles as a daily markdown digest file.

Output file: digests/YYYY-MM-DD.md

Each digest contains:
  - A header with the date
  - One numbered section per article: title, source, link, and excerpt
  - A footer with generation timestamp
"""

import os
from datetime import datetime, timezone


# ─── Markdown builder ─────────────────────────────────────────────────────────

def render_digest(articles: list[dict], digests_dir: str) -> str:
    """
    Write a markdown digest for today's top articles.

    Args:
        articles    : ordered list of article dicts (from scorer.select_top)
        digests_dir : directory where .md files are saved (from config)

    Returns:
        The full path of the written file.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filename = os.path.join(digests_dir, f"{today}.md")

    lines = _build_markdown(articles, today)

    os.makedirs(digests_dir, exist_ok=True)
    with open(filename, "w") as f:
        f.write("\n".join(lines))

    print(f"  [renderer] Digest written to {filename}")
    return filename


def _build_markdown(articles: list[dict], date_str: str) -> list[str]:
    """Build the markdown lines for the digest."""
    lines = []

    # Header
    lines += [
        f"# AI/ML News Digest — {date_str}",
        "",
        f"> {len(articles)} stories selected from across the web.",
        "",
        "---",
        "",
    ]

    # One section per article
    for i, article in enumerate(articles, 1):
        title   = article["title"]
        source  = article["source"]
        url     = article["url"]
        excerpt = article["excerpt"]
        pub     = article["published"].strftime("%Y-%m-%d %H:%M UTC")

        lines += [
            f"## {i}. {title}",
            "",
            f"**Source:** {source} &nbsp;|&nbsp; **Published:** {pub}",
            "",
            f"**Link:** [{url}]({url})",
            "",
        ]

        if excerpt:
            lines += [
                f"> {excerpt}",
                "",
            ]

        lines += ["---", ""]

    # Footer
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines += [
        f"*Generated on {generated_at}*",
    ]

    return lines


# ─── Quick smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from config import (
        RSS_FEEDS, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS,
        TOP_N, MAX_PER_SOURCE, DIGESTS_DIR,
    )
    from src.fetcher import fetch_all_feeds
    from src.deduplicator import get_new_articles
    from src.scorer import select_top

    print("Fetching feeds...\n")
    articles = fetch_all_feeds(RSS_FEEDS)

    print("\nDeduplicating...")
    new_articles = get_new_articles(articles, SEEN_ARTICLES_FILE, DEDUP_WINDOW_DAYS)

    print(f"\nScoring (top {TOP_N}, max {MAX_PER_SOURCE} per source)...")
    top = select_top(new_articles, TOP_N, MAX_PER_SOURCE)

    if not top:
        print("\nNo new articles today — nothing to render.")
        sys.exit(0)

    print("\nRendering digest...")
    path = render_digest(top, DIGESTS_DIR)

    print(f"\nDone! Open {path} to review.")

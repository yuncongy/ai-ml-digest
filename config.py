# ─── Digest settings ──────────────────────────────────────────────────────────

TOP_N = 5                  # Number of articles to include in each digest
DEDUP_WINDOW_DAYS = 7      # How many days to remember a seen article

# ─── RSS feed sources ─────────────────────────────────────────────────────────

RSS_FEEDS = [
    {
        "name": "Hacker News (AI)",
        "url": "https://hnrss.org/newest?q=AI+machine+learning+LLM",
    },
    {
        "name": "ArXiv cs.AI",
        "url": "https://arxiv.org/rss/cs.AI",
    },
    {
        "name": "ArXiv cs.LG",
        "url": "https://arxiv.org/rss/cs.LG",
    },
    {
        "name": "MIT Tech Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed/",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    },
    {
        "name": "VentureBeat AI",
        "url": "https://venturebeat.com/category/ai/feed/",
    },
]

# ─── File paths ───────────────────────────────────────────────────────────────

DATA_DIR = "data"
DIGESTS_DIR = "digests"
SEEN_ARTICLES_FILE = f"{DATA_DIR}/seen_articles.json"

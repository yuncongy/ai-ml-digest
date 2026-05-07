# ─── Service toggle ───────────────────────────────────────────────────────────

ENABLED = True          # Set to False to pause the service without removing anything

# ─── Schedule settings ────────────────────────────────────────────────────────

SEND_DAY = "monday"     # Which day of the week to send the digest email
                        # Options: monday  tuesday  wednesday  thursday
                        #          friday  saturday  sunday
# Note: send TIME is controlled by the cron line in .github/workflows/daily_digest.yml

# ─── Digest settings ──────────────────────────────────────────────────────────

TOP_N            = 10   # Articles per weekly digest
DEDUP_WINDOW_DAYS = 7   # Days to remember a seen article (prevents repeats across weeks)
MAX_PER_SOURCE   = 3    # Max articles from any single source in one digest

# ─── Email settings ───────────────────────────────────────────────────────────

EMAIL_TO      = "17yuyuncong@gmail.com"
EMAIL_FROM    = "17yuyuncong@gmail.com"
EMAIL_SUBJECT = "Weekly AI/ML News Digest"
# GMAIL_USER and GMAIL_APP_PASSWORD are read from environment variables.
# Set them as GitHub Actions secrets (Settings → Secrets → Actions).

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

DATA_DIR           = "data"
SEEN_ARTICLES_FILE = f"{DATA_DIR}/seen_articles.json"
WEEKLY_POOL_FILE   = f"{DATA_DIR}/weekly_pool.json"

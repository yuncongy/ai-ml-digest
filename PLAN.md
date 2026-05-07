# Daily AI/ML News Digest — Project Plan

## Overview

A weekly AI/ML news digest that collects articles from RSS feeds throughout the week, then emails the top 10 stories every Monday (configurable). Runs automatically via GitHub Actions — no computer needs to stay on, no git pulls needed.

**Core flow:**
```
Daily: Fetch RSS feeds → Deduplicate → Add to weekly_pool.json → Commit data/
Monday: Pick top 10 from pool → Send HTML email → Clear pool
```

---

## Requirements

- Python + conda environment
- RSS/news sources only (no paid APIs)
- No AI summarization — include title, source, link, and excerpt
- Output: HTML email sent via Gmail SMTP on the configured send day
- Deduplication: remember seen articles for 7 days (JSON store)
- Top 10 articles per weekly digest
- Scheduled via GitHub Actions (daily cron to accumulate, email on send day)
- `ENABLED` toggle and `SEND_DAY` setting in `config.py`

---

## Default RSS Sources

| Source | Feed URL |
|---|---|
| Hacker News (AI filter) | `https://hnrss.org/newest?q=AI+machine+learning+LLM` |
| ArXiv cs.AI | `https://arxiv.org/rss/cs.AI` |
| ArXiv cs.LG | `https://arxiv.org/rss/cs.LG` |
| MIT Tech Review AI | `https://www.technologyreview.com/topic/artificial-intelligence/feed/` |
| The Verge AI | `https://www.theverge.com/rss/ai-artificial-intelligence/index.xml` |
| VentureBeat AI | `https://venturebeat.com/category/ai/feed/` |

---

## File Structure

```
daily_news/
├── .github/
│   └── workflows/
│       └── daily_digest.yml    # GitHub Actions: runs daily, emails on SEND_DAY
├── src/
│   ├── fetcher.py              # Fetch & parse RSS feeds
│   ├── deduplicator.py         # Track seen articles, expire after 7 days
│   ├── scorer.py               # Rank articles by recency + source diversity
│   ├── emailer.py              # Build HTML email + send via Gmail SMTP
│   └── main.py                 # Orchestrates the weekly pipeline
├── data/
│   ├── seen_articles.json      # Dedup store (committed to repo)
│   └── weekly_pool.json        # Articles accumulated this week (committed to repo)
├── config.py                   # Settings: ENABLED, SEND_DAY, email, RSS feeds
├── requirements.txt
├── environment.yml             # Conda env definition
└── README.md
```

---

## Milestones

| # | Milestone | Deliverable | Status |
|---|---|---|---|
| M1 | Project setup | Conda env, folder structure, `config.py`, `requirements.txt` | [x] |
| M2 | RSS fetcher | `fetcher.py` — fetch all feeds, return normalized article list | [x] |
| M3 | Deduplication | `deduplicator.py` — JSON store, skip seen URLs, expire after 7 days | [x] |
| M4 | Scoring & selection | `scorer.py` — rank by recency + source diversity, return top 5 | [x] |
| M5 | Markdown renderer | `renderer.py` — produce `digests/YYYY-MM-DD.md` with title, source, link, excerpt | [x] |
| M6 | GitHub Actions | `.github/workflows/daily_digest.yml` — runs at 7am UTC daily, commits digest | [x] |
| M7 | Gmail delivery + weekly schedule | `emailer.py` — HTML email via Gmail SMTP; weekly pool accumulation; ENABLED toggle; SEND_DAY config | [x] |

---

## Notes & Decisions

- `seen_articles.json` is committed to the repo so GitHub Actions can persist dedup state across runs.
- `weekly_pool.json` accumulates article dicts Monday–Sunday; cleared after sending.
- Scoring uses recency + source diversity (no LLM needed).
- Gmail uses App Passwords via GitHub Actions secrets — no OAuth needed.
- To pause: set `ENABLED = False` in `config.py` and push.
- To change send day: edit `SEND_DAY` in `config.py` and push.
- To change send time: edit the cron hour in `.github/workflows/daily_digest.yml` and push.

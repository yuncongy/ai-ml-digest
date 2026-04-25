# Daily AI/ML News Digest — Project Plan

## Overview

A daily AI/ML news update system that collects recent machine learning and AI news from RSS feeds, picks the top 5 most relevant items, and writes a markdown digest file. Runs automatically via GitHub Actions so no computer needs to stay on.

**Core flow:**
```
Fetch RSS feeds → Deduplicate against seen.json → Score & pick top 5 → Write daily .md digest → Commit via GitHub Actions
```

---

## Requirements

- Python + conda environment
- RSS/news sources only (no paid APIs)
- No AI summarization in MVP — include title, source, link, and excerpt
- Output: one `.md` file per day in `digests/`
- Deduplication: remember seen articles for 7 days (JSON store)
- Top 5 articles per digest
- Scheduled daily via GitHub Actions (no need to keep Mac on)
- Future: Gmail delivery

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
│       └── daily_digest.yml    # GitHub Actions cron job
├── src/
│   ├── fetcher.py              # Fetch & parse RSS feeds
│   ├── deduplicator.py         # Track seen articles, expire after 7 days
│   ├── scorer.py               # Rank articles, pick top 5
│   ├── renderer.py             # Generate markdown digest
│   └── main.py                 # Orchestrates everything
├── data/
│   └── seen_articles.json      # Persisted dedup store (committed to repo)
├── digests/
│   └── YYYY-MM-DD.md           # One file per day, committed by Actions
├── config.py                   # RSS feed list, settings (top_n, window_days)
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
| M4 | Scoring & selection | `scorer.py` — rank by recency + source diversity, return top 5 | [ ] |
| M5 | Markdown renderer | `renderer.py` — produce `digests/YYYY-MM-DD.md` with title, source, link, excerpt | [ ] |
| M6 | GitHub Actions | `.github/workflows/daily_digest.yml` — runs at 7am UTC daily, commits digest | [ ] |
| M7 *(future)* | Gmail delivery | Replace/extend renderer to send HTML email via Gmail SMTP | [ ] |

---

## Notes & Decisions

- `seen_articles.json` is committed to the repo so GitHub Actions can persist dedup state across runs.
- Scoring in M4 uses recency + source diversity (no LLM needed).
- Gmail (M7) will use app passwords via GitHub Actions secrets — no OAuth needed for MVP.

# AI/ML Weekly Digest — Guide

Collects AI/ML news from RSS feeds all week, then emails you a digest every Monday.
Runs on GitHub Actions — nothing needs to stay on.

---

## How it works

Every day at 7 AM UTC, GitHub Actions runs and:
1. Fetches articles from 6 RSS feeds
2. Skips anything seen in the last 7 days
3. Saves new articles to `data/weekly_pool.json`

On Monday (or whichever day you set), it also:
4. Picks the top 10 articles from the pool
5. Sends you an HTML email via Gmail
6. Clears the pool for the next week

---

## Settings — `config.py`

| Setting | Default | What it does |
|---|---|---|
| `ENABLED` | `True` | Set to `False` to pause the service |
| `SEND_DAY` | `"monday"` | Which day to send the email |
| `TOP_N` | `10` | Number of articles per digest |
| `MAX_PER_SOURCE` | `3` | Max articles from any one source |
| `DEDUP_WINDOW_DAYS` | `7` | How long to remember a seen article |
| `EMAIL_TO` | your Gmail | Where the digest is sent |
| `EMAIL_SUBJECT` | `"Weekly AI/ML News Digest"` | Email subject line |

**To change send day:** edit `SEND_DAY = "friday"` (any lowercase weekday) and push.

**To change send time:** edit the cron line in `.github/workflows/daily_digest.yml`:
```yaml
- cron: "0 7 * * *"   # hour is 0–23 UTC
```

**To pause:** set `ENABLED = False` in `config.py` and push.

---

## One-time setup: Gmail secrets

The service needs a Gmail App Password (not your account password).

1. Go to: **Google Account → Security → 2-Step Verification → App passwords**
2. Create one and copy it
3. Go to your GitHub repo → **Settings → Secrets and variables → Actions**
4. Add two secrets:
   - `GMAIL_USER` → your Gmail address
   - `GMAIL_APP_PASSWORD` → the 16-character app password

Without these, the workflow will fail when it tries to send.

---

## Run locally

```bash
conda activate daily_news
python src/main.py
```

It will accumulate articles into the pool on non-send days, and send the email on the send day.

---

## Key files

| File | Purpose |
|---|---|
| `config.py` | All settings |
| `src/main.py` | Pipeline: fetch → dedup → pool → email |
| `src/emailer.py` | Builds HTML email and sends via Gmail SMTP |
| `src/fetcher.py` | Fetches RSS feeds |
| `src/scorer.py` | Ranks articles by recency + source diversity |
| `data/seen_articles.json` | Dedup store (auto-managed) |
| `data/weekly_pool.json` | This week's accumulated articles (auto-managed) |
| `.github/workflows/daily_digest.yml` | GitHub Actions schedule and secrets |

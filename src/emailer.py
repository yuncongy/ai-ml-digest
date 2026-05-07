"""
emailer.py — Build an HTML email digest and send it via Gmail SMTP.

Requires two environment variables (set as GitHub Actions secrets):
    GMAIL_USER         — your Gmail address (e.g. you@gmail.com)
    GMAIL_APP_PASSWORD — a Gmail App Password (not your account password)

How to create an App Password:
    Google Account → Security → 2-Step Verification → App passwords
"""

import os
import smtplib
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# ─── HTML builder ─────────────────────────────────────────────────────────────

def build_html(articles: list[dict], subject: str) -> str:
    """Return a complete HTML email string for the given articles."""
    now = datetime.now(timezone.utc)
    date_str = now.strftime("%B %d, %Y")

    article_blocks = ""
    for i, a in enumerate(articles, 1):
        title   = _esc(a["title"])
        source  = _esc(a["source"])
        url     = a["url"]
        excerpt = _esc(a.get("excerpt") or "")
        pub     = a["published"].strftime("%b %d, %Y")

        article_blocks += f"""
        <div class="article">
          <h2><a href="{url}">{i}. {title}</a></h2>
          <div class="meta">{source} &nbsp;·&nbsp; {pub}</div>
          {"<p class='excerpt'>" + excerpt + "</p>" if excerpt else ""}
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  body      {{ font-family: Georgia, 'Times New Roman', serif; max-width: 680px;
               margin: 40px auto; padding: 0 20px; color: #222; background: #fff; }}
  h1        {{ font-size: 24px; border-bottom: 3px solid #0055cc; padding-bottom: 12px;
               color: #0055cc; }}
  .subtitle {{ color: #555; font-size: 14px; margin-top: -10px; margin-bottom: 30px; }}
  .article  {{ margin: 28px 0; padding: 18px 20px; border-left: 4px solid #0055cc;
               background: #f7f9ff; border-radius: 0 6px 6px 0; }}
  .article h2  {{ margin: 0 0 6px 0; font-size: 17px; line-height: 1.4; }}
  .article h2 a {{ color: #0055cc; text-decoration: none; }}
  .article h2 a:hover {{ text-decoration: underline; }}
  .meta     {{ color: #888; font-size: 13px; margin-bottom: 10px; }}
  .excerpt  {{ font-size: 14px; line-height: 1.7; color: #444; margin: 0; }}
  .footer   {{ margin-top: 40px; padding-top: 14px; border-top: 1px solid #ddd;
               color: #aaa; font-size: 12px; font-family: Arial, sans-serif; }}
</style>
</head>
<body>
  <h1>{subject}</h1>
  <p class="subtitle">{date_str} &nbsp;·&nbsp; {len(articles)} stories this week</p>

  {article_blocks}

  <div class="footer">
    Sent by your Weekly AI/ML News Digest running on GitHub Actions.
    To pause delivery, set <code>ENABLED = False</code> in <code>config.py</code>.
  </div>
</body>
</html>"""


def _esc(text: str) -> str:
    """Minimal HTML escaping for plain-text values."""
    return (text
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


# ─── SMTP sender ──────────────────────────────────────────────────────────────

def send_email(
    articles: list[dict],
    email_to: str,
    email_from: str,
    subject: str,
) -> None:
    """
    Send the weekly digest to email_to via Gmail SMTP.

    Reads GMAIL_USER and GMAIL_APP_PASSWORD from the environment.
    Raises RuntimeError if the credentials are missing.
    """
    gmail_user = os.environ.get("GMAIL_USER", "").strip()
    gmail_pass = os.environ.get("GMAIL_APP_PASSWORD", "").strip()

    if not gmail_user or not gmail_pass:
        raise RuntimeError(
            "GMAIL_USER and GMAIL_APP_PASSWORD environment variables must be set.\n"
            "Add them as GitHub Actions secrets (Settings → Secrets → Actions)."
        )

    html_body = build_html(articles, subject)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = email_from
    msg["To"]      = email_to
    msg.attach(MIMEText(html_body, "html"))

    print(f"  [emailer] Connecting to smtp.gmail.com:587 as {gmail_user}...")
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(gmail_user, gmail_pass)
        smtp.sendmail(email_from, email_to, msg.as_string())

    print(f"  [emailer] Email sent to {email_to}")

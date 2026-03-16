"""
Experiment: Email Daily Summary Agent
Connects to Gmail via IMAP (no Google Cloud needed) and uses Claude
to categorize emails and generate a daily KPI report.
"""
import imaplib
import email
import os
from datetime import datetime
from email.header import decode_header
from dotenv import load_dotenv
import anthropic

load_dotenv()

IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ── IMAP helpers ──────────────────────────────────────────────────────────────

def connect(gmail_address: str, app_password: str) -> imaplib.IMAP4_SSL:
    mail = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
    mail.login(gmail_address, app_password)
    return mail


def decode_str(value: str) -> str:
    parts = decode_header(value)
    result = []
    for part, enc in parts:
        if isinstance(part, bytes):
            result.append(part.decode(enc or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def count_today(mail: imaplib.IMAP4_SSL, folder: str) -> int:
    """Count emails received today in a given folder."""
    try:
        status, _ = mail.select(folder, readonly=True)
        if status != "OK":
            return 0
        today = datetime.now().strftime("%d-%b-%Y")
        _, data = mail.search(None, f'(SINCE "{today}")')
        ids = data[0].split()
        return len(ids)
    except Exception:
        return 0


def fetch_inbox_sample(mail: imaplib.IMAP4_SSL, max_results: int = 20) -> list[dict]:
    """Fetch From + Subject for today's inbox emails."""
    mail.select("INBOX", readonly=True)
    today = datetime.now().strftime("%d-%b-%Y")
    _, data = mail.search(None, f'(SINCE "{today}")')
    ids = data[0].split()[-max_results:]  # most recent N

    sample = []
    for uid in ids:
        _, msg_data = mail.fetch(uid, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)
        sample.append({
            "from": decode_str(msg.get("From", "Unknown")),
            "subject": decode_str(msg.get("Subject", "(no subject)")),
        })
    return sample


def count_unread_today(mail: imaplib.IMAP4_SSL) -> int:
    mail.select("INBOX", readonly=True)
    today = datetime.now().strftime("%d-%b-%Y")
    _, data = mail.search(None, f'(UNSEEN SINCE "{today}")')
    return len(data[0].split())


def fetch_stats(mail: imaplib.IMAP4_SSL) -> dict:
    print("  Counting inbox...")
    inbox = count_today(mail, "INBOX")
    print("  Counting unread...")
    unread = count_unread_today(mail)
    print("  Counting spam...")
    spam = count_today(mail, "[Gmail]/Spam")
    print("  Counting trash...")
    trash = count_today(mail, "[Gmail]/Trash")
    print("  Fetching inbox sample for Claude to categorize...")
    sample = fetch_inbox_sample(mail)

    return {
        "date": datetime.now().strftime("%B %d, %Y"),
        "inbox": inbox,
        "unread": unread,
        "spam": spam,
        "trash": trash,
        "total": inbox + spam,
        "sample": sample,
    }


# ── Claude analysis ───────────────────────────────────────────────────────────

def generate_summary(stats: dict) -> str:
    sample_lines = "\n".join(
        f"  - FROM: {e['from']} | SUBJECT: {e['subject']}"
        for e in stats["sample"]
    ) or "  (no inbox emails today)"

    prompt = f"""Here are my Gmail statistics for today ({stats['date']}):

Raw KPIs:
- Total emails received: {stats['total']}
- In inbox: {stats['inbox']}
- Unread: {stats['unread']}
- Spam (auto-filtered): {stats['spam']}
- Deleted / Trash: {stats['trash']}

Sample of today's inbox emails (From + Subject):
{sample_lines}

Tasks:
1. Categorize the sample emails into: Ads/Promotions, Newsletters, Social, Work/Personal, Notifications, Other
2. Estimate counts per category based on the sample (extrapolate to full inbox if needed)
3. Write a concise end-of-day report with:
   - Overview paragraph (2-3 sentences)
   - KPI table (total, inbox, unread, spam, trash + your category breakdown)
   - Key patterns or observations
   - One actionable recommendation

Keep it sharp and practical."""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="You are a personal email productivity assistant. Analyze email metadata and write clear, concise daily reports.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    gmail_address = os.environ["GMAIL_ADDRESS"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    print("📧  Email Daily Summary Agent")
    print(f"    {datetime.now().strftime('%B %d, %Y — %H:%M')}\n")

    print("→ Connecting to Gmail via IMAP...")
    mail = connect(gmail_address, app_password)

    print("→ Fetching stats...")
    stats = fetch_stats(mail)
    mail.logout()

    print("→ Generating summary with Claude...\n")
    print("=" * 60)
    print(generate_summary(stats))
    print("=" * 60)


if __name__ == "__main__":
    main()

"""
Experiment: Email Daily Summary Agent
Reads Gmail emails and generates a daily KPI report using Claude.
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import anthropic

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
CREDENTIALS_FILE = "credentials/credentials.json"
TOKEN_FILE = "credentials/token.json"

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ── Gmail auth ────────────────────────────────────────────────────────────────

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# ── Data fetching ─────────────────────────────────────────────────────────────

def today_query():
    return f"after:{datetime.now().strftime('%Y/%m/%d')}"


def count_label(service, label: str) -> int:
    result = service.users().messages().list(
        userId="me", q=today_query(), labelIds=[label], maxResults=1
    ).execute()
    return result.get("resultSizeEstimate", 0)


def fetch_inbox_sample(service, max_results: int = 15) -> list[dict]:
    """Fetch metadata (From, Subject) for a sample of today's inbox emails."""
    result = service.users().messages().list(
        userId="me", q=today_query(), labelIds=["INBOX"], maxResults=max_results
    ).execute()
    messages = result.get("messages", [])
    sample = []
    for msg in messages:
        detail = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        sample.append({
            "from": headers.get("From", "Unknown"),
            "subject": headers.get("Subject", "(no subject)"),
        })
    return sample


def fetch_stats(service) -> dict:
    print("  Counting inbox...")
    inbox = count_label(service, "INBOX")
    print("  Counting unread...")
    unread = count_label(service, "UNREAD")
    print("  Counting promotions/ads...")
    promotions = count_label(service, "CATEGORY_PROMOTIONS")
    print("  Counting social...")
    social = count_label(service, "CATEGORY_SOCIAL")
    print("  Counting updates/notifications...")
    updates = count_label(service, "CATEGORY_UPDATES")
    print("  Counting forums...")
    forums = count_label(service, "CATEGORY_FORUMS")
    print("  Counting spam...")
    spam = count_label(service, "SPAM")
    print("  Counting trash...")
    trash = count_label(service, "TRASH")
    print("  Fetching inbox sample...")
    sample = fetch_inbox_sample(service)

    total = inbox + spam + promotions
    return {
        "date": datetime.now().strftime("%B %d, %Y"),
        "total": total,
        "inbox": inbox,
        "unread": unread,
        "promotions": promotions,
        "social": social,
        "updates": updates,
        "forums": forums,
        "spam": spam,
        "trash": trash,
        "sample": sample,
    }


# ── Claude summary ────────────────────────────────────────────────────────────

def generate_summary(stats: dict) -> str:
    sample_lines = "\n".join(
        f"  - [{e['from']}] {e['subject']}" for e in stats["sample"]
    ) or "  (no inbox emails today)"

    prompt = f"""Here are my Gmail statistics for today ({stats['date']}):

KPIs:
- Total emails: {stats['total']}
- Inbox: {stats['inbox']}
- Unread: {stats['unread']}
- Promotions / Ads: {stats['promotions']}
- Social: {stats['social']}
- Updates / Notifications: {stats['updates']}
- Forums: {stats['forums']}
- Spam (auto-filtered): {stats['spam']}
- Deleted / Trash: {stats['trash']}

Sample of today's inbox:
{sample_lines}

Generate a concise end-of-day email report with:
1. A short overview paragraph (2-3 sentences)
2. The KPIs laid out clearly
3. Any notable patterns from the sample (types of senders, recurring topics, etc.)
4. A single actionable recommendation (e.g. how many emails likely need a reply)

Keep it sharp and practical — this is a personal productivity report."""

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="You are a personal email productivity assistant. Write clear, concise daily reports.",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("📧  Email Daily Summary Agent")
    print(f"    {datetime.now().strftime('%B %d, %Y — %H:%M')}\n")

    print("→ Connecting to Gmail...")
    service = get_gmail_service()

    print("→ Fetching stats...")
    stats = fetch_stats(service)

    print("→ Generating summary with Claude...\n")
    print("=" * 60)
    print(generate_summary(stats))
    print("=" * 60)


if __name__ == "__main__":
    main()

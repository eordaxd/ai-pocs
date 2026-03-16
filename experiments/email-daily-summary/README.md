# Experiment: Email Daily Summary Agent

## What
Connects to Gmail via IMAP (no Google Cloud Console needed) and uses Claude to categorize emails and generate a concise end-of-day KPI report.

## Why
Automate the daily email triage — know at a glance how noisy your inbox is and what actually needs attention.

## KPIs tracked
- Total emails received
- Inbox / Unread
- Spam (auto-filtered)
- Deleted / Trash
- Claude-categorized breakdown: Ads, Newsletters, Social, Work/Personal, Notifications

## Setup

### 1. Install dependencies
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Create a Gmail App Password
No Google Cloud Console needed — just an App Password from your Gmail account:

1. Go to [myaccount.google.com/security](https://myaccount.google.com/security)
2. Make sure **2-Step Verification** is enabled
3. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
4. Click **Create** → name it (e.g. "email-agent") → copy the 16-character password

### 3. Set up your .env
```bash
cp .env.example .env
```

Edit `.env` and fill in:
```
ANTHROPIC_API_KEY=sk-ant-...
GMAIL_ADDRESS=you@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
```

### 4. Run
```bash
python3 main.py
```

## Results / Findings
<!-- Fill in after running -->

# Experiment: Email Daily Summary Agent

## What
Connects to Gmail, counts emails by category (inbox, spam, ads, trash, etc.) and uses Claude to generate a concise end-of-day KPI report.

## Why
Automate the daily email triage — know at a glance how noisy your inbox is and what actually needs attention.

## KPIs tracked
- Total emails received
- Inbox / Unread
- Promotions & Ads
- Social notifications
- Updates & system notifications
- Forums
- Spam (auto-filtered)
- Deleted / Trash

## Setup

### 1. Install dependencies
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Set your Anthropic API key
```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Set up Gmail API credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project (or select an existing one)
3. Go to **APIs & Services → Library** → enable **Gmail API**
4. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**
5. Choose **Desktop app**, click Create
6. Download the JSON and save it as `credentials/credentials.json`

> The first run opens a browser to authorize access. A `token.json` is saved and reused automatically after that.

### 4. Run
```bash
python3 main.py
```

## Results / Findings
<!-- Fill in after running -->

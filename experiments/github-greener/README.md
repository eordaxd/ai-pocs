# Experiment: Github Greener

## What

Automatically makes a daily commit and push to keep your GitHub contributions graph green.

## Why

A greener GitHub profile signals consistent activity to external visitors. This experiment automates a small daily commit so you never miss a day.

## How to Run

### One-time setup

```bash
cd experiments/github-greener
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Test it manually first
python main.py
```

### Automate daily (macOS)

```bash
# Install the LaunchAgent (runs daily at 10:00 AM)
python setup_scheduler.py install

# Check status
python setup_scheduler.py status

# Uninstall
python setup_scheduler.py uninstall
```

## How It Works

1. Appends today's date + a random dev tip to `contributions/daily_log.md`
2. Commits with a meaningful message
3. Pushes to the `main` branch on GitHub
4. Logs results to `logs/greener.log`

## Results / Findings

Running since initial setup. Check `contributions/daily_log.md` for the history.

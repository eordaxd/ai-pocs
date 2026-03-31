"""
Github Greener — daily commit bot to keep your contributions graph green.

Usage:
    python main.py          # run once (commit + push today's entry)
    python main.py --dry    # preview without committing
"""

import os
import subprocess
import sys
import random
import logging
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent.parent  # ai-pocs root
CONTRIB_DIR = REPO_ROOT / "experiments" / "github-greener" / "contributions"
LOG_DIR = REPO_ROOT / "experiments" / "github-greener" / "logs"
DAILY_LOG = CONTRIB_DIR / "daily_log.md"
BRANCH = "main"

# Dev tips / quotes that rotate through the log entries
TIPS = [
    "Keep functions small and focused on a single task.",
    "Write tests before fixing bugs to prevent regressions.",
    "Use meaningful variable names — future you will thank you.",
    "Refactor early and often; tech debt compounds.",
    "Code reviews are a learning opportunity, not a gatekeeping exercise.",
    "Document the 'why', not the 'what' — the code shows the what.",
    "Automate repetitive tasks to free up creative energy.",
    "Ship small increments; big PRs are hard to review.",
    "Measure before you optimize.",
    "Learn one new keyboard shortcut every week.",
    "Good error messages save hours of debugging.",
    "Prefer composition over inheritance.",
    "Delete dead code — version control remembers it for you.",
    "Take breaks; debugging with fresh eyes is a superpower.",
    "Read other people's code to expand your toolkit.",
    "Keep dependencies up to date to avoid security surprises.",
    "Profile before you optimize — intuition lies about bottlenecks.",
    "Treat logs as a first-class feature, not an afterthought.",
    "Version your APIs from day one.",
    "Use feature flags to decouple deployment from release.",
    "Embrace the UNIX philosophy: do one thing well.",
    "Immutable data structures prevent entire classes of bugs.",
    "A failing test is more valuable than no test at all.",
    "Pair programming accelerates knowledge sharing.",
    "Security is a feature, not a phase.",
    "Design for observability: metrics, logs, and traces.",
    "Continuous integration catches problems while context is fresh.",
    "Master your debugger — print statements only get you so far.",
    "Build for accessibility from the start, not as a retrofit.",
    "The best code is the code you don't have to write.",
    "Progress over perfection — ship and iterate.",
]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "greener.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("github-greener")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def git(*args: str) -> str:
    """Run a git command inside the repo root and return stdout."""
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        log.error("git %s failed: %s", " ".join(args), result.stderr.strip())
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def already_committed_today() -> bool:
    """Check if there's already an entry for today in the daily log."""
    if not DAILY_LOG.exists():
        return False
    marker = f"## {today_str()}"
    return marker in DAILY_LOG.read_text()


def append_daily_entry() -> str:
    """Append today's entry to the daily log. Returns the tip used."""
    CONTRIB_DIR.mkdir(parents=True, exist_ok=True)

    tip = random.choice(TIPS)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    entry = f"\n## {today_str()}\n\n> {tip}\n\n_Logged at {now}_\n"

    # Create file with header if it doesn't exist
    if not DAILY_LOG.exists():
        DAILY_LOG.write_text(
            "# Daily Dev Tips\n\n"
            "A new tip every day — powered by Github Greener.\n"
        )

    with open(DAILY_LOG, "a") as f:
        f.write(entry)

    return tip


def commit_and_push(dry: bool = False) -> None:
    """Stage, commit, and push the daily log update."""
    rel_path = DAILY_LOG.relative_to(REPO_ROOT)

    if dry:
        log.info("[DRY RUN] Would commit and push %s", rel_path)
        return

    git("add", str(rel_path))
    msg = f"daily: dev tip for {today_str()}"
    git("commit", "-m", msg)
    git("push", "origin", BRANCH)
    log.info("Pushed: %s", msg)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    dry = "--dry" in sys.argv

    log.info("Github Greener starting (dry=%s)", dry)

    if already_committed_today() and not dry:
        log.info("Already committed today (%s). Skipping.", today_str())
        return

    tip = append_daily_entry()
    log.info("Today's tip: %s", tip)

    commit_and_push(dry=dry)
    log.info("Done!")


if __name__ == "__main__":
    main()

"""
Setup / manage the macOS LaunchAgent for Github Greener.

Usage:
    python setup_scheduler.py install    # create & load the daily job
    python setup_scheduler.py uninstall  # remove the daily job
    python setup_scheduler.py status     # show current state
"""

import os
import sys
import subprocess
import plistlib
from pathlib import Path

LABEL = "com.github-greener.daily"
PLIST_PATH = Path.home() / "Library" / "LaunchAgents" / f"{LABEL}.plist"
SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON = SCRIPT_DIR / ".venv" / "bin" / "python"
MAIN_PY = SCRIPT_DIR / "main.py"
LOG_DIR = SCRIPT_DIR / "logs"


def build_plist() -> dict:
    """Build the LaunchAgent plist dictionary."""
    return {
        "Label": LABEL,
        "ProgramArguments": [str(PYTHON), str(MAIN_PY)],
        "RunAtLoad": True,  # run immediately on login / wake
        "StartInterval": 14400,  # also retry every 4 hours as fallback
        "StandardOutPath": str(LOG_DIR / "launchd_stdout.log"),
        "StandardErrorPath": str(LOG_DIR / "launchd_stderr.log"),
        "WorkingDirectory": str(SCRIPT_DIR),
        "EnvironmentVariables": {
            "PATH": "/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin",
            "HOME": str(Path.home()),
        },
    }


def install():
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    if not PYTHON.exists():
        print(f"ERROR: Virtual env not found at {PYTHON}")
        print("Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)

    plist = build_plist()
    PLIST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(plist, f)

    # Unload first in case it's already loaded
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    result = subprocess.run(["launchctl", "load", str(PLIST_PATH)], capture_output=True, text=True)

    if result.returncode == 0:
        print(f"Installed and loaded: {PLIST_PATH}")
        print("Github Greener will run on every login/wake and retry every 4 hours.")
        print(f"\nTo test now: {PYTHON} {MAIN_PY}")
    else:
        print(f"Failed to load: {result.stderr}")
        sys.exit(1)


def uninstall():
    if PLIST_PATH.exists():
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
        PLIST_PATH.unlink()
        print(f"Uninstalled: {PLIST_PATH}")
    else:
        print("Not installed.")


def status():
    result = subprocess.run(
        ["launchctl", "list"],
        capture_output=True, text=True,
    )
    found = [line for line in result.stdout.splitlines() if LABEL in line]
    if found:
        print(f"ACTIVE: {found[0]}")
    else:
        print("NOT LOADED")

    if PLIST_PATH.exists():
        print(f"Plist: {PLIST_PATH}")
    else:
        print("Plist: not found")

    log_file = LOG_DIR / "greener.log"
    if log_file.exists():
        lines = log_file.read_text().strip().splitlines()
        print(f"\nLast 5 log entries:")
        for line in lines[-5:]:
            print(f"  {line}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python setup_scheduler.py [install|uninstall|status]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "install":
        install()
    elif cmd == "uninstall":
        uninstall()
    elif cmd == "status":
        status()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()

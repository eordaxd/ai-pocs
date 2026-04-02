"""
Github Greener — Web UI
Run: python app.py   (opens at http://localhost:5050)
"""

import subprocess
from pathlib import Path
from flask import Flask, render_template, request, jsonify
from main import (
    run_multiple, count_today_commits, today_str, already_committed_today,
    append_entry, commit_and_push, log,
)

app = Flask(__name__)

SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON = SCRIPT_DIR / ".venv" / "bin" / "python"
SETUP_PY = SCRIPT_DIR / "setup_scheduler.py"
LABEL = "com.github-greener.daily"


def scheduler_is_active() -> bool:
    result = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    return LABEL in result.stdout


@app.route("/")
def index():
    return render_template(
        "index.html",
        today=today_str(),
        commits_today=count_today_commits(),
        scheduler_active=scheduler_is_active(),
    )


@app.route("/api/status")
def api_status():
    return jsonify({
        "today": today_str(),
        "commits_today": count_today_commits(),
        "scheduler_active": scheduler_is_active(),
    })


@app.route("/api/push", methods=["POST"])
def api_push():
    data = request.get_json(force=True)
    count = min(max(int(data.get("count", 1)), 1), 20)
    results = run_multiple(count)
    return jsonify({
        "results": results,
        "commits_today": count_today_commits(),
    })


@app.route("/api/scheduler", methods=["POST"])
def api_scheduler():
    data = request.get_json(force=True)
    action = data.get("action")  # "install" or "uninstall"
    if action not in ("install", "uninstall"):
        return jsonify({"error": "invalid action"}), 400

    result = subprocess.run(
        [str(PYTHON), str(SETUP_PY), action],
        capture_output=True, text=True,
    )
    return jsonify({
        "output": result.stdout + result.stderr,
        "success": result.returncode == 0,
        "scheduler_active": scheduler_is_active(),
    })


if __name__ == "__main__":
    print("\n  Github Greener UI: http://localhost:5050\n")
    app.run(port=5050, debug=False)

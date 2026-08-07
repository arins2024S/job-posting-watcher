"""
Polls a set of GitHub-hosted new-grad job list repos and sends a push
notification (via ntfy.sh) whenever new job rows are added.

Run manually with: python job_watch.py
Designed to be run on a schedule via the included GitHub Actions workflow.
"""

import os
import json
import requests

# Add or remove repos/files to watch here.
REPOS = [
    {"owner": "SimplifyJobs", "repo": "New-Grad-Positions", "path": "README.md"},
    {"owner": "speedyapply", "repo": "2027-SWE-College-Jobs", "path": "NEW_GRAD_USA.md"},
    {"owner": "speedyapply", "repo": "2027-AI-College-Jobs", "path": "NEW_GRAD_USA.md"},
]

STATE_FILE = "state.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
GH_TOKEN = os.environ.get("GH_TOKEN")

HEADERS = {"Accept": "application/vnd.github+json"}
if GH_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GH_TOKEN}"


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def latest_commit_sha(owner, repo, path):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    r = requests.get(url, headers=HEADERS, params={"path": path, "per_page": 1}, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data[0]["sha"] if data else None


def diff_added_lines(owner, repo, base, head):
    url = f"https://api.github.com/repos/{owner}/{repo}/compare/{base}...{head}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    added = []
    for f in r.json().get("files", []):
        for line in f.get("patch", "").splitlines():
            if line.startswith("+") and not line.startswith("+++"):
                text = line[1:].strip()
                if text.startswith("|") and "---" not in text:
                    added.append(text)
    return added


def notify(title, message):
    if not NTFY_TOPIC:
        print("NTFY_TOPIC not set, skipping notification")
        return
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=message.encode("utf-8"),
        headers={"Title": title},
        timeout=15,
    )


def main():
    state = load_state()
    for cfg in REPOS:
        key = f"{cfg['owner']}/{cfg['repo']}:{cfg['path']}"
        try:
            latest = latest_commit_sha(cfg["owner"], cfg["repo"], cfg["path"])
        except Exception as e:
            print(f"Error checking {key}: {e}")
            continue
        if not latest:
            continue

        prev = state.get(key)
        if prev is None:
            state[key] = latest
            print(f"First run for {key}, storing baseline (no notification)")
            continue

        if prev != latest:
            try:
                added = diff_added_lines(cfg["owner"], cfg["repo"], prev, latest)
            except Exception as e:
                print(f"Error diffing {key}: {e}")
                added = []
            if added:
                preview = "\n".join(added[:15])
                if len(added) > 15:
                    preview += f"\n...and {len(added) - 15} more"
                notify(f"New postings: {cfg['repo']}", preview)
            state[key] = latest

    save_state(state)


if __name__ == "__main__":
    main()

# Job Posting Watcher

Checks the job-list repos below every 30 minutes and pushes a notification
to your phone/browser the moment a new posting is added — no noise from
housekeeping commits, since it diffs the actual file content.

## What it watches
- SimplifyJobs/New-Grad-Positions
- speedyapply/2027-SWE-College-Jobs
- speedyapply/2027-AI-College-Jobs

Add or remove repos/files by editing the `REPOS` list in `job_watch.py`.

## Setup (about 5 minutes)
1. Create a new GitHub repo (public or private) and add these three files,
   keeping the folder structure: `job_watch.py`, `README.md`, and
   `.github/workflows/job-watch.yml`.
2. Pick a hard-to-guess topic name for notifications, e.g. `arin-jobs-8x2k`
   — ntfy.sh topics are public if someone guesses the name, so avoid
   anything obvious.
3. In the repo: **Settings > Secrets and variables > Actions > New
   repository secret** — name it `NTFY_TOPIC`, value = the topic name from
   step 2.
4. Install the [ntfy app](https://ntfy.sh/app) on your phone and subscribe
   to your topic, or just keep `https://ntfy.sh/<your-topic>` open in a
   browser tab.
5. Push to `main`. The workflow runs automatically every 30 minutes, and
   you can trigger it manually anytime from the repo's Actions tab.

The first run only records a baseline — no notification — so it doesn't
dump the entire existing job list on you at once. Every run after that
notifies only on what's genuinely new.

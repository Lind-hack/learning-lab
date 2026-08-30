# 383 Learning Lab

A small, interactive computer-science learning dashboard for Lind.

- `index.html` is the live browser lesson/quiz surface.
- `data/latest.json` is the newest source-backed lesson.
- `data/history/` stores previous lessons.
- `scripts/publish_lesson.py` validates and publishes generated lesson JSON through the authenticated GitHub API.

Vercel should be connected to this repository's `main` branch. The daily Hermes cron writes and validates lesson JSON, then runs the publisher. The page uses `Cache-Control: no-store` for lesson data so a new Git deployment is visible without stale JSON caching.

The quiz score is stored locally in the learner's browser; no answers or personal data are sent to the repository.

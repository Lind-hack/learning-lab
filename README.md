# 383 Learning Lab

A small, interactive computer-science learning dashboard for Lind.

- `index.html` is the live browser lesson/quiz surface.
- `data/latest.json` is the newest source-backed lesson.
- `data/history/` stores previous lessons.
- `scripts/publish_lesson.py` validates and publishes generated lesson JSON through the authenticated GitHub API.

Vercel should be connected to this repository's `main` branch. The daily Hermes cron writes and validates lesson JSON, then runs the publisher. The page uses `Cache-Control: no-store` for lesson data so a new Git deployment is visible without stale JSON caching.

The quiz score is stored locally in the learner's browser; no answers or personal data are sent to the repository.

## AI Research Library

The lesson actions and sidebar link to the [AI Research Library](https://ai-research-library.vercel.app/), the separate searchable daily research archive. Links open in a new tab so the current lesson and quiz stay open. The sidebar also links to the [GitHub archive](https://github.com/Lind-hack/ai-research-library) for source access. The library maintains its own data and deployment workflow.

For dashboard code changes, push a verified branch and merge it into `main` to trigger the Git-connected Vercel production deployment. Check the commit’s Vercel status and production page before reporting success. The lesson publisher only uploads lesson JSON; it does not publish dashboard HTML.

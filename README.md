# 383 Learning Lab

A small, interactive computer-science learning dashboard for Lind.

- `index.html` is the live browser lesson/quiz surface.
- `data/latest.json` is the newest source-backed lesson.
- `data/history/` stores previous lessons.
- `scripts/publish_lesson.py` validates and publishes generated lesson JSON through the authenticated GitHub API.

## Production hosting

Learning Lab runs at https://agents.383ks.com/learning-lab/ and the research archive at https://agents.383ks.com/research-library/, using the existing VPS dashboard and Cloudflare Tunnel. Sign in with the dashboard login. Both are available under **Learning** in the dashboard navigation.

The dashboard serves an allowlist of public files from each repository's `main` branch. Browser responses use `Cache-Control: private, no-store`; the VPS requests source files with a 60-second revalidation interval. No Vercel account, new DNS record, or separate web service is needed.

The daily Hermes cron still writes and validates lesson JSON, then runs `python scripts/publish_lesson.py` to publish it to GitHub. The dashboard reads that same Git-backed data. No cron or publisher credentials have changed. Vercel remains an optional mirror; it is not required for production hosting.

The quiz score is stored locally in the learner's browser; no answers or personal data are sent to the repository.

## AI Research Library

The lesson actions and sidebar link to the [AI Research Library](https://agents.383ks.com/research-library/), the separate searchable daily research archive. Links open in a new tab so the current lesson and quiz stay open. The sidebar also links to the [GitHub archive](https://github.com/Lind-hack/ai-research-library) for source access. The library maintains its own data and deployment workflow.

For lesson-site changes, push a verified branch and merge it into `main`, then verify the page and `/learning-lab/data/latest.json` through the Cloudflare URL. The dashboard mounting routes live in `Lind-hack/agent-dashboard`; their deployment and rollback steps are documented in that repository's `deploy/learning-sites.md`. The lesson publisher only uploads lesson JSON; it does not publish dashboard HTML.

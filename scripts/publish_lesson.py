#!/usr/bin/env python3
"""Validate and publish the generated Learning Lab JSON through GitHub.

This script deliberately uses the user's existing `gh auth token` keyring entry
without printing or persisting the token. It never reads .env files and never
uses a Vercel CLI token.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = os.environ.get("LEARNING_LAB_GITHUB_REPO", "Lind-hack/learning-lab")
API = "https://api.github.com"
SAFE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,100}$")


def find_gh() -> str:
    configured = os.environ.get("GH_EXE")
    if configured and Path(configured).exists():
        return configured
    for path in sorted(Path(r"C:\Users\PC1\AppData\Local\Microsoft\WinGet\Packages").glob("GitHub.cli_*/bin/gh.exe")):
        if path.exists():
            return str(path)
    return "gh"


def token() -> str:
    value = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if value:
        return value.strip()
    return subprocess.check_output([find_gh(), "auth", "token"], text=True, timeout=30).strip()


TOKEN = token()


def api(path: str, method: str = "GET", payload: dict | None = None) -> tuple[int, dict | list | str]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        API + path,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + TOKEN,
            "User-Agent": "383-learning-lab-publisher",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Content-Type": "application/json"} if data is not None else {}),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            try:
                return response.status, json.loads(raw)
            except json.JSONDecodeError:
                return response.status, raw
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", "replace")
        try:
            detail = json.loads(raw)
        except json.JSONDecodeError:
            detail = raw
        return error.code, detail


def fail(message: str) -> None:
    print(json.dumps({"ok": False, "error": message}, ensure_ascii=False))
    raise SystemExit(1)


def validate_lesson(lesson: dict) -> None:
    required = ["id", "isDemo", "publishedAt", "topic", "learningGoal", "sections", "example", "diagram", "sources", "quiz", "review"]
    missing = [field for field in required if field not in lesson]
    if missing:
        fail("missing fields: " + ", ".join(missing))
    lesson_id = str(lesson.get("id", ""))
    if not SAFE_ID.fullmatch(lesson_id):
        fail("unsafe lesson id")
    if lesson.get("isDemo") is True:
        fail("demo lesson cannot be published")
    if not isinstance(lesson.get("sections"), list) or len(lesson["sections"]) < 4:
        fail("at least four explanation sections are required")
    sources = lesson.get("sources")
    if not isinstance(sources, list) or len(sources) < 1:
        fail("at least one source is required")
    for source in sources:
        if source.get("factChecked") is not True:
            fail("every source must be marked factChecked")
        if not str(source.get("url", "")).startswith(("https://", "http://")):
            fail("source URL must be direct HTTP(S)")
        image = source.get("imageUrl")
        if image is not None and not str(image).startswith(("https://", "http://", "/")):
            fail("image URL must be direct HTTP(S) or same-origin")
    checks = lesson.get("claimChecks")
    if not isinstance(checks, list) or not checks:
        fail("claimChecks are required")
    quiz = lesson.get("quiz")
    if not isinstance(quiz, list) or not 4 <= len(quiz) <= 6:
        fail("quiz must contain four to six questions")
    for question in quiz:
        options = question.get("options")
        index = question.get("correctIndex")
        if not isinstance(options, list) or len(options) < 3 or not isinstance(index, int) or not 0 <= index < len(options):
            fail("invalid quiz question")
    video = lesson.get("video")
    if video is not None and not str(video.get("url", "")).startswith(("https://", "http://")):
        fail("video URL must be direct HTTP(S)")


def put_file(relative: str, message: str) -> str:
    path = ROOT / relative
    if not path.is_file():
        fail(f"missing local file: {relative}")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    endpoint = "/repos/" + REPO + "/contents/" + urllib.parse.quote(relative, safe="/")
    status, current = api(endpoint)
    payload = {"message": message, "content": encoded, "branch": "main"}
    if status == 200 and isinstance(current, dict) and current.get("sha"):
        payload["sha"] = current["sha"]
    elif status not in {200, 404}:
        fail(f"GitHub read failed for {relative}: HTTP {status}")
    status, result = api(endpoint, "PUT", payload)
    if status not in {200, 201} or not isinstance(result, dict):
        fail(f"GitHub publish failed for {relative}: HTTP {status}")
    return str(result.get("commit", {}).get("sha", ""))


def main() -> None:
    latest_path = ROOT / "data" / "latest.json"
    try:
        latest = json.loads(latest_path.read_text(encoding="utf-8"))
    except Exception as error:
        fail(f"latest JSON is invalid: {error}")
    if not isinstance(latest, dict):
        fail("latest JSON must be an object")
    validate_lesson(latest)
    lesson_id = latest["id"]
    history = ROOT / "data" / "history" / f"{lesson_id}.json"
    if history.exists():
        try:
            validate_lesson(json.loads(history.read_text(encoding="utf-8")))
        except SystemExit:
            raise
        except Exception as error:
            fail(f"history JSON is invalid: {error}")
    commits = []
    if history.exists():
        commits.append({"path": str(history.relative_to(ROOT)).replace("\\", "/"), "commit": put_file(str(history.relative_to(ROOT)).replace("\\", "/"), f"lesson: archive {lesson_id}")})
    commits.append({"path": "data/latest.json", "commit": put_file("data/latest.json", f"lesson: publish {lesson_id}")})
    index = ROOT / "data" / "index.json"
    if index.exists():
        commits.append({"path": "data/index.json", "commit": put_file("data/index.json", f"lesson: update index {lesson_id}")})
    print(json.dumps({"ok": True, "repo": REPO, "lesson_id": lesson_id, "commits": commits}, ensure_ascii=False))


if __name__ == "__main__":
    main()

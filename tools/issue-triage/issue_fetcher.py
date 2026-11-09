#!/usr/bin/env python3
"""Fetch and display open non‑pull‑request issues from a GitHub repository.

Usage:
    python3 issue_fetcher.py [owner/repo]

If no repository is supplied the default is
`HivemindOS-Agents/bee-scouts`.

The script performs a read‑only GET request against
`https://api.github.com/repos/<owner>/<repo>/issues?state=open&per_page=100`.
It filters out pull requests (items that contain a ``pull_request`` key).
For each remaining issue it prints a single line
``<title> #<number> <html_url>``.

Exit codes:
    0 – success, 1 – bad arguments, 2 – fetch/parse failure

The module is importable; ``fetch_open_issues`` can be supplied with an optional
custom opener to facilitate testing without network access.
"""
import json
import sys
import urllib.request
import urllib.error

DEFAULT_REPO = "HivemindOS-Agents/bee-scouts"
API_URL_TEMPLATE = (
    "https://api.github.com/repos/{owner_repos}/issues?state=open&per_page=100"
)



def fetch_open_issues(repo: str, opener=None):
    """Return a list of issue dictionaries from *repo*.

    The function accepts an optional *opener* which should be a callable
    compatible with ``urllib.request.urlopen``. This is used in the self‑test
    to inject fixture data.
    """
    url = API_URL_TEMPLATE.format(owner_repos=repo)
    opener = opener or urllib.request.urlopen
    try:
        with opener(url) as resp:
            if resp.status != 200:
                raise urllib.error.HTTPError(url, resp.status, "Non‑200", None, None)
            data = resp.read().decode("utf-8")
            return json.loads(data)
    except Exception as exc:  # pragma: no cover – error path
        raise RuntimeError(f"Failed to fetch issues from {repo!r}: {exc}")


def format_issues(issues):
    """Yield formatted lines for each issue dict.

    Only items that are plain issues are considered. The item must contain a
    numeric ``number`` field; items missing that field are skipped.
    """
    for item in issues:
        # Pull‑requests are returned from the same endpoint; they carry a
        # ``pull_request`` key.
        if "pull_request" in item:
            continue
        title = item.get("title", "")
        number = item.get("number")
        url = item.get("html_url", "")
        if not isinstance(number, int):
            continue
        yield f"{title} #{number} {url}"


def main(argv=None):
    argv = argv or sys.argv[1:]
    if len(argv) > 1:
        print("Usage: python3 issue_fetcher.py [owner/repo]", file=sys.stderr)
        return 1
    repo = argv[0] if argv else DEFAULT_REPO
    try:
        issues = fetch_open_issues(repo)
    except Exception as exc:  # pragma: no cover – network error
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    for line in format_issues(issues):
        print(line)
    return 0


if __name__ == "__main__":  # pragma: no cover – manual run
    sys.exit(main())

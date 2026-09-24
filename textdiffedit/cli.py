"""Line edits with GitHub PR and issue body providers."""

import argparse
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path


class EditError(Exception):
    pass


URL = re.compile(r"^https://github\.com/([^/]+)/([^/]+)/(pull|issues)/(\d+)/?$")


class GitHubBody:
    def __init__(self, kind, url):
        match = URL.fullmatch(url)
        expected = "pull" if kind == "gh-pr-body" else "issues"
        if not match or match.group(3) != expected:
            raise EditError(f"Expected a GitHub {expected} URL")
        owner, repo, _, number = match.groups()
        self.path = f"repos/{owner}/{repo}/{'pulls' if expected == 'pull' else 'issues'}/{number}"

    def request(self, *args, input_text=None):
        try:
            result = subprocess.run(
                ["gh", "api", "--hostname", "github.com", self.path, *args], input=input_text, text=True,
                encoding="utf-8",
                capture_output=True, check=True,
            )
            return json.loads(result.stdout)
        except FileNotFoundError as exc:
            raise EditError("gh is required") from exc
        except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
            raise EditError(f"GitHub request failed: {exc}") from exc

    def fetch(self):
        data = self.request()
        return data["body"] or ""

    def update(self, body):
        self.request("--method", "PATCH", "--input", "-", input_text=json.dumps({"body": body}))


def replace_lines(original, range_spec, expected, replacement):
    match = re.fullmatch(r"([1-9]\d*):([1-9]\d*)", range_spec)
    if not match:
        raise EditError("Range must be START:END (1-based, inclusive)")
    start, end = map(int, match.groups())
    lines = original.splitlines(keepends=True)
    if end < start or end > len(lines):
        raise EditError("Line range is outside the text")
    old = "".join(lines[start - 1:end])
    if old != expected:
        raise EditError("Selected lines do not match --expect")
    if not old.endswith("\n") and end < len(lines):
        raise EditError("Invalid line boundary")
    if end < len(lines) and replacement and not replacement.endswith("\n"):
        raise EditError("Replacement needs a trailing newline before following lines")
    return "".join(lines[:start - 1]) + replacement + "".join(lines[end:])


def render_diff(before, after):
    records = difflib.unified_diff(
        before.splitlines(keepends=True), after.splitlines(keepends=True),
        fromfile="before", tofile="after",
    )
    return "".join(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n"
                   for line in records)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Review a line edit before updating remote text")
    parser.add_argument("provider", choices=("gh-pr-body", "gh-issue-body"))
    parser.add_argument("url")
    parser.add_argument("--replace", required=True, metavar="START:END")
    parser.add_argument("--expect", required=True, type=Path, metavar="FILE")
    parser.add_argument("--with", dest="replacement", required=True, type=Path, metavar="FILE")
    parser.add_argument("--yes", action="store_true", help="Apply after validation without a prompt")
    args = parser.parse_args(argv)
    try:
        provider = GitHubBody(args.provider, args.url)
        original = provider.fetch()
        updated = replace_lines(original, args.replace, args.expect.read_text(encoding="utf-8"),
                                args.replacement.read_text(encoding="utf-8"))
        if updated == original:
            print("No changes")
            return 0
        sys.stdout.write(render_diff(original, updated))
        sys.stdout.flush()
        if not args.yes and input("Apply this change? [y/N] ").strip().lower() != "y":
            return 1
        if provider.fetch() != original:
            raise EditError("Remote text changed since it was read; edit aborted")
        provider.update(updated)
        print("Updated")
        return 0
    except (EditError, OSError, EOFError) as exc:
        print(f"textdiffedit: {exc}", file=sys.stderr)
        return 1

"""Build release notes grouped by project, with Renovate PRs last.

Starts from GitHub's generated notes, so the PR range and line format match
`gh release create --generate-notes`. A PR is listed under every top-level
project directory it touches, under "Cross-project" if it touches more than
MAX_PROJECTS, or under "Repository" if it touches none.

Usage: release_notes.py <repo> <tag> <target-sha>  (prints Markdown to stdout)
"""

import json
import re
import subprocess
import sys
from collections import defaultdict

PR_LINE = re.compile(r"^\* .+ by @(?P<author>\S+).* in https://github\.com/\S+/pull/(?P<number>\d+)$")
RENOVATE = "renovate[bot]"
REPOSITORY = "Repository"
CROSS_PROJECT = "Cross-project"
MAX_PROJECTS = 3


def gh_api(*args: str) -> str:
    return subprocess.run(["gh", "api", *args], check=True, capture_output=True, text=True).stdout


def generated_notes(repo: str, tag: str, target: str) -> str:
    response = gh_api(
        f"repos/{repo}/releases/generate-notes",
        "-f",
        f"tag_name={tag}",
        "-f",
        f"target_commitish={target}",
    )
    return json.loads(response)["body"]


def projects_touched(repo: str, number: str) -> set[str]:
    files = gh_api("--paginate", f"repos/{repo}/pulls/{number}/files", "--jq", ".[].filename").split()
    projects = {project_of(path) for path in files} - {REPOSITORY}
    if len(projects) > MAX_PROJECTS:
        return {CROSS_PROJECT}
    return projects or {REPOSITORY}


def project_of(path: str) -> str:
    top, sep, _ = path.partition("/")
    if not sep or top.startswith("."):
        return REPOSITORY
    return top


def render(repo: str, body: str) -> str:
    by_project: dict[str, list[str]] = defaultdict(list)
    dependencies: list[str] = []
    rest: list[str] = []

    for line in body.splitlines():
        match = PR_LINE.match(line)
        if match is None:
            if line != "## What's Changed":
                rest.append(line)
        elif match["author"] == RENOVATE:
            dependencies.append(line)
        else:
            for project in projects_touched(repo, match["number"]):
                by_project[project].append(line)

    projects = sorted(by_project, key=lambda project: (project in (CROSS_PROJECT, REPOSITORY), project))
    sections = ["## What's Changed"]
    sections += [f"### {project}\n" + "\n".join(by_project[project]) for project in projects]
    if dependencies:
        sections.append("### Dependency updates\n" + "\n".join(dependencies))
    sections.append("\n".join(rest).strip())
    return "\n\n".join(section for section in sections if section) + "\n"


def main() -> None:
    repo, tag, target = sys.argv[1:]
    print(render(repo, generated_notes(repo, tag, target)), end="")


if __name__ == "__main__":
    main()

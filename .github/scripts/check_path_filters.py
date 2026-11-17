"""Fail when a workflow that runs for a project misses a path filter for one of its path dependencies.

A workflow runs for a project when one of its `paths` filters matches the project folder.
Path dependencies come from `[tool.uv.sources]` in pyproject.toml and the dependency tables
of Cargo.toml, followed through the dependencies' own manifests.

Usage: check_path_filters.py  (from the repository root)
"""

import re
import sys
import tomllib
from fnmatch import fnmatchcase
from pathlib import Path

ROOT = Path.cwd()
PROJECT_FOLDERS = ("*", "packages/*/*")
MANIFESTS = ("pyproject.toml", "Cargo.toml")
CARGO_TABLES = ("dependencies", "dev-dependencies", "build-dependencies")
PATHS_BLOCK = re.compile(r"^\s*paths:\n((?:\s*- .+\n)+)", re.MULTILINE)


def direct_dependencies(project: Path) -> set[str]:
    specs = []
    if (pyproject := project / "pyproject.toml").exists():
        uv = tomllib.loads(pyproject.read_text()).get("tool", {}).get("uv", {})
        specs += uv.get("sources", {}).values()
    if (cargo := project / "Cargo.toml").exists():
        manifest = tomllib.loads(cargo.read_text())
        specs += [spec for table in CARGO_TABLES for spec in manifest.get(table, {}).values()]
    paths = [spec["path"] for spec in specs if isinstance(spec, dict) and "path" in spec]
    return {(project / path).resolve().relative_to(ROOT).as_posix() for path in paths}


def all_dependencies(project: str) -> set[str]:
    direct = direct_dependencies(ROOT / project)
    return direct.union(*(all_dependencies(dependency) for dependency in direct))


def path_filters(workflow: Path) -> list[str]:
    blocks = PATHS_BLOCK.findall(workflow.read_text())
    return [line.strip().removeprefix("- ").strip("\"'") for block in blocks for line in block.splitlines()]


def covers(filters: list[str], folder: str) -> bool:
    return any(fnmatchcase(f"{folder}/", pattern) for pattern in filters)


def missing_filters() -> list[str]:
    projects = {
        manifest.parent.relative_to(ROOT).as_posix()
        for pattern in PROJECT_FOLDERS
        for name in MANIFESTS
        for manifest in ROOT.glob(f"{pattern}/{name}")
    }
    workflows = {workflow.name: path_filters(workflow) for workflow in sorted(ROOT.glob(".github/workflows/*.yaml"))}
    return [
        f"{name} runs for {project} but not for its dependency {dependency}: add `{dependency}/**` to its paths"
        for project in sorted(projects)
        for dependency in sorted(all_dependencies(project))
        for name, filters in workflows.items()
        if covers(filters, project) and not covers(filters, dependency)
    ]


if __name__ == "__main__":
    if missing := missing_filters():
        print("\n".join(missing))
        sys.exit(1)
    print("Every workflow runs on changes to the path dependencies of the projects it covers")

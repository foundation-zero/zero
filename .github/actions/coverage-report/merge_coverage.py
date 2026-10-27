"""Merge Cobertura reports into one report with repo-relative paths.

Python, Rust and Vitest each write Cobertura with their own <source> root.
diff-cover and the total comparison need one report whose filenames are
relative to the repo root, and a project can produce several reports
(unit + integration runs) that cover the same files.

Usage: merge_coverage.py <report-dir> <repo-root> <out.xml>
Prints the merged line coverage as a percentage.
"""

import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path, PurePosixPath


def repo_relative(source: str, filename: str, repo_root: str) -> str:
    # Reports are written on another runner (the test job, or main for the
    # baseline), but GitHub-hosted runners share the same checkout path.
    return str(PurePosixPath(source, filename).relative_to(repo_root))


def merge(report_dir: Path, repo_root: str) -> dict[str, dict[int, int]]:
    hits: dict[str, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    reports = sorted(report_dir.rglob("*.xml"))
    if not reports:
        sys.exit(f"no Cobertura reports found in {report_dir}")
    for report in reports:
        root = ET.parse(report).getroot()
        source = root.findtext("sources/source", default=".")
        for cls in root.iter("class"):
            path = repo_relative(source, cls.attrib["filename"], repo_root)
            for line in cls.iter("line"):
                hits[path][int(line.attrib["number"])] += int(line.attrib["hits"])
    return hits


def write_report(hits: dict[str, dict[int, int]], repo_root: str, out: Path) -> float:
    valid = sum(len(lines) for lines in hits.values())
    covered = sum(1 for lines in hits.values() for h in lines.values() if h > 0)
    rate = covered / valid if valid else 1.0

    coverage = ET.Element(
        "coverage",
        {"line-rate": f"{rate:.4f}", "lines-valid": str(valid), "lines-covered": str(covered)},
    )
    ET.SubElement(ET.SubElement(coverage, "sources"), "source").text = repo_root
    classes = ET.SubElement(ET.SubElement(ET.SubElement(coverage, "packages"), "package"), "classes")
    for path, lines in sorted(hits.items()):
        cls = ET.SubElement(classes, "class", {"name": path, "filename": path})
        lines_el = ET.SubElement(cls, "lines")
        for number, count in sorted(lines.items()):
            ET.SubElement(lines_el, "line", {"number": str(number), "hits": str(count)})
    ET.ElementTree(coverage).write(out, encoding="utf-8", xml_declaration=True)
    return rate * 100


def main() -> None:
    report_dir, repo_root, out = Path(sys.argv[1]), sys.argv[2].rstrip("/"), Path(sys.argv[3])
    print(f"{write_report(merge(report_dir, repo_root), repo_root, out):.2f}")


if __name__ == "__main__":
    main()

"""Stamp a manual with the version of the control it describes.

The version is a fingerprint of the module's facts and of the source files that
define it (see module_facts.py), so any change to those makes the manual stale.
Run it from `zero-thrs-control`:

    uv run python docs/skills/thrs-module-manual/scripts/manual_version.py dhw /tmp/thrs-manuals/dhw.html

tests/manuals/test_published_manuals.py fails when a published manual's stamp no
longer matches.
"""

import argparse
import re
from datetime import UTC, datetime
from pathlib import Path

from module_facts import fingerprint

VERSION_LINE = re.compile(r"<p\s+class=\"version\"[^>]*>.*?</p>\n?", re.DOTALL)
STAMP = re.compile(r'data-module="(?P<module>[^"]+)"\s+data-facts="(?P<facts>[^"]+)"')


def version_line(module_name: str, facts: str) -> str:
    today = datetime.now(UTC).date().isoformat()
    return (
        f'<p class="version" data-module="{module_name}" data-facts="{facts}">'
        f"Control version {facts} · {today}</p>\n"
    )


def stamp(module_name: str, path: Path) -> None:
    facts = fingerprint(module_name)
    manual = VERSION_LINE.sub("", path.read_text()).rstrip("\n")
    path.write_text(f"{manual}\n\n{version_line(module_name, facts)}")
    print(f"Stamped {path} with control version {facts}")


def read_stamp(path: Path) -> tuple[str, str]:
    found = STAMP.search(path.read_text())
    if found is None:
        raise ValueError(
            f"{path.name} has no control version; stamp it with `just manual_stamp`"
        )
    return found["module"], found["facts"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("module")
    parser.add_argument("path", type=Path)
    args = parser.parse_args()
    stamp(args.module, args.path)


if __name__ == "__main__":
    main()

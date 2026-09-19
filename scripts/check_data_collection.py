#!/usr/bin/env python3
"""Validate the library corpus against the Checkpoint 2 requirements."""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


REQUIRED_FIELDS = [
    "doc_id",
    "title",
    "source_url",
    "retrieved_at",
    "document_version",
    "audience",
]


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    return {
        key: value.strip().strip('"')
        for key, value in re.findall(r"^(\w+):\s*(.+)$", parts[1], re.MULTILINE)
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    directory = args.directory

    markdown_files = sorted(directory.glob("*.md"))
    with (directory / "sources.csv").open(encoding="utf-8", newline="") as source:
        rows = list(csv.DictReader(source))

    document_ids: list[str | None] = []
    audiences: dict[str | None, int] = {}
    files_ok = True
    for path in markdown_files:
        metadata = parse_frontmatter(path)
        document_id = metadata.get("doc_id")
        document_ids.append(document_id)
        audience = metadata.get("audience")
        audiences[audience] = audiences.get(audience, 0) + 1
        ok = all(metadata.get(key) for key in REQUIRED_FIELDS) and document_id == path.stem
        files_ok &= ok
        print(f"{path.name:40} {'OK' if ok else 'THIEU METADATA'}")

    count_ok = 5 <= len(markdown_files) <= 10
    csv_ok = sorted(row["doc_id"] for row in rows) == sorted(document_ids)
    audience_ok = len(audiences) >= 2 and None not in audiences
    print("so file :", len(markdown_files), "OK" if count_ok else "CAN 5-10")
    print("csv     :", "OK" if csv_ok else "LECH")
    print("audience:", audiences, "OK" if audience_ok else "CAN IT NHAT 2 GIA TRI")
    return 0 if files_ok and count_ok and csv_ok and audience_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

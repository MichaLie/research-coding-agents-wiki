#!/usr/bin/env python3
"""Assign stable record IDs and durable catalog-entry dates.

Run with --check in validation and --apply only when records need migration.
Existing IDs and dates are preserved. The obsolete relative "new" flag is
removed because newness must be derived from dates, not stored indefinitely.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from pathlib import Path


def slugify(value: str) -> str:
    value = value.replace("+", " plus ").replace("&", " and ")
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii").lower()
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def names_at(commit: str, data_file: str) -> set[str]:
    raw = subprocess.check_output(
        ["git", "show", f"{commit}:{data_file}"],
        text=True,
    )
    return {record["name"].casefold() for record in json.loads(raw)}


def migrated_records(metadata: dict, records: list[dict]) -> tuple[list[dict], int]:
    data_file = metadata["data_file"]
    baseline_commit = metadata["baseline_commit"]
    legacy_names = names_at(metadata["legacy_snapshot_commit"], data_file)
    baseline_names = names_at(baseline_commit, data_file)
    prefix = metadata["id_prefix"]

    migrated = []
    changes = 0
    ids: dict[str, str] = {}
    for record in records:
        name = record["name"]
        record_id = record.get("id") or f"{prefix}-{slugify(name)}"
        if not record_id or record_id == prefix + "-":
            raise ValueError(f"cannot derive a stable ID for {name!r}")
        if record_id in ids and ids[record_id] != name:
            raise ValueError(
                f"ID collision {record_id!r}: {ids[record_id]!r} and {name!r}; "
                "assign explicit IDs before applying"
            )
        ids[record_id] = name

        folded = name.casefold()
        if record.get("date_added"):
            date_added = record["date_added"]
        elif folded in legacy_names:
            date_added = metadata["legacy_snapshot_date"]
        elif folded in baseline_names:
            date_added = metadata["baseline_data_date"]
        else:
            date_added = metadata["modified"]

        updated = {"id": record_id, "date_added": date_added}
        updated.update(
            (key, value)
            for key, value in record.items()
            if key not in {"id", "date_added", "new"}
        )
        if updated != record:
            changes += 1
        migrated.append(updated)
    return migrated, changes


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    metadata = json.loads(Path("resource_metadata.json").read_text(encoding="utf-8"))
    path = Path(metadata["data_file"])
    records = json.loads(path.read_text(encoding="utf-8"))
    migrated, changes = migrated_records(metadata, records)
    print(f"{path}: {len(records)} records; {changes} require ID/date migration")

    if args.apply and changes:
        path.write_text(
            json.dumps(migrated, ensure_ascii=False, indent=1) + "\n",
            encoding="utf-8",
        )
        print(f"updated {path}")
    return 1 if args.check and changes else 0


if __name__ == "__main__":
    raise SystemExit(main())

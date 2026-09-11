#!/usr/bin/env python3
"""Apply reviewed September decisions without changing unreviewed verification dates.

The compact decision file is the reviewable migration payload. Absolute field
values make this idempotent; generated distributions are rebuilt by build.py.
This is a local preview and does not create a release, commit, or remote write.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-09-11"


def main() -> None:
    payload = json.loads((ROOT / "evidence/reverify-2026-09-11/decisions.json").read_text())
    records = json.loads((ROOT / "tools.json").read_text())
    by_id = {r["id"]: r for r in records}
    changed = 0
    for decision in payload["retained_reviews"]:
        record = by_id[decision["id"]]
        before = copy.deepcopy(record)
        for field, value in decision["updates"].items():
            record[field] = copy.deepcopy(value)
        if decision["full_reverification"]:
            record["verified"] = TODAY
        elif record["verified"] != decision["previous_verified"]:
            raise SystemExit(f"Unexpected verification date for {record['id']}; review the migration.")
        material_before = {k: v for k, v in before.items() if k not in {"verified", "date_modified"}}
        material_after = {k: v for k, v in record.items() if k not in {"verified", "date_modified"}}
        if material_before != material_after:
            record["date_modified"] = TODAY
            changed += 1
    held_ids = {r["id"] for r in payload.get("held_records", [])}
    records = [r for r in records if r["id"] not in held_ids]
    by_id = {r["id"]: r for r in records}
    for addition in payload["additions"]:
        if addition["id"] not in by_id:
            records.append(copy.deepcopy(addition))
            by_id[addition["id"]] = records[-1]
            changed += 1
        elif by_id[addition["id"]] != addition:
            if by_id[addition["id"]]["date_added"] != TODAY:
                raise SystemExit(f"Addition ID predates this migration: {addition['id']}")
            by_id[addition["id"]].clear()
            by_id[addition["id"]].update(copy.deepcopy(addition))
            changed += 1
    (ROOT / "tools.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")
    metadata_path = ROOT / "resource_metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata.update(payload["metadata_updates"])
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(records)} records; {changed} material changes applied; local preview only")


if __name__ == "__main__":
    main()

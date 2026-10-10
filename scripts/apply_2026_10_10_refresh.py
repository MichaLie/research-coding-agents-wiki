#!/usr/bin/env python3
"""Apply the reviewed October 2026 re-verification without changing unreviewed dates.

evidence/reverify-2026-10-10/decisions.json holds the complete merged records
(re-verification proposal + adversarial verdict + cross-tool integration), the
additions and the evidence holds. Absolute record values make this idempotent;
generated distributions are rebuilt by build.py. Local preview only: no release,
commit or remote write.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    payload = json.loads((ROOT / "evidence/reverify-2026-10-10/decisions.json").read_text())
    date = payload["review_date"]
    current = json.loads((ROOT / "tools.json").read_text())
    held = {h["id"] for h in payload["held_records"]}
    final = {r["id"]: r for r in payload["final_records"]}
    if len(final) != len(payload["final_records"]):
        raise SystemExit("Duplicate IDs in the reviewed payload")
    if held & set(final):
        raise SystemExit("An ID cannot be displayed and held")
    for record in current:
        if record["id"] not in held and record["id"] not in final:
            raise SystemExit(f"Retained record {record['id']} has no reviewed final record")
    order = [r["id"] for r in current if r["id"] in final] + [i for i in payload["additions"] if i not in {r["id"] for r in current}]
    records = [final[i] for i in order]
    (ROOT / "tools.json").write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n")

    special = Counter(r["suitability"]["special"] for r in records)
    verified_now = sum(1 for r in records if r["verified"] == date)
    metadata_path = ROOT / "resource_metadata.json"
    metadata = json.loads(metadata_path.read_text())
    metadata.update(
        resource_version="2.3.0", modified=date, evidence_review_date=date,
        baseline_commit=payload["baseline_commit"],
        baseline_commit_url=metadata["repository"] + "/commit/" + payload["baseline_commit"], release_ref=None,
        evidence_statement=(
            f"Local 2.3.0 preview reviewed {date}. {len(records)} tools; {verified_now} carry this review date after a full "
            "first-party re-verification, an adversarial check of every safety-relevant change and addition, and a cross-tool "
            f"consistency pass. {special.get('cfg', 0)} offer a configurable route for special-category data on infrastructure the "
            f"institution controls; {special.get('no', 0)} are not appropriate for it. Evidence holds and unresolved limits are recorded "
            "in evidence/LIVE_AUDIT_2026-10-10.md."),
    )
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(records)} tools ({len(payload['additions'])} added, {len(held & {r['id'] for r in current})} moved to evidence hold); "
          f"special {dict(special)}; local preview only")


if __name__ == "__main__":
    main()

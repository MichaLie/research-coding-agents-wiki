#!/usr/bin/env python3
"""Run deterministic, FAIR, structural, and optional live-link maintenance gates."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError as exc:  # pragma: no cover - explicit operator guidance
    raise SystemExit(
        "Missing maintenance dependency. Run: python3 -m pip install -r requirements-maintenance.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = ROOT / ".maintenance-output" / "maintenance-report.json"


def normalized(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.replace("+", " plus ").casefold()).strip()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command_step(name: str, command: list[str], *, required: bool = True) -> dict[str, Any]:
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = (completed.stdout + completed.stderr)[-16000:]
    return {
        "name": name,
        "command": command,
        "required": required,
        "returncode": completed.returncode,
        "status": "pass" if completed.returncode == 0 else ("fail" if required else "review"),
        "output": output,
    }


def schema_and_invariants(metadata: dict[str, Any]) -> dict[str, Any]:
    data_path = ROOT / metadata["data_file"]
    schema_path = ROOT / metadata["schema_file"]
    records = json.loads(data_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    failures: list[str] = []
    warnings: list[str] = []

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(records), key=lambda item: list(item.absolute_path)):
        locator = "/".join(str(part) for part in error.absolute_path) or "catalog"
        failures.append(f"{locator}: {error.message}")

    identities: dict[str, tuple[str, str]] = {}
    for index, record in enumerate(records):
        record_id = str(record.get("id", f"index-{index}"))
        values = [("name", record.get("name", "")), ("current_name", record.get("current_name", ""))]
        values.extend((f"aliases[{alias_index}]", alias) for alias_index, alias in enumerate(record.get("aliases", [])))
        local: set[str] = set()
        for field, value in values:
            if not value:
                continue
            key = normalized(str(value))
            if key in local:
                continue
            local.add(key)
            if key in identities and identities[key][0] != record_id:
                other_id, other_field = identities[key]
                failures.append(f"{record_id}.{field}: identity collides with {other_id}.{other_field}")
            else:
                identities[key] = (record_id, field)

        parsed: dict[str, date] = {}
        for field in ("date_added", "date_modified", "verified"):
            value = record.get(field)
            if not value:
                continue
            try:
                parsed[field] = date.fromisoformat(value)
            except (TypeError, ValueError):
                failures.append(f"{record_id}.{field}: invalid calendar date {value!r}")
        if parsed.get("date_modified") and parsed.get("date_added") and parsed["date_modified"] < parsed["date_added"]:
            failures.append(f"{record_id}: date_modified precedes date_added")
        if parsed.get("verified") and parsed.get("date_added") and parsed["verified"] < parsed["date_added"]:
            failures.append(f"{record_id}: verified precedes date_added")

    baseline_commit = str(metadata.get("baseline_commit") or "")
    baseline_url = str(metadata.get("baseline_commit_url") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", baseline_commit) or not baseline_url.endswith(baseline_commit):
        failures.append("baseline provenance must contain one matching full Git SHA and HTTPS commit URL")
    if metadata.get("release_ref") is None:
        warnings.append("release_ref is intentionally null in preview; a human-created tag/release URL is required for release")

    return {
        "name": "full-schema-and-invariants",
        "status": "fail" if failures else "pass",
        "records": len(records),
        "failures": failures,
        "warnings": warnings,
    }


def link_result(report_dir: Path) -> dict[str, Any]:
    output = report_dir / "link-audit.tsv"
    step = command_step(
        "live-link-audit",
        [sys.executable, "scripts/audit_links.py", "--workers", "24", "--timeout", "20", "--output", str(output)],
    )
    if step["returncode"] != 0 or not output.is_file():
        return step
    counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    with output.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            outcome = row["outcome"]
            counts[outcome] = counts.get(outcome, 0) + 1
            examples.setdefault(outcome, [])
            if row["url"] not in examples[outcome] and len(examples[outcome]) < 10:
                examples[outcome].append(row["url"])
    if counts.get("missing"):
        status = "fail"
    elif counts.get("http_error") or counts.get("network_error"):
        status = "review"
    else:
        status = "pass"
    step.update(status=status, counts=counts, examples=examples, artifact=str(output.relative_to(ROOT)))
    return step


def git_context() -> dict[str, Any]:
    def read(command: list[str]) -> str:
        completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        return completed.stdout.strip() if completed.returncode == 0 else ""

    return {
        "commit": read(["git", "rev-parse", "HEAD"]),
        "branch": read(["git", "branch", "--show-current"]),
        "dirty": bool(read(["git", "status", "--porcelain"])),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("quick", "full", "release"), default="quick")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--skip-links", action="store_true", help="Skip live links in full/release mode (for isolated simulation only).")
    parser.add_argument("--check-only", action="store_true", help="Validate current distributions without rebuilding them.")
    args = parser.parse_args()

    metadata = json.loads((ROOT / "resource_metadata.json").read_text(encoding="utf-8"))
    canonical = ROOT / metadata["data_file"]
    before_hash = sha256(canonical)
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    steps: list[dict[str, Any]] = []

    if not args.check_only:
        build_command = [sys.executable, "build.py"] + (["--release"] if args.mode == "release" else [])
        steps.append(command_step("deterministic-build-and-validator", build_command))
    else:
        validate_command = [sys.executable, "validate_catalog.py"] + (["--release"] if args.mode == "release" else [])
        steps.append(command_step("validator-without-rebuild", validate_command))

    steps.append(schema_and_invariants(metadata))
    after_hash = sha256(canonical)
    steps.append({
        "name": "canonical-data-immutability",
        "status": "pass" if before_hash == after_hash else "fail",
        "before": before_hash,
        "after": after_hash,
    })
    steps.append(command_step("git-diff-check", ["git", "diff", "--check"]))

    if args.mode in {"full", "release"} and not args.skip_links:
        steps.append(link_result(report_path.parent))

    if any(step["status"] == "fail" for step in steps):
        verdict = "fail"
        exit_code = 1
    elif any(step["status"] == "review" for step in steps):
        verdict = "review_required"
        exit_code = 2
    else:
        verdict = "pass"
        exit_code = 0

    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "profile": metadata["profile"],
        "mode": args.mode,
        "check_only": args.check_only,
        "git": git_context(),
        "verdict": verdict,
        "steps": steps,
        "publication_authorized": False,
    }
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"MAINTENANCE {verdict.upper()} profile={metadata['profile']} mode={args.mode}")
    for step in steps:
        print(f"{step['status'].upper():>6}  {step['name']}")
    print(f"report: {report_path}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

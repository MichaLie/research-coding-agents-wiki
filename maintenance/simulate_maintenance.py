#!/usr/bin/env python3
"""Fault-inject the maintenance gates in disposable clean-copy workspaces."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".maintenance-output" / "simulation-report.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_repo(parent: Path, name: str) -> Path:
    target = parent / name
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".maintenance-output", "__pycache__", "*.pyc"),
    )
    return target


def records(repo: Path) -> tuple[Path, list[dict], dict]:
    metadata = json.loads((repo / "resource_metadata.json").read_text(encoding="utf-8"))
    path = repo / metadata["data_file"]
    return path, json.loads(path.read_text(encoding="utf-8")), metadata


def write_records(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def valid_synthetic(repo: Path) -> None:
    path, data, metadata = records(repo)
    fixture = json.loads(json.dumps(data[0]))
    fixture["id"] = f"{metadata['id_prefix']}-maintenance-synthetic-fixture"
    fixture["name"] = "Synthetic maintenance fixture"
    if "current_name" in fixture:
        fixture["current_name"] = fixture["name"]
    fixture["aliases"] = []
    fixture["date_added"] = metadata["modified"]
    fixture["date_modified"] = metadata["modified"]
    fixture["verified"] = metadata["modified"]
    data.append(fixture)
    write_records(path, data)


def invalid_vocabulary(repo: Path) -> None:
    path, data, _ = records(repo)
    field = next(field for field in ("type", "category", "modality") if field in data[0])
    data[0][field] = "__invalid_fixture__"
    write_records(path, data)


def alias_collision(repo: Path) -> None:
    path, data, _ = records(repo)
    data[0].setdefault("aliases", []).append(data[1]["name"])
    write_records(path, data)


def impossible_date(repo: Path) -> None:
    path, data, _ = records(repo)
    data[0]["verified"] = "2026-02-31"
    write_records(path, data)


def distribution_drift(repo: Path) -> None:
    _, _, metadata = records(repo)
    (repo / "docs" / metadata["data_file"]).write_text("[]\n", encoding="utf-8")


def mismatched_release_governance(repo: Path) -> None:
    path = repo / "resource_metadata.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["release_ref"] = metadata["repository"].rstrip("/") + "/releases/tag/v0.0.0"
    path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(repo: Path, extra: list[str] | None = None) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "maintenance/run_maintenance.py", "--mode", "quick"]
    command.extend(extra or [])
    return subprocess.run(command, cwd=repo, text=True, capture_output=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=OUTPUT)
    args = parser.parse_args()
    original_metadata = json.loads((ROOT / "resource_metadata.json").read_text(encoding="utf-8"))
    original_hash = digest(ROOT / original_metadata["data_file"])
    scenarios: list[dict] = []

    specifications: list[tuple[str, Callable[[Path], None] | None, bool, list[str]]] = [
        ("baseline_clean_copy", None, True, []),
        ("valid_synthetic_addition", valid_synthetic, True, []),
        ("invalid_controlled_vocabulary", invalid_vocabulary, False, []),
        ("normalized_alias_collision", alias_collision, False, []),
        ("impossible_calendar_date", impossible_date, False, []),
        ("stale_public_distribution", distribution_drift, False, ["--check-only"]),
        ("mismatched_release_governance", mismatched_release_governance, False, ["--mode", "release", "--skip-links"]),
    ]

    with tempfile.TemporaryDirectory(prefix="catalog-maintenance-simulation-") as tmp:
        parent = Path(tmp)
        for name, mutation, expected_success, extra in specifications:
            repo = copy_repo(parent, name)
            if mutation:
                mutation(repo)
            if extra and extra[0] == "--mode":
                command = [sys.executable, "maintenance/run_maintenance.py", *extra]
                completed = subprocess.run(command, cwd=repo, text=True, capture_output=True)
            else:
                completed = run(repo, extra)
            actual_success = completed.returncode == 0
            scenarios.append({
                "name": name,
                "expected": "pass" if expected_success else "blocked",
                "returncode": completed.returncode,
                "result": "pass" if actual_success else "blocked",
                "test_passed": actual_success == expected_success,
                "output_tail": (completed.stdout + completed.stderr)[-5000:],
            })

    original_unchanged = original_hash == digest(ROOT / original_metadata["data_file"])
    passed = all(scenario["test_passed"] for scenario in scenarios) and original_unchanged
    report = {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "profile": original_metadata["profile"],
        "verdict": "pass" if passed else "fail",
        "real_catalog_unchanged": original_unchanged,
        "synthetic_data_only": True,
        "scenarios": scenarios,
    }
    report_path = args.report if args.report.is_absolute() else ROOT / args.report
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for scenario in scenarios:
        print(f"{'PASS' if scenario['test_passed'] else 'FAIL'} {scenario['name']}: expected {scenario['expected']}, got {scenario['result']}")
    print(f"{'PASS' if original_unchanged else 'FAIL'} real catalog unchanged")
    print(f"report: {report_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

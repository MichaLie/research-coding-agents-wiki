#!/usr/bin/env python3
"""Apply the 2026-07-13 release-audit corrections idempotently.

The script deliberately makes catalogue claims more conservative. It also adds
structured special-data route and software-licence fields so later maintenance
can validate them instead of inferring safety from prose or ``runs_locally``.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "tools.json"
EVIDENCE = ROOT / "evidence" / "CLAIM_EVIDENCE_2026-07-13.tsv"

CONFIRMED_LICENSES = {
    "rca-gemini-cli": "Apache-2.0",
    "rca-aider": "Apache-2.0",
    "rca-goose": "Apache-2.0",
    "rca-cline": "Apache-2.0",
    "rca-jupyter-ai": "BSD-3-Clause",
    "rca-opencode": "MIT",
    "rca-mini-swe-agent": "MIT",
    "rca-gptme": "MIT",
    "rca-open-interpreter": "Apache-2.0",
    "rca-kilo-code": "MIT",
    "rca-marimo": "Apache-2.0",
    "rca-ollama": "MIT",
}


def source_for(record: dict, needle: str) -> str:
    for source in record.get("sources", []):
        if needle.casefold() in source.casefold():
            return source
    return record.get("sources", [""])[0]


def apply() -> None:
    records = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_id = {record["id"]: record for record in records}

    for record in records:
        if record["openness"] == "commercial":
            record["software_license"] = None
            record["license_status"] = "proprietary"
        elif record["id"] in CONFIRMED_LICENSES:
            record["software_license"] = CONFIRMED_LICENSES[record["id"]]
            record["license_status"] = "confirmed"
        elif record["id"] == "rca-crush":
            record["software_license"] = "FSL-1.1-MIT"
            record["license_status"] = "source-available"
        else:
            record["software_license"] = None
            record["license_status"] = "unconfirmed"

        special = record["suitability"]["special"]
        special_note = record["suitability_notes"].get("special", "")
        if special == "no":
            record["special_route"] = {
                "status": "not-appropriate",
                "boundary": "none",
                "inference": "none",
                "required_controls": [],
                "residual_risks": [special_note],
            }
        else:
            record["special_route"] = {
                "status": "ready" if special == "ok" else "config-required",
                "boundary": "customer-controlled",
                "inference": "local-only",
                "required_controls": [special_note],
                "residual_risks": [
                    "Conditional route: revalidate the exact deployment, model endpoint, integrations, telemetry, and institutional approval before use."
                ],
            }

    for record_id in ("rca-aider", "rca-goose"):
        by_id[record_id]["suitability"]["personal"] = "cfg"

    deepnote = by_id["rca-deepnote"]
    deepnote["data_handling_note"] = (
        "Deepnote Cloud uses vendor AI providers under no-training/retention terms. "
        "Enterprise custom-model settings can route the agent, edits, and suggestions to a customer-controlled endpoint, "
        "but native code completions continue through Deepnote's provider unless separately disabled. "
        "Block-output sharing is another separate control. A controlled route therefore requires explicit configuration; "
        "an Enterprise or customer-managed deployment alone is not sufficient."
    )
    deepnote["suitability_notes"]["special"] = (
        "Only a customer-managed Enterprise deployment with a customer-controlled model endpoint can qualify. "
        "Disable native code completions, make native AI providers unavailable, disable block-output sharing, "
        "review every integration, and obtain institutional approval. Deepnote Cloud does not qualify."
    )
    deepnote["special_route"] = {
        "status": "config-required",
        "boundary": "customer-controlled",
        "inference": "customer-controlled-endpoint",
        "required_controls": [
            "Enterprise customer-managed deployment behind the institutional boundary",
            "Customer-controlled model endpoint for agent, edits, and suggestions",
            "Native code completions disabled",
            "Native Deepnote AI providers unavailable",
            "Block-output sharing disabled",
            "All integrations and subprocessors reviewed",
            "DPO or data-steward approval before use",
        ],
        "residual_risks": [
            "Product updates may introduce or re-enable cloud AI paths; configuration must be rechecked after upgrades."
        ],
    }
    custom_model_source = "https://deepnote.com/docs/ai-custom-models"
    if custom_model_source not in deepnote["sources"]:
        deepnote["sources"].append(custom_model_source)

    mistral = by_id["rca-mistral-vibe"]
    mistral["pricing"] = (
        "Free: basic access, approximately 25 messages/day; Pro: $14.99/month; Team: $24.99/user/month; "
        "Enterprise: custom; Education/student offer: $5.99/month where eligible. "
        "Free, Pro, and Education inputs/outputs are eligible for training by default unless the user opts out. "
        "Team and Enterprise inputs/outputs are not used for training. API usage is billed separately."
    )

    crush = by_id["rca-crush"]
    crush["pricing"] = crush["pricing"].replace(
        "free and open source (FSL-1.1-MIT)",
        "free and source-available under FSL-1.1-MIT",
    )

    windsurf = by_id["rca-windsurf"]
    windsurf["current_name"] = "Devin Desktop"
    windsurf["aliases"] = sorted(set(windsurf.get("aliases", []) + ["Windsurf"]))

    official_repositories = {
        "rca-cline": "https://github.com/cline/cline",
        "rca-opencode": "https://github.com/anomalyco/opencode",
        "rca-open-interpreter": "https://github.com/openinterpreter/openinterpreter",
        "rca-kilo-code": "https://github.com/Kilo-Org/kilocode",
        "rca-ollama": "https://github.com/ollama/ollama",
    }
    for record_id, repository in official_repositories.items():
        if repository not in by_id[record_id]["sources"]:
            by_id[record_id]["sources"].append(repository)

    for record in records:
        record["date_modified"] = max(record.get("date_modified", ""), "2026-07-13")

    CATALOG.write_text(json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    with EVIDENCE.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(("record_id", "claim", "status", "source", "verified", "note"))
        for record in records:
            writer.writerow((record["id"], "deployment_and_privacy", "current-review", source_for(record, "privacy"), record["verified"], "See data_handling_note and special_route"))
            writer.writerow((record["id"], "pricing", "current-review", record["links"].get("pricing", ""), record["verified"], "Volatile; recheck before release"))
            writer.writerow((record["id"], "software_license", record["license_status"], source_for(record, "github.com"), record["verified"], record["software_license"] or "Licence not yet confirmed at record level"))


if __name__ == "__main__":
    apply()

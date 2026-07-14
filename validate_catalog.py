#!/usr/bin/env python3
"""Validate catalog structure, FAIR artifacts, and release gates without dependencies."""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, urlsplit

from fair_metadata import load_resource_metadata


SENSITIVE_PAIR_RE = re.compile(
    r"(?i)(?:^|[?&;\s])(?:auth_token|access_token|token|api[_-]?key|apikey|secret|"
    r"password|passwd|session|cookie|state|ip_address)="
)


class FairScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if (
            tag == "script"
            and values.get("id") == "fair-metadata"
            and values.get("type") == "application/ld+json"
        ):
            self.capture = True

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            self.capture = False


def is_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    if any(character.isspace() for character in value):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def normalized_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.replace("+", " plus ").casefold()).strip()


def main(release: bool = False) -> int:
    errors: list[str] = []
    warnings: list[str] = []

    metadata = load_resource_metadata()
    profile = metadata.get("profile")
    data_path = Path(metadata["data_file"])
    schema_path = Path(metadata["schema_file"])
    records = json.loads(data_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    if not isinstance(records, list) or not records:
        errors.append(f"{data_path}: expected a non-empty JSON array")
        records = []

    item_schema = schema["items"]
    required = set(item_schema["required"])
    properties = item_schema["properties"]
    allowed = set(properties)
    seen_ids: dict[str, int] = {}
    seen_names: dict[str, int] = {}
    missing_verified = 0
    expected_link_urls: set[str] = set()

    for index, record in enumerate(records):
        where = f"{data_path}[{index}]"
        if not isinstance(record, dict):
            errors.append(f"{where}: record is not an object")
            continue
        missing = sorted(required - set(record))
        unknown = sorted(set(record) - allowed)
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
        if unknown:
            errors.append(f"{where}: unknown fields {', '.join(unknown)}")
        if "new" in record:
            errors.append(f"{where}: obsolete relative field 'new' is not allowed")

        record_id = record.get("id")
        pattern = properties["id"].get("pattern")
        if not isinstance(record_id, str) or not re.fullmatch(pattern, record_id):
            errors.append(f"{where}.id: invalid or missing stable ID")
        elif record_id in seen_ids:
            errors.append(f"{where}.id: duplicate of record {seen_ids[record_id]}")
        else:
            seen_ids[record_id] = index

        date_added = record.get("date_added")
        if not isinstance(date_added, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date_added):
            errors.append(f"{where}.date_added: expected YYYY-MM-DD")

        name = record.get("name")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{where}.name: required non-empty string")
        else:
            key = normalized_name(name)
            if key in seen_names:
                errors.append(f"{where}.name: normalized duplicate of record {seen_names[key]}")
            else:
                seen_names[key] = index

        for key, spec in properties.items():
            if key in record and "enum" in spec and record[key] not in spec["enum"]:
                errors.append(f"{where}.{key}: {record[key]!r} is outside the controlled vocabulary")

        if not record.get("verified"):
            missing_verified += 1

        if not record.get("sources"):
            errors.append(f"{where}.sources: at least one evidence URL is required")
        for source_index, source in enumerate(record.get("sources", [])):
            if not is_http_url(source):
                errors.append(f"{where}.sources[{source_index}]: invalid URL")
            else:
                expected_link_urls.add(source)

        if profile == "foundation-models":
            for field in ("paper_links", "code_links"):
                for link_index, link in enumerate(record.get(field, [])):
                    if not isinstance(link, dict) or not link.get("label"):
                        errors.append(f"{where}.{field}[{link_index}]: missing label")
                    if not is_http_url(link.get("url") if isinstance(link, dict) else None):
                        errors.append(f"{where}.{field}[{link_index}]: invalid URL")
        elif profile == "autonomous-agents":
            for field in ("paper_links", "repo_links"):
                for link_index, link in enumerate(record.get(field, [])):
                    if not isinstance(link, dict) or not link.get("label"):
                        errors.append(f"{where}.{field}[{link_index}]: missing label")
                    if not is_http_url(link.get("url") if isinstance(link, dict) else None):
                        errors.append(f"{where}.{field}[{link_index}]: invalid URL")
        elif profile == "coding-agents":
            links = record.get("links", {})
            for url in links.values() if isinstance(links, dict) else []:
                if url:
                    expected_link_urls.add(url)
            for field in ("docs", "privacy"):
                if not is_http_url(links.get(field) if isinstance(links, dict) else None):
                    errors.append(f"{where}.links.{field}: invalid URL")
            pricing = links.get("pricing") if isinstance(links, dict) else None
            if pricing and not is_http_url(pricing):
                errors.append(f"{where}.links.pricing: invalid URL")
            for source_index, source in enumerate(record.get("sources", [])):
                if not is_http_url(source):
                    errors.append(f"{where}.sources[{source_index}]: invalid URL")
            special = (record.get("suitability") or {}).get("special")
            route = record.get("special_route") or {}
            expected_status = {"no": "not-appropriate", "cfg": "config-required", "ok": "ready"}.get(special)
            if route.get("status") != expected_status:
                errors.append(f"{where}.special_route.status: inconsistent with suitability.special")
            if special == "no":
                if route.get("boundary") != "none" or route.get("inference") != "none":
                    errors.append(f"{where}.special_route: non-approved route must have no boundary/inference claim")
            else:
                if route.get("boundary") != "customer-controlled":
                    errors.append(f"{where}.special_route.boundary: special-data route must be customer-controlled")
                if route.get("inference") not in {"local-only", "customer-controlled-endpoint"}:
                    errors.append(f"{where}.special_route.inference: cloud/vendor inference is not allowed")
                if not route.get("required_controls"):
                    errors.append(f"{where}.special_route.required_controls: conditional route needs explicit controls")
            if record.get("openness") == "open-source" and record.get("license_status") != "confirmed":
                errors.append(f"{where}: open-source classification requires a confirmed record-level software licence")
            if record.get("license_status") in {"confirmed", "source-available"} and not record.get("software_license"):
                errors.append(f"{where}.software_license: licence identifier required for {record.get('license_status')}")
        else:
            errors.append(f"resource_metadata.json: unknown profile {profile!r}")

    if missing_verified:
        message = f"{missing_verified}/{len(records)} records lack an explicit evidence-verification date"
        if release:
            errors.append(message)
        else:
            warnings.append(message)

    link_audit_path = Path("evidence/link_audit.tsv")
    if not link_audit_path.is_file():
        errors.append(f"missing link-audit evidence: {link_audit_path}")
    else:
        observed_link_urls: set[str] = set()
        unsafe_rows = 0
        with link_audit_path.open(encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle, delimiter="\t"):
                if row.get("url"):
                    observed_link_urls.add(row["url"])
                final_url = row.get("final_url", "")
                if final_url:
                    parsed = urlsplit(final_url)
                    if parsed.query or parsed.fragment:
                        unsafe_rows += 1
                if any(SENSITIVE_PAIR_RE.search(row.get(field, "")) for field in ("url", "final_url", "error")):
                    unsafe_rows += 1
        missing_urls = expected_link_urls - observed_link_urls
        stale_urls = observed_link_urls - expected_link_urls
        if missing_urls or stale_urls:
            errors.append(
                f"{link_audit_path}: URL coverage differs from canonical catalog "
                f"({len(missing_urls)} missing, {len(stale_urls)} stale)"
            )
        if unsafe_rows:
            errors.append(f"{link_audit_path}: {unsafe_rows} row(s) retain unsafe URL/error material")

    docs = Path("docs")
    pairs = [
        (data_path, docs / metadata["data_file"]),
        (schema_path, docs / metadata["schema_file"]),
        (Path("metadata.jsonld"), docs / "metadata.jsonld"),
        (Path("assets/fonts/SourceSans3-Variable.ttf"), docs / "assets/fonts/SourceSans3-Variable.ttf"),
        (Path("assets/fonts/OFL.txt"), docs / "assets/fonts/OFL.txt"),
    ]
    for source, published in pairs:
        if not source.is_file():
            errors.append(f"missing generated/source artifact: {source}")
        if not published.is_file():
            errors.append(f"missing public distribution: {published}")
        elif source.is_file() and source.read_bytes() != published.read_bytes():
            errors.append(f"public distribution differs from source: {published}")

    metadata_path = Path("metadata.jsonld")
    if metadata_path.is_file():
        jsonld = json.loads(metadata_path.read_text(encoding="utf-8"))
        required_terms = {
            "dct:identifier",
            "dct:title",
            "dct:description",
            "dct:accessRights",
            "dcat:landingPage",
            "dcat:distribution",
            "dct:provenance",
            "prov:wasDerivedFrom",
            "dct:conformsTo",
        }
        absent = sorted(required_terms - set(jsonld))
        if absent:
            errors.append(f"metadata.jsonld: missing FAIR terms {', '.join(absent)}")
        if jsonld.get("schema:numberOfItems") != len(records):
            errors.append("metadata.jsonld: record count does not match canonical data")
        if metadata.get("license"):
            if "dct:license" not in jsonld:
                errors.append("metadata.jsonld: configured licence was not emitted")
        else:
            message = "reuse licence is unresolved; FAIR R1.1 and legal reuse remain blocked"
            (errors if release else warnings).append(message)

        index_path = docs / "index.html"
        if not index_path.is_file():
            errors.append(f"missing generated page: {index_path}")
        else:
            parser = FairScriptParser()
            parser.feed(index_path.read_text(encoding="utf-8"))
            if not parser.parts:
                errors.append("docs/index.html: embedded FAIR JSON-LD not found")
            else:
                embedded = json.loads("".join(parser.parts))
                if embedded != jsonld:
                    errors.append("docs/index.html: embedded JSON-LD differs from metadata.jsonld")

    if not metadata.get("publisher"):
        message = "formal publisher identity is unresolved"
        (errors if release else warnings).append(message)
    if not metadata.get("release_ref"):
        message = "published release reference is unresolved (expected a human-created tag or release URL)"
        (errors if release else warnings).append(message)
    elif not is_http_url(metadata["release_ref"]):
        errors.append("resource_metadata.json: release_ref must be an HTTP(S) URL")
    elif release:
        expected_release_ref = metadata["repository"].rstrip("/") + "/releases/tag/v" + metadata["resource_version"]
        if metadata["release_ref"].rstrip("/") != expected_release_ref:
            errors.append(
                "resource_metadata.json: release_ref must match the repository and resource_version "
                f"(expected {expected_release_ref})"
            )
    if release and ("preview" in metadata["resource_version"].casefold() or "-rc" in metadata["resource_version"].casefold()):
        errors.append("resource_version is still a preview/release candidate")
    print(f"VALIDATION profile={profile} records={len(records)}")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"PASS: 0 errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release",
        action="store_true",
        help="Turn unresolved governance and evidence coverage into hard failures.",
    )
    args = parser.parse_args()
    raise SystemExit(main(release=args.release))

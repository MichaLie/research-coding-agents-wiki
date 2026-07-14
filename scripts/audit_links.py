#!/usr/bin/env python3
"""Resolve every catalog URL and write a provenance-preserving TSV audit.

This verifies network resolution and captures page titles. It does not by itself
prove that a page supports every catalog claim; flagged rows require source
appraisal.
"""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fair_metadata import load_resource_metadata

USER_AGENT = (
    "Mozilla/5.0 (compatible; CatalogFairAudit/1.0; "
    "+https://github.com/MichaLie)"
)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def sanitize_url(value: str) -> str:
    """Keep redirect provenance without persisting query values or fragments."""
    if not value:
        return ""
    parsed = urllib.parse.urlsplit(value)
    return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", ""))


def sanitize_error(exc: BaseException) -> str:
    """Record the failure class, never exception text that may contain a URL or secret."""
    return type(exc).__name__


def occurrences(profile: str, records: list[dict]) -> list[dict]:
    rows: list[dict] = []
    for record in records:
        common = {"record_id": record["id"], "record_name": record["name"]}
        if profile == "foundation-models":
            fields = ("paper_links", "code_links")
            for field in fields:
                for index, link in enumerate(record.get(field, [])):
                    rows.append({**common, "field": f"{field}[{index}]", "url": link["url"]})
        elif profile == "autonomous-agents":
            fields = ("paper_links", "repo_links")
            for field in fields:
                for index, link in enumerate(record.get(field, [])):
                    rows.append({**common, "field": f"{field}[{index}]", "url": link["url"]})
        elif profile == "coding-agents":
            for field, url in record.get("links", {}).items():
                if url:
                    rows.append({**common, "field": f"links.{field}", "url": url})
            for index, url in enumerate(record.get("sources", [])):
                rows.append({**common, "field": f"sources[{index}]", "url": url})
        else:
            raise ValueError(f"unknown profile {profile!r}")
    return rows


def clean_title(payload: bytes, content_type: str) -> str:
    if "html" not in content_type.casefold():
        return ""
    text = payload.decode("utf-8", errors="replace")
    match = TITLE_RE.search(text)
    if not match:
        return ""
    value = TAG_RE.sub(" ", match.group(1))
    return SPACE_RE.sub(" ", html.unescape(value)).strip()[:500]


def _fetch_once(url: str, timeout: float) -> dict:
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.5",
            "Range": "bytes=0-131071",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(
            request,
            timeout=timeout,
            context=ssl.create_default_context(),
        ) as response:
            payload = response.read(131072)
            status = response.getcode() or 200
            content_type = response.headers.get("Content-Type", "").split(";", 1)[0]
            final_url = sanitize_url(response.geturl())
            outcome = "reachable" if 200 <= status < 400 else "http_error"
            return {
                "outcome": outcome,
                "http_status": status,
                "final_url": final_url,
                "content_type": content_type,
                "page_title": clean_title(payload, content_type),
                "checked_at": checked_at,
                "error": "",
            }
    except urllib.error.HTTPError as exc:
        status = exc.code
        if status in {401, 403, 429} or 300 <= status < 400:
            outcome = "restricted"
        elif status in {404, 410}:
            outcome = "missing"
        else:
            outcome = "http_error"
        content_type = exc.headers.get("Content-Type", "").split(";", 1)[0]
        try:
            payload = exc.read(131072)
        except Exception:
            payload = b""
        return {
            "outcome": outcome,
            "http_status": status,
            "final_url": sanitize_url(exc.geturl() or url),
            "content_type": content_type,
            "page_title": clean_title(payload, content_type),
            "checked_at": checked_at,
            "error": sanitize_error(exc),
        }
    except Exception as exc:
        return {
            "outcome": "network_error",
            "http_status": "",
            "final_url": "",
            "content_type": "",
            "page_title": "",
            "checked_at": checked_at,
            "error": sanitize_error(exc),
        }


def fetch(url: str, timeout: float) -> dict:
    """Retry one transient network failure; never retry or soften HTTP outcomes."""
    first = _fetch_once(url, timeout)
    if first["outcome"] != "network_error":
        return first
    time.sleep(0.5)
    second = _fetch_once(url, timeout)
    if second["outcome"] == "network_error":
        second["error"] = f"attempt 1: {first['error']}; attempt 2: {second['error']}"
    return second


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="evidence/link_audit.tsv")
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    metadata = load_resource_metadata()
    records = json.loads(Path(metadata["data_file"]).read_text(encoding="utf-8"))
    rows = occurrences(metadata["profile"], records)
    urls = sorted({row["url"] for row in rows})
    results: dict[str, dict] = {}

    probe = sanitize_url("https://example.invalid/path?auth_token=secret&state=opaque#fragment")
    if probe != "https://example.invalid/path":
        raise SystemExit("redirect sanitization self-check failed")

    print(f"checking {len(urls)} unique URLs across {len(rows)} catalog link occurrences")
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(fetch, url, args.timeout): url for url in urls}
        done = 0
        for future in as_completed(futures):
            url = futures[future]
            results[url] = future.result()
            done += 1
            if done % 100 == 0 or done == len(urls):
                print(f"checked {done}/{len(urls)}")

    unsafe_results = [
        url for url, result in results.items()
        if result.get("final_url") and (
            urllib.parse.urlsplit(result["final_url"]).query
            or urllib.parse.urlsplit(result["final_url"]).fragment
        )
    ]
    if unsafe_results:
        raise SystemExit(f"refusing to write {len(unsafe_results)} unsanitized redirect URL(s)")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "record_id",
        "record_name",
        "field",
        "url",
        "outcome",
        "http_status",
        "final_url",
        "content_type",
        "page_title",
        "error",
        "checked_at",
    ]
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in sorted(rows, key=lambda item: (item["record_id"], item["field"], item["url"])):
            writer.writerow({**row, **results[row["url"]]})

    counts: dict[str, int] = {}
    for result in results.values():
        counts[result["outcome"]] = counts.get(result["outcome"], 0) + 1
    print(f"wrote {output}: {counts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

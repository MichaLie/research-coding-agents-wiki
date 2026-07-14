#!/usr/bin/env python3
"""Dependency-free FAIR metadata support for the catalog build.

The human-maintained inputs are resource_metadata.json, schema.json, and the
canonical catalog JSON. Generated copies under docs/ must never be hand-edited.
"""
from __future__ import annotations

import hashlib
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

CONFIG_PATH = Path("resource_metadata.json")
SCHEMA_PATH = Path("schema.json")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PUBLIC_ACCESS = "http://publications.europa.eu/resource/authority/access-right/PUBLIC"


def load_resource_metadata(path: Path = CONFIG_PATH) -> dict:
    metadata = json.loads(path.read_text(encoding="utf-8"))
    required = (
        "identifier",
        "title",
        "description",
        "resource_version",
        "issued",
        "modified",
        "data_file",
        "schema_file",
        "repository",
        "baseline_commit",
        "baseline_commit_url",
        "release_ref",
        "creator",
        "rights_statement",
        "provenance",
        "keywords",
        "evidence_statement",
    )
    missing = [key for key in required if key not in metadata]
    if missing:
        raise ValueError(f"{path}: missing required metadata fields: {', '.join(missing)}")
    if not metadata["identifier"].startswith("https://"):
        raise ValueError(f"{path}: identifier must be an HTTPS URL")
    if not re.fullmatch(r"[0-9a-f]{40}", metadata["baseline_commit"]):
        raise ValueError(f"{path}: baseline_commit must be a full Git SHA")
    if not metadata["baseline_commit_url"].startswith("https://"):
        raise ValueError(f"{path}: baseline_commit_url must be an HTTPS URL")
    if metadata.get("release_ref") is not None and not str(metadata["release_ref"]).startswith("https://"):
        raise ValueError(f"{path}: release_ref must be null or an HTTPS tag/release URL")
    for key in ("issued", "modified"):
        if not DATE_RE.fullmatch(metadata[key]):
            raise ValueError(f"{path}: {key} must use YYYY-MM-DD")
    for field in ("creator", "publisher"):
        agent = metadata.get(field)
        if agent is None and field == "publisher":
            continue
        if not isinstance(agent, dict) or not agent.get("name") or not agent.get("url"):
            raise ValueError(f"{path}: {field} requires name and url")
        if agent.get("type", "Person") not in {"Person", "Organization"}:
            raise ValueError(f"{path}: {field}.type must be Person or Organization")
        affiliation = agent.get("affiliation")
        if affiliation and (not isinstance(affiliation, dict) or not affiliation.get("name") or not affiliation.get("url")):
            raise ValueError(f"{path}: {field}.affiliation requires name and url")
    return metadata


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _iri(value: str) -> dict:
    return {"@id": value}


def _agent(value: dict) -> dict:
    agent_type = value.get("type", "Person")
    if agent_type not in {"Person", "Organization"}:
        raise ValueError(f"agent type must be Person or Organization, not {agent_type!r}")
    agent = {
        "@id": value["url"],
        "@type": f"schema:{agent_type}",
        "schema:name": value["name"],
    }
    if value.get("email"):
        agent["schema:email"] = "mailto:" + value["email"]
    if value.get("affiliation"):
        affiliation = value["affiliation"]
        agent["schema:affiliation"] = {
            "@id": affiliation["url"],
            "@type": "schema:Organization",
            "schema:name": affiliation["name"],
        }
    return agent


def _distribution(
    *,
    identifier: str,
    suffix: str,
    title: str,
    download_url: str,
    media_type: str,
    media_type_iri: str,
    source_path: Path,
) -> dict:
    return {
        "@id": f"{identifier}#distribution-{suffix}",
        "@type": ["dcat:Distribution", "schema:DataDownload"],
        "dct:title": title,
        "dcat:accessURL": _iri(identifier),
        "dcat:downloadURL": _iri(download_url),
        "dct:format": _iri(media_type_iri),
        "schema:encodingFormat": media_type,
        "dcat:byteSize": source_path.stat().st_size,
        "spdx:checksum": {
            "@type": "spdx:Checksum",
            "spdx:algorithm": _iri("http://spdx.org/rdf/terms#checksumAlgorithm_sha256"),
            "spdx:checksumValue": _sha256(source_path),
        },
    }


def build_jsonld(metadata: dict, data_path: str | Path, record_count: int) -> dict:
    data_path = Path(data_path)
    schema_path = Path(metadata["schema_file"])
    if data_path.name != metadata["data_file"]:
        raise ValueError(
            f"build input {data_path.name!r} does not match metadata data_file "
            f"{metadata['data_file']!r}"
        )
    if not schema_path.is_file():
        raise FileNotFoundError(schema_path)

    identifier = metadata["identifier"]
    base = identifier if identifier.endswith("/") else identifier + "/"
    creator = _agent(metadata["creator"])
    distributions = [
        _distribution(
            identifier=identifier,
            suffix="json",
            title="Canonical catalog data",
            download_url=urljoin(base, metadata["data_file"]),
            media_type="application/json",
            media_type_iri="https://www.iana.org/assignments/media-types/application/json",
            source_path=data_path,
        ),
        _distribution(
            identifier=identifier,
            suffix="schema",
            title="JSON Schema for the catalog",
            download_url=urljoin(base, metadata["schema_file"]),
            media_type="application/schema+json",
            media_type_iri="https://www.iana.org/assignments/media-types/application/schema+json",
            source_path=schema_path,
        ),
        {
            "@id": f"{identifier}#distribution-html",
            "@type": "dcat:Distribution",
            "dct:title": "Interactive HTML catalog",
            "dcat:accessURL": _iri(identifier),
            "dct:format": _iri("https://www.iana.org/assignments/media-types/text/html"),
        },
    ]

    resource = {
        "@context": {
            "dcat": "http://www.w3.org/ns/dcat#",
            "dct": "http://purl.org/dc/terms/",
            "prov": "http://www.w3.org/ns/prov#",
            "schema": "https://schema.org/",
            "spdx": "http://spdx.org/rdf/terms#",
            "xsd": "http://www.w3.org/2001/XMLSchema#",
        },
        "@id": identifier,
        "@type": ["dcat:Dataset", "schema:Dataset"],
        "dct:identifier": identifier,
        "schema:identifier": identifier,
        "dct:title": metadata["title"],
        "schema:name": metadata["title"],
        "dct:description": metadata["description"],
        "schema:description": metadata["description"],
        "dct:creator": creator,
        "schema:creator": creator,
        "dct:issued": {"@value": metadata["issued"], "@type": "xsd:date"},
        "dct:modified": {"@value": metadata["modified"], "@type": "xsd:date"},
        "schema:dateModified": metadata["modified"],
        "schema:version": metadata["resource_version"],
        "schema:url": _iri(identifier),
        "dcat:landingPage": _iri(identifier),
        "dct:accessRights": _iri(PUBLIC_ACCESS),
        "schema:isAccessibleForFree": True,
        "dct:language": _iri("http://id.loc.gov/vocabulary/iso639-1/en"),
        "dct:source": _iri(metadata["repository"]),
        "schema:sameAs": _iri(metadata["repository"]),
        "prov:wasDerivedFrom": _iri(metadata["baseline_commit_url"]),
        "dct:provenance": metadata["provenance"],
        "dct:conformsTo": [
            _iri("https://doi.org/10.1038/sdata.2016.18"),
            _iri("https://www.w3.org/TR/vocab-dcat-3/"),
            _iri("https://www.w3.org/TR/json-ld11/"),
            _iri("https://json-schema.org/draft/2020-12/schema"),
        ],
        "dcat:keyword": metadata["keywords"],
        "schema:numberOfItems": record_count,
        "dcat:distribution": distributions,
        "prov:wasGeneratedBy": {
            "@id": metadata.get("release_ref") or f"{identifier}#local-preview-build-{metadata['resource_version']}",
            "@type": "prov:Activity",
            "dct:type": "Versioned release build" if metadata.get("release_ref") else "Working build without an immutable release reference",
            "prov:used": [_iri(metadata["repository"]), _iri(metadata["baseline_commit_url"])],
            "prov:endedAtTime": {
                "@value": metadata["modified"],
                "@type": "xsd:date",
            },
        },
    }

    if metadata.get("is_part_of"):
        resource["dct:isPartOf"] = _iri(metadata["is_part_of"])
    if metadata.get("publisher"):
        resource["dct:publisher"] = _agent(metadata["publisher"])
    resource["dct:rights"] = metadata["rights_statement"]
    if metadata.get("license"):
        resource["dct:license"] = _iri(metadata["license"])
        resource["schema:license"] = _iri(metadata["license"])

    if metadata.get("under_review_file"):
        register_path = Path(metadata["under_review_file"])
        register = json.loads(register_path.read_text(encoding="utf-8"))
        resource["dct:relation"] = {
            "@id": urljoin(base, register_path.name),
            "@type": "dcat:Dataset",
            "dct:title": register["title"],
            "dct:description": register["description"],
            "schema:numberOfItems": register["record_count"],
            "dct:type": "Editorial under-review register; not part of the canonical displayed catalog",
        }

    return resource


def fair_head(metadata: dict, jsonld: dict) -> str:
    identifier = metadata["identifier"]
    base = identifier if identifier.endswith("/") else identifier + "/"
    parts = [
        f'<link rel="canonical" href="{html.escape(identifier, quote=True)}">',
        (
            '<link rel="alternate" type="application/ld+json" '
            f'href="{html.escape(urljoin(base, "metadata.jsonld"), quote=True)}" '
            'title="FAIR metadata">'
        ),
        (
            '<link rel="describedby" type="application/schema+json" '
            f'href="{html.escape(urljoin(base, metadata["schema_file"]), quote=True)}">'
        ),
    ]
    if metadata.get("license"):
        parts.append(
            f'<link rel="license" href="{html.escape(metadata["license"], quote=True)}">'
        )
    payload = json.dumps(jsonld, ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    parts.append(
        '<script id="fair-metadata" type="application/ld+json">'
        + payload
        + "</script>"
    )
    return "\n".join(parts)


def publish_fair_artifacts(
    metadata: dict,
    jsonld: dict,
    *,
    data_path: str | Path,
    output_path: str | Path,
) -> None:
    data_path = Path(data_path)
    output_path = Path(output_path)
    serialized = json.dumps(jsonld, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    Path("metadata.jsonld").write_text(serialized, encoding="utf-8")

    if output_path.parent.name != "docs":
        return

    docs = output_path.parent
    docs.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(data_path, docs / metadata["data_file"])
    shutil.copyfile(Path(metadata["schema_file"]), docs / metadata["schema_file"])
    (docs / "metadata.jsonld").write_text(serialized, encoding="utf-8")

    identifier = metadata["identifier"]
    base = identifier if identifier.endswith("/") else identifier + "/"
    (docs / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nSitemap: " + urljoin(base, "sitemap.xml") + "\n",
        encoding="utf-8",
    )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{html.escape(identifier)}</loc>\n"
        f"    <lastmod>{metadata['modified']}</lastmod>\n"
        "  </url>\n"
        "</urlset>\n"
    )
    (docs / "sitemap.xml").write_text(sitemap, encoding="utf-8")

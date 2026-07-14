#!/usr/bin/env python3
"""Build every public artifact twice, prove determinism, then validate."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import subprocess
from pathlib import Path

from fair_metadata import load_resource_metadata
from validate_catalog import main as validate


COMMANDS = {
    "foundation-models": [
        ["python3", "build_html.py", "models_final.json", "docs/index.html"],
        ["python3", "build_html.py", "models_final.json", "biological_foundation_models_wiki.html"],
        ["python3", "build_md.py"],
    ],
    "autonomous-agents": [
        ["python3", "build_html.py", "agents_final.json", "docs/index.html"],
        ["python3", "build_html.py", "agents_final.json", "autonomous_stem_agents_wiki.html"],
        ["python3", "build_md.py"],
    ],
    "coding-agents": [
        ["python3", "build_html.py", "tools.json", "docs/index.html"],
    ],
}

OUTPUTS = {
    "foundation-models": [
        "biological_foundation_models_wiki.html",
        "biological_foundation_models_wiki.md",
        "metadata.jsonld",
        "docs/index.html",
        "docs/models_final.json",
        "docs/schema.json",
        "docs/metadata.jsonld",
        "docs/biological_foundation_models_wiki.md",
        "docs/robots.txt",
        "docs/sitemap.xml",
        "docs/assets/fonts/SourceSans3-Variable.ttf",
        "docs/assets/fonts/OFL.txt",
    ],
    "autonomous-agents": [
        "autonomous_stem_agents_wiki.html",
        "autonomous_stem_agents_wiki.md",
        "metadata.jsonld",
        "docs/index.html",
        "docs/agents_final.json",
        "docs/schema.json",
        "docs/metadata.jsonld",
        "docs/autonomous_stem_agents_wiki.md",
        "docs/robots.txt",
        "docs/sitemap.xml",
    ],
    "coding-agents": [
        "metadata.jsonld",
        "docs/index.html",
        "docs/tools.json",
        "docs/schema.json",
        "docs/metadata.jsonld",
        "docs/robots.txt",
        "docs/sitemap.xml",
    ],
}


def digest(path: str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_build(commands: list[list[str]]) -> None:
    for command in commands:
        subprocess.check_call(command)
    font_dir = Path("docs/assets/fonts")
    font_dir.mkdir(parents=True, exist_ok=True)
    for name in ("SourceSans3-Variable.ttf", "OFL.txt"):
        shutil.copyfile(Path("assets/fonts") / name, font_dir / name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release", action="store_true")
    args = parser.parse_args()

    profile = load_resource_metadata()["profile"]
    commands = COMMANDS[profile]
    outputs = OUTPUTS[profile]

    run_build(commands)
    first = {path: digest(path) for path in outputs}
    run_build(commands)
    second = {path: digest(path) for path in outputs}

    changed = [path for path in outputs if first[path] != second[path]]
    if changed:
        print("ERROR: non-deterministic build outputs:")
        for path in changed:
            print(f"  {path}")
        return 1
    print(f"DETERMINISM PASS: {len(outputs)} generated artifacts are byte-stable")
    return validate(release=args.release)


if __name__ == "__main__":
    raise SystemExit(main())

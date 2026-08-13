#!/usr/bin/env python3
"""Apply the 2026-08-13 first-party re-verification and additions to tools.json.

This is a dated, reviewable, idempotent data migration (running it twice is a
no-op the second time). Every change is backed by the delegated verification
evidence in evidence/reverify-2026-08-13/ and evidence/additions-2026-08-13/,
each claim of which carries a fetched first-party source URL and quote. It is
intentionally conservative: unverified claims are removed or labelled, cloud
use is never treated as acceptable for special-category data, and absent
vendor commitments are classified at the strict end of the vocabulary.

Scope:
- All 43 retained records were re-checked on 2026-08-13; every record gets
  verified=2026-08-13, and the 28 materially changed records also get
  date_modified=2026-08-13.
- 17 new records (accepted by per-candidate first-party verification) are
  appended. Rejected candidates (shai: maintenance health; Rowboat: scope)
  are documented in evidence/LIVE_AUDIT_2026-08-13.md and add no records.
- Windsurf -> Devin Desktop is completed as a first-party-confirmed rename
  (windsurf.com 308-redirects to devin.ai/desktop) following the existing
  renamed-record convention (name updated, former name kept in aliases).
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools.json"
TODAY = "2026-08-13"

GENERIC_RESIDUAL = (
    "Conditional route: revalidate the exact deployment, model endpoint, "
    "integrations, telemetry, and institutional approval before use."
)

records = json.loads(DATA.read_text(encoding="utf-8"))
by_id = {record["id"]: record for record in records}

changed_ids: set[str] = set()


def patch(identifier: str, **fields: object) -> None:
    """Set absolute field values (dicts are merged); marks the record changed."""
    record = by_id[identifier]
    for key, value in fields.items():
        if isinstance(value, dict) and isinstance(record.get(key), dict):
            record[key].update(value)
        else:
            record[key] = value
    changed_ids.add(identifier)


def replace_in(identifier: str, field: str, old: str, new: str) -> None:
    """Idempotent substring update backed by a reverify change entry."""
    record = by_id[identifier]
    value = record[field]
    if old in value:
        record[field] = value.replace(old, new)
    elif new not in value:
        raise SystemExit(f"{identifier}.{field}: neither old nor new text present")
    changed_ids.add(identifier)


# ---------------------------------------------------------------------------
# Re-verification updates (evidence/reverify-2026-08-13/rca_reverify_1..6.json)
# ---------------------------------------------------------------------------

# rca-claude-code (claude.com/pricing; code.claude.com/docs/en/zero-data-retention)
patch(
    "rca-claude-code",
    pricing=(
        "Free (limited) - Pro $20/mo - Max $100-200/mo - Team Standard $20/seat/mo "
        "(annual; $25 monthly) - Team Premium $100/seat/mo (annual; $125 monthly) - "
        "Enterprise: seat price plus usage at API rates, starting at $20/seat "
        "(self-serve and sales-assisted). Education/university plan available for "
        "institutions (contact sales)"
    ),
)
replace_in(
    "rca-claude-code",
    "data_handling_note",
    "but remote/web sessions and third-party integrations require separate scope review.",
    "and under ZDR features that require storing prompts or completions (Claude Code on "
    "the Web, Desktop cloud sessions, Artifacts, feedback submission, Remote Control) "
    "are automatically disabled at the backend level; third-party integrations and MCP "
    "servers remain outside ZDR scope and require separate review.",
)

# rca-openai-codex (learn.chatgpt.com/docs/models)
patch(
    "rca-openai-codex",
    model_backend=(
        "GPT-5.6 family (5.6 Sol, 5.6 Terra, 5.6 Luna) plus 5.3 Codex Spark as the "
        "recommended set; gpt-5.4/gpt-5.4-mini are deprecated and retire 2026-08-31. "
        "Codex can also be pointed at any third-party model/provider supporting the "
        "Chat Completions or Responses APIs (availability changes over time)"
    ),
    sources=[
        "https://developers.openai.com/api/docs/guides/your-data",
        "https://openai.com/business-data/",
        "https://openai.com/business/pricing/",
        "https://openai.com/index/codex-flexible-pricing-for-teams/",
        "https://help.openai.com/en/articles/20001147-codex-credits-for-students-terms-of-service",
        "https://learn.chatgpt.com/docs/models",
    ],
)

# rca-gemini-cli (developers.googleblog.com transition announcement)
patch(
    "rca-gemini-cli",
    model_backend=(
        "Gemini models via paid API, Vertex AI, or Gemini Code Assist; consumer "
        "Google-account access ended 2026-06-18 and moved to the separate Antigravity "
        "CLI product"
    ),
    data_handling_note=(
        "The Apache-2.0 Gemini CLI remains an active open-source client with "
        "enterprise-supported paid API, Vertex AI, and Code Assist routes. Gemini CLI "
        "and the Code Assist IDE extensions stopped serving consumer free-tier and "
        "Google AI Pro/Ultra requests on 2026-06-18; Gemini Code Assist "
        "Standard/Enterprise license access is unchanged. Paid Gemini API, Vertex AI, "
        "and enterprise Code Assist do not train on customer data. The completed "
        "consumer migration to Antigravity CLI does not rename or close the Gemini CLI "
        "project."
    ),
    pricing=(
        "Open-source CLI is free; model use follows Gemini API, Vertex AI, or Code "
        "Assist quotas and pricing. Consumer Google-account access ended 2026-06-18 "
        "and moved to the separate Antigravity CLI product."
    ),
    academic=(
        "No dedicated academic/student discount program identified. Since 2026-06-18 "
        "Gemini CLI itself has no free consumer route; free consumer access exists "
        "only via the separate Antigravity CLI product."
    ),
    tier_gate="paid API / Vertex / enterprise Code Assist (no consumer route since 2026-06-18)",
    notes=(
        "Keep Gemini CLI and Google Antigravity as separate records: Gemini CLI "
        "remains an Apache-2.0 client for paid API/Vertex/enterprise use, while "
        "consumer access moved to the proprietary Antigravity CLI on 2026-06-18. The "
        "project's github.io docs still describe the retired consumer free tier; the "
        "dated first-party blog announcement is treated as authoritative."
    ),
)

# rca-cursor (cursor.com/pricing, /students, /blog/cursor-start)
patch(
    "rca-cursor",
    pricing=(
        "Hobby (free) - Pro ($20/mo) - Teams ($40/user/mo) - Enterprise (custom); "
        "~20% discount on annual billing. A Cursor Start individual tier launched "
        "2026-07-28 for India (INR 649/month, billed in INR). Current Pro+/Ultra "
        "prices were not displayed on the fetched pricing page and should be checked "
        "directly rather than assumed from earlier figures."
    ),
    academic=(
        "No active student offer; the official students page points only to future "
        "on-campus and online-event promotions."
    ),
    sources=[
        "https://cursor.com/data-use",
        "https://cursor.com/security",
        "https://cursor.com/privacy",
        "https://cursor.com/terms/dpa",
        "https://cursor.com/pricing",
        "https://cursor.com/students",
        "https://cursor.com/blog/cursor-start",
    ],
)

# rca-github-copilot (docs.github.com/en/copilot/get-started/plans)
patch(
    "rca-github-copilot",
    academic=(
        "Copilot Student plan is listed as available and free for verified students; "
        "verified teachers and popular open-source maintainers may be eligible for "
        "free Copilot Pro."
    ),
)

# rca-windsurf -> Devin Desktop (windsurf.com 308-redirects to devin.ai/desktop;
# cognition.com/blog/introducing-devin-desktop). Rename convention follows the
# existing renamed-record precedent (rca-chatgpt-advanced-data-analysis).
patch(
    "rca-windsurf",
    name="Devin Desktop",
    current_name="Devin Desktop",
    status="renamed",
    aliases=["Windsurf"],
    model_backend=(
        "Proprietary SWE models plus frontier models (OpenAI, Claude, Gemini on paid "
        "plans); the default SWE model version changes over time and was not "
        "re-confirmed on current pages"
    ),
    pricing="Free ($0) - Pro ($20/mo) - Max ($200/mo) - Teams ($80/mo base + $40/seat) - Enterprise (custom). No student discount is shown on the current pricing page.",
    notes=(
        "Renamed to Devin Desktop after the Cognition acquisition: windsurf.com now "
        "redirects to devin.ai/desktop, whose FAQ states 'Devin Desktop is the new "
        "name for Windsurf'; plans and settings carry over via update. The Windsurf "
        "name survives only for the JetBrains plugin. It is cloud-based even when the "
        "client runs locally; vendor-hosted dedicated deployment must not be described "
        "as self-hosted or on-prem."
    ),
    confidence="high",
    sources=[
        "https://cognition.com/blog/introducing-devin-desktop",
        "https://cognition.com/legal/platform-terms-of-service",
        "https://cognition.com/legal/privacy-policy",
        "https://docs.devin.ai/enterprise/deployment/overview",
        "https://docs.devin.ai/admin/billing/self-serve",
        "https://cognition.com/documents/Cognition-DPA.pdf",
        "https://devin.ai/desktop",
    ],
)

# rca-google-antigravity (antigravity.google/blog, /pricing)
patch(
    "rca-google-antigravity",
    model_backend=(
        "Gemini 3.1 Pro / 3.5 Flash / 3.6 Flash (Gemini 3.6 Flash announced "
        "2026-07-21); non-Google models remain supported (the terms name Anthropic as "
        "an example third-party model provider). Earlier GPT-OSS support was not "
        "re-confirmed on current first-party pages."
    ),
    notes=(
        "Proprietary agentic development platform distinct from the open-source "
        "Gemini CLI. Antigravity 2.0 (agent command center), Antigravity CLI, and the "
        "Antigravity SDK are live surfaces; the Organization plan via Google Cloud "
        "grants access to 2.0 and the CLI with consumption-based API pricing. "
        "Consumer and enterprise/GCP data terms differ materially; enterprise access "
        "is no longer invite-only."
    ),
    sources=[
        "https://antigravity.google/terms",
        "https://antigravity.google/blog/google-antigravity-for-enterprises",
        "https://antigravity.google/blog/changes-to-antigravity-plans",
        "https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/",
        "https://antigravity.google/blog",
    ],
)

# rca-tabnine (tabnine.com/pricing)
patch(
    "rca-tabnine",
    data_handling_note=(
        "Paid cloud plans document no-training/no-retention handling (SaaS code is "
        "processed ephemerally and immediately discarded). The pricing page now "
        "advertises fully private deployment on SaaS or self-hosted (VPC, "
        "on-premises, optionally fully air-gapped) for both self-service tiers, not "
        "only Enterprise. Confirm who controls any VPC deployment before treating it "
        "as the qualifying boundary."
    ),
    tier_gate=(
        "self-hosted/on-prem/air-gapped installation on institution-controlled "
        "infrastructure (advertised on both self-service tiers); Tabnine SaaS does "
        "not qualify"
    ),
    pricing=(
        "Code Assistant $39/user/month - Agentic Platform $59/user/month (both "
        "annual; free tier discontinued April 2025; no free tier or trial is shown on "
        "the current pricing page). Enterprise Context Engine priced on request."
    ),
    suitability_notes={
        "special": (
            "Requires an actual self-hosted/on-prem/air-gapped installation on "
            "institution-controlled infrastructure (now advertised on both "
            "self-service tiers). Confirm who controls any VPC deployment; cloud "
            "infrastructure certifications do not substitute for product-scope "
            "evidence."
        ),
    },
    special_route={
        "required_controls": [
            "Requires an actual self-hosted/on-prem/air-gapped installation on "
            "institution-controlled infrastructure (now advertised on both "
            "self-service tiers). Confirm who controls any VPC deployment; cloud "
            "infrastructure certifications do not substitute for product-scope "
            "evidence."
        ],
    },
    notes=(
        "Privacy-focused commercial assistant. The qualifying special-category path "
        "is a private/self-hosted installation, now advertised on both self-service "
        "tiers as well as Enterprise; cloud-provider datacenter certifications must "
        "not be presented as Tabnine product certifications."
    ),
)

# rca-openhands (GitHub API: repo moved to OpenHands/OpenHands, MIT)
patch(
    "rca-openhands",
    software_license="MIT",
    license_status="confirmed",
    notes=(
        "Open-source/self-hostable coding agent with a separate cloud service. The "
        "repository moved to the OpenHands GitHub org (MIT license confirmed via the "
        "GitHub API); docs now describe a re-architected stack (Agent Canvas browser "
        "client, Software Agent SDK, Agent Server, Sandbox Server) with the legacy "
        "Local GUI deprecated. Data safety depends on deployment and the configured "
        "model route."
    ),
    sources=[
        "https://www.openhands.dev/privacy",
        "https://www.openhands.dev/pricing",
        "https://docs.openhands.dev/overview/introduction",
        "https://docs.openhands.dev/enterprise",
        "https://github.com/OpenHands/OpenHands/releases",
        "https://api.github.com/repos/OpenHands/OpenHands",
    ],
)

# rca-julius-ai (julius.ai/pricing, /privacy-policy, /legal/dpa now 404)
patch(
    "rca-julius-ai",
    model_backend=(
        "Julius Lite/Julius models plus GPT-5.6, Claude Sonnet 5 (Plus and up), and "
        "Claude Fable 5 (Pro and up), hosted by Julius; Gemini is no longer "
        "advertised on the pricing page"
    ),
    pricing=(
        "Free; Plus $20 monthly/$16 annual; Pro $45/$37; Max $200/$166; Business "
        "$450/$375; Enterprise custom. Credit allowances: Plus 2,000, Pro 5,000, Max "
        "25,000, Business 60,000 credits/month. The former Ultra tier is no longer "
        "shown."
    ),
    academic=(
        "The formerly advertised 50% student/educator discount is absent from the "
        "current pricing and education pages; treat it as unverified."
    ),
    data_handling_note=(
        "Julius states that user data is not used for internal or external model "
        "training. Processing and storage occur in the US; Enterprise provides a DPA. "
        "The former public DPA URL (julius.ai/legal/dpa) now returns 404, but the "
        "privacy policy (updated 2026-07-01) still offers a DPA with standard "
        "contractual clauses. No public HIPAA BAA was confirmed, so regulated "
        "health/genetic/clinical data remains excluded."
    ),
    compliance=[
        "SOC 2 Type 2 (stated in site footer and pricing table)",
        "GDPR (not re-confirmed on current pages)",
        "CCPA",
        "TX-RAMP (not re-confirmed on current pages)",
    ],
    use_cases=[
        "natural language data analysis",
        "data visualization",
        "reproducible notebooks",
        "database querying (Snowflake, BigQuery, PostgreSQL)",
        "automated reports",
        "slide/presentation generation",
        "Excel/CSV/PDF analysis",
        "website/web app and image/video generation (AI workspace features)",
    ],
    notes=(
        "Cloud service repositioned as an AI workspace (data analysis plus "
        "presentations, reports, websites, image and video generation) with a public "
        "no-training commitment. A DPA is still offered via the privacy policy, but "
        "the former public DPA page is dead; US processing/storage and the absence of "
        "a confirmed public BAA remain material boundaries."
    ),
    sources=[
        "https://julius.ai/privacy-policy",
        "https://julius.ai/security",
        "https://julius.ai/pricing",
        "https://julius.ai/docs/get-started/privacy-and-data-security",
    ],
)

# rca-hex-magic ('Magic' branding retired; hex.tech; learn.hex.tech ai-data-privacy)
patch(
    "rca-hex-magic",
    name="Hex",
    current_name="Hex",
    status="renamed",
    aliases=["Hex Magic"],
    data_handling_note=(
        "Hex's LLM providers (OpenAI, Anthropic) operate under zero-data-retention "
        "by default, with an admin-controllable exception for models that require "
        "safety retention (e.g. Claude Fable 5). Hex itself may use AI-session data "
        "for feature improvement unless the organization opts out in workspace "
        "settings. Personal-data use requires contractual controls, DPA, and "
        "appropriate residency; uploaded/output data still traverses Hex "
        "infrastructure. BYOK is Enterprise-only."
    ),
    pricing=(
        "Community (free) - Professional ($36/editor/month) - Team ($75/editor/month) "
        "- Enterprise (custom). Academic: Professional plan free for students and "
        "educators (contact support@hex.tech); non-profits also qualify."
    ),
    compliance=[
        "SOC 2 Type II",
        "HIPAA (BAA available)",
        "GDPR",
        "CCPA (not re-confirmed on current pages)",
        "EU-U.S. Data Privacy Framework (not re-confirmed on current pages)",
    ],
    notes=(
        "Collaborative cloud analytics platform. The 'Magic' AI branding is retired: "
        "AI features are now named agents (Notebook Agent on Professional+, Threads "
        "Agent and Semantic Model Agent on Team+, App Agent) under an 'AI Analytics "
        "Platform' positioning; the former record name is kept as an alias. Provider "
        "ZDR is not equivalent to Hex deleting or never using all AI-session data; "
        "organization opt-out and contract scope must be checked."
    ),
    sources=[
        "https://learn.hex.tech/docs/trust/ai-data-privacy",
        "https://hex.tech/security/",
        "https://trust.hex.tech",
        "https://hex.tech/pricing/",
        "https://hex.tech/blog/hipaa-multi-tenant/",
        "https://hex.tech/",
    ],
)

# rca-kiro (kiro.dev/docs/models/available-models/)
patch(
    "rca-kiro",
    model_backend=(
        "Amazon Bedrock backbone: Anthropic Claude Opus 5 and Sonnet 5 "
        "(experimental) alongside Opus 4.5-4.8, Sonnet 4.0-4.6, Haiku 4.5; OpenAI "
        "GPT-5.6 Sol/Terra/Luna (experimental); open-weight MiniMax M2.5/M2.1, GLM-5, "
        "DeepSeek 3.2, Qwen3 Coder Next (Kimi no longer listed); \"Auto\" mode "
        "selects dynamically"
    ),
    academic=(
        "Student program: eligible students at 11 universities (including Arizona "
        "State, Carnegie Mellon, Georgia Tech, NYU, University of Waterloo; "
        "'expanding to more universities soon') get 1,000 credits/month free for one "
        "year via SheerID verification; no credit card required. Startup program: up "
        "to one year of free Pro+ access. No general researcher or academic "
        "institutional discount documented."
    ),
    sources=[
        "https://kiro.dev/docs/privacy-and-security/data-protection/",
        "https://kiro.dev/docs/privacy-and-security/compliance-validation/",
        "https://kiro.dev/pricing/",
        "https://kiro.dev/docs/",
        "https://kiro.dev/docs/web/data-protection/",
        "https://kiro.dev/docs/models/available-models/",
    ],
)

# rca-zed (zed.dev/education; zed.dev/security 404)
patch(
    "rca-zed",
    academic=(
        "Verified students receive the Student plan free for 12 months with all Pro "
        "features, $10 monthly token credits, and unlimited edit predictions; Claude "
        "Fable, Claude Opus, and GPT Pro models are excluded. Verification uses a "
        "GitHub account plus a university email checked against JetBrains' university "
        "domain database."
    ),
)
replace_in(
    "rca-zed",
    "data_handling_note",
    "SOC 2 Type 1 certification in progress (not yet issued as of mid-2026).",
    "A previously stated in-progress SOC 2 Type 1 status could not be re-confirmed "
    "(zed.dev/security now returns 404); treat it as unverified.",
)

# rca-amp (ampcode.com/modes, /pricing, /security, /terms, /privacy-policy)
patch(
    "rca-amp",
    model_backend=(
        "Managed modes Low/Medium/High/Ultra plus Puck (navigation): Low = GLM-5.2 "
        "agent with GPT-5.6 Sol oracle; Medium = GPT-5.6 Sol; High = GPT-5.6 Sol "
        "with Fable 5 oracle; Ultra = Fable 5 agent with GPT-5.6 Sol oracle; Puck = "
        "GPT-5.6 Terra. Backend remains managed by Amp and is not user-configurable"
    ),
    data_handling="no-train",
    data_handling_note=(
        "The enterprise feature is now 'Minimal Data Retention' rather than ZDR: "
        "commercially reasonable efforts to minimize third-party LLM provider "
        "retention; providers do not train on customer data but may retain safety "
        "monitoring information for up to 30 days. Amp itself stores threads and "
        "customer content in US infrastructure (Google Cloud, AES-256 at rest); "
        "explicit deletion completes within 30 days, and enterprise workspace "
        "threads persist with the organization."
    ),
    pricing=(
        "Pay-as-you-go credits with zero markup on providers' API pricing for "
        "non-enterprise use, plus subscriptions: Megawatt $20/month (low and medium "
        "modes) and Gigawatt $200/month (all modes); linked third-party "
        "subscriptions (e.g. ChatGPT) incur no per-token fees. Purchased credits "
        "expire twelve months after purchase. A free tier remains, but the former "
        "$5 minimum and $10/day free-credit figures are no longer documented. "
        "Enterprise: +50% cost with a one-time $1,000 minimum purchase."
    ),
    academic=(
        "No dedicated academic or student discount program found. A free tier "
        "remains available to all users including researchers (the former $10/day "
        "credit figure is no longer documented). No evidence of institutional or "
        "academic pricing."
    ),
    notes=(
        "Cloud coding agent. Distinguish model-provider retention minimization from "
        "Amp's own storage of threads and customer content; no public DPA was "
        "confirmed during this audit. Vendor-identity discrepancy: the terms name "
        "Amp Frontier Corporation as the provider while the privacy policy still "
        "names Sourcegraph, Inc. as data controller; unresolved on first-party "
        "pages."
    ),
    sources=[
        "https://ampcode.com/security",
        "https://ampcode.com/privacy-policy",
        "https://ampcode.com/terms",
        "https://ampcode.com/manual#pricing",
        "https://ampcode.com/manual",
        "https://ampcode.com/news/drop-the-neo",
        "https://ampcode.com/modes",
        "https://ampcode.com/pricing",
    ],
)

# rca-sourcegraph-cody (sourcegraph.com/docs/cody/capabilities/supported-models)
patch(
    "rca-sourcegraph-cody",
    model_backend=(
        "Anthropic Claude (Opus 5, Sonnet 5, plus Opus 4.6-4.8, Sonnet 4.5/4.6, "
        "Haiku 4.5 incl. Thinking variants), OpenAI GPT-5.6 Sol/Terra/Luna, "
        "GPT-5.4/5.2/5.1/5 families, GPT-4o/-mini, o3, Google Gemini 2.5 Flash/Pro, "
        "3.1 Flash Lite/Pro, 3.5 Flash, Fireworks DeepSeek V2 Lite Base "
        "(autocomplete); BYOK/BYOLLM supported on Enterprise"
    ),
    academic=(
        "No published academic or student discount. Free and Pro tiers were "
        "discontinued in July 2025; no per-user price is published on the current "
        "pricing page (Enterprise starts around $16K/year). Contact sales for "
        "possible institutional pricing."
    ),
    notes=(
        "Active enterprise-only coding assistant integrated with Sourcegraph. Prior "
        "self-service plans have ended. The Cody Enterprise Terms of Use "
        "(cody-notice) was last modified 2024-02-15 and scopes itself to licenses "
        "granted before 2025-01-29; current enterprise contracts may supersede it, so "
        "assess model-provider routing under the actual contract."
    ),
    sources=[
        "https://sourcegraph.com/terms/cody-notice",
        "https://sourcegraph.com/docs/model-provider",
        "https://sourcegraph.com/pricing",
        "https://sourcegraph.com/docs/cody/faq",
        "https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans",
        "https://sourcegraph.com/changelog/releases",
        "https://sourcegraph.com/docs/cody/capabilities/supported-models",
    ],
)

# rca-opencode (opencode.ai/docs/zen/)
patch(
    "rca-opencode",
    model_backend=(
        "BYO-key (75+ providers via Models.dev: Claude, GPT, Gemini, AWS Bedrock, "
        "Groq, Azure, OpenRouter, Ollama, LM Studio, llama.cpp and others); optional "
        "hosted gateway (Zen, pay-as-you-go per-1M-token pricing; team workspaces "
        "free during beta)"
    ),
    pricing=(
        "OpenCode is open source. OpenCode Zen is pay-as-you-go (per-1M-token "
        "prices) with automatic $20 reload when balance falls below $5; the former "
        "Go/Black tiers no longer appear, and team workspaces are currently free in "
        "beta with pricing to be announced."
    ),
)

# rca-mistral-vibe (help.mistral.ai ZDR article; mistral.ai/pricing; releases)
patch(
    "rca-mistral-vibe",
    data_handling_note=(
        "Free, Pro, and Education accounts use inputs/outputs for training by "
        "default unless the user opts out. Team and Enterprise do not train. ZDR is "
        "available only with pay-as-you-go API usage, on a request Mistral approves "
        "at its discretion; it applies only to stateless API endpoints and is not "
        "available for Vibe Work or Chat on any plan. Vibe CLI stateless API calls "
        "follow the organization's API ZDR if enabled. Offline/local models create a "
        "separate controlled-infrastructure route."
    ),
    tier_gate=(
        "Team/Enterprise no-training; discretionary pay-as-you-go API-only ZDR "
        "(never Vibe Work/Chat); fully local model for special data"
    ),
    suitability_notes={
        "personal": (
            "Use Team/Enterprise no-training terms or discretionary pay-as-you-go "
            "API ZDR with an appropriate DPA; consumer opt-out alone is weaker."
        ),
    },
    pricing=(
        "Free: basic access with limited messages; Pro: $14.99/month; Team: "
        "$24.99/user/month (minimum $50/month); Enterprise: custom; "
        "Education/student offer: $5.99/month where eligible. Free, Pro, and "
        "Education inputs/outputs are eligible for training by default unless the "
        "user opts out. Team and Enterprise inputs/outputs are not used for "
        "training. API usage is billed separately."
    ),
    notes=(
        "Latest release v2.24.1 (2026-08-11). Training defaults differ by account "
        "class; cloud ZDR is discretionary, API-only, and never covers Vibe "
        "Work/Chat. Remove unverified EU-default-storage and certification "
        "assertions."
    ),
)

# rca-kiro-cli (kiro.dev/docs/models/; docs URLs moved out of /docs/cli/)
patch(
    "rca-kiro-cli",
    model_backend=(
        "Amazon Bedrock backbone: Anthropic Claude Opus 5 (1M context) and Claude "
        "Sonnet 5 alongside Opus 4.5-4.8, Sonnet 4.0/4.5/4.6, Haiku 4.5; OpenAI "
        "GPT-5.6 Sol/Terra/Luna (272K context); open-weight MiniMax M2.5/M2.1, "
        "GLM-5, DeepSeek 3.2, Qwen3 Coder Next; Auto router default. The models page "
        "does not state Bedrock routing for the OpenAI models."
    ),
    compliance=[
        "HIPAA (explicitly listed for Kiro IDE and CLI)",
        "AWS shared-responsibility model (SOC 2/ISO 27001 via AWS infrastructure - confirm scope via AWS Artifact)",
        "TLS 1.2+ in transit",
        "AWS KMS at rest (customer-managed keys available for enterprise)",
    ],
    data_handling_note=(
        "Free and individual users may have content used for improvement/training by "
        "default; paid individual status does not itself establish no-training. The "
        "service-improvement exclusion for individuals applies when accessing Kiro "
        "through an AWS account with an Amazon Q Developer Pro subscription; "
        "social-login and Builder ID users are individual subscribers whose content "
        "may be used unless they opt out in Settings. Free-tier inputs are retained "
        "up to 60 days for abuse detection (not for training). Enterprise is the "
        "documented no-storage/no-improvement route. CLI execution is local but "
        "inference is cloud-based."
    ),
    pricing=(
        "Free: 50 credits/month; Pro: $20/month (1,000 credits); Pro+: $40/month "
        "(2,000 credits); Pro Max: $100/month (5,000 credits); Power: $200/month "
        "(10,000 credits). Overage: $0.04/credit across all paid tiers. New: $20 "
        "sign-up credit for social-login/Builder ID upgrades. GovCloud pricing ~20% "
        "higher; free tier unavailable there and IAM Identity Center required. "
        "Startup program: up to 1 year of free Pro+. Enterprise: custom/contact "
        "sales with centralized billing and organizational dashboard."
    ),
    links={
        "privacy": "https://kiro.dev/docs/privacy-and-security/data-protection/",
    },
    notes=(
        "Terminal client for Kiro's cloud inference. Apply the same enterprise "
        "data-protection boundary as the IDE; do not infer no-training from payment "
        "alone. A previously listed in-progress FedRAMP claim no longer appears on "
        "the compliance page. Privacy/compliance docs moved out of /docs/cli/ to "
        "shared /docs/privacy-and-security/ paths."
    ),
    sources=[
        "https://kiro.dev/docs/privacy-and-security/data-protection/",
        "https://kiro.dev/docs/privacy-and-security/compliance-validation/",
        "https://kiro.dev/pricing/",
        "https://kiro.dev/docs/cli/",
        "https://kiro.dev/docs/models/",
    ],
)

# rca-warp (warp.dev/pricing; docs.warp.dev security overview: client AGPL v3)
patch(
    "rca-warp",
    software_license="AGPL-3.0",
    license_status="confirmed",
    pricing=(
        "Free ($0, limited AI credits); Build ($20/month, 1,500 credits of included "
        "agent usage at API rates); Max ($200/month, 18,000 credits); Business "
        "($50/user/month, up to 25 seats, 1,500 credits per seat, team ZDR, SAML "
        "SSO); Enterprise (custom pricing, self-hosted execution, BYOLLM). Annual "
        "billing is 10% off. No documented academic or student discount."
    ),
    notes=(
        "Cloud-orchestrated terminal/agent. Separate provider ZDR from Warp "
        "collection, and do not treat self-hosted execution-plane components as full "
        "on-prem deployment. Warp's client code is published under AGPL v3 per its "
        "enterprise security docs; the server/control plane remains proprietary "
        "cloud."
    ),
)

# rca-augment-code (docs.augmentcode.com/models/available-models.md; enterprise 404)
patch(
    "rca-augment-code",
    deployment="cloud",
    model_backend=(
        "Claude Fable 5, Claude Opus 5/4.8/4.7/4.6/4.5, Claude Sonnet 5/4.6/4.5, "
        "Claude Haiku 4.5; OpenAI GPT-5.6 Sol/Terra/Luna, GPT-5.5/5.4/5.2/5.1; "
        "Gemini 3.1 Pro; GLM 5.2; Kimi K3/K2.6; 'Prism' router variants Prism "
        "(Claude + Gemini) and Prism (GPT)"
    ),
    data_handling_note=(
        "Paid plans state that customer data is not used for training ('No AI "
        "training allowed' on Business and Enterprise). No VPC, single-tenant, "
        "on-prem, or self-hosted deployment statement could be located on current "
        "public pages (the enterprise page returns 404 and the trust center did not "
        "render); treat such options as unverified pending an enterprise contract. "
        "Only vendor-cloud deployment is currently documented, and ZDR plan scope "
        "remains contract-specific."
    ),
    suitability_notes={
        "personal": (
            "GDPR-compliant posture with DPA and Standard Contractual Clauses "
            "available; 'no AI training allowed' is stated on Business and "
            "Enterprise. On-prem/VPC options are not currently documented publicly - "
            "verify any such deployment contractually before relying on it."
        ),
    },
    compliance=[
        "SOC 2 Type II",
        "ISO/IEC 42001",
        "HIPAA BAA available",
        "GDPR",
        "CCPA",
        "CMEK",
    ],
    notes=(
        "Commercial coding platform (Auggie CLI; a 'Cosmos' automation product sits "
        "alongside it) with current Business team pricing and negotiated enterprise "
        "deployment controls. Previously advertised VPC/single-tenant/on-prem "
        "deployment statements were not found on current public pages and are "
        "treated as unverified enterprise-contract options."
    ),
    sources=[
        "https://www.augmentcode.com/security",
        "https://www.augmentcode.com/legal/privacy-policy",
        "https://trust.augmentcode.com",
        "https://www.augmentcode.com/pricing",
        "https://docs.augmentcode.com/cli/overview",
        "https://www.augmentcode.com/product/cli",
        "https://www.augmentcode.com/contact",
        "https://docs.augmentcode.com/models/available-models.md",
    ],
)

# rca-open-interpreter (openinterpreter.com/desktop; /pricing now 404)
patch(
    "rca-open-interpreter",
    pricing=(
        "Free: desktop/terminal agent with BYO API keys, local Ollama models, or "
        "'Sign in with ChatGPT' (a cloud route under the user's ChatGPT account); "
        "the terminal agent installs via shell script. Pro: $20/month (hosted "
        "models, 4x more usage than Free, experimental macOS control). Business: "
        "$60/month (3x more usage than Pro). A contact path offers dedicated "
        "support, compliance options, and automation services for teams. The former "
        "/pricing URL returns 404; pricing now lives on the desktop-app page."
    ),
    links={"pricing": "https://www.openinterpreter.com/desktop"},
    sources=[
        "https://www.openinterpreter.com/",
        "https://www.openinterpreter.com/cli",
        "https://github.com/openinterpreter/openinterpreter",
        "https://www.openinterpreter.com/privacy",
        "https://www.openinterpreter.com/desktop",
    ],
)

# rca-kilo-code (kilo.ai pricing/homepage/terms)
patch(
    "rca-kilo-code",
    model_backend=(
        "BYOK (500+ models via OpenRouter / direct providers: Anthropic, OpenAI, "
        "Google, etc.) or local via Ollama / LM Studio; optional Kilo Gateway "
        "(pay-as-you-go, no markup)"
    ),
    pricing=(
        "Free (open-source extension + CLI, BYOK; no credit card required); Kilo "
        "Gateway pay-as-you-go at exact provider rates (zero markup); Kilo Pass "
        "subscription $19/month (Starter), $49/month (Pro), $199/month (Expert); "
        "Teams $15/user/month (14-day trial); Enterprise custom pricing. KiloClaw "
        "(managed cloud agent hosting) $55/month separately. The formerly advertised "
        "$20 signup credit no longer appears."
    ),
    academic=(
        "No academic or student discount programme found on the pricing page. The "
        "free BYOK tier and open-source nature make it accessible without a special "
        "discount."
    ),
    data_handling_note=(
        "Kilo supports fully local Ollama/LM Studio and local indexing. Official "
        "materials state no prompt/output retention on paid plans, but this must not "
        "be generalized to every free cloud route. Kilo's terms grant a broad "
        "license to use Customer Data to provide and improve the Service, with a "
        "separate elective license for AI-model training (declining it may restrict "
        "certain models). Cloud terms prohibit regulated sensitive data."
    ),
)

# rca-deepnote (deepnote.com/pricing; docs/ai-data-privacy)
replace_in("rca-deepnote", "model_backend", "OpenAI (GPT-5),", "OpenAI (GPT-5.5),")
replace_in("rca-deepnote", "pricing", "GPT-5 + Sonnet 4.6 AI access", "GPT-5.5 and Sonnet 4.6 access")
patch(
    "rca-deepnote",
    suitability_notes={
        "personal": (
            "Personal/pseudonymised data (GDPR): DPA is available to all customer "
            "tiers (not enterprise-only), incorporates EU Standard Contractual "
            "Clauses (2021/914), and covers GDPR/UK GDPR/Swiss FADP. No-train policy "
            "is stated. However, AI context can be processed in the US and worldwide "
            "(no EU data residency guarantee by default). cfg = use with a signed "
            "DPA, disable block-output sharing, and confirm your team plan includes "
            "DPA coverage. Enterprise single-tenancy with possible EU residency "
            "(contact sales) would upgrade this to closer to ok."
        ),
    },
)

# rca-marimo (marimo.io privacy URL now 308-redirects to CoreWeave's policy)
patch(
    "rca-marimo",
    data_handling_note=(
        "The local marimo core can use local or BYOK providers, while molab is a "
        "hosted service with separate terms and free hosted models. molab expressly "
        "prohibits HIPAA-regulated and GDPR Article 9 special-category data. The "
        "marimo.io privacy URL now permanently redirects to CoreWeave's privacy "
        "policy, and the subprocessors page states molab runs on CoreWeave "
        "infrastructure."
    ),
    pricing=(
        "Free and open-source (Apache-2.0). molab cloud is free (4 CPU / 32 GB RAM; "
        "optional NVIDIA RTX Pro 6000 GPU; 12-hour sessions; limited persistent "
        "storage); the 'beta' label no longer appears on the molab guide. "
        "Enterprise/commercial arrangements via demo request."
    ),
    links={"privacy": "https://docs.coreweave.com/policies/terms-of-service/privacy-policy"},
    notes=(
        "Open-source reactive notebook with local AI-provider support and a "
        "separate molab hosted service. The marimo.io privacy URL now redirects to "
        "CoreWeave's privacy policy and the subprocessors page names CoreWeave for "
        "molab hosting; no first-party acquisition statement was found, so no "
        "ownership change is asserted."
    ),
    sources=[
        "https://docs.marimo.io/guides/editor_features/ai_completion/",
        "https://docs.marimo.io/guides/molab/",
        "https://molab.marimo.io/pages/legal/terms",
        "https://marimo.io/pages/legal/subprocessors",
        "https://marimo.io/pages/legal/privacy",
        "https://docs.coreweave.com/policies/terms-of-service/privacy-policy",
        "https://github.com/marimo-team/marimo",
    ],
)

# rca-runcell (runcell.dev pricing renders client-side; privacy policy tiers)
patch(
    "rca-runcell",
    pricing=(
        "Plan lineup is now Free, Pro, Ultra, and Team ('Hobby' and 'Pro+' no "
        "longer appear). Exact current prices and credit amounts render client-side "
        "and could not be extracted on the audit date; treat earlier figures as "
        "stale and verify on the pricing page. Privacy Mode is tied to paid plans."
    ),
    data_handling_note=(
        "The privacy policy frames Privacy Mode as enabled by default on Pro and "
        "Team paid plans ('we do not use your prompts, context, or model outputs to "
        "train or fine-tune models'), while the free plan explicitly permits "
        "training; whether Ultra is covered was not explicit, so confirm per tier. "
        "No current public DPA or institutional processor terms were verified. Code "
        "snippets/prompts still traverse cloud model routes."
    ),
)

# rca-jetbrains-datalore (configure-ai-assistance.html; buy page shop payload)
patch(
    "rca-jetbrains-datalore",
    model_backend=(
        "JetBrains AI in Cloud; On-Premises AI assistance (disabled by default, "
        "requires an active paid On-Premises license) lists OpenAI GPT-5.2, "
        "Anthropic Claude Opus 4.5 / Sonnet 4.5, and Google Gemini 3.1 Pro, plus "
        "BYOK routes: OpenAI, Azure OpenAI, and OpenAI-compatible providers "
        "including self-hosted models"
    ),
    pricing=(
        "Cloud Free and paid plans are listed publicly. The buy page's embedded "
        "shop payload now lists fixed, geo-localized On-Premises and Professional "
        "prices (e.g. Datalore On-Premises approx. USD 2,000/year commercial, shown "
        "as CZK 46,800 in the Czech geo; Datalore Professional CZK 479/month "
        "personal); the per-user/seat basis is not labeled, so confirm with "
        "JetBrains."
    ),
    academic=(
        "No dedicated academic pricing; Datalore is classified as a \"Team Tool\" "
        "and excluded from JetBrains' free student/teacher IDE pack. Students and "
        "researchers must use the Cloud Free tier or purchase paid plans."
    ),
    suitability_notes={
        "special": (
            "Requires Datalore On-Premises/air-gapped deployment plus a self-hosted "
            "LLM on controlled infrastructure. On-Premises AI defaults now include "
            "cloud providers (OpenAI, Anthropic, Google), so the special-category "
            "route must explicitly configure a self-hosted OpenAI-compatible "
            "endpoint. Cloud remains unsuitable."
        ),
    },
    special_route={
        "required_controls": [
            "Requires Datalore On-Premises/air-gapped deployment plus a self-hosted "
            "LLM on controlled infrastructure. On-Premises AI defaults now include "
            "cloud providers (OpenAI, Anthropic, Google), so the special-category "
            "route must explicitly configure a self-hosted OpenAI-compatible "
            "endpoint. Cloud remains unsuitable."
        ],
    },
)

# rca-chatgpt-advanced-data-analysis (chatgpt pricing page; openai.com/business-data/)
patch(
    "rca-chatgpt-advanced-data-analysis",
    model_backend=(
        "GPT-5.6 family in current ChatGPT availability (Sol / Sol Pro / Terra / "
        "Luna by plan); model assignment can change by plan and rollout"
    ),
    data_handling_note=(
        "OpenAI's no-train default is enumerated across ChatGPT Enterprise, "
        "Business, Edu, ChatGPT for Healthcare, ChatGPT for Teachers, and the API, "
        "with organizational retention controls; a BAA is offered to ChatGPT for "
        "Healthcare and API healthcare customers. Consumer tiers (Free/Go/Plus/Pro) "
        "train by default with an opt-out. Public ZDR documentation primarily "
        "concerns eligible API configurations, not a general ChatGPT guarantee. "
        "Data residency at rest is available in the US, Europe, UK, Japan, Canada, "
        "South Korea, Singapore, Australia, India, and UAE for eligible plans. "
        "Uploaded/generated files may persist in ChatGPT Library depending on plan "
        "and rollout."
    ),
    pricing=(
        "Current lineup: Free, Go, Plus, Pro, Business, Enterprise (plus ChatGPT "
        "Edu, ChatGPT for Teachers, and ChatGPT for Healthcare). The former Team "
        "plan is no longer offered; Business is available starting at 2 users, and "
        "the low-cost Go tier may include ads. Use current official localized "
        "pricing; Enterprise/Edu are contractual."
    ),
    suitability_notes={
        "personal": (
            "Personal/pseudonymised (GDPR) data requires at minimum the ChatGPT "
            "Business tier with a signed DPA and no-training defaults. On "
            "Free/Go/Plus/Pro the default trains on data and there is no DPA - not "
            "suitable. With Enterprise + signed DPA + EU data residency configured: "
            "usable for GDPR personal data."
        ),
    },
    tier_gate="Business/Enterprise/Edu with DPA and accepted retention controls",
)

# rca-ollama (ollama.com/pricing; GitHub API)
patch(
    "rca-ollama",
    pricing=(
        "Free: $0 - unlimited local models, 1 concurrent cloud model, light cloud "
        "usage; Pro: $20/month or $200/year - 50x more cloud usage, 3 concurrent "
        "cloud models, private model sharing; Max: $100/month - 5x more than Pro, 10 "
        "concurrent cloud models, continuous agent tasks (new Max signups are "
        "temporarily paused while capacity is added); Team: $25/seat/month with a "
        "5-seat minimum - shared billing/administration and priority support (SSO "
        "and model access controls coming soon); Enterprise: custom terms for larger "
        "organizations. Local execution is unlimited and free across all tiers."
    ),
    notes=(
        "Local model infrastructure rather than a standalone coding agent. Do not "
        "preserve a fixed model inventory, release version, or integration list "
        "across updates."
    ),
)

# ---------------------------------------------------------------------------
# New records (evidence/additions-2026-08-13/rca_result_1..5.json; 17 accepts)
# ---------------------------------------------------------------------------


def cfg_route(*controls: str) -> dict:
    return {
        "status": "config-required",
        "boundary": "customer-controlled",
        "inference": "local-only",
        "required_controls": list(controls),
        "residual_risks": [GENERIC_RESIDUAL],
    }


def endpoint_route(*controls: str) -> dict:
    return {
        "status": "config-required",
        "boundary": "customer-controlled",
        "inference": "customer-controlled-endpoint",
        "required_controls": list(controls),
        "residual_risks": [GENERIC_RESIDUAL],
    }


def no_route(residual: str) -> dict:
    return {
        "status": "not-appropriate",
        "boundary": "none",
        "inference": "none",
        "required_controls": [],
        "residual_risks": [residual],
    }


NEW_RECORDS: list[dict] = [
    {
        "id": "rca-grok-build",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Grok Build",
        "vendor": "xAI",
        "type": "cli",
        "openness": "open-source",
        "deployment": "local CLI / cloud inference (xAI default); custom or self-hosted endpoints configurable",
        "model_backend": "xAI Grok (grok-4.6 default, 500k context); custom OpenAI-style endpoints, including self-hosted, via ~/.grok/config.toml",
        "data_handling": "opt-out",
        "data_handling_note": (
            "Telemetry is on by default (config docs show telemetry, Mixpanel product "
            "analytics, session trace upload, and a feedback system default-enabled), "
            "with opt-outs via config.toml or GROK_TELEMETRY_ENABLED and "
            "organization-enforced policy via /etc/grok/requirements.toml. A separate "
            "/privacy settings screen governs coding data, retention, and training, "
            "but its default is not documented in fetched sources and xAI's legal "
            "pages were unreachable during verification, so the current "
            "retention/training default is unverified. Enterprise documentation "
            "states no prompts, code, or responses are persisted at the inference "
            "layer for ZDR organizations (team-level); inference-layer ZDR does not "
            "establish product-level zero retention."
        ),
        "capability": "frontier",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Only with team-level enterprise ZDR enforced, or a self-hosted model "
                "endpoint via config.toml, and all telemetry/analytics/trace-upload/"
                "feedback toggles disabled (ideally enforced via "
                "/etc/grok/requirements.toml). The default individual setup (xAI "
                "cloud, telemetry on, undocumented retention default) is not "
                "appropriate for personal data."
            ),
            "special": (
                "Requires institution-controlled inference only - a self-hosted/local "
                "endpoint via config.toml - plus organization-enforced telemetry "
                "disable via requirements.toml, with network-level egress "
                "verification. Default xAI-cloud operation is not acceptable, ZDR "
                "notwithstanding."
            ),
        },
        "compliance": ["ZDR (enterprise, team-level, inference layer only)"],
        "pricing": (
            "Product/plan pricing unverified - no first-party Grok Build pricing "
            "page was found. Underlying grok-4.6 API: $2.00/M input, $6.00/M output, "
            "$0.50/M cached below 200k context (doubles above); auth via browser "
            "sign-in or API key."
        ),
        "academic": "No academic or student program found.",
        "use_cases": [
            "terminal-native agentic coding on large codebases",
            "headless/CI scripting and long-running tasks",
            "Agent Client Protocol integration into third-party editors",
            "BYO/self-hosted model endpoint workflows for controlled environments",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://docs.x.ai/build/overview",
            "pricing": "https://docs.x.ai/developers/models/grok-4.6",
            "privacy": "https://docs.x.ai/build/enterprise",
        },
        "notes": (
            "Apache-2.0 Rust CLI published by xAI (source-published but vendor-only "
            "development; external contributions are not accepted). Press reported a "
            "July 2026 incident in which the client uploaded full repositories with a "
            "non-functional opt-out before a server-side fix and the open-sourcing of "
            "the client; this is context, not first-party-verified, and motivates the "
            "conservative classification."
        ),
        "sources": [
            "https://github.com/xai-org/grok-build",
            "https://raw.githubusercontent.com/xai-org/grok-build/main/README.md",
            "https://raw.githubusercontent.com/xai-org/grok-build/main/crates/codegen/xai-grok-pager/docs/user-guide/05-configuration.md",
            "https://docs.x.ai/build/overview",
            "https://docs.x.ai/build/enterprise",
            "https://docs.x.ai/developers/models/grok-4.6",
        ],
        "status": "active",
        "current_name": "Grok Build",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "team-level enterprise ZDR for cloud use; fully self-hosted endpoint + enforced telemetry disable for regulated data",
        "software_license": "Apache-2.0",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Institution-controlled inference only (self-hosted/local endpoint via "
            "config.toml), organization-enforced telemetry disable via "
            "/etc/grok/requirements.toml, and network-level egress verification. "
            "Default xAI-cloud operation is not acceptable."
        ),
    },
    {
        "id": "rca-muse-code",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Muse Code",
        "vendor": "Meta (Meta Superintelligence Labs)",
        "type": "cli",
        "openness": "commercial",
        "deployment": "cloud",
        "model_backend": (
            "Meta Muse Spark (muse-spark-1.2 default; muse-spark-1.1; "
            "muse-spark-1.2-contributor; 1M-token context; multimodal input); no "
            "custom/self-hosted endpoint support found in fetched docs"
        ),
        "data_handling": "no-train",
        "data_handling_note": (
            "Standard tier: 'your prompts and completions are not used to train Meta "
            "models' (first-party pricing docs). The Contributor tier is an opt-in "
            "training-for-discount route (roughly 10-20x cheaper in exchange for "
            "permission to train on prompts and completions) and must not be selected "
            "for any non-public code or data. No retention statement, telemetry "
            "statement, DPA, or compliance page was found anywhere in the developer "
            "docs at verification, so the retention posture is unverified. Client-side "
            "safety defaults are strong: approvals and OS sandboxing on by default, "
            "proxy-only network with per-destination approval, workspace-scoped "
            "writes."
        ),
        "capability": "frontier",
        "backend_dependent": False,
        "suitability": {"nonsensitive": "ok", "personal": "no", "special": "no"},
        "suitability_notes": {
            "personal": (
                "Conservative 'no' pending evidence: pure Meta-cloud inference with "
                "no published retention policy, no DPA or enterprise data terms, and "
                "no compliance certifications found shortly after launch. The "
                "standard tier's no-training default does not substitute for "
                "retention/DPA evidence. Revisit if Meta publishes trust/DPA pages."
            ),
            "special": (
                "Pure vendor cloud with no self-hosted or customer-controlled "
                "deployment option; not acceptable under this index's "
                "controlled-infrastructure rule regardless of the no-training "
                "default."
            ),
        },
        "compliance": [],
        "pricing": (
            "Usage-based Meta Model API. Standard (muse-spark-1.2): $1.25/M input, "
            "$4.25/M output, $0.15/M cached input. Contributor tier: $0.10/M input, "
            "$0.20/M output - in exchange for training permission."
        ),
        "academic": "No academic or student program found.",
        "use_cases": [
            "agentic coding on large codebases (1M-token context)",
            "CI/headless automation",
            "parallel sub-agents in isolated git worktrees",
            "sandboxed command execution with staged shell review",
        ],
        "runs_locally": False,
        "links": {
            "docs": "https://dev.meta.ai/docs/muse-code",
            "pricing": "https://dev.meta.ai/docs/pricing-rate-limits.md",
            "privacy": "https://dev.meta.ai/docs/pricing-rate-limits.md",
        },
        "notes": (
            "Meta's terminal/CI coding agent, launched 2026-08-05. No dedicated "
            "privacy/data-use page exists in the developer docs; the pricing page "
            "carries the only first-party training statements, so the privacy link "
            "points there. Never select the contributor model for non-public data."
        ),
        "sources": [
            "https://dev.meta.ai/docs/muse-code",
            "https://dev.meta.ai/docs/pricing-rate-limits.md",
            "https://dev.meta.ai/docs/muse-code/permissions.md",
            "https://dev.meta.ai/docs/muse-code/auth.md",
            "https://dev.meta.ai/docs/models.md",
        ],
        "status": "active",
        "current_name": "Muse Code",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "no personal-data route verified (no DPA or retention documentation)",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": no_route(
            "Pure vendor cloud with no self-hosted or customer-controlled deployment "
            "option; not acceptable under this index's controlled-infrastructure "
            "rule regardless of the no-training default."
        ),
    },
    {
        "id": "rca-ante",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Ante",
        "vendor": "Antigma Labs",
        "type": "cli",
        "openness": "open-source",
        "deployment": "local-capable (single binary; fully offline with embedded llama.cpp) / BYO cloud APIs",
        "model_backend": (
            "BYO: built-in llama.cpp for local GGUF models (fully offline, no API "
            "key); 17 provider presets incl. Anthropic, OpenAI, Google Gemini, Grok, "
            "DeepSeek, OpenRouter; custom OpenAI-compatible endpoints"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "No vendor inference service; product-level data stays local. Caveat: "
            "telemetry is on by default and opt-out (set ANTE_TELEMETRY=off to "
            "disable export entirely); it is described as anonymous (a deletable "
            "random installation label, never username, hostname, or machine id). "
            "The prebuilt binary ships under separate Binary Preview Terms that "
            "contain no data-collection clauses. When cloud presets are used, data "
            "handling is governed by the chosen provider's terms, not Ante's."
        ),
        "capability": "strong",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Use local GGUF inference (or an institution-approved endpoint) and "
                "set ANTE_TELEMETRY=off. With cloud presets, the selected provider's "
                "retention/training terms govern."
            ),
            "special": (
                "Fully offline only: embedded llama.cpp with a local GGUF model and "
                "ANTE_TELEMETRY=off gives a documented researcher-controlled, "
                "air-gappable boundary. Any cloud preset is that provider's cloud "
                "and is not acceptable. Alpha maturity: validate outputs."
            ),
        },
        "compliance": [],
        "pricing": (
            "Free: Apache-2.0 source; the prebuilt binary is free (incl. commercial "
            "use) during the alpha preview under Binary Preview Terms. Costs are BYO "
            "API usage, or zero with local GGUF models."
        ),
        "academic": "No academic or student program found; free open source.",
        "use_cases": [
            "fully offline/air-gapped coding assistance on sensitive or pre-publication code",
            "single-binary install on locked-down or HPC-adjacent machines",
            "BYO-key multi-provider terminal agent",
            "headless scripting",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://github.com/AntigmaLabs/ante",
            "pricing": "https://github.com/AntigmaLabs/ante/blob/main/BINARY-TERMS.md",
            "privacy": "https://github.com/AntigmaLabs/ante",
        },
        "notes": (
            "Alpha-preview single-binary Rust CLI (~15 MB, zero runtime "
            "dependencies) with the strongest documented offline/air-gap story in "
            "this update's CLI lane. Source is Apache-2.0; the binary uses separate "
            "preview terms. Self-reported Terminal-Bench score is unaudited; "
            "capability tracks the chosen backend, and local GGUF models trail "
            "frontier APIs. Expect breaking changes."
        ),
        "sources": [
            "https://github.com/AntigmaLabs/ante",
            "https://github.com/AntigmaLabs/ante/blob/main/BINARY-TERMS.md",
        ],
        "status": "active",
        "current_name": "Ante",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "fully offline local GGUF model + ANTE_TELEMETRY=off for regulated data",
        "software_license": "Apache-2.0",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Fully offline configuration only: embedded llama.cpp with a local GGUF "
            "model on controlled infrastructure and ANTE_TELEMETRY=off. Any cloud "
            "preset is not acceptable."
        ),
    },
    {
        "id": "rca-nanocoder",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Nanocoder",
        "vendor": "Nano Collective (non-profit community organization)",
        "type": "cli",
        "openness": "open-source",
        "deployment": "local-capable",
        "model_backend": (
            "BYO: Ollama (local models); OpenAI-compatible APIs (OpenRouter, "
            "Anthropic, Google, others); Atlas Cloud sponsor preset"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "First-party repo commitments: no telemetry ('no telemetry quietly "
            "shipping your prompts somewhere'), no closed-source features, and no "
            "paid tiers - there is no vendor-side data plane at all. No product-level "
            "retention exists because no product service exists. When cloud APIs are "
            "configured, the chosen provider's retention/training terms govern."
        ),
        "capability": "basic",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Use local inference via Ollama (code never leaves the machine). "
                "With cloud APIs, the selected provider's terms govern - assess that "
                "provider, not Nanocoder."
            ),
            "special": (
                "Local-only configuration: Ollama (or another local runtime) on "
                "institution-controlled hardware gives a researcher-controlled "
                "boundary with no telemetry. Any cloud API backend is that "
                "provider's cloud and is not acceptable."
            ),
        },
        "compliance": ["self-hosted"],
        "pricing": (
            "Free, MIT-licensed, explicitly no paid tiers; costs are BYO API usage, "
            "or zero with local Ollama models."
        ),
        "academic": "Free community open-source project.",
        "use_cases": [
            "local-first coding assistance where code must stay on-machine",
            "zero-telemetry environments",
            "teaching agentic coding without vendor lock-in",
            "BYO-key multi-provider terminal agent",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://github.com/nano-collective/nanocoder",
            "pricing": "https://github.com/nano-collective/nanocoder",
            "privacy": "https://github.com/nano-collective/nanocoder",
        },
        "notes": (
            "Community-governed local-first CLI coding agent (MIT confirmed via the "
            "repository LICENSE). Fills a niche no vendor tool covers: no vendor "
            "data pipeline at all. Agent scaffold is lighter than vendor agents; "
            "capability ceiling depends on the configured backend."
        ),
        "sources": [
            "https://github.com/nano-collective/nanocoder",
            "https://raw.githubusercontent.com/nano-collective/nanocoder/main/LICENSE.md",
        ],
        "status": "active",
        "current_name": "Nanocoder",
        "confidence": "high",
        "verified": TODAY,
        "established": False,
        "tier_gate": "fully local Ollama model for regulated data",
        "software_license": "MIT",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Local-only configuration: Ollama or another local runtime on "
            "institution-controlled hardware. Any cloud API backend is not "
            "acceptable."
        ),
    },
    {
        "id": "rca-qwen-code",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Qwen Code",
        "vendor": "Alibaba (QwenLM)",
        "type": "cli",
        "openness": "open-source",
        "deployment": "local CLI; inference via cloud providers or local/self-hosted endpoints",
        "model_backend": (
            "Multi-provider: Alibaba ModelStudio Coding Plan / API key (regional "
            "endpoints in Beijing and international); built-in DeepSeek, MiniMax, "
            "Z.AI, OpenRouter; any OpenAI-compatible, Anthropic, Google GenAI, or "
            "Vertex AI protocol endpoint; local endpoints incl. Ollama and vLLM. "
            "The Qwen OAuth free tier was discontinued 2026-04-15."
        ),
        "data_handling": "local",
        "data_handling_note": (
            "Docs state Qwen Code itself does not use prompts, code, or responses "
            "for model training; training/retention is governed entirely by the "
            "chosen backend (API-key mode under the provider's policy, ModelStudio "
            "under Alibaba Cloud's privacy policy). Anonymous usage statistics "
            "(commands, performance metrics, error reports - documented as excluding "
            "code content, prompts, responses, and personal information) may be "
            "collected; the default on/off state is not explicitly stated in fetched "
            "docs, so assume enabled and disable explicitly in settings."
        ),
        "capability": "strong",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Only with a self-hosted/local inference endpoint (Ollama, vLLM, an "
                "institutional OpenAI-compatible server) or a provider under an "
                "institutional DPA; the default Alibaba ModelStudio backend sends "
                "code to Alibaba Cloud under Alibaba's policies, which were not "
                "assessed here. Disable anonymous usage statistics."
            ),
            "special": (
                "Only in a fully researcher/institution-controlled configuration: "
                "local CLI plus a local or institution-hosted inference endpoint "
                "(Ollama/vLLM/self-hosted OpenAI-compatible), telemetry disabled. "
                "Any commercial cloud backend is not acceptable."
            ),
        },
        "compliance": [],
        "pricing": (
            "Tool free and open source (Apache-2.0). Inference billed by the chosen "
            "backend: Alibaba ModelStudio Coding Plan/API key (prices not published "
            "on fetched docs pages - unverified), third-party API keys, or free with "
            "local models. The Qwen OAuth free tier was discontinued 2026-04-15."
        ),
        "academic": "No academic or student program found on fetched pages.",
        "use_cases": [
            "terminal-based agentic coding with local open-weight models (Ollama/vLLM) for data-sensitive environments",
            "scriptable headless code automation in pipelines",
            "Qwen/Alibaba-ecosystem coding with the ModelStudio Coding Plan",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://qwenlm.github.io/qwen-code-docs/en/users/overview",
            "pricing": "https://github.com/QwenLM/qwen-code",
            "privacy": "https://qwenlm.github.io/qwen-code-docs/en/users/support/tos-privacy/",
        },
        "notes": (
            "Originally based on Gemini CLI v0.8.2 but independently developed since "
            "v0.1 with a multi-protocol provider layer, desktop app variant, agent "
            "plugins, and its own release cadence - accepted as an independent "
            "open-source CLI agent, not a thin fork."
        ),
        "sources": [
            "https://github.com/QwenLM/qwen-code",
            "https://github.com/QwenLM/qwen-code/releases",
            "https://qwenlm.github.io/qwen-code-docs/en/users/overview",
            "https://qwenlm.github.io/qwen-code-docs/en/users/configuration/auth/",
            "https://qwenlm.github.io/qwen-code-docs/en/users/support/tos-privacy/",
        ],
        "status": "active",
        "current_name": "Qwen Code",
        "confidence": "medium",
        "verified": TODAY,
        "established": True,
        "tier_gate": "self-hosted/local endpoint + telemetry disabled for regulated data",
        "software_license": "Apache-2.0",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Fully researcher/institution-controlled configuration only: local CLI "
            "plus a local or institution-hosted inference endpoint "
            "(Ollama/vLLM/self-hosted OpenAI-compatible), telemetry disabled. Any "
            "commercial cloud backend is not acceptable."
        ),
    },
    {
        "id": "rca-factory",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Factory (Droids)",
        "vendor": "Factory (factory.ai)",
        "type": "cloud",
        "openness": "commercial",
        "deployment": (
            "cloud-managed; enterprise hybrid (Droid entirely in customer "
            "infrastructure), EU-specific, or fully air-gapped on-prem (incl. NVIDIA "
            "DGX Spark with Nemotron 3.5 Lightning)"
        ),
        "model_backend": (
            "Multi-model with router and 'Model Independence': Anthropic Claude "
            "(Fable 5, Opus/Sonnet/Haiku), OpenAI GPT-5.x, Google Gemini 3.x, xAI "
            "Grok 4.5, open-weight models via Droid Core (GLM, Kimi, DeepSeek, "
            "Nemotron, MiniMax), custom endpoints/BYOK; in the cloud-managed pattern "
            "LLM traffic routes through customer gateways"
        ),
        "data_handling": "no-train",
        "data_handling_note": (
            "First-party security page states customer code is not used as training "
            "data; AES-256 at rest, TLS 1.2+ in transit, sandboxed single-tenant "
            "environments. No session-content retention period is published on "
            "fetched pages (the privacy policy covers personal data only, with US "
            "processing except the EU deployment option), so retention is treated as "
            "unverified. Anthropic Mythos-class models carry 30-day trust-and-safety "
            "retention where org admins opt in."
        ),
        "capability": "frontier",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "cfg only via enterprise deployments (hybrid in own infrastructure, "
                "EU-specific, or air-gapped) or cloud-managed with LLM traffic "
                "through a customer-monitored gateway and an institutional DPA. "
                "Standard Pro/Plus/Max cloud tiers are US-hosted with undocumented "
                "session-content retention - not suitable for personal data without "
                "contractual review."
            ),
            "special": (
                "Only the documented customer-controlled patterns qualify: Hybrid "
                "(Droid runs entirely within your infrastructure) or fully "
                "air-gapped on-prem (incl. DGX Spark with local Nemotron execution), "
                "with models and collectors on-premises. These are enterprise "
                "contact-sales tiers. Any Factory-hosted cloud tier is not "
                "acceptable regardless of vendor VPC/single-tenant claims."
            ),
        },
        "compliance": [
            "SOC 2 Type I (claimed)",
            "ISO 42001 (adoption claimed)",
            "GDPR (claimed)",
            "CCPA (claimed)",
        ],
        "pricing": (
            "Pro $20/mo; Plus $100/mo (~5x Pro usage, Factory-managed cloud "
            "computers); Max $200/mo (~10x Pro usage); Business custom (up to 150 "
            "seats, SSO/SAML/SCIM, audit logging); Enterprise custom (on-premise "
            "deployment options, dedicated compute, customer-managed encryption "
            "keys). No free tier listed."
        ),
        "academic": "No academic or student program mentioned on the pricing page.",
        "use_cases": [
            "hosted asynchronous coding agents opening PRs from chat-assigned tasks",
            "air-gapped/on-prem autonomous coding for security-sensitive institutional codebases",
            "enterprise-governed multi-agent software maintenance (code review, QA, incident response)",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://docs.factory.ai",
            "pricing": "https://factory.ai/pricing",
            "privacy": "https://factory.ai/privacy-policy",
        },
        "notes": (
            "Factory 2.0 autonomous coding-agent platform (Droids) across web/"
            "desktop, CLI, SDK, and cloud computers. The enterprise hybrid and "
            "air-gapped deployment patterns are first-party documented and are the "
            "only qualifying special-category routes; the trust center did not "
            "render during verification, so compliance claims are recorded as "
            "claimed rather than attested."
        ),
        "sources": [
            "https://factory.ai/news/software-factory",
            "https://factory.ai/news",
            "https://factory.ai/pricing",
            "https://factory.ai/security",
            "https://factory.ai/privacy-policy",
            "https://docs.factory.ai",
            "https://docs.factory.ai/docs/enterprise/network-and-deployment",
            "https://docs.factory.ai/docs/models",
        ],
        "status": "active",
        "current_name": "Factory (Droids)",
        "confidence": "medium",
        "verified": TODAY,
        "established": True,
        "tier_gate": "enterprise hybrid or fully air-gapped deployment for special-category data",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": cfg_route(
            "Documented customer-controlled patterns only: Hybrid (Droid entirely "
            "within customer infrastructure) or fully air-gapped on-prem (incl. DGX "
            "Spark with local Nemotron execution), with models and collectors "
            "on-premises. Factory-hosted cloud tiers are not acceptable."
        ),
    },
    {
        "id": "rca-roomote",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Roomote",
        "vendor": "Roo Code, Inc.",
        "type": "cloud",
        "openness": "open-core",
        "deployment": (
            "Roomote Cloud (US-hosted) or self-hosted via Docker on an own server "
            "with local Docker task sandboxes by default; optional hosted sandbox "
            "backends move execution to provider infrastructure"
        ),
        "model_backend": (
            "Model-agnostic BYOK: OpenRouter, Anthropic, OpenAI, xAI, Google "
            "Gemini, Amazon Bedrock and others; direct ChatGPT Plus/Pro subscription "
            "connection; frontier, open-weight, and local model support claimed"
        ),
        "data_handling": "no-train",
        "data_handling_note": (
            "Cloud: Customer Content (repositories, prompts, tasks, model outputs, "
            "integration credentials, logs, artifacts) is processed under a DPA; "
            "'We never use Customer Content to train AI models'; workspace deletion "
            "destroys the deployment, trial deployments are deleted 7 days after "
            "expiry, account metadata up to 30 days, billing up to 7 years; "
            "US-hosted with SCCs; subprocessors include Railway, Modal, Vercel, "
            "Resend, Stripe, Google, PostHog, Intercom. Self-hosted: data stays on "
            "the own server with default local Docker sandboxes, but anonymous "
            "telemetry (content-free daily instance reports and usage events) is "
            "enabled by default and must be disabled by admins."
        ),
        "capability": "strong",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Prefer self-hosted (free up to 10 users): code and tasks stay on "
                "institutional infrastructure with default local Docker sandboxes; "
                "disable the on-by-default anonymous telemetry and choose an "
                "inference provider under institutional terms. Roomote Cloud is "
                "US-hosted with DPA+SCCs - usable for personal data only after "
                "institutional DPA review."
            ),
            "special": (
                "Only as: self-hosted deployment + default local Docker sandbox "
                "(not hosted sandbox backends) + local or institution-controlled "
                "inference endpoint + telemetry disabled. Roomote Cloud and any "
                "hosted sandbox or commercial model API are not acceptable. A "
                "dedicated local-provider configuration page was not verified."
            ),
        },
        "compliance": [],
        "pricing": (
            "Cloud: $49/mo up to 10 users, $249/mo up to 50, $499/mo up to 100; "
            "7-day free trial without a card. Self-hosted: free up to 10 registered "
            "users; $249/mo for 11-50 users; $499/mo for 51-100 users. Inference "
            "costs separate (BYOK)."
        ),
        "academic": "No academic or student program found on fetched pages.",
        "use_cases": [
            "chat-assigned background coding tasks returned as reviewable PRs",
            "self-hosted institutional coding agent where repositories never leave the university server",
            "team-shared agent fleet with cost analytics across BYOK inference providers",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://docs.roomote.dev",
            "pricing": "https://roomote.dev/",
            "privacy": "https://roomote.dev/legal/cloud-privacy",
        },
        "notes": (
            "Background/asynchronous coding agent (formerly Roo Code) assigned via "
            "Slack/Teams/Discord/Telegram, opening PRs from isolated sandboxes. "
            "Source-available under the Fair Core License (FCL-1.0-ALv2, converting "
            "to Apache-2.0 two years post-release) - classified source-available, "
            "not open-source. Actively maintained."
        ),
        "sources": [
            "https://roomote.dev/",
            "https://roomote.dev/legal/cloud-privacy",
            "https://docs.roomote.dev",
            "https://docs.roomote.dev/self-hosting.md",
            "https://docs.roomote.dev/compute.md",
            "https://docs.roomote.dev/anonymous-analytics.md",
            "https://github.com/RooCodeInc/Roomote",
            "https://github.com/RooCodeInc/Roomote/releases",
        ],
        "status": "active",
        "current_name": "Roomote",
        "confidence": "high",
        "verified": TODAY,
        "established": False,
        "tier_gate": "self-hosted deployment + local Docker sandbox + institution-controlled inference for special-category data",
        "software_license": "FCL-1.0-ALv2",
        "license_status": "source-available",
        "special_route": endpoint_route(
            "Self-hosted deployment with the default local Docker sandbox (not "
            "hosted sandbox backends), a local or institution-controlled inference "
            "endpoint, and telemetry disabled. Roomote Cloud and commercial model "
            "APIs are not acceptable."
        ),
    },
    {
        "id": "rca-gitlab-duo-agent-platform",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "GitLab Duo Agent Platform",
        "vendor": "GitLab Inc.",
        "type": "cloud",
        "openness": "commercial",
        "deployment": "cloud (GitLab.com / vendor-operated Dedicated) / Self-Managed incl. self-hosted models and offline licenses",
        "model_backend": (
            "Default Anthropic Claude Sonnet 4; admin LLM selection incl. OpenAI "
            "GPT-5 variants, Mistral, Meta Llama, Anthropic Claude; on Self-Managed, "
            "self-hosted models via the GitLab AI Gateway, including fully offline "
            "licenses"
        ),
        "data_handling": "no-train",
        "data_handling_note": (
            "GitLab does not train generative AI models on customer content and all "
            "AI model sub-processors are restricted from using model input/output "
            "for training. Product-level retention exists: Duo Chat and Agent "
            "Platform retain chat and workflow history (user-deletable), and "
            "GitLab.com retains workflow history for anti-abuse purposes; certain "
            "Anthropic and OpenAI models are subject to limited vendor-side "
            "retention - model-provider ZDR does not erase this. On the Self-Managed "
            "self-hosted-model route, inference data (code inputs, prompts, "
            "responses) does not leave the customer network; offline licenses do "
            "not connect to external GitLab components. GitLab Dedicated is "
            "vendor-operated single-tenant cloud, not customer-controlled on-prem."
        ),
        "capability": "strong",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Cloud route (GitLab.com/Dedicated): defensible with a DPA, the "
                "no-training policy, and SOC 2/ISO 27001-family certifications, but "
                "limited vendor-side retention applies to certain Anthropic/OpenAI "
                "models and GitLab.com retains workflow history for anti-abuse - "
                "review under institutional GDPR assessment. Self-Managed with "
                "self-hosted models keeps data in the institutional boundary."
            ),
            "special": (
                "Only the Self-Managed route with self-hosted models (or an "
                "offline/air-gapped license), where first-party docs establish that "
                "inference data does not leave the customer network. Pure "
                "GitLab.com or GitLab Dedicated is not acceptable despite "
                "certifications."
            ),
        },
        "compliance": [
            "SOC 2 (GitLab.com and Dedicated)",
            "ISO/IEC 27001",
            "ISO/IEC 27017",
            "ISO/IEC 27018",
            "ISO/IEC 42001",
            "GDPR (DPA available)",
            "CCPA",
            "TISAX",
            "CSA STAR",
            "Data Privacy Framework certified",
        ],
        "pricing": (
            "Premium $29/user/mo (billed annually); Ultimate custom. Agent Platform "
            "billed via GitLab Credits at $1/credit; Premium includes 12 and "
            "Ultimate 24 credits/user/mo ('for a limited time', subject to change). "
            "Duo Agent Platform Self-Hosted offline licenses use a flat-fee "
            "Enterprise License Agreement (contact sales); a third-party "
            "'$299/seat/mo' figure is absent from first-party pages and unverified."
        ),
        "academic": (
            "GitLab for Education: free Ultimate licenses plus 50K compute "
            "minutes/month for qualifying educational institutions."
        ),
        "use_cases": [
            "automating issue-to-merge-request development flows on institutional GitLab instances",
            "code review and CI/CD pipeline repair agents on research software repositories",
            "air-gapped agentic coding on Self-Managed GitLab with self-hosted models for sensitive codebases",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://docs.gitlab.com/user/duo_agent_platform/",
            "pricing": "https://about.gitlab.com/pricing/",
            "privacy": "https://docs.gitlab.com/user/gitlab_duo/data_usage/",
        },
        "notes": (
            "Agentic software-lifecycle platform inside GitLab (foundational and "
            "custom agents, multi-step flows, agentic chat, external agent and MCP "
            "support), GA since GitLab 18.8 (2026-01-15) on GitLab.com, "
            "Self-Managed, and Dedicated. One record covers both deployment routes; "
            "only Self-Managed with self-hosted/offline models is the qualifying "
            "special-category route."
        ),
        "sources": [
            "https://about.gitlab.com/blog/gitlab-duo-agent-platform-is-generally-available/",
            "https://docs.gitlab.com/user/duo_agent_platform/",
            "https://docs.gitlab.com/user/gitlab_duo/data_usage/",
            "https://docs.gitlab.com/administration/gitlab_duo_self_hosted/",
            "https://about.gitlab.com/pricing/",
            "https://docs.gitlab.com/subscriptions/subscription-add-ons/",
            "https://trust.gitlab.com",
        ],
        "status": "active",
        "current_name": "GitLab Duo Agent Platform",
        "confidence": "high",
        "verified": TODAY,
        "established": True,
        "tier_gate": "Self-Managed with self-hosted models (or offline license) for special-category data",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": cfg_route(
            "Self-Managed route with self-hosted models via the GitLab AI Gateway, "
            "or an offline/air-gapped license, so inference data does not leave the "
            "customer network. GitLab.com and vendor-operated Dedicated are not "
            "acceptable."
        ),
    },
    {
        "id": "rca-clusy",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Clusy",
        "vendor": "Clusy Inc. (Claymont, DE, USA)",
        "type": "cloud",
        "openness": "commercial",
        "deployment": "cloud",
        "model_backend": (
            "Tiered managed models: Free/Plus use an 'Auto' model plus open-source "
            "models (DeepSeek V4 Pro, Kimi K3, Qwen3.8 Max); Pro/Max add Anthropic "
            "Claude (Sonnet, Opus) and OpenAI GPT. Inference hosting location for "
            "the open-source models is unverified."
        ),
        "data_handling": "trains",
        "data_handling_note": (
            "Conservative classification: neither the privacy policy nor the "
            "security page contains any statement on whether notebook/dataset "
            "content is used to train models, so the catalog assumes no contractual "
            "protection. Retention is unspecified ('for as long as it is needed'); "
            "the subprocessor list is available only under NDA; US-based with "
            "possible onward transfers. Workspaces are logically separated; TLS in "
            "transit and encryption at rest via cloud providers. The terms grant "
            "Clusy a limited license to use submitted content 'solely to provide "
            "and secure the Services'."
        ),
        "capability": "capable",
        "backend_dependent": False,
        "suitability": {"nonsensitive": "ok", "personal": "no", "special": "no"},
        "suitability_notes": {
            "personal": (
                "Not recommended for GDPR personal data: no published "
                "training-on-content commitment, no retention specifics, no SOC "
                "2/ISO certification, NDA-only subprocessor list, US transfers. The "
                "Enterprise tier (SSO, custom terms) might change this after "
                "contract review."
            ),
            "special": (
                "Pure cloud with an unresolved training/retention posture and no "
                "self-hosted option; not acceptable for special-category "
                "health/genetic/clinical data."
            ),
        },
        "compliance": [],
        "pricing": (
            "Free $0 (Auto model, 8 vCPU/8 GB CPU sandbox); Plus $30/mo "
            "(open-source models, T4/L4/A10 GPUs, 32 GB RAM); Pro $90/mo (all "
            "models incl. Claude/GPT, L40S/A100, 64 GB RAM); Max $200/mo "
            "(H100/H200, 128 GB RAM, priority capacity); Enterprise custom "
            "(dedicated capacity, SSO). Pay-as-you-go overages on paid tiers."
        ),
        "academic": "No academic or student program mentioned on pricing or product pages.",
        "use_cases": [
            "exploratory ML experiments on public or non-sensitive datasets with agent-driven notebook execution",
            "parallel branched model-architecture comparisons on rented GPUs",
            "agentic analysis over non-sensitive Databricks/Snowflake tables",
        ],
        "runs_locally": False,
        "links": {
            "docs": "https://docs.clusy.io",
            "pricing": "https://clusy.io/pricing",
            "privacy": "https://clusy.io/privacy-policy",
        },
        "notes": (
            "Agent-native cloud notebook for data science and ML (plans workflows, "
            "writes and executes notebook cells, sources data, branches parallel "
            "experiments; GPU sandboxes up to H100/H200). Accepted despite thin "
            "governance documentation and classified sharply conservatively - "
            "flagged for owner review."
        ),
        "sources": [
            "https://www.clusy.io",
            "https://clusy.io/pricing",
            "https://clusy.io/privacy-policy",
            "https://clusy.io/security",
            "https://clusy.io/terms-of-use",
        ],
        "status": "active",
        "current_name": "Clusy",
        "confidence": "low",
        "verified": TODAY,
        "established": False,
        "tier_gate": "no qualifying route; Enterprise contract review required before any personal data",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": no_route(
            "Pure cloud with an unresolved training/retention posture and no "
            "self-hosted option; not acceptable for special-category "
            "health/genetic/clinical data."
        ),
    },
    {
        "id": "rca-datafoundry",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "DataFoundry",
        "vendor": "datagallery-lab (open-source community project)",
        "type": "data",
        "openness": "open-source",
        "deployment": "self-hosted",
        "model_backend": (
            "Any OpenAI-compatible provider (Qwen, DeepSeek, GPT, etc.) via a "
            "configurable LLM_BASE_URL - including self-hosted/local models"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "Self-hosted only; analyses run inside read-only boundaries with every "
            "step auditable and replayable. Guardrails by default: read-only "
            "queries, credential isolation, field masking, row limits, and "
            "timeouts; SQL audit logs, tool-call records, and event streams are "
            "persisted; datasource credentials, model API keys, and MCP tokens "
            "never enter messages or context. No vendor cloud exists, so no "
            "product-level retention or training question arises; the configured "
            "LLM endpoint's policy governs prompt data - use a self-hosted model to "
            "keep everything in-boundary."
        ),
        "capability": "capable",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Self-hosted with read-only guardrails, masking, and a full audit "
                "trail - suitable when the configured LLM endpoint is itself "
                "compliant (self-hosted model or provider under an institutional "
                "DPA). Row-level data can enter prompts during analysis."
            ),
            "special": (
                "Institution-controlled self-hosting qualifies, but only with a "
                "self-hosted/in-boundary model backend; pointing it at a commercial "
                "cloud LLM API sends query results off-boundary. Early-stage "
                "software - validate the guardrails before production use on "
                "clinical/genetic data."
            ),
        },
        "compliance": ["self-hosted"],
        "pricing": "Free, open source (Apache-2.0). No commercial tier documented.",
        "academic": "Free open-source project.",
        "use_cases": [
            "in-boundary natural-language analysis over institutional research databases",
            "governed multi-step SQL analyses with audit/replay for reproducibility",
            "embedding a data-analysis agent runtime into institutional tools via REST/AG-UI",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://datagallery-lab.github.io/datafoundry/",
            "pricing": "",
            "privacy": "https://github.com/datagallery-lab/datafoundry",
        },
        "notes": (
            "Conversational data-analysis agent workbench over structured data (28 "
            "datasource types; web workbench, TUI, and REST/AG-UI runtime) with a "
            "unified semantics layer. Young project (v0.2.0, repository about two "
            "months old at verification, self-described early but usable) - "
            "maturity risk carried explicitly."
        ),
        "sources": [
            "https://github.com/datagallery-lab/datafoundry",
            "https://raw.githubusercontent.com/datagallery-lab/datafoundry/main/LICENSE",
            "https://datagallery-lab.github.io/datafoundry/",
        ],
        "status": "active",
        "current_name": "DataFoundry",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "self-hosted with an in-boundary model endpoint for regulated data",
        "software_license": "Apache-2.0",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Institution-controlled self-hosting with a self-hosted/in-boundary "
            "model backend only; commercial cloud LLM APIs send query results "
            "off-boundary and are not acceptable. Validate the guardrails before "
            "production use on clinical/genetic data."
        ),
    },
    {
        "id": "rca-nobie",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Nobie",
        "vendor": "Nobie, Inc.",
        "type": "data",
        "openness": "commercial",
        "deployment": "local (macOS app + CLI engine); connected coding agents bring their own cloud routes",
        "model_backend": (
            "None built in - bring-your-own coding agent (Claude, Codex, Gemini) "
            "connects to the local Excel-compatible engine via nobie-cli and agent "
            "skills; spreadsheet content flows to whichever agent/model the user "
            "connects"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "The product page claims strictly local processing ('Your data never "
            "leaves your Mac', 'No servers, no uploads, no exceptions'), but the "
            "privacy policy discloses PostHog and Sentry activity/diagnostic "
            "collection without stating defaults and contains no section on "
            "spreadsheet-file handling or AI-provider data flows - the local-only "
            "marketing claim is not restated in the policy, so the gap is recorded "
            "here. When a coding agent is connected, spreadsheet content it reads "
            "is governed by that provider's retention/training policy, not "
            "Nobie's. Retention: 'as long as it is reasonably needed', no "
            "timeframes."
        ),
        "capability": "basic",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "The local engine keeps files on-device, but telemetry defaults are "
                "undocumented and any connected cloud agent reads spreadsheet "
                "content under that provider's terms - acceptable only with a "
                "vetted agent backend and telemetry addressed."
            ),
            "special": (
                "Only under researcher-controlled use: local engine only, with a "
                "local/institution-controlled agent backend (no cloud agent "
                "connected) and telemetry blocked or verified off. The privacy "
                "policy does not document spreadsheet-data handling, so verify "
                "before use on clinical/genetic spreadsheets. Beta software - "
                "maturity risk."
            ),
        },
        "compliance": [],
        "pricing": (
            "Free during beta ('Free forever' claim on the product page); "
            "proprietary Desktop App License Terms (licensed, not sold). No paid "
            "tiers disclosed."
        ),
        "academic": "No academic or student program mentioned.",
        "use_cases": [
            "letting CLI coding agents analyze and recalculate .xlsx files without uploading them",
            "local formula-preserving programmatic editing of Excel workbooks from the terminal",
            "rendering spreadsheet outputs to PNG/PDF in local pipelines",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://github.com/nobie-org/nobie-cli",
            "pricing": "https://nobie.com",
            "privacy": "https://nobie.com/privacy",
        },
        "notes": (
            "Native macOS Excel-compatible spreadsheet app and engine with full "
            "formula recalculation on standard .xlsx; nobie-cli exposes the engine "
            "to coding agents. Accepted despite an unreconciled local-only "
            "marketing claim versus a thin privacy policy (PostHog/Sentry, no "
            "spreadsheet-data section) and very early beta maturity - classified "
            "sharply conservatively and flagged for owner review."
        ),
        "sources": [
            "https://nobie.com",
            "https://nobie.com/privacy",
            "https://github.com/nobie-org/nobie-cli",
        ],
        "status": "active",
        "current_name": "Nobie",
        "confidence": "low",
        "verified": TODAY,
        "established": False,
        "tier_gate": "local engine + local/institution-controlled agent backend; telemetry verified off",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": cfg_route(
            "Local engine only, with a local/institution-controlled agent backend "
            "(no cloud agent connected) and telemetry blocked or verified off. The "
            "privacy policy does not document spreadsheet-data handling; verify "
            "before use on clinical/genetic spreadsheets."
        ),
    },
    {
        "id": "rca-ada-automated-data-analyst",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Ada (Automated Data Analyst)",
        "vendor": "saineshnakra (independent open-source project)",
        "type": "data",
        "openness": "open-source",
        "deployment": "local (Streamlit app on researcher hardware)",
        "model_backend": (
            "None required (deterministic pandas calculations); optional OpenAI API "
            "layer for query planning and narrative synthesis only"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "The core runs with no LLM at all: the dashboard does not require an "
            "API key, execute generated code, or intentionally persist uploaded "
            "datasets, and files are processed within the active Streamlit session "
            "(project SECURITY.md). With the optional OpenAI layer enabled, only "
            "computed schema roles, summaries, evidence, deterministic "
            "recommendations, and user-typed context are sent; raw uploaded rows "
            "are not included in model prompts and request storage is disabled for "
            "model API calls. The project's own security notes warn that the "
            "boundary does not turn a public hosted app into an approved "
            "environment for regulated data. Streamlit framework-level telemetry "
            "defaults are not addressed in the repo (unverified)."
        ),
        "capability": "basic",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Run locally on researcher-controlled hardware; do not use the "
                "public Streamlit Cloud demo. Even with the optional OpenAI layer, "
                "derived summaries can themselves be personal data - avoid enabling "
                "it for identifiable data."
            ),
            "special": (
                "Only fully local with the optional OpenAI layer disabled (no API "
                "key configured, which is the default). Single-maintainer project "
                "with no vendor security program or DPA - the institution assumes "
                "all operational responsibility."
            ),
        },
        "compliance": ["self-hosted"],
        "pricing": (
            "Free (MIT-licensed open source). Optional OpenAI API usage billed to "
            "the user's own OpenAI account."
        ),
        "academic": "Free open-source project.",
        "use_cases": [
            "quick exploratory analysis of tabular research data without sending anything to an LLM",
            "natural-language questions over CSV/Excel with auditable deterministic calculations",
            "teaching example of a privacy-first LLM-optional analysis architecture",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://github.com/saineshnakra/automated-data-analyst",
            "pricing": "https://github.com/saineshnakra/automated-data-analyst",
            "privacy": "https://github.com/saineshnakra/automated-data-analyst/blob/main/SECURITY.md",
        },
        "notes": (
            "Zero-config exploratory data analysis on CSV/Excel with a transparent "
            "deterministic pandas core and an evidence ledger; the optional LLM "
            "layer adds planning and narrative only. Niche, single-maintainer "
            "project with tiny adoption - included for its genuinely privacy-first "
            "architecture."
        ),
        "sources": [
            "https://github.com/saineshnakra/automated-data-analyst",
            "https://github.com/saineshnakra/automated-data-analyst/commits/main",
            "https://github.com/saineshnakra/automated-data-analyst/blob/main/SECURITY.md",
        ],
        "status": "active",
        "current_name": "Ada (Automated Data Analyst)",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "fully local run with the optional OpenAI layer disabled for regulated data",
        "software_license": "MIT",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Fully local execution with the optional OpenAI layer disabled (no API "
            "key configured). Single-maintainer project without a vendor security "
            "program or DPA; the institution assumes all operational "
            "responsibility."
        ),
    },
    {
        "id": "rca-microsoft-365-copilot-analyst",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Microsoft 365 Copilot Analyst",
        "vendor": "Microsoft",
        "type": "cloud",
        "openness": "commercial",
        "deployment": "cloud (Microsoft 365 tenant service boundary)",
        "model_backend": (
            "OpenAI o3-mini reasoning model at launch, optimized for advanced data "
            "analysis; models are regularly updated, and Microsoft 365 Copilot now "
            "offers admin-selectable OpenAI and Anthropic models as Microsoft "
            "subprocessors. The current exact Analyst model is not separately "
            "documented."
        ),
        "data_handling": "no-train",
        "data_handling_note": (
            "Analyst operates entirely within the Microsoft 365 commercial data "
            "processing boundary and inherits Microsoft 365's security, privacy, "
            "and compliance commitments. Prompts, responses, and Microsoft Graph "
            "data are not used to train foundation LLMs; interactions are stored "
            "encrypted as Copilot activity history in the tenant, governed by "
            "Purview retention policies and user deletion. Copilot services opted "
            "out of Azure OpenAI abuse-monitoring human review. The EU Data "
            "Boundary applies for EU users, but Anthropic-provided models are "
            "currently excluded from it. Python-sandbox data handling specifics "
            "are not separately documented (unverified)."
        ),
        "capability": "strong",
        "backend_dependent": False,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "no"},
        "suitability_notes": {
            "personal": (
                "Only within an institutional Microsoft 365 tenant under the "
                "organization's existing Microsoft 365 DPA, GDPR and (for EU) EU "
                "Data Boundary commitments, with Purview retention configured. Not "
                "for personal accounts. If admins enable Anthropic models, note "
                "those are currently excluded from the EU Data Boundary."
            ),
            "special": (
                "Microsoft-operated cloud is not researcher/institution-controlled "
                "infrastructure; HIPAA/GDPR/ISO claims and the tenant service "
                "boundary do not change that under this catalog's rules. No local "
                "or self-hosted option exists."
            ),
        },
        "compliance": [
            "GDPR",
            "EU Data Boundary (EU users; Anthropic models excluded)",
            "ISO 27001",
            "ISO 42001",
            "HIPAA",
            "ISO/IEC 27018",
        ],
        "pricing": (
            "Microsoft 365 Copilot Business add-on: $21.00/user/month, promotional "
            "$18.00/user/month through 2026-09-30 (annual commitment, USD); bundles "
            "from $23.50/user/month. Analyst is listed among included pre-built "
            "Microsoft agents (with Researcher and Facilitator). Enterprise pricing "
            "not fetched this session."
        ),
        "academic": (
            "No education/academic pricing mentioned on the fetched pricing page; "
            "EDU-tenant availability unverified."
        ),
        "use_cases": [
            "statistical analysis of institutional spreadsheets and uploaded datasets inside the university M365 tenant",
            "chain-of-thought data exploration with inspectable Python code",
            "report/insight generation grounded in tenant documents under existing M365 governance",
        ],
        "runs_locally": False,
        "links": {
            "docs": "https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps",
            "pricing": "https://www.microsoft.com/en-us/microsoft-365/copilot/business",
            "privacy": "https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy",
        },
        "notes": (
            "Reasoning-model data analyst inside Microsoft 365 Copilot Chat with "
            "visible real-time Python execution. Launched 2025-03-25 (before this "
            "update's discovery window); accepted under the older-notable-miss "
            "rule. Tenant-boundary operation is first-party confirmed; pure vendor "
            "cloud, so special-category data remains excluded despite compliance "
            "claims."
        ),
        "sources": [
            "https://www.microsoft.com/en-us/microsoft-365/blog/2025/03/25/introducing-researcher-and-analyst-in-microsoft-365-copilot/",
            "https://learn.microsoft.com/en-us/copilot/microsoft-365/microsoft-365-copilot-privacy",
            "https://learn.microsoft.com/en-us/microsoft-365/admin/manage/manage-copilot-agents-integrated-apps",
            "https://www.microsoft.com/en-us/microsoft-365/copilot/business",
        ],
        "status": "active",
        "current_name": "Microsoft 365 Copilot Analyst",
        "confidence": "high",
        "verified": TODAY,
        "established": True,
        "tier_gate": "institutional M365 tenant + DPA + Purview retention controls for personal data",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": no_route(
            "Microsoft-operated cloud is not researcher/institution-controlled "
            "infrastructure; HIPAA/GDPR/ISO claims and the tenant service boundary "
            "do not change that under this catalog's rules. No local or "
            "self-hosted option exists."
        ),
    },
    {
        "id": "rca-zerve",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Zerve",
        "vendor": "Zerve AI",
        "type": "cloud",
        "openness": "commercial",
        "deployment": (
            "cloud SaaS (US-hosted) / self-hosted into the customer's own AWS, GCP, "
            "or Azure account (Pro+) / Enterprise on-premise air-gapped"
        ),
        "model_backend": (
            "Not disclosed for the managed service; the privacy policy lists "
            "Exafunction (Codeium) and OpenAI as AI subprocessors (both USA); BYOK "
            "for OpenAI and Anthropic on Pro and Team plans"
        ),
        "data_handling": "trains",
        "data_handling_note": (
            "Conservative classification: the privacy policy (effective 2024-01-22) "
            "does not address whether customer data trains AI/ML models - treated "
            "as no commitment. SaaS is hosted and operated in the United States "
            "with retention for as long as the account stays open. Self-hosting "
            "(Pro+) deploys into the customer's own AWS/GCP/Azure account ('Data "
            "stays in your environment'); Enterprise adds on-premise air-gapped. "
            "Whether the agent's LLM calls remain inside the boundary in "
            "self-hosted mode is unverified - OpenAI/Codeium are cloud "
            "subprocessors and air-gapped model provisioning is not documented on "
            "fetched pages."
        ),
        "capability": "capable",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "The managed SaaS is US-hosted with account-lifetime retention and "
                "no model-training commitment - avoid it for identifiable data. Use "
                "the self-hosted deployment (own cloud account) so data stays in "
                "the institution's environment, and verify where the agent's LLM "
                "calls route before onboarding personal data."
            ),
            "special": (
                "Only the Enterprise on-premise air-gapped deployment qualifies as "
                "institution-controlled infrastructure, and only after the vendor "
                "confirms how LLM inference is provided in-boundary (undocumented "
                "on fetched pages; the cloud agent depends on OpenAI/Codeium "
                "subprocessors). Never on the managed SaaS."
            ),
        },
        "compliance": [],
        "pricing": (
            "Pay As You Go free tier ($0, 150 credits, up to 4 editors); Pro "
            "$18.75/user/month (250 credits/mo, self-hosting, private projects, GPU "
            "compute); Team $37.50/user/month (500 credits/mo, SSO, BYOK); "
            "Enterprise custom (multi-cloud, on-prem air-gapped). Add-on credits "
            "non-expiring. Annual billing prices."
        ),
        "academic": "No academic or student program mentioned on the pricing page.",
        "use_cases": [
            "AI-assisted notebook analysis with institutional memory for research data teams",
            "self-hosted data-science workspace inside the institution's own cloud account",
            "auto-generated, continuously synced data reports and deployed analysis apps",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://docs.zerve.ai/guide/",
            "pricing": "https://www.zerve.ai/pricing",
            "privacy": "https://docs.zerve.ai/privacy-policy",
        },
        "notes": (
            "Agentic data-science platform (agentic notebooks, data-estate "
            "discovery, auto-generated reports, deployment of APIs/apps from "
            "notebooks). Predates this update's discovery window; accepted under "
            "the older-notable-miss rule for its self-hosted/on-prem options. No "
            "named compliance certifications (only an unlabelled ISMS/ISO badge); "
            "classified conservatively."
        ),
        "sources": [
            "https://www.zerve.ai/",
            "https://www.zerve.ai/pricing",
            "https://docs.zerve.ai/privacy-policy",
            "https://docs.zerve.ai/guide/",
        ],
        "status": "active",
        "current_name": "Zerve",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "Enterprise on-premise air-gapped deployment (with vendor-confirmed in-boundary inference) for special-category data",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": endpoint_route(
            "Enterprise on-premise air-gapped deployment only, and only after the "
            "vendor confirms that LLM inference is provided inside the boundary "
            "(undocumented on fetched pages). The managed SaaS is not acceptable."
        ),
    },
    {
        "id": "rca-lm-studio-bionic",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "LM Studio Bionic",
        "vendor": "LM Studio (lmstudio.ai)",
        "type": "cli",
        "openness": "commercial",
        "deployment": "local-capable (desktop app; fully on-device by default) / optional vendor Secure Cloud",
        "model_backend": (
            "Local open-weight models via the LM Studio runtime (llama.cpp and MLX), "
            "e.g. GLM 5.2, Kimi K2.7 Code; offline voice via Mistral Voxtral; "
            "optional LM Studio Secure Cloud hosting frontier open models (DeepSeek "
            "V4 Flash/Pro, GLM-5.2, Kimi K2.6/K2.7-Code/K3); LM Link relays models "
            "from the user's other devices"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "Local path: the app can run entirely on-device - messages, chat "
            "histories, and documents are never transmitted when running local "
            "models, and the application includes no telemetry or user-specific "
            "tracking (network requests occur only for update checks and model "
            "search/download). Voice audio is processed locally. Optional Secure "
            "Cloud is pay-as-you-go on US servers with vendor ZDR claims ('Zero "
            "Data Retention across the board', no training on user data); native "
            "web search sends queries off-device when used."
        ),
        "capability": "capable",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Fine when using local models only (the default free tier is fully "
                "on-device with no telemetry). If Secure Cloud is used, requests go "
                "to vendor US servers under ZDR - acceptable for personal data only "
                "with institutional review; web search also sends queries "
                "off-device."
            ),
            "special": (
                "Local models only, on researcher-controlled hardware, with Secure "
                "Cloud and web search left unused - that configuration is fully "
                "on-device. The Secure Cloud path is vendor cloud and remains "
                "unsuitable for special-category data despite ZDR."
            ),
        },
        "compliance": [],
        "pricing": (
            "Free tier $0 (Bionic agent, local models, offline voice, web search, "
            "LM Link up to 5 devices). Secure Cloud pay-as-you-go per 1M tokens "
            "(e.g. DeepSeek V4 Flash $0.13 in/$0.26 out; GLM-5.2 $1.50 in/$4.50 "
            "out; Kimi K3 $3.00 in/$15.00 out). 'Bionic Pass' plan details coming "
            "soon; Enterprise referenced without details."
        ),
        "academic": "No academic discounts mentioned on the pricing page.",
        "use_cases": [
            "fully offline coding agent over local repositories with diff review",
            "local document/PDF/spreadsheet processing with open-weight models",
            "offline multilingual voice transcription for interviews and notes",
            "occasional burst to larger open models via ZDR cloud for non-sensitive tasks",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://lmstudio.ai/docs/bionic",
            "pricing": "https://lmstudio.ai/pricing",
            "privacy": "https://lmstudio.ai/app-privacy",
        },
        "notes": (
            "Agent for open models (launched 2026-07-16), a separate desktop app "
            "from LM Studio proper: inspects local codebases, edits with inline "
            "diff review and checkpoints, works on documents in sandboxed projects. "
            "Clean local/cloud separation; ZDR does not make the cloud path "
            "suitable for special-category data."
        ),
        "sources": [
            "https://lmstudio.ai/blog/introducing-lm-studio-bionic",
            "https://lmstudio.ai/bionic",
            "https://lmstudio.ai/app-privacy",
            "https://lmstudio.ai/pricing",
            "https://lmstudio.ai/docs/bionic",
        ],
        "status": "active",
        "current_name": "LM Studio Bionic",
        "confidence": "high",
        "verified": TODAY,
        "established": True,
        "tier_gate": "local models only (Secure Cloud and web search unused) for regulated data",
        "software_license": None,
        "license_status": "proprietary",
        "special_route": cfg_route(
            "Local models only on researcher-controlled hardware, with Secure "
            "Cloud and native web search left unused. The Secure Cloud path is "
            "vendor cloud and is not acceptable despite ZDR."
        ),
    },
    {
        "id": "rca-juggler",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "Juggler",
        "vendor": "juggler-ai (Julian Storer)",
        "type": "cli",
        "openness": "open-source",
        "deployment": "local desktop app / self-hostable headless server (localhost-only by default)",
        "model_backend": (
            "BYO: Claude Code (CLI or API), OpenAI (Codex plan or API), GitHub "
            "Copilot, Gemini, Mistral, Z.AI, DeepSeek, OpenRouter, Ollama (local)"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "Local-only product layer: sessions are stored as documents on disk and "
            "the server is localhost-only by default ('nothing off your machine can "
            "reach it'). No telemetry, analytics, or crash reporting is mentioned "
            "in first-party sources, but no formal privacy policy exists either, so "
            "the absence of telemetry is inferred rather than policy-guaranteed. "
            "The opt-in LAN mode is unauthenticated (anyone who can reach the "
            "address can drive the agent). Official binaries may include "
            "proprietary components per LICENSING.md. With Ollama as backend, code "
            "never leaves the machine; hosted backends are governed by their own "
            "provider policies."
        ),
        "capability": "strong",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Local app with no vendor cloud; exposure is determined entirely by "
                "the chosen model backend. Use Ollama or an institution-controlled "
                "endpoint to keep personal data on-machine; keep the server in its "
                "default localhost-only mode. No formal privacy policy - verify "
                "build behaviour if policy documentation is required."
            ),
            "special": (
                "Only on researcher-controlled infrastructure: open-source build, "
                "local models via Ollama or institution-hosted backends, default "
                "localhost-only mode. Never enable the passwordless LAN mode on "
                "shared networks. Young single-maintainer project without a privacy "
                "policy; prefer building from source for air-gapped/clinical "
                "environments."
            ),
        },
        "compliance": ["self-hosted"],
        "pricing": (
            "Free, open source (AGPL-3.0 application; Apache-2.0 extension SDK). "
            "Commercial licensing available on contact for uses the AGPL does not "
            "permit. No paid tiers found."
        ),
        "academic": "No academic or student program found; free open source.",
        "use_cases": [
            "inspectable, steerable agentic coding with every tool call visible and editable before execution",
            "coding agents on sensitive codebases with local models via Ollama",
            "self-hosted headless server on lab hardware with browser clients",
            "teaching how agent tool-calling works (branching, editable context trees)",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://github.com/juggler-ai/juggler",
            "pricing": "",
            "privacy": "https://github.com/juggler-ai/juggler",
        },
        "notes": (
            "GUI agent workbench (visible/editable tool calls, branching "
            "conversation trees, persistent on-disk sessions) by the JUCE creator. "
            "About two months old and single-maintainer at verification - maturity "
            "risk carried explicitly; no formal privacy policy exists."
        ),
        "sources": [
            "https://github.com/juggler-ai/juggler",
            "https://raw.githubusercontent.com/juggler-ai/juggler/develop/README.md",
            "https://raw.githubusercontent.com/juggler-ai/juggler/develop/LICENSING.md",
            "https://juggler.studio",
            "https://api.github.com/repos/juggler-ai/juggler",
        ],
        "status": "active",
        "current_name": "Juggler",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "local models via Ollama + default localhost-only mode for regulated data",
        "software_license": "AGPL-3.0",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Researcher-controlled infrastructure only: open-source build, local "
            "models via Ollama or institution-hosted backends, default "
            "localhost-only mode, and the passwordless LAN mode never enabled on "
            "shared networks. Prefer building from source for air-gapped/clinical "
            "environments."
        ),
    },
    {
        "id": "rca-opensquilla",
        "date_added": TODAY,
        "date_modified": TODAY,
        "name": "OpenSquilla",
        "vendor": "OpenSquilla project (opensquilla.cn; no legal entity identified in first-party sources)",
        "type": "cli",
        "openness": "open-source",
        "deployment": "local/self-hosted (CLI + gateway server, localhost by default; Docker/Compose; offline deployment supported)",
        "model_backend": (
            "BYO multi-provider (20+): Anthropic, OpenAI, Gemini, OpenRouter, "
            "DeepSeek, DashScope/Qwen, Moonshot, Mistral, Groq, Zhipu, SiliconFlow, "
            "and the optional TokenRhythm hosted service; local models via Ollama, "
            "vLLM, LM Studio"
        ),
        "data_handling": "local",
        "data_handling_note": (
            "Self-hosted runtime: config, sessions, logs, memory, and cache stay "
            "under ~/.opensquilla; prompts/code go only to the user-configured "
            "provider ('only when the user configures a provider and starts a "
            "workflow that uses that provider'). Caveat: pseudonymous install "
            "telemetry plus daily aggregate token counts are ON by default; the "
            "policy states telemetry excludes usernames, hostnames, paths, keys, "
            "provider configuration, and all content, and it can be disabled with "
            "OPENSQUILLA_PRIVACY_DISABLE_NETWORK_OBSERVABILITY=true. Gaps: the "
            "telemetry endpoint domain, its retention period, and a data "
            "controller/legal entity are not disclosed."
        ),
        "capability": "strong",
        "backend_dependent": True,
        "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
        "suitability_notes": {
            "personal": (
                "Run self-hosted with local providers (Ollama/vLLM/LM Studio) and "
                "set OPENSQUILLA_PRIVACY_DISABLE_NETWORK_OBSERVABILITY=true - "
                "telemetry is on by default and the receiving endpoint/operator is "
                "not disclosed. With hosted providers, the provider's "
                "retention/training policies govern the content."
            ),
            "special": (
                "Only on institution-controlled infrastructure: fully self-hosted "
                "(air-gap possible since offline deployment is supported), local "
                "model backends only, telemetry and update checks disabled, "
                "TokenRhythm and hosted providers avoided. Governance caveats: no "
                "legal entity or jurisdiction identified for the project, telemetry "
                "endpoint undisclosed, and maintenance durability unproven (~3 "
                "months old)."
            ),
        },
        "compliance": ["self-hosted"],
        "pricing": (
            "Free, open source (Apache-2.0); no paid tiers for the software found. "
            "The optional associated TokenRhythm API service runs a CNY-denominated "
            "pilot with no standard price list published."
        ),
        "academic": "No academic or student program found.",
        "use_cases": [
            "self-hosted agent runtime on lab or institutional hardware (gateway bound to localhost by default)",
            "local-model agentic coding and data tasks with sandboxed shell and file tools",
            "token-budget-constrained agent workflows (routing/ensembles reducing token spend)",
            "offline/air-gapped deployment with on-device embeddings",
        ],
        "runs_locally": True,
        "links": {
            "docs": "https://github.com/opensquilla/opensquilla",
            "pricing": "",
            "privacy": "https://raw.githubusercontent.com/opensquilla/opensquilla/main/PRIVACY.md",
        },
        "notes": (
            "Self-hostable agent runtime (CLI REPL, one-shot mode, gateway server) "
            "with three-tier OS sandboxing and persistent memory. Very active but "
            "young (~3 months); no legal entity or jurisdiction is identified in "
            "first-party sources (primary domain redirects to opensquilla.cn and "
            "the associated TokenRhythm service is CNY-priced - entity UNVERIFIED), "
            "and the default-on telemetry's endpoint is undisclosed. Classified "
            "conservatively."
        ),
        "sources": [
            "https://github.com/opensquilla/opensquilla",
            "https://raw.githubusercontent.com/opensquilla/opensquilla/main/PRIVACY.md",
            "https://raw.githubusercontent.com/opensquilla/opensquilla/main/LICENSE",
            "https://opensquilla.cn/",
            "https://api.github.com/repos/opensquilla/opensquilla",
        ],
        "status": "active",
        "current_name": "OpenSquilla",
        "confidence": "medium",
        "verified": TODAY,
        "established": False,
        "tier_gate": "fully self-hosted + local models + telemetry disabled for regulated data",
        "software_license": "Apache-2.0",
        "license_status": "confirmed",
        "special_route": cfg_route(
            "Institution-controlled infrastructure only: fully self-hosted, local "
            "model backends only, telemetry and update checks disabled "
            "(OPENSQUILLA_PRIVACY_DISABLE_NETWORK_OBSERVABILITY=true), TokenRhythm "
            "and hosted providers avoided."
        ),
    },
]


for new_record in NEW_RECORDS:
    if new_record["id"] not in by_id:
        records.append(new_record)
        by_id[new_record["id"]] = new_record

# ---------------------------------------------------------------------------
# Dates: every record was re-checked today; only materially changed retained
# records get date_modified (new records carry their own dates already).
# ---------------------------------------------------------------------------

new_ids = {record["id"] for record in NEW_RECORDS}
for record in records:
    record["verified"] = TODAY
    if record["id"] in changed_ids and record["id"] not in new_ids:
        record["date_modified"] = TODAY

# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------

ids = [record["id"] for record in records]
if len(ids) != len(set(ids)):
    raise SystemExit("duplicate record IDs after 2026-08-13 refresh")
if len(records) != 60:
    raise SystemExit(f"expected 60 records after refresh, found {len(records)}")
for required_id in sorted(new_ids):
    if required_id not in by_id:
        raise SystemExit(f"missing new record {required_id}")
if by_id["rca-windsurf"]["name"] != "Devin Desktop" or "Windsurf" not in by_id["rca-windsurf"].get("aliases", []):
    raise SystemExit("Windsurf -> Devin Desktop rename not applied")
if by_id["rca-hex-magic"]["name"] != "Hex" or "Hex Magic" not in by_id["rca-hex-magic"].get("aliases", []):
    raise SystemExit("Hex Magic -> Hex rename not applied")
for record in records:
    if record["verified"] != TODAY:
        raise SystemExit(f"{record['id']}: verified date not refreshed")

DATA.write_text(json.dumps(records, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
print(
    f"updated {DATA}: {len(records)} records "
    f"({len(changed_ids)} changed, {len(new_ids)} added, all verified {TODAY})"
)

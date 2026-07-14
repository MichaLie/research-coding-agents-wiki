#!/usr/bin/env python3
"""Apply the 2026-07-13 first-party live audit to tools.json.

This is a dated, reviewable data migration. It is intentionally conservative:
unsupported privacy/compliance claims are removed, cloud use is never treated as
acceptable for special-category data, and runnable local paths are stated as
configuration requirements rather than product-wide guarantees.
"""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools.json"
TODAY = "2026-07-13"


records = json.loads(DATA.read_text(encoding="utf-8"))
by_id = {record["id"]: record for record in records}


def patch(identifier: str, **fields: object) -> None:
    record = by_id[identifier]
    for key, value in fields.items():
        if isinstance(value, dict) and isinstance(record.get(key), dict):
            record[key].update(value)
        else:
            record[key] = value


patch(
    "rca-claude-code",
    data_handling_note=(
        "Consumer training depends on the user's data-use setting rather than being universally on: "
        "retention is up to 5 years when model improvement is enabled and 30 days when disabled. "
        "Commercial Claude/API data is not used for training by default. Approved Enterprise "
        "organizations and eligible API configurations can receive Zero Data Retention, but remote/web "
        "sessions and third-party integrations require separate scope review. Claude Code also stores "
        "local plaintext transcripts under ~/.claude/projects/ for 30 days by default."
    ),
    tier_gate="approved Enterprise organization or eligible API ZDR configuration",
    suitability_notes={
        "personal": "Use a commercial plan with a signed DPA and confirm that the exact Claude Code surface is covered by the retention agreement; review and protect local plaintext transcripts.",
        "special": "Cloud inference means data leaves controlled infrastructure. Do not use for identifiable or controlled-access health/genetic/clinical data under this index's strict rule.",
    },
    links={"privacy": "https://privacy.claude.com/en/"},
    sources=[
        "https://code.claude.com/docs/en/data-usage",
        "https://code.claude.com/docs/en/zero-data-retention",
        "https://code.claude.com/docs/en/legal-and-compliance",
        "https://privacy.claude.com/en/articles/10015870-what-certifications-has-anthropic-obtained",
    ],
    notes="Claude Code spans CLI, IDE, desktop, web, and remote surfaces. Retention and ZDR scope must be checked for the exact surface and integration; local transcripts are a separate governance boundary.",
)

patch(
    "rca-openai-codex",
    model_backend="GPT-5.6 Codex family (availability changes over time; OpenAI proprietary)",
    pricing="Included with eligible ChatGPT plans; ChatGPT Business is $20/user/month annually or $25 monthly. New Codex-only Business seats stopped being offered June 24, 2026; existing eligible workspaces may retain them. API usage is metered separately.",
    links={
        "docs": "https://learn.chatgpt.com/docs",
        "pricing": "https://learn.chatgpt.com/docs/pricing",
        "privacy": "https://openai.com/business-data/",
    },
    sources=[
        "https://developers.openai.com/api/docs/guides/your-data",
        "https://openai.com/business-data/",
        "https://openai.com/business/pricing/",
        "https://openai.com/index/codex-flexible-pricing-for-teams/",
        "https://help.openai.com/en/articles/20001147-codex-credits-for-students-terms-of-service",
    ],
    notes="Current Codex is OpenAI's multi-surface coding agent, distinct from the retired 2021 code-completion models. Product versions, model availability, and seat packaging are dynamic; use the dated sources rather than retained user-count or CLI-version claims.",
)

patch(
    "rca-gemini-cli",
    openness="open-source",
    deployment="local CLI / cloud inference",
    model_backend="Gemini models via paid API, Vertex AI, or Gemini Code Assist; consumer access is transitioning to the separate Antigravity CLI product",
    data_handling_note="The Apache-2.0 Gemini CLI remains an active open-source client with enterprise-supported paid API, Vertex AI, and Code Assist routes. Unpaid consumer use may be used for product/model improvement unless the user opts out; paid Gemini API, Vertex AI, and enterprise Code Assist do not train on customer data. Consumer migration to Antigravity CLI does not rename or close the Gemini CLI project.",
    pricing="Open-source CLI is free; model use follows Gemini API, Vertex AI, or Code Assist quotas and pricing. Consumer Google-account access is transitioning to the separate Antigravity CLI product.",
    status="active",
    current_name="Gemini CLI",
    notes="Keep Gemini CLI and Google Antigravity as separate records: Gemini CLI remains an Apache-2.0 client for paid API/Vertex/enterprise use, while consumer access is moving to the proprietary Antigravity CLI.",
    sources=[
        "https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/",
        "https://github.com/google-gemini/gemini-cli/discussions/27274",
        "https://google-gemini.github.io/gemini-cli/docs/tos-privacy.html",
        "https://google-gemini.github.io/gemini-cli/docs/quota-and-pricing.html",
    ],
)

patch(
    "rca-aider",
    suitability={"special": "cfg"},
    suitability_notes={
        "personal": "Use a fully local model, or a cloud provider covered by an appropriate DPA and no-training terms; Aider itself is not the processor for cloud inference.",
        "special": "Requires a fully local model on controlled infrastructure. Any cloud-model configuration moves data outside that boundary and is not acceptable under this index's strict rule.",
    },
    notes="Open-source pair-programming CLI whose capability and data boundary depend on the configured model. Analytics are opt-in and exclude code, chat, and API keys; remove volatile popularity/version counts from maintenance claims.",
)

patch(
    "rca-goose",
    data_handling_note="Goose can use local models with all prompts/code kept on-device, or cloud providers under their own terms. Usage-data collection is offered at first use and the documented default is disabled; it covers operational metadata, not code or prompts. No project-level DPA or clinical certification replaces assessment of the selected model route.",
    suitability_notes={
        "personal": "Prefer a fully local model, or use a cloud provider only under an appropriate DPA/no-training agreement. Keep optional usage-data collection disabled.",
        "special": "Requires a fully local model on controlled infrastructure. Keep optional usage-data collection disabled; cloud model routes are not acceptable.",
    },
    notes="Open-source CLI and desktop agent under Agentic AI Foundation/Linux Foundation governance. Its privacy posture is determined mainly by the configured model provider; optional usage-data collection is disabled by default.",
    sources=[
        "https://goose-docs.ai/docs/guides/usage-data/",
        "https://goose-docs.ai/docs/guides/environment-variables/",
        "https://github.com/aaif-goose/goose",
        "https://www.linuxfoundation.org/press/linux-foundation-announces-the-formation-of-the-agentic-ai-foundation",
    ],
)

patch(
    "rca-cursor",
    data_handling_note="Privacy Mode can be enabled by individuals and is enforced for users who belong to a team. It prevents Cursor and model providers from using content for training, but requests still route through Cursor's backend, including BYOK requests. Cursor's DPA prohibits submission of sensitive/special-category data. There is no controlled-infrastructure inference path.",
    tier_gate="Privacy Mode + appropriate team/enterprise DPA",
    academic="No current general student entitlement was confirmed on the official student page.",
    suitability_notes={
        "personal": "Enable Privacy Mode and use an organizational contract/DPA that permits the intended personal-data processing. BYOK does not bypass Cursor's backend.",
        "special": "Cloud-only and the DPA restricts sensitive-data submission. Not suitable for health/genetic/clinical data under this index's controlled-infrastructure rule.",
    },
    sources=[
        "https://cursor.com/data-use",
        "https://cursor.com/security",
        "https://cursor.com/privacy",
        "https://cursor.com/terms/dpa",
        "https://cursor.com/pricing",
        "https://cursor.com/students",
    ],
    notes="AI-native editor with cloud inference. Privacy Mode is available to individuals and enforced for teams, but BYOK still traverses Cursor's backend; no self-hosted or air-gapped inference option was confirmed.",
)

patch(
    "rca-github-copilot",
    compliance=[
        "SOC 2 Type I",
        "ISO/IEC 27001:2013",
        "GDPR (DPA available for Business/Enterprise)",
    ],
    academic="Verified students and teachers may qualify for Copilot access, but student chat/agent capabilities are reduced and new student signups were temporarily paused as of this audit.",
    notes="Individual Free/Pro/Pro+ interaction data can be used for training by default unless the user opts out; Business/Enterprise remain no-training. EU/US residency changes model multipliers rather than adding a flat plan surcharge. Copilot itself was not yet documented as FedRAMP authorized.",
    sources=[
        "https://github.com/features/copilot/plans",
        "https://docs.github.com/en/copilot/get-started/plans",
        "https://docs.github.com/en/copilot/how-tos/manage-your-account/manage-policies",
        "https://github.blog/changelog/2026-04-13-copilot-data-residency-in-us-eu-and-fedramp-compliance-now-available/",
        "https://github.blog/changelog/2026-06-01-updates-to-github-copilot-billing-and-plans/",
    ],
)

patch(
    "rca-windsurf",
    deployment="cloud",
    runs_locally=False,
    data_handling_note="Windsurf is now Devin Desktop. Paid users can opt out of training; after opt-out Cognition applies no-training and model-provider ZDR, with team controls administered centrally. Cognition's Customer Dedicated Deployment is vendor-hosted isolated infrastructure, not customer-controlled on-prem or self-hosting; the Devin brain remains in Cognition Cloud.",
    tier_gate="paid plan + training opt-out; organizational DPA for personal data",
    suitability_notes={
        "personal": "Use a paid plan, opt out of training, and execute the Cognition DPA before processing personal data. Customer Dedicated Deployment is still Cognition-hosted.",
        "special": "Cloud inference remains in Cognition infrastructure. Not suitable for special-category data under the controlled-infrastructure rule.",
    },
    compliance=["SOC 2 Type II"],
    academic="No current official student discount was confirmed.",
    links={
        "docs": "https://docs.devin.ai/desktop/getting-started",
        "pricing": "https://devin.ai/pricing",
        "privacy": "https://cognition.com/legal/privacy-policy",
    },
    sources=[
        "https://cognition.com/blog/introducing-devin-desktop",
        "https://cognition.com/legal/platform-terms-of-service",
        "https://cognition.com/legal/privacy-policy",
        "https://docs.devin.ai/enterprise/deployment/overview",
        "https://docs.devin.ai/admin/billing/self-serve",
        "https://cognition.com/documents/Cognition-DPA.pdf",
    ],
    notes="Renamed to Devin Desktop after the Cognition acquisition. It is cloud-based even when the client runs locally; vendor-hosted dedicated deployment must not be described as self-hosted or on-prem.",
)

patch(
    "rca-google-antigravity",
    data_handling_note="Consumer use follows Google consumer terms and may contribute to improvement unless opted out. Enterprise/GCP access is broadly available and provides contractual no-training and DPA controls; inference remains cloud-based.",
    tier_gate="enterprise/GCP contract + DPA",
    suitability={"personal": "cfg"},
    suitability_notes={
        "personal": "Use the enterprise/GCP route with contractual no-training and a signed DPA; consumer use is not suitable for personal data by default.",
        "special": "Cloud-only. Not suitable for special-category data under the controlled-infrastructure rule.",
    },
    pricing="Free, Google AI Pro ($20), Google AI Ultra ($100), and top Ultra ($200) tiers are documented; enterprise/GCP terms are contractual.",
    academic="No separate academic entitlement was confirmed; do not treat consumer family sharing as an academic control.",
    sources=[
        "https://antigravity.google/terms",
        "https://antigravity.google/blog/google-antigravity-for-enterprises",
        "https://antigravity.google/blog/changes-to-antigravity-plans",
        "https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/",
    ],
    notes="Proprietary agentic development platform distinct from the open-source Gemini CLI. Consumer and enterprise/GCP data terms differ materially; enterprise access is no longer invite-only.",
)

patch(
    "rca-jetbrains-junie",
    deployment="cloud / local-capable",
    data_handling="local",
    data_handling_note="Junie CLI supports Ollama and custom local endpoints, allowing inference to remain on controlled infrastructure. For JetBrains-hosted/provider routes, detailed code-data sharing is opt-in and disabled by default for commercial organizations; one-year retention applies only after opt-in. BYOK and cloud routes must be assessed separately.",
    tier_gate="fully local endpoint for special-category data; AI Enterprise terms for organizational cloud use",
    suitability={"special": "cfg"},
    suitability_notes={
        "personal": "Use a signed DPA and keep detailed data sharing disabled, or configure a fully local endpoint.",
        "special": "Requires Junie CLI with a fully local Ollama/custom endpoint on controlled infrastructure. Cloud provider routes are not acceptable.",
    },
    pricing="AI Free; AI Pro ($10/month individual, $20 organization); AI Ultimate ($30 individual, $60 organization); AI Enterprise $60/user/month. BYOK/provider costs are separate.",
    sources=[
        "https://junie.jetbrains.com/docs/custom-llm-ollama.html",
        "https://junie.jetbrains.com/docs/custom-llm-models.html",
        "https://www.jetbrains.com/help/ai-assistant/how-we-handle-your-code-and-data.html",
        "https://www.jetbrains.com/legal/docs/terms/product_data_collection/",
        "https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html",
    ],
    notes="Agentic assistant in JetBrains IDEs and a CLI. The fully local Ollama/custom-endpoint path is the qualifying controlled-infrastructure route; do not generalize cloud no-training terms to local execution or vice versa.",
)

patch(
    "rca-continue-dev",
    vendor="Continue Dev, Inc. (archived project)",
    status="discontinued",
    current_name="Continue v2.0.0 (archived)",
    notes="Final v2.0.0 removed telemetry and authentication, and the repository is read-only. Local use remains technically possible, but no active vendor, DPA, or support path remains; the record is removed below under the maintenance-health rule.",
    sources=[
        "https://www.continue.dev/",
        "https://github.com/continuedev/continue",
        "https://www.continue.dev/privacy",
    ],
)

patch(
    "rca-cline",
    deployment="local-capable / cloud provider dependent",
    data_handling_note="With direct BYOK, prompts/code go to the selected provider and are not received by Cline; with Ollama or LM Studio they can remain fully local. Cline-hosted/provider routes remain subject to Cline's service terms. Official enterprise claims cover client-side execution, provider choice, VPC options, and no code/prompt visibility, not a universally self-hosted Cline service.",
    suitability_notes={
        "personal": "Use a fully local model or a direct provider route covered by an appropriate DPA/no-training agreement. Assess Cline-hosted service routes separately.",
        "special": "Requires a fully local Ollama/LM Studio model on controlled infrastructure. Enterprise/VPC wording alone does not establish this boundary.",
    },
    links={"docs": "https://docs.cline.bot/cline-overview"},
    sources=[
        "https://cline.bot/pricing",
        "https://cline.bot/tos",
        "https://cline.bot/privacy",
        "https://cline.bot/enterprise",
        "https://docs.cline.bot/running-models-locally/overview",
    ],
    notes="Open-source client with direct-provider and local-model routes. Privacy claims must be scoped to the selected route; enterprise does not automatically mean a fully self-hosted inference service.",
)

patch(
    "rca-tabnine",
    data_handling_note="Paid cloud plans document no-training/no-retention handling. Private installation, on-prem, and air-gapped deployment are Enterprise capabilities; they were not confirmed for both self-service price tiers.",
    tier_gate="Enterprise private installation for controlled-infrastructure use",
    suitability_notes={
        "personal": "Use an appropriate DPA for SaaS or Enterprise private installation when data must remain within institutional infrastructure.",
        "special": "Requires Enterprise private installation/on-prem/air-gap on controlled infrastructure. Cloud infrastructure certifications do not substitute for product-scope evidence.",
    },
    compliance=["SOC 2", "ISO/IEC 27001", "ISO 9001", "GDPR posture"],
    sources=[
        "https://docs.tabnine.com/main/administering-tabnine/managing-your-team",
        "https://docs.tabnine.com/main/welcome/readme/security",
        "https://trust.tabnine.com/",
        "https://www.tabnine.com/pricing/",
    ],
    notes="Privacy-focused commercial assistant. The qualifying special-category path is Enterprise private installation; cloud-provider datacenter certifications must not be presented as Tabnine product certifications.",
)

patch(
    "rca-tabby",
    model_backend="Self-hosted open-weight models for Tabby; Pochi is Apache-2.0, BYOK, and also supports self-hosted/custom model endpoints",
    data_handling_note="Tabby and Pochi can run with self-hosted models so code stays on controlled infrastructure. Pochi does not require an account for BYOK. Anonymous server/extension usage collection is enabled by default, contains documented non-code operational statistics, and can be disabled. The website privacy policy is not evidence for prompt handling in every model route.",
    suitability_notes={
        "personal": "Use a self-hosted model and disable anonymous usage collection where required; assess any cloud provider separately.",
        "special": "Requires self-hosted Tabby/Pochi with a local model on controlled infrastructure and usage collection disabled.",
    },
    sources=[
        "https://www.tabbyml.com/pricing",
        "https://github.com/TabbyML/pochi",
        "https://github.com/TabbyML/tabby",
        "https://tabby.tabbyml.com/docs/administration/usage-collection/",
        "https://tabby.tabbyml.com/docs/extensions/configurations/",
        "https://www.tabbyml.com/privacy",
    ],
    notes="Self-hostable coding stack with the Pochi agent. Pochi is not cloud-only; its BYOK and custom/local model routes must be distinguished from Tabby-hosted services.",
)

patch(
    "rca-devin",
    deployment="cloud / Cognition-hosted dedicated deployment",
    data_handling="no-train",
    data_handling_note="Cognition's baseline terms may permit training on Customer Data. Paid tiers can opt out; after opt-out Cognition applies no-training and model-provider ZDR. Customer Dedicated Deployment is Cognition-hosted isolated infrastructure, not self-hosting; the agent brain remains in Cognition Cloud.",
    tier_gate="paid plan + training opt-out + DPA",
    suitability_notes={
        "personal": "Use a paid plan, opt out of training, and execute the Cognition DPA with an appropriate legal basis.",
        "special": "The platform terms prohibit medical/sensitive personal information absent separate written authorization, and inference remains in vendor cloud. Not suitable under this index's rule.",
    },
    pricing="Free; Pro $20/month; Max $200/month; Teams $80 minimum plus $40/full seat; Enterprise uses order-form/ACU pricing.",
    sources=[
        "https://cognition.com/legal/platform-terms-of-service",
        "https://docs.devin.ai/enterprise/deployment/overview",
        "https://docs.devin.ai/admin/billing/self-serve",
        "https://docs.devin.ai/admin/billing",
        "https://cognition.com/legal/security",
        "https://cognition.com/documents/Cognition-DPA.pdf",
    ],
    confidence="high",
    notes="Autonomous cloud software engineer. Dedicated deployment is vendor-hosted, not customer-controlled on-prem; no-training requires a paid-tier opt-out and contractual review.",
)

patch(
    "rca-replit-agent",
    model_backend="Managed, dynamically changing model stack; Replit does not currently enumerate one fixed authoritative backend for Agent 4",
    data_handling_note="Replit's Commercial Agreement states that Customer Content is not used for training. Consumer/noncommercial privacy terms still permit machine-learning and product-improvement uses. Personal data therefore requires a commercial/enterprise agreement and DPA. All AI processing remains cloud-based.",
    suitability_notes={
        "personal": "Use a commercial/enterprise contract with the no-training clause and execute Replit's DPA; do not infer AI data residency from application-hosting regions.",
        "special": "Cloud-only and no public product-specific BAA was confirmed. Not suitable under the controlled-infrastructure rule even though the DPA contemplates regulated categories.",
    },
    links={"docs": "https://docs.replit.com/build/welcome", "privacy": "https://replit.com/privacy-policy"},
    sources=[
        "https://replit.com/commercial-agreement",
        "https://replit.com/dpa/",
        "https://replit.com/privacy-policy/",
        "https://replit.com/pricing",
        "https://replit.com/blog/introducing-agent-4-built-for-creativity",
        "https://replit.com/blog/whats-changed-agent3-to-agent4",
    ],
    notes="Agent 4 is released. The product uses a managed model stack and cloud execution; model identities and hosting-region claims should not be frozen without current first-party evidence.",
)

patch(
    "rca-openhands",
    data_handling_note="OpenHands Cloud may use customer content and feedback for model improvement. The controlled-infrastructure path is self-hosted OpenHands with a fully local model; enterprise deployment claims must be evaluated with the selected model/provider rather than assumed private by default.",
    suitability_notes={
        "personal": "Do not use the public cloud tier for personal data. Self-host and use a local model, or obtain an appropriate enterprise contract/DPA for every processor.",
        "special": "Requires self-hosted OpenHands plus a fully local model on controlled infrastructure. Cloud OpenHands and cloud LLM routes are not acceptable.",
    },
    links={
        "docs": "https://docs.openhands.dev/overview/introduction",
        "privacy": "https://www.openhands.dev/privacy",
    },
    sources=[
        "https://www.openhands.dev/privacy",
        "https://www.openhands.dev/pricing",
        "https://docs.openhands.dev/overview/introduction",
        "https://docs.openhands.dev/enterprise",
        "https://github.com/All-Hands-AI/OpenHands/releases",
    ],
    notes="Open-source/self-hostable coding agent with a separate cloud service. Remove volatile star/version counts; data safety depends on deployment and the configured model route.",
)

patch(
    "rca-jupyter-ai",
    model_backend="Jupyter AI v3 integrates agents through Agent Client Protocol; direct model access remains available through supported provider integrations, including local runtimes",
    pricing="Free and open source (BSD-3-Clause); users pay only any selected cloud-model provider costs",
    links={"pricing": "https://github.com/jupyterlab/jupyter-ai"},
    sources=[
        "https://github.com/jupyterlab/jupyter-ai",
        "https://jupyter-ai.readthedocs.io/en/latest/",
        "https://jupyter.org/privacy",
        "https://github.com/jupyterlab/jupyter-ai/releases",
    ],
    notes="Stable v3.0.1 was released 2026-06-30. Version 3 centers Agent Client Protocol integration; privacy remains determined by the chosen local agent/model or cloud provider.",
)

patch(
    "rca-julius-ai",
    pricing="Free; Plus $20 monthly/$16 annual; Pro $45/$37; Max $200/$166; Ultra $500/$416; Business $450/$375; Enterprise custom.",
    data_handling_note="Julius states that user data is not used for internal or external model training. Processing and storage occur in the US; Enterprise provides a DPA. No public HIPAA BAA was confirmed, so regulated health/genetic/clinical data remains excluded.",
    sources=[
        "https://julius.ai/privacy-policy",
        "https://julius.ai/security",
        "https://julius.ai/legal/dpa",
        "https://julius.ai/pricing",
        "https://julius.ai/docs/get-started/privacy-and-data-security",
    ],
    confidence="high",
    notes="Cloud data-analysis service with a public no-training commitment. A current official DPA is available; US processing/storage and the absence of a confirmed public BAA remain material boundaries.",
)

patch(
    "rca-hex-magic",
    data_handling_note="Hex uses provider no-training/ZDR arrangements, but Hex itself may use AI-session data for feature improvement unless the organization opts out. Personal-data use requires contractual controls, DPA, and appropriate residency; uploaded/output data still traverses Hex infrastructure.",
    tier_gate="Team/Enterprise + DPA and appropriate data stack",
    links={"docs": "https://learn.hex.tech/docs"},
    sources=[
        "https://learn.hex.tech/docs/trust/ai-data-privacy",
        "https://hex.tech/security/",
        "https://trust.hex.tech",
        "https://hex.tech/pricing/",
        "https://hex.tech/blog/hipaa-multi-tenant/",
    ],
    notes="Collaborative cloud analytics environment. Provider ZDR is not equivalent to Hex deleting or never using all AI-session data; organization opt-out and contract scope must be checked.",
)

patch(
    "rca-kiro",
    data_handling_note="Free and individual subscribers may have content used for service improvement/model training by default; individuals can opt out. Enterprise data is documented as not stored or used for improvement. Paid individual status alone does not establish no-training or no-storage.",
    tier_gate="Enterprise",
    suitability_notes={
        "personal": "Use Enterprise with its no-storage/no-improvement terms and appropriate institutional AWS agreements; individual paid plans are insufficient by themselves.",
        "special": "Cloud inference only. HIPAA eligibility or contractual controls do not satisfy this index's controlled-infrastructure requirement.",
    },
    compliance=["HIPAA eligible on documented Kiro services; contractual scope applies"],
    sources=[
        "https://kiro.dev/docs/privacy-and-security/data-protection/",
        "https://kiro.dev/docs/privacy-and-security/compliance-validation/",
        "https://kiro.dev/pricing/",
        "https://kiro.dev/docs/",
        "https://kiro.dev/docs/web/data-protection/",
    ],
    notes="Local IDE client with cloud inference. Enterprise, not paid individual status, is the documented no-storage/no-improvement route; product-scoped compliance must not be inferred from unrelated AWS services.",
)

patch(
    "rca-zed",
    data_handling="local",
    tier_gate="fully local model for sensitive data; Business for organization controls",
    suitability={"special": "cfg"},
    suitability_notes={
        "personal": "Use a fully local model, or a provider/DPA configuration accepted by the institution. Hosted models process data outside local infrastructure.",
        "special": "Requires Ollama or another fully local/self-hosted endpoint on controlled infrastructure. Hosted Zed/provider models are not acceptable.",
    },
    pricing="Personal free; Pro $10/month; Business $30/seat/month. Current official plan details and usage credits vary by model.",
    academic="Verified students receive the Student plan free for one year, with Pro features except Claude Opus and $10 monthly credits.",
    compliance=["GDPR rights and DPA pathway; verify contract and provider scope"],
    sources=[
        "https://zed.dev/docs/ai/privacy-and-security",
        "https://zed.dev/privacy-policy",
        "https://zed.dev/pricing",
        "https://zed.dev/docs/ai/plans-and-usage",
        "https://zed.dev/education",
        "https://zed.dev/docs/ai/overview",
        "https://github.com/zed-industries/zed",
    ],
    notes="Local-capable editor with hosted, BYOK, and fully local model routes. Special-category suitability applies only to the fully local route; no pending certification should be presented as achieved.",
)

patch(
    "rca-amp",
    data_handling_note="Enterprise provider ZDR covers model inputs/outputs, but Amp itself stores threads/customer content in US infrastructure. Explicit deletion may take up to 30 days; enterprise workspace threads may persist for the contract term, and provider caches may last up to 24 hours.",
    tier_gate="Enterprise + confirm signed DPA and retention terms",
    suitability_notes={
        "personal": "Only after confirming a signed DPA and accepting Amp's own thread/content retention; provider ZDR is not end-to-end deletion.",
        "special": "The service prohibits sensitive personal information including health/genetic data and remains cloud-based.",
    },
    sources=[
        "https://ampcode.com/security",
        "https://ampcode.com/privacy-policy",
        "https://ampcode.com/terms",
        "https://ampcode.com/manual#pricing",
        "https://ampcode.com/manual",
        "https://ampcode.com/news/drop-the-neo",
    ],
    notes="Cloud coding agent. Distinguish model-provider ZDR from Amp's own storage of threads and customer content; no public DPA was confirmed during this audit.",
)

patch(
    "rca-sourcegraph-cody",
    pricing="Enterprise platform pricing starts around $16,000/year and includes AI credits; contact sales. Free, Pro, and Enterprise Starter ended 2025-07-23.",
    notes="Active enterprise-only coding assistant integrated with Sourcegraph. Prior self-service plans have ended; assess current model-provider routing and Cody notice under the enterprise contract.",
    sources=[
        "https://sourcegraph.com/terms/cody-notice",
        "https://sourcegraph.com/docs/model-provider",
        "https://sourcegraph.com/pricing",
        "https://sourcegraph.com/docs/cody/faq",
        "https://sourcegraph.com/blog/changes-to-cody-free-pro-and-enterprise-starter-plans",
        "https://sourcegraph.com/changelog/releases",
    ],
)

patch(
    "rca-opencode",
    data_handling_note="OpenCode can use fully local providers, but OpenCode Zen is not uniformly ZDR: official documentation reports 30-day retention for OpenAI and Anthropic requests, and some free models may retain or train. Sharing must be disabled for private work and every selected provider must be reviewed.",
    pricing="OpenCode is open source. OpenCode Zen is pay-as-you-go with automatic $20 reload when balance falls below $5; model charges vary.",
    tier_gate="fully local model with sharing disabled for regulated data",
    suitability_notes={
        "personal": "Use a fully local provider, or verify the exact Zen/provider retention and DPA. Do not assume Zen-wide ZDR.",
        "special": "Requires a fully local model and disabled sharing on controlled infrastructure. Zen/cloud providers are not acceptable.",
    },
    sources=[
        "https://opencode.ai/legal/privacy-policy",
        "https://opencode.ai/legal/terms-of-service",
        "https://opencode.ai/docs/providers/",
        "https://opencode.ai/docs/zen/",
        "https://opencode.ai/docs/share/",
        "https://opencode.ai/docs/enterprise/",
        "https://github.com/anomalyco/opencode",
    ],
    notes="Open-source coding agent with local, direct-provider, and Zen routes. Privacy is route-specific; remove volatile launch/version/star claims and never describe Zen as uniformly zero-retention.",
)

patch(
    "rca-crush",
    suitability_notes={
        "special": "Requires a fully local model, provider updates disabled/offline, metrics disabled, and controlled execution. FSL-1.1-MIT is source-available and converts later; it is not presently an OSI open-source license.",
    },
    links={"docs": "https://github.com/charmbracelet/crush"},
    sources=[
        "https://hyper.charm.land/privacy",
        "https://hyper.charm.land",
        "https://github.com/charmbracelet/crush",
        "https://github.com/charmbracelet/crush/releases",
    ],
    notes="Local-capable coding agent under FSL-1.1-MIT (source-available, future conversion to MIT). Sensitive-data use requires a fully local/offline model and disabled metrics/provider updates.",
)

patch(
    "rca-mistral-vibe",
    data_handling_note="Free, Pro, and Education accounts use inputs/outputs for training by default unless the user opts out. Team and Enterprise do not train. Approved Scale customers may receive ZDR; Vibe CLI stateless API calls can use that scope. Offline/local models create a separate controlled-infrastructure route.",
    tier_gate="Team/Enterprise no-training; approved Scale ZDR; fully local model for special data",
    suitability_notes={
        "personal": "Use Team/Enterprise no-training terms or approved Scale ZDR with an appropriate DPA; consumer opt-out alone is weaker.",
        "special": "Requires Vibe with a fully local model on controlled infrastructure. Cloud no-training/ZDR is not sufficient.",
    },
    links={"docs": "https://docs.mistral.ai/vibe/code/cli/offline-models"},
    sources=[
        "https://help.mistral.ai/en/articles/347617-do-you-use-my-user-data-to-train-your-artificial-intelligence-models",
        "https://help.mistral.ai/en/articles/347612-can-i-activate-zero-data-retention-zdr",
        "https://legal.mistral.ai/terms/privacy-policy",
        "https://mistral.ai/pricing/",
        "https://mistral.ai/products/vibe/code/",
        "https://docs.mistral.ai/vibe/code/cli/offline-models",
        "https://github.com/mistralai/mistral-vibe",
    ],
    notes="Current stable release v2.19.1 (2026-07-09). Training defaults differ by account class; remove unverified EU-default-storage and certification assertions.",
)

patch(
    "rca-kiro-cli",
    data_handling_note="Free and individual users may have content used for improvement/training by default; paid individual status does not itself establish no-training. Enterprise is the documented no-storage/no-improvement route. CLI execution is local but inference is cloud-based.",
    tier_gate="Enterprise",
    suitability_notes={
        "personal": "Use Enterprise terms with institutional AWS agreements; individual paid/social-login plans are insufficient by themselves.",
        "special": "Cloud inference only; not suitable under the controlled-infrastructure rule.",
    },
    sources=[
        "https://kiro.dev/docs/cli/privacy-and-security/data-protection/",
        "https://kiro.dev/docs/cli/privacy-and-security/compliance-validation/",
        "https://kiro.dev/pricing/",
        "https://kiro.dev/docs/cli/",
    ],
    notes="Terminal client for Kiro's cloud inference. Apply the same enterprise data-protection boundary as the IDE; do not infer no-training from payment alone.",
)

patch(
    "rca-warp",
    data_handling_note="Warp contracts model providers for ZDR/no-training, but Warp's own AI/console collection is a separate control. Business and Enterprise disable that collection by default; Free can opt out with effects on AI availability. Self-hosting covers execution-plane components, not the cloud orchestration/control plane.",
    tier_gate="Business or Enterprise",
    suitability_notes={
        "personal": "Use Business/Enterprise with DPA and collection disabled; confirm all connected model and orchestration processors.",
        "special": "Warp's control/orchestration plane remains cloud-based even with self-hosted execution components; not suitable under this index's rule.",
    },
    sources=[
        "https://docs.warp.dev/support-and-community/privacy-and-security/privacy",
        "https://docs.warp.dev/enterprise/security-and-compliance/security-overview",
        "https://www.warp.dev/legal/privacy-policy",
        "https://www.warp.dev/legal/security",
        "https://www.warp.dev/legal/data-processing-addendum",
        "https://www.warp.dev/pricing",
    ],
    notes="Cloud-orchestrated terminal/agent. Separate provider ZDR from Warp collection, and do not treat self-hosted execution-plane components as full on-prem deployment.",
)

patch(
    "rca-augment-code",
    pricing="Business $100/month for the whole team (up to 50 seats, including $100 usage); Enterprise custom.",
    data_handling_note="Paid plans state that customer data is not used for training. Public documentation advertises VPC, single-tenant, on-prem, BYOK, CMEK, and residency options, but ZDR plan scope was not sufficiently explicit to generalize beyond a negotiated enterprise contract.",
    tier_gate="Enterprise contract for ZDR/on-prem controls",
    sources=[
        "https://www.augmentcode.com/security",
        "https://www.augmentcode.com/legal/privacy-policy",
        "https://trust.augmentcode.com",
        "https://www.augmentcode.com/pricing",
        "https://docs.augmentcode.com/cli/overview",
        "https://www.augmentcode.com/product/cli",
        "https://www.augmentcode.com/contact",
    ],
    notes="Commercial coding platform with current Business team pricing and negotiated enterprise deployment controls. Remove obsolete Indie/Standard/Max tiers and unsupported trust-center availability claims.",
)

patch(
    "rca-plandex",
    status="discontinued",
    notes="Plandex Cloud wound down in 2025 and the official repository has been stale since 2025-10-03. Self-hosting can still send data to configured cloud models; it is removed below under the maintenance-health rule.",
    sources=[
        "https://github.com/plandex-ai/plandex/blob/main/guides/PRIVACY.md",
        "https://github.com/plandex-ai/plandex",
        "https://docs.plandex.ai",
        "https://github.com/plandex-ai/plandex/releases",
    ],
)

patch(
    "rca-jules",
    model_backend="Gemini models managed by Google; Free currently uses Gemini 2.5 Pro and paid plans receive newer model access",
    data_handling_note="Google states that private repositories are not used for training; do not extend that statement to public repositories. Task VMs are destroyed, but persisted product memory/context is a separate retention boundary. Current Jules plans are individual Google-account plans, with no public Jules-specific DPA, institutional residency control, or retention SLA confirmed.",
    tier_gate="no institutional personal-data route publicly verified",
    suitability={"personal": "no"},
    suitability_notes={
        "personal": "No public Jules-specific DPA, retention SLA, or institutional residency control was confirmed. Do not submit personal data.",
        "special": "Cloud-only and no institutional controlled-infrastructure route exists. Do not submit health/genetic/clinical data.",
    },
    pricing="Free: 15 tasks/day and 3 concurrent; Pro: 100/day and 15 concurrent; Ultra: 300/day and 60 concurrent. Subscription prices depend on the current localized Google AI plan.",
    academic="No current Jules-specific institutional or academic plan was verified.",
    sources=[
        "https://jules.google/docs/usage-limits",
        "https://jules.google/docs/faq/",
        "https://jules.google/docs/environment/",
        "https://jules.google/docs/changelog/",
    ],
    notes="Out of beta cloud coding agent for individual Google accounts. Private repositories are excluded from training, but product memory and missing institutional contract controls prevent a personal-data recommendation.",
)

patch(
    "rca-swe-agent",
    status="discontinued",
    notes="Maintenance-only predecessor superseded by mini-SWE-agent. The record is replaced below so the curated index points to the actively maintained implementation.",
)

patch(
    "rca-gptme",
    deployment="local-capable / optional hosted service",
    data_handling_note="The open-source tool can run locally/self-hosted, but gptme now also presents a managed service. Hosted-service retention, training, DPA, and residency terms were not adequately documented. Local execution runs with the user's permissions and should use a container or restricted account.",
    tier_gate="fully local/self-hosted model for regulated data",
    suitability={"personal": "cfg", "special": "cfg"},
    suitability_notes={
        "personal": "Use a fully local model and controlled execution. Do not use the hosted path for personal data until contractual processing terms are published and accepted.",
        "special": "Requires a fully local model plus container/restricted-user execution on controlled infrastructure. Hosted/cloud model routes are not acceptable.",
    },
    sources=[
        "https://gptme.org/docs/providers.html",
        "https://gptme.org/docs/getting-started.html",
        "https://gptme.org/docs/security.html",
        "https://gptme.org/docs/contributing.html",
        "https://gptme.ai/pricing",
    ],
    notes="Local-capable coding agent with an emerging managed-service path. Privacy claims are confined to the local configuration; no blanket OpenRouter deny-collection guarantee is asserted.",
)

patch(
    "rca-open-interpreter",
    deployment="local-capable / optional hosted inference",
    model_backend="Current Rust desktop/CLI agent derived from Codex; local models, direct BYO-key providers, or Open Interpreter-hosted inference",
    data_handling_note="The current Rust product replaces the former Python implementation (now community-maintained separately). Local models can remain on-device; BYO-key requests go directly to the provider. Open Interpreter-hosted requests traverse its infrastructure and may be logged for up to 30 days. No adequate public DPA, BAA, certification, or residency evidence was confirmed for hosted mode.",
    tier_gate="fully local model for personal/special-category data",
    suitability={"personal": "cfg", "special": "cfg"},
    suitability_notes={
        "personal": "Use the current client with a fully local model, or independently contract the direct provider. Do not use Open Interpreter-hosted inference for personal data without adequate terms.",
        "special": "Requires a fully local model on controlled infrastructure. Hosted and direct cloud-provider routes are not acceptable.",
    },
    use_cases=[
        "local coding and shell automation",
        "computer and file task automation",
        "code generation and execution",
        "agentic workflows with local or direct-provider models",
    ],
    links={
        "docs": "https://www.openinterpreter.com/cli",
        "pricing": "https://www.openinterpreter.com/",
        "privacy": "https://www.openinterpreter.com/privacy",
    },
    sources=[
        "https://www.openinterpreter.com/",
        "https://www.openinterpreter.com/cli",
        "https://github.com/openinterpreter/openinterpreter",
        "https://www.openinterpreter.com/privacy",
    ],
    confidence="high",
    notes="Current Rust product, distinct from the former Python implementation. Local, direct-provider, and Open Interpreter-hosted routes have different data boundaries; old offline/telemetry documentation must not be carried forward.",
)

patch(
    "rca-kilo-code",
    data_handling_note="Kilo supports fully local Ollama/LM Studio and local indexing. Official materials state no prompt/output retention on paid plans, but this must not be generalized to every free cloud route. Cloud terms prohibit regulated sensitive data.",
    tier_gate="fully local model and local indexing for special-category data; paid/enterprise terms for cloud",
    suitability_notes={
        "personal": "Prefer fully local inference/indexing, or use a paid plan only after confirming DPA and retention scope.",
        "special": "Requires fully local Ollama/LM Studio and local indexing on controlled infrastructure. Kilo cloud routes prohibit regulated sensitive data.",
    },
    compliance=["SOC 2 materials available through Trust Center; public type/scope not confirmed"],
    sources=[
        "https://kilo.ai/pricing",
        "https://kilo.ai/security-and-compliance",
        "https://kilo.ai/privacy",
        "https://kilo.ai/terms",
        "https://kilo.ai/docs/ai-providers/ollama",
        "https://kilo.ai/docs/customize/context/codebase-indexing",
    ],
    notes="Local and cloud coding-agent routes. The special-category recommendation applies only to fully local inference and indexing; paid-cloud no-retention wording is not a universal product guarantee.",
)

patch(
    "rca-google-colab-data-science-agent",
    model_backend="Managed Gemini backend; Google does not currently document one fixed model for all Data Science Agent use",
    data_handling_note="Consumer Colab AI may collect prompts, code, outputs, usage, and feedback for product/model improvement, including human review and retention up to 18 months; Google warns against sensitive/personal data. Colab Enterprise provides contractual Cloud controls but remains cloud-based.",
    tier_gate="Colab Enterprise + Cloud DPA/governance for personal data",
    pricing="Consumer Colab plan pricing varies. Colab Enterprise Data Science Agent is billed at $3 per million input tokens and $20 per million output tokens, plus compute.",
    academic="No separate current academic privacy tier was confirmed; consumer educational use does not change data-handling terms.",
    compliance=["Google Cloud controls only where the exact Colab Enterprise service, region, and contract are in scope"],
    suitability_notes={
        "personal": "Use Colab Enterprise only with an accepted Cloud DPA and governance configuration; consumer Colab AI is not suitable.",
        "special": "Cloud-only. Do not use for special-category data under this index's controlled-infrastructure rule.",
    },
    sources=[
        "https://research.google.com/colaboratory/faq.html",
        "https://docs.cloud.google.com/colab/docs/use-data-science-agent",
        "https://cloud.google.com/colab/pricing",
    ],
    notes="Cloud notebook agent. Consumer and Enterprise data terms differ substantially; avoid fixed model identities and broad GCP certifications without product/region/contract scope.",
)

patch(
    "rca-deepnote",
    deployment="cloud / Enterprise on-prem or customer-managed single-tenant",
    runs_locally=True,
    tier_gate="Enterprise on-prem/customer-managed deployment + approved local model for special data",
    suitability={"special": "cfg"},
    suitability_notes={
        "special": "Requires Enterprise deployment behind the customer firewall and an approved local/self-hosted model backend. Deepnote Cloud remains unsuitable; PHI also requires a BAA under vendor terms.",
    },
    sources=[
        "https://deepnote.com/docs/ai-data-privacy",
        "https://deepnote.com/pricing",
        "https://deepnote.com/docs/security-overview",
        "https://deepnote.com/enterprise",
        "https://deepnote.com/docs/local-setup",
        "https://deepnote.com/docs/acceptable-use-policy",
    ],
    notes="Cloud collaborative notebook with Enterprise customer-managed/on-prem deployment options. Local file tooling is not a complete local AI product; special-category suitability requires the controlled Enterprise deployment plus local inference.",
)

patch(
    "rca-databricks-genie-code",
    data_handling_note="Partner-model contracts may provide no-training/ZDR, but Databricks stores Genie Code chat history with notebook/control-plane content and agents may inspect outputs/data samples. Provider ZDR is therefore not end-to-end deletion.",
    tier_gate="appropriate Databricks contract, region, compliance profile, and workspace governance",
    pricing="Billing began 2026-07-08. Official example: 150 DBUs is approximately $10.50 in US East; compute is additional and regional pricing varies.",
    compliance=["Contract-, cloud-, region-, and compliance-profile dependent; verify exact Databricks service scope"],
    sources=[
        "https://docs.databricks.com/aws/en/genie-code",
        "https://docs.databricks.com/aws/en/genie/budgets",
        "https://www.databricks.com/product/pricing/genie",
        "https://docs.databricks.com/aws/en/databricks-ai/databricks-ai-trust",
        "https://docs.databricks.com/aws/en/security/privacy/hipaa",
    ],
    notes="Cloud data-platform agent. Distinguish partner-model ZDR from Databricks persistence of chats, notebook content, outputs, and samples; remove speculative future compliance claims.",
)

patch(
    "rca-posit-ai-posit-assistant",
    model_backend="Anthropic Claude and Posit-hosted Google Gemma 4; Workbench/provider extensions remain preview or experimental",
    data_handling_note="ZDR is specifically documented for the Anthropic route and must not be generalized to Posit-hosted Gemma. With trace sharing disabled, operational metadata is retained for 30 days; opt-in traces may be retained up to five years and used for improvement/training.",
    tier_gate="Posit AI subscription + Anthropic backend + trace opt-out",
    suitability_notes={
        "personal": "Use the documented Anthropic route with trace sharing disabled and an accepted Posit contract/DPA.",
        "special": "No fully local model path was confirmed for the product; self-hosting the IDE/session alone is insufficient.",
    },
    sources=[
        "https://docs.posit.co/posit-ai/user/faq/",
        "https://docs.posit.co/ide/user/ide/guide/tools/posit-ai.html",
        "https://docs.posit.co/ide/server-pro/admin/positron_sessions/positron-assistant.html",
        "https://posit.co/blog/posit-ai-priced-long-run",
    ],
    notes="Posit AI product in transition: Databot is deprecated and Posit says Positron Assistant is planned to be superseded in Q3 2026. Treat backend-specific data terms separately.",
)

patch(
    "rca-marimo",
    model_backend="Local/BYOK providers in marimo; molab additionally offers free hosted models",
    data_handling_note="The local marimo core can use local or BYOK providers, while molab is a hosted service with separate terms and free hosted models. molab expressly prohibits HIPAA-regulated and GDPR Article 9 special-category data.",
    notes="Open-source reactive notebook with local AI-provider support and a separate molab hosted service. Do not describe the product as having no hosted model or claim that its privacy page redirects elsewhere.",
    sources=[
        "https://docs.marimo.io/guides/editor_features/ai_completion/",
        "https://docs.marimo.io/guides/molab/",
        "https://molab.marimo.io/pages/legal/terms",
        "https://marimo.io/pages/legal/subprocessors",
        "https://marimo.io/pages/legal/privacy",
        "https://github.com/marimo-team/marimo",
    ],
)

patch(
    "rca-runcell",
    data_handling_note="Paid plans enable Privacy Mode and state no training, but no current public DPA or institutional processor terms were verified. Free/Hobby lacks Privacy Mode. Code snippets/prompts still traverse cloud model routes.",
    tier_gate="paid Privacy Mode; personal data blocked pending a signed DPA",
    suitability={"personal": "no"},
    suitability_notes={
        "personal": "No current public DPA was verified. Treat personal-data use as blocked unless the institution obtains and approves a signed processor agreement.",
        "special": "Cloud service without a controlled-infrastructure route; not suitable.",
    },
    pricing="Hobby: 20 credits; Pro $20/500 credits; Pro+ $60/2,000; Ultra $200/10,000; Teams from $40/seat. Privacy Mode is paid-only.",
    sources=[
        "https://www.runcell.dev/pricing",
        "https://www.runcell.dev/privacy",
        "https://www.runcell.dev/terms",
        "https://www.runcell.dev/docs/credits-consumption-by-feature",
    ],
    notes="Cloud-connected notebook agent. Paid Privacy Mode supplies a no-training statement but not the missing public DPA; no public Enterprise plan was confirmed.",
)

patch(
    "rca-jetbrains-datalore",
    model_backend="JetBrains AI in Cloud; On-Premises can use OpenAI, Azure OpenAI, or an OpenAI-compatible self-hosted model",
    data_handling="local",
    runs_locally=True,
    tier_gate="Datalore On-Premises + self-hosted LLM",
    suitability={"special": "cfg"},
    suitability_notes={
        "personal": "Prefer On-Premises with a self-hosted model, or use Cloud only under an accepted DPA and collection configuration.",
        "special": "Requires Datalore On-Premises/air-gapped deployment plus a self-hosted LLM on controlled infrastructure. Cloud remains unsuitable.",
    },
    pricing="Cloud Free and paid plans are listed publicly; On-Premises pricing is custom and must be obtained from JetBrains.",
    compliance=["Deployment- and contract-dependent; verify exact Datalore product scope"],
    sources=[
        "https://www.jetbrains.com/datalore/buy/",
        "https://www.jetbrains.com/help/datalore/configure-ai-assistance.html",
        "https://www.jetbrains.com/help/datalore/datalore-on-premises.html",
        "https://www.jetbrains.com/help/datalore/frequently-asked-questions.html",
        "https://www.jetbrains.com/help/ai-assistant/how-we-handle-your-code-and-data.html",
    ],
    notes="Server-based notebook platform with Cloud and On-Premises/air-gapped routes. Controlled-infrastructure suitability requires On-Premises plus a self-hosted model; remove fixed on-prem pricing and overbroad access claims.",
)

patch(
    "rca-chatgpt-advanced-data-analysis",
    name="ChatGPT Data Analysis",
    aliases=["ChatGPT Advanced Data Analysis"],
    current_name="ChatGPT Data Analysis",
    model_backend="GPT-5.4 in current ChatGPT availability; model assignment can change by plan and rollout",
    data_handling="no-train",
    data_handling_note="ChatGPT Business, Enterprise, and Edu do not train on customer data by default and provide organizational retention controls; public ZDR documentation primarily concerns eligible API configurations, not a general ChatGPT guarantee. Uploaded/generated files may persist in ChatGPT Library depending on plan and rollout.",
    tier_gate="Business/Enterprise/Edu with DPA and accepted retention controls",
    pricing="Use current official ChatGPT plan pricing; Enterprise/Edu are contractual. Unsupported price ranges and minimum-seat estimates are omitted.",
    academic="ChatGPT Edu is available through institutional agreements; no general individual academic discount is asserted.",
    compliance=["OpenAI business controls; verify exact ChatGPT plan, contract, residency, and Trust Portal scope"],
    links={
        "docs": "https://help.openai.com/en/articles/8437071-advanced-data-analysis-chatgpt",
        "pricing": "https://openai.com/chatgpt/pricing",
        "privacy": "https://openai.com/business-data/",
    },
    sources=[
        "https://help.openai.com/en/articles/8437071-advanced-data-analysis-chatgpt",
        "https://openai.com/business-data/",
        "https://help.openai.com/en/articles/9903489-eu-data-residency",
        "https://openai.com/chatgpt/pricing",
        "https://help.openai.com/en/articles/20001052-library",
    ],
    notes="Current product name is ChatGPT Data Analysis. It is cloud-only; organizational no-training and retention controls do not make it acceptable for special-category data under this index's stricter controlled-infrastructure rule.",
)

patch(
    "rca-qodo",
    notes="Qodo now focuses on AI code review and governance; code generation/autocomplete/chat generation were deprecated. The record is removed below because code-review/PR bots are explicitly out of scope.",
    sources=[
        "https://www.qodo.ai/",
        "https://www.qodo.ai/pricing/",
        "https://docs.qodo.ai/code-review",
        "https://www.qodo.ai/formerly-qodo-merge/",
        "https://www.qodo.ai/blog/an-update-on-code-generation-at-qodo/",
    ],
)

patch(
    "rca-ollama",
    model_backend="Open-weight models run locally or on optional Ollama Cloud; model availability is dynamic",
    use_cases=[
        "local/air-gapped model infrastructure for coding agents",
        "private model serving for research workflows",
        "backend for Claude Code, Codex, Copilot CLI, OpenCode, Droid, and other compatible clients",
        "local model evaluation and agent pipelines",
    ],
    compliance=["Local mode avoids a vendor processor; no exhaustive public cloud certification claim is made"],
    sources=[
        "https://ollama.com/privacy",
        "https://ollama.com/pricing",
        "https://github.com/ollama/ollama",
        "https://ollama.com/blog/launch",
        "https://github.com/ollama/ollama/releases",
    ],
    notes="Local model infrastructure rather than a standalone coding agent. Stable v0.31.2 was current at verification; do not preserve a fixed model inventory or misspelled integration names across future updates.",
)


mini_swe_agent = {
    "id": "rca-mini-swe-agent",
    "date_added": TODAY,
    "date_modified": TODAY,
    "name": "mini-SWE-agent",
    "vendor": "SWE-agent academic open-source project",
    "type": "cli",
    "openness": "open-source",
    "deployment": "local-capable",
    "model_backend": "Any supported model through LiteLLM, including local Ollama models",
    "data_handling": "local",
    "data_handling_note": "The tool can run with a fully local model and local/Docker/Singularity/Apptainer execution so code and prompts remain on controlled infrastructure. Cloud model providers create separate processing boundaries. The default local environment executes commands directly on the host and should not be used for untrusted tasks without isolation.",
    "capability": "frontier",
    "backend_dependent": True,
    "suitability": {"nonsensitive": "ok", "personal": "cfg", "special": "cfg"},
    "suitability_notes": {
        "personal": "Use a fully local model and isolated execution, or independently approve the selected cloud provider under a DPA.",
        "special": "Requires a fully local model plus controlled Docker/Singularity/Apptainer execution. Cloud models and unisolated host execution are not acceptable.",
    },
    "compliance": ["self-hosted"],
    "pricing": "Free and open source (MIT); users pay only any selected cloud-model provider costs",
    "academic": "Free academic open-source project",
    "use_cases": [
        "autonomous issue resolution",
        "software-engineering agent research",
        "SWE-bench-style evaluation",
        "trajectory generation in isolated environments",
    ],
    "runs_locally": True,
    "links": {
        "docs": "https://mini-swe-agent.com/latest/quickstart/",
        "pricing": "https://github.com/SWE-agent/mini-swe-agent",
        "privacy": "https://mini-swe-agent.com/latest/models/local_models/",
    },
    "sources": [
        "https://mini-swe-agent.com/latest/quickstart/",
        "https://mini-swe-agent.com/latest/models/local_models/",
        "https://mini-swe-agent.com/latest/advanced/environments/",
        "https://github.com/SWE-agent/mini-swe-agent/releases",
    ],
    "status": "active",
    "current_name": "mini-SWE-agent",
    "confidence": "high",
    "verified": TODAY,
    "established": False,
    "tier_gate": "fully local model + isolated execution for regulated data",
    "notes": "Actively maintained successor to SWE-agent; stable v2.3.0 was current at verification. The default host execution is not isolated, so sensitive/untrusted work should use a controlled container or HPC isolation backend.",
}


remove_ids = {"rca-continue-dev", "rca-plandex", "rca-qodo"}
result = []
for record in records:
    identifier = record["id"]
    if identifier in remove_ids:
        continue
    if identifier == "rca-swe-agent":
        result.append(mini_swe_agent)
        continue
    record["verified"] = TODAY
    record["date_modified"] = TODAY
    result.append(record)

ids = [record["id"] for record in result]
if len(ids) != len(set(ids)):
    raise SystemExit("duplicate record IDs after live-audit migration")
if any(identifier in ids for identifier in remove_ids | {"rca-swe-agent"}):
    raise SystemExit("retired record survived live-audit migration")
if "rca-mini-swe-agent" not in ids:
    raise SystemExit("mini-SWE-agent replacement missing")

DATA.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
print(f"updated {DATA}: {len(records)} -> {len(result)} records")

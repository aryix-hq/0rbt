# FEAT-001: Autonomous Engineering Blog Intelligence Pipeline

> **Lifecycle Stage**: Stage 2 (Product Requirements & RICE Prioritization)  
> **Status**: Approved  
> **Author**: Product Manager (`@product-manager`)  
> **Target Branch**: `feat/eng-blog-intelligence-pipeline`  
> **Source Research Note**: [`wiki/research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md)  
> **Phased Implementation Plan**: [`wiki/plans/PLAN-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../plans/PLAN-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md)  

---

## 1. Executive Summary & Problem Statement

### User Problem
Engineering insights published by tier-1 tech giants (Google, Netflix, Stripe, Uber, Meta, GitHub, Datadog, etc.) are a goldmine for architecture decision-making, client advisory, and thought leadership. However, engineers and tech founders:
1. Cannot realistically monitor 60+ individual blogs daily.
2. Suffer from marketing noise and truncated RSS feeds.
3. Lack an automated bridge to translate massive multi-region patterns into lean, cost-effective architectures for startups and small clients.
4. Miss out on converting continuous technical discoveries into living rules and invariants for their local AI agent codebases.

### Proposed Solution
An end-to-end autonomous pipeline orchestrated via **n8n** that monitors 60+ engineering blogs, extracts and sanitizes full articles, runs multi-dimensional LLM analysis, and delivers:
- **LinkedIn Thought Leadership**: 3 hook variants, slide-by-slide carousel outlines, and engaging posts for engineering leaders.
- **Living Architecture Knowledge Base**: Structured records of distributed systems invariants, outage causes, and resilience patterns.
- **Small-Scale Client Playbook**: Pragmatic, lean startup translations of Big Tech architectures (Postgres/Redis equivalents).
- **`ai-agents` Evolution Proposals**: Direct pull-request-ready rule and invariant suggestions for repository governance.

---

## 2. RICE Prioritization & Scoring

$$\text{RICE Score} = \frac{\text{Reach} \times \text{Impact} \times \text{Confidence}}{\text{Effort}}$$

| Factor | Value | Rationale |
| :--- | :---: | :--- |
| **Reach (R)** | `30` | Average high-signal technical articles ingested per week across 60+ tier-1 engineering blogs |
| **Impact (I)** | `3.0` | Massive — establishes LinkedIn thought leadership, creates client consulting blueprints, and continuously hardens the `ai-agents` codebase |
| **Confidence (C)**| `95%` | High empirical confidence — verified feed endpoints, deterministic hash deduplication, and structured JSON LLM output schemas |
| **Effort (E)** | `1.0` | 1 person-week to scaffold n8n workflow JSON, feed catalog, and automated verification tests |
| **TOTAL SCORE** | **`85.5`** | **(30 × 3.0 × 0.95) / 1.0 = 85.5** |

---

## 3. User Acceptance Criteria (UAC)

- [ ] **Scenario 1 (Scheduled Feed Ingestion & Deduplication)**:
  - *Given* an n8n schedule trigger and a registry of 60+ blog RSS/Atom feeds,
  - *When* the workflow executes,
  - *Then* it queries feeds with `ETag`/`If-Modified-Since`, computes `SHA256(canonical_url)`, verifies against the deduplication store, and processes only net-new articles.

- [ ] **Scenario 2 (Full-Text Extraction & Sanitization)**:
  - *Given* a new article entry whose RSS feed provides only a partial summary,
  - *When* the extractor node runs,
  - *Then* it fetches the origin HTML, applies clean article extraction (stripping ads, nav, cookie banners), preserves code blocks and headings, and enforces a minimum word-count threshold (>300 words).

- [ ] **Scenario 3 (4-Dimensional Structured AI Synthesis)**:
  - *Given* sanitized article markdown,
  - *When* the LLM synthesis chain executes,
  - *Then* it returns a strictly validated JSON payload containing:
    1. LinkedIn post drafts (3 distinct hook styles: counter-intuitive, narrative, tactical; carousel outline; hashtags).
    2. Enterprise architecture learnings (core pattern, problem statement, invariants, failure modes).
    3. Small-scale client translation (lean architecture alternative, estimated cost savings, 3-step implementation checklist).
    4. `ai-agents` evolution proposal (target skill or invariant rule, concrete rule definition).

- [ ] **Scenario 4 (Multi-Destination Output Dispatch)**:
  - *Given* the synthesized JSON payload,
  - *When* the distribution nodes run,
  - *Then* it dispatches an approval message to Telegram/Slack, writes a markdown record to the local wiki/learnings directory, and appends proposed improvements to `.agents/memory/incoming_engineering_insights.json`.

---

## 4. Technical Scope & System Impact

- **Workflow Orchestration**: n8n workflow engine (modular sub-workflows for polling, extraction, LLM synthesis, and dispatch).
- **Feed Registry**: Curated configuration `config/engineering_blogs_registry.json` containing 60+ validated RSS/Atom endpoints.
- **Deduplication Store**: Lightweight persistent table (`processed_articles`) tracking `article_hash`, `canonical_url`, `company`, `title`, and `first_seen_at`.
- **LLM Integration**: Compatible with local Ollama (`qwen2.5-coder:14b`) and cloud models via standard n8n LLM Chain nodes.
- **Repository Impact**: New files in `n8n/`, `config/`, `bin/`, and living document updates in `wiki/`. Zero changes to production runtime boundaries.

---

## 5. Definition of Done (DoD)

- [x] Stage 1 Research Note linked (`wiki/research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`)
- [x] RICE score computed (85.5) and prioritized
- [x] Stage 2 Feature Spec approved
- [ ] Stage 3 Phased Implementation Plan (`wiki/plans/PLAN-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`) co-authored with Planning Trio
- [ ] ADR-001 authored in `wiki/adr/` defining feed normalization and multi-dimensional LLM output contracts
- [ ] Production-grade n8n workflow definition JSON committed to `n8n/engineering_blogs_pipeline.json`
- [ ] Curated blog registry committed to `config/engineering_blogs_registry.json`
- [ ] Automated zero-mock test harness (`bin/test-blog-pipeline.py`) verifying feed schemas, canonical hashing, and JSON output contracts
- [ ] 6 Core Living Context Documents (`prd.md`, `architecture.md`, `rules.md`, `design.md`, `tasks.md`, `memory.md`) fully synchronized
- [ ] PR reviewed & signed off by Engineering Manager
- [ ] `CHANGELOG.md` updated per Keep a Changelog standards

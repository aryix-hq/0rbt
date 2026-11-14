# PLAN-001: Autonomous Engineering Blog Intelligence Pipeline

> **Lifecycle Stage**: Stage 3 (Phased Project Planning)  
> **Status**: IN_PROGRESS  
> **Target Branch**: `feat/eng-blog-intelligence-pipeline`  
> **Created**: 2026-11-14  
> **Upstream Feature Spec**: [`wiki/features/FEAT-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../features/FEAT-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md) (RICE Score: 85.5)  
> **Source Research Note**: [`wiki/research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md)  
> **Planning Trio Sign-off**:
> - [x] Product Manager (`@product-manager`)
> - [x] System Architect (`@architect`)
> - [x] Technical Project Manager (`@project-manager`)

---

## 1. Executive Summary & Objective

Build an autonomous, production-ready **n8n Workflow Intelligence Pipeline** that:
1. Ingests articles from 60+ premier engineering organizations.
2. Deduplicates incoming posts via canonical URL hashing (`SHA256`).
3. Extracts full clean Markdown while discarding noise and marketing copy.
4. Executes a 4-Dimensional AI Synthesis Engine to generate:
   - High-engagement LinkedIn thought leadership drafts (3 hooks + carousel outlines).
   - Architectural knowledge base records (invariants, post-mortem root causes).
   - Lean startup / client consulting blueprints (downscaled implementations).
   - Direct codebase and invariant evolution proposals for `ai-agents`.
5. Dispatches outputs to Telegram/Slack approval queues and commits architectural notes to the repository wiki.

---

## 2. Living Phase & Milestone Tracker

| Phase | Milestone Description | Lead Agent(s) | Status | Evidence / Artifact Link |
| :---: | :--- | :--- | :---: | :---: |
| **Phase 1** | Contract Definition, ADR & Blog Registry | `@architect`, `@database-architect` | `[COMPLETED]` | [`wiki/adr/ADR-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../adr/ADR-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md), [`config/engineering_blogs_registry.json`](../../config/engineering_blogs_registry.json) |
| **Phase 2** | n8n Workflow Topology & Prompt Engineering | `@fullstack-developer`, `@n8n-automation-engineer` | `[IN PROGRESS]` | [`n8n/engineering_blogs_pipeline.json`](../../n8n/engineering_blogs_pipeline.json) |
| **Phase 3** | Automated Pipeline Verification Harness | `@qa`, `@devops-sre` | `[PENDING]` | [`bin/test-blog-pipeline.py`](../../bin/test-blog-pipeline.py) |
| **Phase 4** | Living Context Synchronization & EM Gate | `@documentation-manager`, `@engineering-manager` | `[PENDING]` | `prd.md`, `architecture.md`, `tasks.md`, `memory.md`, `CHANGELOG.md` |

---

## 3. Associated Living Artifacts

- **Stage 1 Research**: [`wiki/research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../research/RES-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md)
- **Stage 2 Feature Spec**: [`wiki/features/FEAT-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../features/FEAT-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md)
- **Architecture Decision Record**: [`wiki/adr/ADR-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`](../adr/ADR-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md)
- **System Architecture**: [`wiki/ARCHITECTURE.md`](../ARCHITECTURE.md)
- **Active Task Board**: [`wiki/TASK_BOARD.md`](../TASK_BOARD.md)
- **Knowledge Memory**: [`wiki/memory.md`](../memory.md)

---

## 4. Phase Execution Details & Deliverables

### Phase 1: Contract Definition, ADR & Blog Registry
- Author `wiki/adr/ADR-001-AUTONOMOUS-ENGINEERING-BLOG-INTELLIGENCE-PIPELINE.md`.
- Compile and deduplicate 60+ verified RSS/Atom feed endpoints into `config/engineering_blogs_registry.json`.
- Define the JSON output contract schema for the 4-dimensional synthesis engine.

### Phase 2: n8n Workflow Architecture & Synthesis Nodes
- Build the complete, valid n8n workflow definition in `n8n/engineering_blogs_pipeline.json`.
- Include:
  - Schedule Trigger node (cron configured).
  - Feed Ingestion & HTTP Request nodes with `ETag` / `If-Modified-Since`.
  - Canonical URL hash deduplication Code node.
  - Readability / Full-text HTML sanitization Code node.
  - Structured LLM Chain node with multi-output prompt.
  - Multi-destination dispatch branches (Telegram/Slack notification, Markdown generation, insight staging).
  - Global Error Trigger node for resilient failure telemetry.

### Phase 3: Automated Verification & Test Harness
- Implement `bin/test-blog-pipeline.py` with zero-mock verification:
  - Validates all feed URLs in `engineering_blogs_registry.json`.
  - Tests canonical URL normalization and SHA-256 deduplication logic against corner cases (tracking params, anchors, uppercase protocols).
  - Validates `n8n/engineering_blogs_pipeline.json` against n8n workflow schema rules.
  - Runs synthetic end-to-end synthesis validation against realistic domain articles (Netflix tracing, Stripe idempotency, Uber dynamic pricing).

### Phase 4: Living Context Synchronization & Review
- Synchronize all 6 living context files: `prd.md`, `architecture.md`, `rules.md`, `design.md`, `tasks.md`, `memory.md`.
- Update `CHANGELOG.md` following Keep a Changelog standards.
- Run static review checks and secure Engineering Manager sign-off.

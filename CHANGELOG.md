# Changelog

All notable changes to the `ai-agents` Antigravity plugin and project template will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- **10-Year Historical Engineering Corpus & Diagram Archive (FEAT-002, PLAN-003)**:
  - **Massive 10-Year Historical Crawl**: Enhanced candidate harvesting in `bin/bulk-harvest-2000.py` to traverse child sitemaps and archives spanning 2012–2026 across Cloudflare, Datadog, GitHub, Meta, Shopify, AWS, Dropbox, GitLab, Docker, Red Hat, Netflix, and Google.
  - **4,169 Authentic Engineering Articles**: Extracted, cleaned, and categorized 4,169 substantive technical posts in `data/engineering_intelligence.db` and `dataset/engineering_corpus_2000.jsonl` with strict `INV-06` compliance.
  - **11,936 System Architecture Diagrams**: Ingested and stored 11,936 high-resolution system topology diagrams, state charts, and network flows in `data/images/`.
  - **4,719 Fine-Tuning Pairs**: Merged 4,169 empirical engineering post-mortems with 550 Anti-Vibe Invariant pairs into a unified `dataset/instruction_tuning_v1.jsonl`.
  - **Model Rebuild**: Updated `Modelfile` to eliminate placeholder entities and rebuilt `aryix/0rbt-architect:latest` (ID `6d2aa0339b65`, 9.0 GB) on local Ollama at $0 cloud tokens.
- Implemented **AI-Agents Skills & Anti-Vibe Invariants Integration into aryix/0rbt-architect (FEAT-002, PLAN-003, ADR-016)**:
  - **Deterministic Invariants Synthesizer**: Created `bin/synthesize-skills-dataset.py` synthesizing 550 high-signal instruction-tuning pairs derived from the 20 Anti-Vibe Invariants (`INV-SEC-01` to `INV-SEC-10`), SRE resilience doctrine (`INV-RES-01` to `INV-RES-05`), and multi-domain backend invariants.
  - **Dataset Expansion & Unification**: Merged 550 invariant instruction pairs with the 2,065 empirical engineering post-mortem corpus, expanding `dataset/instruction_tuning_v1.jsonl` to **2,615 total ChatML pairs** alongside standalone `dataset/invariants_instruction_dataset.jsonl`.
  - **Modelfile System Prompt Upgrade**: Refactored `Modelfile` with the compact Invariant Enforcement & Outage Defense rules matrix (<1,024 tokens) and standardized 4-part architectural review output protocol (Verdict, Violated Invariant, Big Tech Precedent, Hardened Code Fix). Rebuilt `aryix/0rbt-architect:latest` in local Ollama at $0 cloud tokens.
  - **Automated Invariant Benchmark Suite**: Built `bin/eval-architect-invariants.py` evaluating 10 deterministic architectural dilemmas, achieving a verified **90.0% live pass rate** on `aryix/0rbt-architect` (catching missing idempotency keys, unkeyed retries, liveness probe coupling, and BOLA tenant leaks).
- Implemented **0rbt Open-Source Launch, Public Dataset & `aryix/0rbt-architect` Model (PLAN-002, PRD)**:
  - **Open-Source Repository Infrastructure**: Created Apache 2.0 `LICENSE`, contributor guides (`CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`), issue templates (`.github/ISSUE_TEMPLATE/`), and comprehensive `README.md` documenting architecture, quickstarts, and CLI operations.
  - **Phase A Local Ollama Model (`aryix/0rbt-architect`)**: Created `Modelfile` embedding Staff Systems Architect reasoning, low temperature (0.2), and anti-vibe engineering invariants (`INV-RES-01..04`, `INV-SEC-09`). Automated build and verification via `bin/build-ollama-model.sh` running locally on Apple Silicon Metal GPU at $0 cloud tokens.
  - **Phase B Fine-Tuning & Quantization Pipeline**: Implemented `training/train_lora.py` (4-bit QLoRA SFTTrainer with ChatML prompts) and `training/export_gguf.py` (LoRA adapter merge & GGUF quantization) with zero-token mock testing (`--mock-test`).
  - **Public Dataset Curation & Exporter**: Built `bin/export-hf-dataset.py` exporting SQLite intelligence records to Hugging Face standard datasets (`dataset/engineering_postmortems_v1.jsonl` and `dataset/instruction_tuning_v1.jsonl`) with Hugging Face dataset card (`dataset/README.md`).
  - **Historical Archive Crawler**: Built `bin/crawl-historical-archives.py` with multi-threaded sitemap extraction and Medium publication parsing.
  - **Peanuts & Hay Leaf Contract**: Added `training/README.md` enforcing `INV-DOC-02` contracts.
- Implemented **Autonomous Engineering Blog Intelligence Pipeline (FEAT-001, PLAN-001, ADR-001)**:
  - **Curated 60+ Source Registry**: Consolidated verified RSS, Atom, and Medium feed endpoints across 63 tier-1 technology organizations (Google, Netflix, Stripe, Uber, Meta, GitHub, Datadog, Cloudflare, etc.) into `config/engineering_blogs_registry.json`.
  - **Deterministic Canonical URL Deduplication**: Enforced `INV-BLOG-01` via SHA-256 hashing over normalized URLs (stripping query parameters, tracking tags, and protocol fragments) with PostgreSQL/Datatable persistence.
  - **Substance & Readability Gate**: Enforced `INV-BLOG-02` with 200-word thresholds and noise filtering to discard event announcements and marketing copy.
  - **Structured 4-Dimensional AI Synthesis**: Enforced `INV-BLOG-03` generating LinkedIn thought leadership drafts (3 hooks, 4-slide carousel outline, post body), architectural knowledge base records, lean client advisory blueprints ("Big Tech to Lean Startup"), and continuous `ai-agents` codebase rule proposals.
  - **Multi-Channel Dispatch & Living Wiki Integration**: Structured dispatch to Telegram review queues, living Markdown scribe (`wiki/learnings/`), and `.agents/` improvement staging.
  - **Automated Zero-Mock Verification Harness**: Added `bin/test-blog-pipeline.py` testing registry integrity, deduplication hashing, substance gating, n8n workflow graph connectivity, and 4D synthesis JSON schema conformance with 100% pass rate.
- Implemented **Dual-Scale Architecture, Polyglot Persistence & End-to-End Observability Standards** (`wiki/adr/ADR-003.md`, `wiki/DEPLOYMENT.md`, `agents/database-architect.md`, `agents/devops-sre.md`):
  - **Database Architect SQL, NoSQL & Streaming Mastery**: Expanded `agents/database-architect.md` and `skills/database-architect/SKILL.md` to cover relational SQL (PostgreSQL 16 RLS, non-blocking migrations, PgBouncer), NoSQL (Redis 7 in-memory caching, jittered TTL, distributed locks, MongoDB document modeling), and Event Streaming / Message Queues (Apache Kafka partitioned topics, RabbitMQ DLX, lightweight Redis Streams, Transactional Outbox pattern, and idempotent consumer deduplication).
  - **DevOps / SRE Observability & Distributed Traceability**: Expanded `agents/devops-sre.md` and `skills/devops-sre/SKILL.md` to implement full-spectrum observability (structured JSON logging, Prometheus RED/USE metrics, Grafana dashboards, multi-window burn rate alerts) and end-to-end distributed tracing (OpenTelemetry W3C `traceparent` propagation across HTTP headers and message queue payloads, correlation ID stitching, and commit-to-artifact SBOM provenance).
  - **Dual-Scale Sizing & Deployment Model**: Codified applications to run identically with zero code changes across two operational profiles: Small-Scale (<2GB RAM on developer laptop / $5-10/mo VPS via Docker Compose & Redis Streams) and Enterprise-Scale (multi-AZ Kubernetes, Kafka cluster, PostgreSQL HA, Redis cluster, and OpenTelemetry collector daemonsets).
- Implemented **Stateless Microservices & Anti-"Vibe Coding" Engineering Standard** (`rules/stateless_microservices_engineering.md`, `rules/AGENTS.md` Invariant 8, and `wiki/adr/ADR-002.md`), mandating:
  - **100% Stateless Compute Tiers**: Forbids in-memory sessions, sticky sessions, or local disk dependencies; externalizes all session and relational state to PostgreSQL 16 and Redis 7 clusters.
  - **Layered Decoupling & Explicit Contracts**: Enforces strict Controller $\to$ Service $\to$ Repository separation, prohibiting monolithic code dumps, with versioned API contracts (`/api/v1/`) and OpenAPI schemas.
  - **Defensive Engineering & Non-Happy Paths**: Mandates timeout budgets, exponential backoffs, transactional rollbacks, and client-supplied `Idempotency-Key` headers on all mutating endpoints (`POST`, `PUT`, `PATCH`).
  - **Strict Boundary Validation**: Requires 100% ingress payload validation via runtime schemas (Zod/Pydantic), defending against malformed JSON, oversized payloads, and null injections.
  - **BOLA / IDOR Defense**: Enforces mandatory tenant-scoped authorization on every database query (`WHERE id = :id AND tenant_id = :tenant_id`).
  - **Performance & Resource Invariants**: Prohibits $O(N^2)+$ nested loops, mandates database indexes on foreign keys/filters, eliminates N+1 queries, and enforces cursor/limit pagination on list endpoints.
  - **Deterministic Debugging & Code Ownership**: Eradicates "prompt roulette" symptom patching in favor of stack trace inspection, reproducer tests, and line-by-line understanding.
  - **Structured Observability**: Mandates structured JSON logging with OpenTelemetry `traceparent` propagation and zero-mock integration testing against live containers.
- Enhanced `agents/fullstack-developer.md` and `agents/architect.md` with explicit stateless microservices and defensive engineering operating mandates.
- Expanded `skills/fullstack-developer/SKILL.md` and `skills/production-engineering-111/SKILL.md` with concrete implementation patterns for idempotency headers, Zod schemas, tenant scoping, and Big-O hash lookups.
- Recorded `wiki/adr/ADR-002.md` and refreshed `wiki/ARCHITECTURE.md` with the Stateless Microservices Topology.
- Implemented **360° Software Engineering Security Remediations (SEC-01 to SEC-04)**:
  - **SEC-01 (Deep Secret & Confidentiality Auditor)**: Built `bin/audit-secrets.sh` (`ai-agents audit`) performing static audits across staged diffs and historical Git commit trees, detecting high-entropy tokens (AWS, GitHub, Stripe, Slack), private cryptographic keys, and historical confidential artifacts (`DEF-*`, `INC-*`, `VULN-*`, `RES-*`).
  - **SEC-02 (Pre-Commit & Pre-Push Security Guard)**: Built and installed mandatory hooks (`hooks/pre-commit`, `hooks/pre-push`, `.git/hooks/pre-commit`, `.git/hooks/pre-push`): strictly prevents direct commits or direct git pushes to `main`/`master` (Rule 1 PR mandate), blocks staging of confidential files (`wiki/defects/DEF-*.md`, `INC-*.md`, `VULN-*.md`, `RES-*.md`, `.env*`, `token_ledger.json`), and rejects commits containing private cryptographic keys or live API credentials. Updated `bootstrap.sh`, `init-project`, and `propagate` to install both hooks on all developer environments and downstream repositories.
  - **SEC-03 (DevSecOps Preview Deploy Gate)**: Upgraded Step 2 of `bin/deploy-preview.sh` to run `bin/audit-secrets.sh` and perform dependency vulnerability checks (`npm audit` / `pip-audit`), halting ephemeral builds on detected security or credential violations.
  - **SEC-04 (GitHub MCP CLI & Remote Branch Protection Engine)**: Implemented `bin/github-mcp` wrapping `ghcr.io/github/github-mcp-server` over Docker JSON-RPC stdio with macOS Keychain credentials for zero-overhead PR creation, branch listing, and review comment workflows. Added `bin/github-protect-main.sh` (`ai-agents protect-main`) applying automated branch protection rulesets on `origin/main` (required PR approvals, stale review dismissal, admin enforcement, force-push blocking) with auto-detection of GitHub Free plan visibility constraints.
- Implemented **Public Repository Confidentiality & Data Classification Standard** across `.gitignore`, `rules/quality_documentation.md`, and `wiki/WIKI_GUIDE.md`: excludes raw defect records (`wiki/defects/DEF-*.md`), zero-day incidents (`wiki/incidents/INC-*.md`), vulnerabilities (`wiki/vulnerabilities/VULN-*.md`), commercial RICE research notes (`wiki/research/RES-*.md`), and local runtime memory (`.agents/memory/sessions/`, `token_ledger.json`, `active_feature.md`) from Git to prevent zero-day exploit disclosure, attack surface enumeration, and IP leakage while keeping high-level architecture and guides open.
- Migrated `n8n-mcp` credentials in `mcp_config.json` to environment variable `${N8N_API_KEY}` and exported it in user shell environment (`~/.zshrc`), enforcing zero plaintext secrets in Git repository.
- Integrated **GitHub MCP on Docker** (`ghcr.io/github/github-mcp-server`) in `~/.gemini/config/mcp_config.json` and `mcp_config.json`, enabling agents to autonomously create Pull Requests (`create_pull_request`), leave review comments (`add_comment_to_pending_review`), merge approved PRs (`merge_pull_request`), synchronize issues, and search code across repositories using dynamic Keychain authentication.
- Added **Enterprise Bootstrap Engine** (`bootstrap.sh`, `setup.sh`, and `ai-agents bootstrap`), an autonomous 8-step pre-flight, configuration, and self-test engine for newly cloned repositories and developer machines: validates dependencies (Git, Python 3.9+, Curl), sets up and launches local Ollama (`qwen2.5-coder:14b`), installs symlinks in `~/.local/bin/`, updates shell `$PATH`, registers global Antigravity plugin, installs Git post-merge reset hooks, scaffolds memory graphs and token ledgers, and validates local zero-token inference.
- Added **Token & Cost Savings Observer** (`ai-agents tokens` and `bin/record-tokens.py`), tracking exact local prompt and completion tokens processed at $0 vs paid cloud tokens, breakdown by tool (`local-coder`, `local-git`, `local-cmd`), and dollar cost savings calculation.
- Integrated Token Savings Snapshot into `ai-agents status` for real-time visibility.
- Codified **Sandbox Loopback & Git Bypass Mandate** in `rules/autonomous_development.md` and `rules/AGENTS.md`: mandates running local workers and git write commands with `BypassSandbox: true` to prevent macOS sandbox loopback blocking (`[Errno 1] Operation not permitted` / code 128) from triggering unintended fallback to cloud tokens.
- Added **Automated Session Context Reset Engine** (`ai-agents session reset [--auto]`):
  - Automatically auto-detects active tickets from Git branches (`feat/FEAT-XXX`), `memory_graph.json`, or active markdown specs with zero manual arguments required.
  - Automatically archives completed session state into `.agents/memory/sessions/`.
  - Atomically updates `memory_graph.json` (`sessionHistory`, `lastSessionReset`, and `activeTicket: null`).
  - Resets `.agents/memory/active_feature.md` to a clean idle slate for the subsequent ticket.
  - Installed Git `post-merge` hook (`.git/hooks/post-merge`) to auto-reset sessions whenever feature branches merge into `main`.
  - Enforced autonomous session resets across `rules/memory_session_rules.md`, `rules/autonomous_development.md`, and `rules/AGENTS.md`: agents autonomously execute the reset upon DoD completion or PR approval.
- Codified the **4-Stage Product & Engineering Lifecycle** across rules, agents, skills, and templates:
  - **Stage 1 (Research & Discovery)**: `@research` and `@client-advocate` uncover pain points, domain constraints, and technical spikes in living discovery notes (`wiki/research/RES-XXX.md` using `wiki/templates/RESEARCH_NOTE.md`).
  - **Stage 2 (Product Scoping & RICE Prioritization)**: `@product-manager` ingests research and defines feature specifications (`wiki/features/FEAT-XXX.md`) with explicit RICE scores ($(R \times I \times C) / E$) and testable User Acceptance Criteria (UAC).
  - **Stage 3 (Phased Project Planning)**: The Planning Trio (`@product-manager`, `@architect`, `@project-manager`) deconstructs prioritized features into phased Implementation Plans (`wiki/plans/PLAN-XXX.md`), synchronizing living Architecture (`wiki/ARCHITECTURE.md`) and Database Schema (`wiki/DATABASE_SCHEMA.md`).
  - **Stage 4 (Phased Autonomous Execution & Verification)**: Development executes phase-by-phase with local Ollama ($0 tokens), zero-mock container testing, live defect tracking (`wiki/defects/DEF-XXX.md`), ephemeral preview builds (`bin/deploy-preview.sh`), Engineering Manager PR gate, and session context resets.
- Added `wiki/templates/RESEARCH_NOTE.md` and `wiki/research/` directory structure for Stage 1 discovery.
- Enhanced `wiki/templates/FEATURE_SPEC.md` and `wiki/templates/IMPLEMENTATION_PLAN.md` with explicit 4-stage lifecycle traceability and living milestone tracking.
- Updated `bin/ai-agents` (`init-project` and `propagate`) to automatically scaffold and synchronize `wiki/research/` and updated templates.
- Added **Local vs. Cloud Execution Mode Switch** (`ai-agents mode [local|cloud|status]` and `AI_AGENTS_MODE` environment variable), providing an instant toggle to turn off local Ollama workers and execute all tasks (code drafting, conventional commits, shell commands) directly through cloud Gemini models.
- Added **Local Git Operations & Shell Command Generation Engine** (`bin/local-git.sh`, `bin/local-cmd.sh`, and `ai-agents git`/`run` CLI commands), offloading conventional commit generation, PR drafting, branch naming, and natural language shell command pipelines to local Ollama (`qwen2.5-coder:14b`) at $0 cloud tokens.
- Mandated **Local Git and Shell Command Execution** across `rules/AGENTS.md`, `rules/git_workflow_pr.md`, `rules/autonomous_development.md`, and `rules/model_assignment.md`, ensuring all command synthesis and git workflows occur locally without consuming cloud context.
- Mandated the **Planning Trio** (`@product-manager`, `@architect`, `@project-manager`) to co-author living phased implementation plans (`wiki/plans/PLAN-XXX.md`) with living phase milestones (`[PENDING]`, `[IN PROGRESS]`, `[COMPLETED]`).
- Enforced **Living Document Synchronization**:
  - Features (`wiki/features/FEAT-XXX.md`) kept continuously updated based on initiative scope and delivery.
  - System Architecture (`wiki/ARCHITECTURE.md`) and Database Schema (`wiki/DATABASE_SCHEMA.md`) updated as living specs on every structural or entity change.
  - Test defect logging (`wiki/defects/DEF-XXX.md`) automated by `@qa` on test failures, tracking status through remediation.
- Enforced **Zero-Token Local Documentation**: Mandated that all wiki authoring, defect logs, implementation plans, and changelog updates route through local Ollama (`bin/local-coder.sh` / `qwen2.5-coder:14b`) at $0 cloud tokens.
- Added Chief Technology Officer (`cto`) agent persona (`agents/cto.md`), Technology Strategy & Build-vs-Buy skill (`skills/cto-technology-strategy/SKILL.md`), and CTO Architecture Governance rule (`rules/cto_governance.md`).
- Integrated CTO into Division 1 leadership and governance structure in `ORGANIZATION.md` and `README.md`, scaling team to 30 agents, 24 skills, and 8 rules.
- Published comprehensive **Hybrid Model Execution Guide** (`wiki/HYBRID_EXECUTION_GUIDE.md`) detailing local vs. cloud task allocation, business/privacy benefits, and hardware limitations.
- Added **Zero-Tagging Autonomous Execution** mandate across `rules/AGENTS.md`, `rules/autonomous_development.md`, and `rules/model_assignment.md`: upon user plan approval, code drafting automatically routes through local Ollama (`bin/local-coder.sh` / `qwen2.5-coder:14b`) without requiring manual user tags.
- Added **HashiCorp Vault Secrets Management** skill (`skills/vault-secrets-management/SKILL.md`) and governance rule (`rules/secrets_vault_management.md`), mandating KV v2 stores, dynamic database credentials, and zero plaintext in Git.
- Configured **n8n MCP** with `"WEBHOOK_SECURITY_MODE": "moderate"` in `~/.gemini/config/mcp_config.json` and repo manifest, eliminating the Docker localhost SSRF block.
- Added comprehensive Table of Contents (Index) and n8n Docker assistant integration runbooks to `HOW_TO_USE.md`.
- Implemented **REA (Reverse Engineer Anything)** MCP integration (`mcp_config.json` and `~/.gemini/config/mcp_config.json`) with dedicated skill (`skills/reverse-engineering/SKILL.md`) linking 207 analysis tools to `@devsecops`, `@architect`, and `@fullstack-developer`.
- Codified the 4 Core Principles of Autonomous Local AI Development into mandatory prompt rule `rules/autonomous_development.md` ("Loop Until Green", zero-token local offloading, deterministic memory, ephemeral preview).
- Enforced autonomous test-fix loops and error stack trace triage across `agents/fullstack-developer.md` and `agents/qa.md`.
- Documented comprehensive autonomous AI engineering best practices in `HOW_TO_USE.md`.
- Bumped plugin manifest `plugin.json` to v1.3.0.
- Documented the Pragmatic Multi-Agent Operating Model ("SWAT Team + 4-Tier Expert Roster", token conservation, anti-bureaucracy guidelines) in `HOW_TO_USE.md`.
- Added token optimization & anti-burn safety mechanism in `rules/model_assignment.md` (targeted diffs, log pruning, pro escalation bans).
- Mandated live documentation across `wiki/ARCHITECTURE.md`, `wiki/DATABASE_SCHEMA.md`, `wiki/DEPLOYMENT.md`, `wiki/FAQS.md`, and `wiki/USER_GUIDE.md` in `rules/quality_documentation.md`.
- Implemented historical incident (`wiki/incidents/`) and vulnerability (`wiki/vulnerabilities/`) ledgers with structured templates (`INCIDENT_RECORD.md`, `VULNERABILITY_RECORD.md`).
- Enhanced `bin/deploy-preview.sh` to differentiate production (`<project>-main-<port>`) and branch preview (`<project>-preview-<branch>-<port>`) container environments.
- Integrated CRM & Outbound Growth Specialist (`crm-specialist`) into Division 5 with dedicated agent persona (`agents/crm-specialist.md`), skill (`skills/crm-specialist/SKILL.md`), and pipeline rule (`rules/crm-specialist.md`). Organization expanded to 29 agents, 23 skills, 7 rules.
- Bumped plugin manifest `plugin.json` to v1.1.0.
- Migrated canonical plugin repository to native local APFS storage at `~/Code/ai-agents` with GitHub tracking (`https://github.com/aryix-hq/ai-agents.git`), completely eliminating macOS sandbox and Google Drive FileProvider permission errors.
- Expanded organization with `n8n-automation-engineer`, `ollama-orchestrator`, and `antigravity-bridge`.
- Added `production-engineering-111`, `n8n-automation`, and `model-router` skills.
- Created living organization chart and SLAs in `ORGANIZATION.md`.
- Created comprehensive guide in `HOW_TO_USE.md`.

### Changed
- Cleaned IDE, VS Code, and CLI configurations to eliminate blanket local model hijacking. Enforced true hybrid routing: Gemini Flash for top-level chat and planning, Gemini Pro for Architect/CISO gates, and Ollama for worker execution.
- Updated `.agents/plugins.json` and plugin CLI to reference the canonical local repository.

### Fixed
- Fixed symlink canonical resolution across CLI and local worker scripts (`bin/ai-agents`, `bin/local-coder.sh`, `bin/local-git.sh`, `bin/local-cmd.sh`) so invoking through `~/.local/bin/` accurately identifies repository paths and executes `record-tokens.py` without `[Errno 2] No such file or directory` errors.
- Handled macOS terminal sandbox loopback isolation (`127.0.0.1:11434`) by adding explicit diagnostic guidance and fallback candidate lookup paths for token metrics recording.

## [1.0.0] - 2026-10-17
### Added
- Core plugin manifest `plugin.json`.
- 25 specialized AI agents across Engineering, Product, Security, Compliance, Finance, Legal, and Executive domains.
- Full suite of skills adapted from `L34D5` and `b00k5` repositories.

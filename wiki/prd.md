# Product Requirements Document (PRD): Antigravity AI-Agents Enterprise Engine

- **Project**: `ai-agents`
- **Status**: Approved / Living Master
- **Target Release**: `v2.3.0`
- **Owner**: Product Management Trio (`@product-manager`, `@architect`, `@cto`, `@engineering-manager`)

---

## 1. Executive Summary & Problem Statement

Software teams leveraging LLM coding assistants face high cloud token expenditure, unpredictable "vibe coding" regressions, and context loss across chat sessions. `ai-agents` is an autonomous engineering organization framework providing:
1. **$0 Cloud Token Local Inference**: Routine coding, git operations, and code review execute locally via Ollama (`qwen2.5-coder:14b`).
2. **Deterministic Invariant Enforcement**: 34 automated static linters blocking BOLA/IDOR, SQL injection, Mass Assignment, N+1 query loops, and AI slop UI before PR merge.
3. **Mandatory Ephemeral Staging Lifecycle**: Strict zero-testing-on-production policy with signed staging attestation certificates.
4. **Universal IDE Distribution**: Automated transpilation to Claude Code, Cursor, Windsurf, Aider, and Gemini CLI.

---

## 2. Target Personas & Core Workflows

| Persona | Role | Key Goal | Invariant Guard |
| :--- | :--- | :--- | :--- |
| **Lead Architect** | System Topology & Scalability | Enforce stateless microservices and clean API contracts | `INV-DOM-04`, `INV-PERF-01` |
| **AppSec Engineer** | Offensive Audits & API Hardening | Prevent OWASP Top 10 leaks, BOLA/IDOR, and secret commits | `INV-SEC-01` to `INV-SEC-10` |
| **Engineering Manager** | Delivery Velocity & Gatekeeping | Ensure zero untested code merges to main | Rule 1 (PR Mandate), `INV-TEST-01` |
| **Frontend Architect** | Design System Governance | Prevent vibe-coded UI slop and magic inline CSS | `INV-UI-01`, `INV-UI-02`, `INV-UI-03` |

---

## 3. Core Capabilities & Invariants

- **Zero Random Coding**: All work strictly follows the 4-Stage Lifecycle (`Research -> Feature Spec -> Plan -> Execution`).
- **Universal Dummy Name Ban**: Absolute ban on fictional placeholders (`Acme`, `Dummy`, `John Doe`).
- **20-Point Anti-Vibe Shield**: Automated detection of the 20 failure points (Security, Backend/Scale, Code).
- **Line-by-Line E2E Coverage**: Every PR must include zero-mock automated test cases covering newly added logic.
- **6-Core AI Context Standard**: Every project must maintain `prd.md`, `architecture.md`, `rules.md`, `design.md`, `tasks.md`, and `memory.md`.
- **Matt Pocock Engineering Skills Suite (FEAT-042)**: Interactive architectural grilling (`grill-with-docs`), vertical tracer-bullet task decomposition (`to-tickets` / `tracer-slicer.py`), secret-scrubbed state compaction (`agent-handoff.py`), decoupled two-axis code review (`two-axis-reviewer.py`), and uncertainty navigation (`wayfinder`).
- **Google Elephant-Goldfish Model Suite (FEAT-043)**: Split cognitive labor eliminating confirmation bias via Dave Rensin's EGM model: stateless 5-pass spec review (`egm-goldfish.py`), leaf-level component contracts reducing monorepo context overhead by >85% (`INV-DOC-02` / `egm-peanuts.py`), and AST-driven spec-to-code drift detection between routes/schemas and architecture docs (`INV-DOC-03` / `egm-drift.py`).
- **Agentic SEO, LLMS.txt & Strict Schema.org Suite (FEAT-044)**: On-page AI discoverability and Google Rich Results compliance: automated `/llms.txt` and `/llms-full.txt` synthesis (`llms-txt-generator.py`), strict Schema.org JSON-LD AST validation for SoftwareApplication/Organization/Article/FAQ (`INV-SEO-01` / `schema-validator.py`), and deterministic heading progression and metadata linting (`INV-SEO-02` / `technical-seo-linter.py`).
- **Frontier Labs Phase 1 Suite (FEAT-045)**: Architectural extraction from Anthropic and OpenAI: Anthropic Structured XML Delimiter Architecture (`<agent_identity>`, `<operating_invariants>`, `<delegation_rules>`, `<tool_usage>`, `<scratchpad>`) eliminating prompt injection and instruction bleed across 5 IDE targets; OpenAI Typed Agent Handoff Routines (`HandoffRoutine`) enforcing DAG acyclicity (`INV-AGENT-01`) and eliminating circular delegation loops; OpenAI Zero-Dependency Simple-Evals Local Runner (`simple-evals.py`) benchmarking coding invariants, mathematical logic, and JSON schema compliance in $<0.05$s.
- **Frontier Labs Phase 2 Suite (FEAT-046)**: Defense & Hardening extraction from NVIDIA and Google: NVIDIA NeMo Colang Guardrails Engine (`agent-guardrails.py`, `.agents/guardrails/rules.co`) providing ultra-fast ($<5\text{ms}$) multi-tier Input Rails (prompt injection shielding), Action Rails (destructive tool interception, prod test blocks), and Output Rails (secret scrubbing, `INV-06` dummy name sanitization); Google OSS-Inspired Invariant Mutation Fuzzer (`invariant-fuzzer.py`) generating 50+ syntactic mutations to mathematically verify 100% linter coverage and zero blindspots.
- **Frontier Labs Phase 3 Suite (FEAT-047)**: Optimization & Synthesis across xAI, Anthropic, OpenAI, Antigravity, and NVIDIA: xAI `x-algorithm` Heavy Ranker & Visibility Filters (`candidate-ranker.py`), OpenAI Fast Offline BPE Tokenizer & Saturation Budgeter (`fast-tokenizer.py`), Anthropic Ephemeral Prompt Cache Breakpoint Optimizer (`context-cache-optimizer.py`), Google Antigravity Swarm Coordinator & Task Slicer (`swarm-coordinator.py`), and NVIDIA Nemotron Synthetic Adversarial Guardrail Stress Tester (`adversarial-fuzzer.py`) maintaining verified 100% defense rate against 30+ injection vectors.
- **Project-Scoped Document Numbering Suite (FEAT-048)**: Strict project isolation preventing cross-project ticket and document numbering leakage (`INV-DOC-04`): dynamic filesystem next-ID calculator and document scaffolder (`doc-numberer.py`), project integrity auditor detecting sequence gaps ($>3$) and duplicates (`ai-agents doc-audit`), and pre-PR static reviewer gate blocking foreign context bleed.
- **Enterprise Resilience, Cellular Multi-Tenancy & Cascading Failure Defense (FEAT-049)**: Big-Tech grade fault tolerance derived from global cloud outage post-mortems: cellular architecture & shuffle sharding ($<3.5\%$ blast radius), Envoy panic mode health checks (`INV-RES-01`), liveness/readiness probe decoupling (`INV-RES-02`), decorrelated full jitter retry mandate (`INV-RES-03`), slow-start warm-up ramps (`INV-RES-04`), and out-of-band control plane isolation (`INV-RES-05`) via `bin/resilience-guard.py`.
- **Autonomous Engineering Blog Intelligence Pipeline (FEAT-001)**: Continuous monitoring of 60+ premier engineering organizations (Google, Netflix, Stripe, Uber, Meta, GitHub, Datadog) via n8n workflow pipeline. Enforces deterministic canonical URL SHA-256 deduplication (`INV-BLOG-01`), 200-word substance gating (`INV-BLOG-02`), and structured 4-Dimensional AI Synthesis (`INV-BLOG-03`) to generate viral LinkedIn thought leadership, living architecture documentation, lean client advisory blueprints, and continuous `ai-agents` codebase rule upgrades.

---

## 4. Key Performance Indicators (KPIs)
- **Local Review Latency**: $<0.10$ seconds for full 35-invariant static check.
- **Guardrails Evaluation Latency**: $<0.005$ seconds ($<5\text{ms}$) per input/action/output tier.
- **Mutation Kill Rate**: 100% kill rate across all generated code mutations.
- **Transpilation Speed**: $<0.25$ seconds for all 53 agents across 5 IDE targets.
- **Evaluation Latency**: $<0.05$ seconds for offline mock evaluation suite across 10 benchmarks.
- **Cloud Token Savings**: $>80\%$ routine operations offloaded to local Ollama ($0 cost).
- **Test Coverage**: 100% line coverage for critical domain engines in `bin/`.

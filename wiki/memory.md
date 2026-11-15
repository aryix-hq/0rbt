# Project Context & Decision Memory: `ai-agents`

- **Project**: `ai-agents` (Antigravity Enterprise Autonomous Framework)
- **Repository**: `github.com/aryix-hq/ai-agents`
- **Active Release**: `v2.3.0`
- **Curator**: Agent Scribe & Memory Specialist (`@documentation-manager`, `@antigravity-bridge`)

---

## 1. Verified Technology Stack & Runtime Bounds

| Component | Choice | Exact Version | Configuration Details |
| :--- | :--- | :--- | :--- |
| **Local LLM Runner** | Ollama | `qwen2.5-coder:14b` | Loopback `127.0.0.1:11434`, $0 cloud tokens |
| **Embedding Model** | Ollama | `nomic-embed-text` | 768-dim vector embeddings in `.agents/memory/vector_store.db` |
| **Core CLI Shell** | Bash / Python | Python 3.12+ | Zero external pip dependencies for core engines in `bin/` |
| **IDE Transpiler** | Python AST | Standalone CLI | Exports to Claude Code, Cursor, Windsurf, Aider, Gemini CLI |
| **UI Telemetry Dashboard** | Python `http.server` | Standalone Web Daemon | Port 4000, zero-npm, dark mode Tailwind + Monaco |

---

## 2. Key Architectural Decisions (ADR Index)

- **ADR-001 (Zero-Token Local Execution)**: All routine coding, git automation, and code reviews run locally via Ollama to conserve cloud context budgets.
- **ADR-002 (Deterministic Static Invariants)**: Regex and AST invariant checks in `bin/local-code-reviewer.py` run in $<0.05$s, acting as an unbypassable pre-push security gate.
- **ADR-003 (Mandatory Ephemeral Staging)**: All testing executes in temporary staging environments that are destroyed immediately after verification. Zero tests on production.
- **ADR-004 (Universal Dummy Name Ban)**: Strictly prohibits `Acme`, `Dummy`, `John Doe`, etc., enforcing domain-authentic realistic entities across all projects.
- **ADR-005 (Mandatory 6-Core AI Context Standard)**: Enforces `prd.md`, `architecture.md`, `rules.md`, `design.md`, `tasks.md`, and `memory.md` across every project.
- **ADR-006 (20-Point Anti-Vibe Shield & Line-by-Line E2E Coverage)**: Automates detection of the 20 failure points with 100% line coverage required in test suites.
- **ADR-007 (Matt Pocock Skills Suite Integration)**: Codifies `grill-with-docs`, `tracer-bullet-slicing` (`to-tickets`), `agent-handoff`, `two-axis-review`, and `wayfinder` into native skills and zero-token CLI engines.
- **ADR-008 (Google Elephant-Goldfish Model Suite Integration)**: Implements cognitive labor separation (spec drafting vs stateless Goldfish review), leaf component contracts (`INV-DOC-02`), and AST spec-to-code drift detection (`INV-DOC-03`).
- **ADR-009 (Agentic Web LLMS.txt & Strict Schema.org Validation)**: Codifies `/llms.txt` and `/llms-full.txt` synthesis (llmstxt.org), Google Rich Results schema validation (`INV-SEO-01`), and sequential heading progression (`INV-SEO-02`).
- **ADR-010 (Frontier Labs Architecture: Anthropic XML, OpenAI Handoffs & Simple-Evals)**: Transpiles agents into canonical XML prompt delimiters (`<agent_identity>`, `<operating_invariants>`, `<delegation_rules>`, `<tool_usage>`, `<scratchpad>`); enforces typed `HandoffRoutine` contracts and DAG acyclicity (`INV-AGENT-01`); establishes zero-dependency local benchmark runner (`bin/simple-evals.py`).
- **ADR-011 (Frontier Labs Defense: NVIDIA Colang Guardrails & Google Mutation Fuzzing)**: Implements multi-tier Colang runtime (`agent-guardrails.py`, `.agents/guardrails/rules.co`) executing Input, Action, and Output rails in $<5\text{ms}$; implements Google OSS-inspired syntactic mutation fuzzer (`invariant-fuzzer.py`) verifying 100% pre-push linter detection rate.
- **ADR-012 (Frontier Labs Synthesis: Candidate Ranking, BPE Token Budgeting, Ephemeral Cache Optimization, Swarm Slicing & Adversarial Fuzzing)**: Implements xAI `x-algorithm` Heavy Ranker & Visibility Filters (`candidate-ranker.py`), OpenAI Fast Offline Tokenizer (`fast-tokenizer.py`), Anthropic 1024-Token Cache Optimizer (`context-cache-optimizer.py`), Google Antigravity Swarm Coordinator (`swarm-coordinator.py`), and NVIDIA Nemotron Synthetic Adversarial Guardrail Stress Tester (`adversarial-fuzzer.py`).
- **ADR-013 (Project-Scoped Document Numbering & Cross-Project Isolation Invariant)**: Enforces strict project isolation (`INV-DOC-04`) via `doc-numberer.py` and pre-PR static reviewer gating, completely eliminating cross-project ticket and document numbering carryover.
- **ADR-014 (Enterprise SRE Resilience, Cellular Architecture & Cascading Failure Immunity)**: Implements cellular architecture & shuffle sharding, Envoy panic mode health checks (`INV-RES-01`), liveness/readiness probe decoupling (`INV-RES-02`), decorrelated full jitter retry mandate (`INV-RES-03`), slow-start warm-up ramps (`INV-RES-04`), and out-of-band control plane isolation (`INV-RES-05`).
- **ADR-015 (Autonomous Engineering Blog Intelligence Pipeline)**: Implements automated n8n pipeline monitoring 60+ tier-1 engineering organizations. Enforces canonical URL SHA-256 deduplication (`INV-BLOG-01`), substance gating (`INV-BLOG-02`), structured 4D AI synthesis (`INV-BLOG-03`), and multi-channel dispatch for LinkedIn thought leadership, living architecture documentation, and lean client advisory.
- **ADR-016 (AI-Agents Skills & Anti-Vibe Invariants Integration into aryix/0rbt-architect)**: Synthesizes the 20 Anti-Vibe Invariants and SRE Resilience doctrine (`INV-RES-01` to `05`) into 550 ChatML instruction pairs (`invariants_instruction_dataset.jsonl`), merges with the 2,065 blog corpus (`instruction_tuning_v1.jsonl` -> 2,615 pairs), upgrades `Modelfile` with compact cache-aligned prompt (<1,024 tokens), and establishes automated benchmark suite (`bin/eval-architect-invariants.py`) verifying $\ge 90\%$ invariant detection rate.
- **ADR-017 (255-Skill AI-Agents Suite Ingestion, Offensive Red Team & 32K Native Context Upgrade)**: Synthesizes all 255 skill domains (78 Offensive Red Team, 35 Bug Hunter, 139 SRE & Distributed Architecture) into 789 ChatML pairs (`all_skills_instruction_dataset.jsonl`), expanding master dataset to 5,508 pairs. Upgrades Ollama context window to native 32K (`PARAMETER num_ctx 32768`). Replaces dogmatic universal assertions with the 3-Tier Reasoning Hierarchy, grounded uncertainty handling, verifiable security finding classification (Confirmed, Likely, Suspicious, Hardening), and implements the 50-Scenario Staff Benchmark (`bin/benchmark-50.py`) with `--compare-base` proving statistically significant uplift over vanilla `qwen2.5-coder:14b`.
- **ADR-018 (Neural Weights Fine-Tuning, LoRA Merging & GGUF Quantization Release Pipeline)**: Establishes the dual-pathway fine-tuning architecture (Local Apple Silicon M4 Pro via MLX vs Cloud GPU via Unsloth/PyTorch) training on 5,600+ ChatML instruction pairs, merging LoRA adapter weights into FP16 base model, quantizing to GGUF `Q4_K_M` via `llama.cpp`, and publishing directly to `ollama.com/aryix/0rbt-architect:latest` to enable zero-RAG parametric recall of 4,169 engineering post-mortems and 255 skills.

---

## 3. Discovered Anti-Patterns & Invariants
- **Big Tech Architecture Copy-Paste Anti-Pattern**: Early-stage companies and client teams blindly copying multi-cluster Kafka, Spanner, or bespoke C++ Envoy meshes from Netflix/Uber blogs without 100M+ scale or a 40-person platform team. Enforce downscale translation (Dimension 3) providing lean Postgres/Redis equivalents.
- **Cascading Health-Check Eviction Death Spiral**: Evicting degraded nodes during partial outages shifts 200-300% load onto surviving nodes, collapsing the entire cluster. Enforce Envoy Panic Mode (`INV-RES-01`) freezing evictions if healthy capacity $<50\%$.
- **Thundering-Herd Reconnect Storms**: Restarted nodes or recovering databases are crushed by thousands of clients retrying on raw exponential backoff. Enforce Decorrelated Full Jitter (`INV-RES-03`) and Slow-Start Traffic Ramps (`INV-RES-04`).
- **Cross-Project Document Numbering Bleed**: In multi-repo environments, agents carry conversational ticket numbers from parent repositories (e.g. `ai-agents` at 45) into downstream repos (e.g. `b00k5` at 6), creating huge numerical leaps. Enforce dynamic filesystem scanning via `bin/doc-numberer.py` and pre-PR leap detection under `INV-DOC-04`.
- **Context Flooding & Ranking Blindness**: Ingesting unranked memory files and research notes into context causes attention dilution and lost instructions. Enforce xAI candidate generation, BM25 scoring, and visibility deduplication (`candidate-ranker.py`).
- **Prompt Cache Poisoning Anti-Pattern**: Embedding dynamic timestamps, nonces, or volatile UUIDs into static system prompt prefixes invalidates 1024-token cache blocks across LLM API calls. Enforce static prefix stability hashing and cache boundary alignment (`context-cache-optimizer.py`).
- **Unchecked Autonomous Tool Actions**: Autonomous subagents left unguarded can be tricked by external prompts or tainted data into executing destructive OS actions (`rm -rf /`, `DROP DATABASE`, production tests). Enforce Action Rails (`agent-guardrails.py`) blocking destructive shell commands deterministically.
- **Static Analysis Regression Blindspots**: Relying only on happy-path or handwritten test diffs leaves linters vulnerable to syntactic evasion (e.g. string formatting vs concatenation, unconventional whitespace, nested scopes). Enforce Google-inspired Invariant Mutation Fuzzing (`bin/invariant-fuzzer.py`) proving 100% mutation kill rate.
- **Multi-Agent Circular Ping-Pong Loop**: Untyped agent delegations without DAG cycle verification risk infinite ping-pong cycles ($A \to B \to A$) that exhaust context and cloud token budgets. Enforce `INV-AGENT-01` DAG acyclicity and typed `HandoffRoutine` contracts.
- **System Instruction Bleed**: Unstructured markdown prompts allow untrusted code or repository text to blur the boundary between system instructions, role identity, and execution rules. Enforce Anthropic canonical XML delimiters (`<agent_identity>`, `<operating_invariants>`, `<delegation_rules>`, `<tool_usage>`, `<scratchpad>`).
- **Framework-Heavy Evaluation Bloat**: Standard LLM evaluation frameworks (lm-evaluation-harness, promptfoo) pull in hundreds of heavy pip dependencies. Enforce zero-dependency, local standard-library runners (`simple-evals.py`) executing in $<0.05$s.
- **Silent Schema Drop Anti-Pattern**: Embedding `<script type="application/ld+json">` with missing mandatory properties (e.g. `applicationCategory` on `SoftwareApplication`, or `acceptedAnswer.text` on `FAQPage`) causes Google Search to silently discard Rich Snippets without HTTP error codes. Enforce strict AST validation (`INV-SEO-01`).
- **Heading Level Skip Anti-Pattern**: Jumping from `<h1>` directly to `<h3>` breaks accessibility outline calculation and confuses crawler content weighting. Enforce sequential increments (`INV-SEO-02`).
- **AI Crawler Token Waste**: Serving full JavaScript-rendered web pages to LLMs causes truncation and hallucinations. Serve clean Markdown via `/llms.txt` and `/llms-full.txt`.
- **Confirmation Bias in Self-Evaluating Specs**: An agent or human that drafts a spec cannot impartially evaluate its own edge cases and omissions. Enforce the Goldfish principle: discard conversational context and run the 5-Pass Review Protocol cold.
- **Monorepo Context Exploration Explosion**: Forcing AI coding tools to recursively read directory trees consumes >85% of working memory. Enforce Peanuts & Hay (`INV-DOC-02`): leaf-level `<pkg>/README.md` contracts indexing purpose, interfaces, and invariants reduce exploration tokens by >85%.
- **Spec-to-Code Drift Decay**: As code evolves, routes and schemas change without corresponding documentation updates. Enforce AST drift auditing (`INV-DOC-03`) to reject PRs with undocumented or phantom endpoints.
- **Horizontal Task Decomposition Anti-Pattern**: Planning tasks horizontally (e.g. all DB schemas first, then all APIs) causes features to remain 0% verifiable until all tasks land. Always enforce vertical tracer-bullet slicing (`INV-STRUCT-02`), cutting through DB + API + UI + E2E test in $\le 25\text{k}$ token context budgets.
- **Sandbox Network Boundary**: Commands like `curl` to external hosts fail inside standard sandbox mode. Use `search_web` for research and `BypassSandbox: true` exclusively for git remote pushes.

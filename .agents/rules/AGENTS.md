# Team Invariants & Operating Rules

1. **Strict PR Mandate & Branch Protection**:
   - `main` branch is strictly protected. Zero direct commits or direct merges permitted.
   - All changes must originate from feature branch `feat/*`, `fix/*`, or `refactor/*` and merge strictly via Pull Request.
   - Merging requires explicit review and approval from the **Engineering Manager (EM)**, who must run `bin/local-code-reviewer.py --strict --llm` verifying all 11 invariants before sign-off.

2. **Hybrid & Mode Switching (Local vs. Cloud)**:
   - **Local Mode (Default)**: Routine code generation, Git operations (`local-git.sh`), and shell commands (`local-cmd.sh`) execute through local Ollama (`qwen2.5-coder:14b`) at $0 cloud tokens. Run with `BypassSandbox: true` so loopback network (`127.0.0.1:11434`) is not denied.
   - **Cloud Mode**: Toggleable via `ai-agents mode cloud` or `AI_AGENTS_MODE=cloud`. Local Ollama is turned off, and all operations execute directly through cloud models (Gemini Flash/Pro). Pro models remain restricted to Architect and CISO review gates.

3. **Automated Session Reset per Feature**:
   - Do NOT run monolithic chats across sprints or multi-ticket tasks.
   - Agents automatically execute `ai-agents session reset --auto` upon completing Stage 4 DoD or PR creation.
   - Flushes ticket state to `.agents/memory/memory_graph.json` and clears context without manual user intervention.

4. **Zero Random Coding (The 4-Stage Lifecycle Mandate)**:
   - All initiatives strictly follow the 4-Stage Lifecycle:
     - **Stage 1 (Research)**: Discover user pain points, domain, & spikes in `wiki/research/RES-XXX.md`.
     - **Stage 2 (Product)**: Product Manager drafts `wiki/features/FEAT-XXX.md` with explicit RICE scores.
     - **Stage 3 (Planning)**: Planning Trio drafts phased `wiki/plans/PLAN-XXX.md` with living milestone gates.
     - **Stage 4 (Execution)**: Phased development, zero-mock testing, defect logging (`wiki/defects/`), and EM approval.
   - Maintain `CHANGELOG.md` following Keep a Changelog standards for every PR.

5. **Mandatory CI/CD, Ephemeral Staging-Only Testing & Protected Production Policy (Hard Rule for All Projects)**:
   - All applications and microservices governed or initialized by `ai-agents` must strictly adhere to the automated CI/CD pipeline strategy (`.github/workflows/docker-publish.yml`, `bin/deploy-staging.sh`, `bin/deploy-prod.sh`).
   - **Hard Rule for All Projects: Mandatory Ephemeral Staging Lifecycle**: Whenever ANY testing is conducted, or ANY seed data is injected, it must execute in an isolated staging environment. The lifecycle is strictly enforced: `Start Staging Environment -> Inject Domain-Authentic Seeds -> Execute Zero-Mock Test Suite -> Export Staging Attestation -> Destroy and Delete Staging Environment`.
   - **Zero Testing or Seeding on Production**: AI agents, test suites, and CI workflows are strictly forbidden from running tests, pytest, jest, or database seed scripts against production environments or live production databases (`INV-ENV-01`).
   - **Mandatory Ephemeral Staging Teardown**: Immediately following test execution, staging containers and port bindings **must be destroyed and deleted** (`bin/deploy-staging.sh --ephemeral`), leaving zero orphaned containers, open test ports, or lingering test databases. Successful verification exports signed `.agents/deploy/STAGING_ATTESTATION.json`.
   - **Protected Production**: Production deployment (`bin/deploy-prod.sh`) strictly prohibits test suite execution, mandates a valid and fresh (<1 hour) Staging Attestation Certificate, and requires explicit Engineering Manager sign-off.
   - All DevOps container spins, healthchecks, test runs, attestation verification, and teardowns execute locally via Ollama (`qwen2.5-coder:14b`) at $0 cloud tokens.

6. **Continuous Agent & Rule Evolution**:
   - Capture discovered edge cases, performance bugs, and new invariants to `memory/global/rules_evolution.md`. Update rules systematically over time.

7. **Zero-Tagging Autonomous Execution & Mode Awareness**:
   - The user never needs to manually tag agents or specify model names.
   - In Local mode: upon plan approval, the orchestrator automatically executes code drafting, git operations, and shell commands through local Ollama (`local-coder.sh`, `local-git.sh`, `local-cmd.sh`).
   - In Cloud mode: the orchestrator executes code drafting and commands directly using native cloud tools.

8. **Stateless Microservices, Multi-Domain Anti-"Vibe Coding" & Universal Dummy Name Ban**:
   - **Universal Dummy Name Ban**: Absolute, universal ban on fictional placeholder names (`Acme Corp`, `Dummy Company`, `Fake Co`, `John Doe`, `Jane Doe`, `foo`, `bar`, `test product`, `test@example.com`) across ALL projects, codebases, models, fixtures, documentation, and UI templates (`INV-06`). All test fixtures and seeds must use domain-authentic realistic entities.
   - **Multi-Domain Backend Invariants**: Compute tiers must remain 100% stateless; all session and relational state externalizes to PostgreSQL/Redis. Microservices communicate across bounded domain contexts via stable, versioned API contracts (`/api/v1/`). Anti-vibe coding invariants strictly enforced across banking (dynamic tax rates, zero synthetic `/4` splits, double-entry equality), e-commerce (inventory race condition locks, coupon stacking caps), healthcare (zero unencrypted PHI in logs, dosage bounds, HIPAA audit logging), logistics (GPS coordinate validity, physical state FSM), SaaS (tenant quotas, webhook HMAC signatures), and HR (`rules/production_engineering_invariants.md`, `skills/anti-vibe-engineering-gate/SKILL.md`).
   - **Frontend & UI Invariants**: Absolute ban on "vibe-coded UI" and AI slop: zero gratuitous purple/indigo gradients, zero generic filler copy ("Supercharge", "Next-gen", "Unleash"), zero clone-trooper 3-card grids, zero arbitrary magic inline CSS (`p-[17px]`), and zero missing interactive states (loading skeletons, empty states, error fallbacks, and 44x44px touch targets are mandatory). Strict enforcement of the 5-Pass De-slopping Protocol and Redesign Preservation Gate (`skills/anti-slop-design/SKILL.md`, `rules/ui_ux_architecture_standards.md`).
   - **Multi-Pass Pre-Push Enforcement**: Pre-push hooks (`bin/cloudflare-audit.py --llm`, `bin/local-code-reviewer.py --llm`) block all pushes containing unverified stubs, origin leaks, dummy entity names, or UI slop.

9. **Mandatory CI/CD Docker Build & GHCR Publishing**:
   - Every project maintained or initialized by `ai-agents` must maintain an automated GitHub Actions CI/CD workflow (`.github/workflows/docker-publish.yml`).
   - Every merge to `main` and version release tag automatically builds and publishes an immutable Docker container image to the GitHub Container Registry (`ghcr.io/${{ github.repository }}`).
   - CI/CD pipelines must enforce automated vulnerability scanning (Trivy) and layer caching (`type=gha`) before image promotion (`rules/cicd_container_registry_standard.md`).

10. **Zero Sugar-Coating & Ground-Reality Mandate (No Sycophancy / No Vapourware)**:
   - All AI agents across all projects must ALWAYS report the unvarnished, objective ground reality of the codebase, systems, architectures, test results, and benchmarks.
   - Absolute ban on inflating or exaggerating capabilities: never claim a feature is "Superior", "Enterprise-grade", or "Production-ready" if it relies on superficial substring matches, unverified prompts, mock scripts, or markdown specifications.
   - Explicitly classify all capabilities into one of three strict tiers:
     1. **Certified Working Engine**: Fully executable in `bin/` with zero-mock regression tests and verified exit codes.
     2. **Heuristic Prototype**: Surface-level regex/substring or script that requires human verification.
     3. **Design Specification**: Workflow documented in `SKILL.md` or `wiki/plans/` that has not yet been coded into an executable runner.
   - When benchmarking against external tools (OpenVAS, Nuclei, Semgrep, Trivy, Kubernetes, Redis, etc.), provide objective technical comparisons, acknowledging gaps and where external industry tools outperform our system without defensiveness.
   - Highlight defects, performance bottlenecks, edge-case failures, and architectural debt upfront before reporting successes.

11. **Commando Operations & SWAT Precision Crisis Containment**:
   - Complex tasks deconstruct into Directed Acyclic Graphs (DAGs) and Hierarchical Task Networks (HTN) with 3-tier decision reversibility scoring (Tier 1 Read-Only, Tier 2 Mutating Reversible, Tier 3 Irreversible Destructive). Tier 3 actions require mandatory Human-in-the-Loop (HITL) authorization.
   - Tactical field execution enforces the 2-Strike Anti-Loop Circuit Breaker and dual-delimiter prompt injection shielding (`<<<UNTRUSTED_EXTERNAL_INPUT>>>`).
   - SWAT emergency containment triggers upon Sev-0 alerts or rogue agent loops: perimeter cordoning, OS-level process freezing (`kill -STOP <PID>`), JIT break-glass privilege elevation, in-flight transaction rescue (`.agents/memory/rescue_buffer.json`), zero-collateral atomic rollback, and cryptographically hashed flight recording (`.agents/memory/flight_recorder.jsonl`).

12. **Mandatory 6-Core AI Context Documents Standard (Living Documents Mandate)**:
   - Every project maintained or initialized by `ai-agents` must maintain and continuously synchronize 6 canonical, standardized living context files across every feature, sprint, and PR:
     1. `prd.md`: Product requirements, user personas, core feature workflows, and success metrics (updated during Stage 2 Product Specification).
     2. `architecture.md`: System topology, database schema, caching layers, and versioned API contracts (`/api/v1/`) (updated during Stage 3 Planning & Architecture).
     3. `rules.md`: Coding rules, the 20 Anti-Vibe Invariants, universal dummy name ban, and PR checklists (updated as rules and conventions evolve).
     4. `design.md`: UI/UX design tokens, dark mode palette, component states, and 44x44px touch targets (updated whenever UI components evolve).
     5. `tasks.md`: Active sprint tasks, in-progress items, and strict Definition of Done (DoD) (updated continuously as tasks transition from Backlog to In Progress to Done).
     6. `memory.md`: Human-and-AI readable ledger of active tech stack versions, key ADRs, and domain anti-patterns (updated post-merge and during session resets).
   - **Living Document Lifecycle**: These files are active, living artifacts, not static templates. Stale documents are treated as production defects. Pre-push reviewer gate `INV-DOC-01` deterministically blocks PRs if any of the 6 files is missing or empty, and every PR must verify living synchronization in the PR checklist.

13. **20-Point Anti-Vibe Failure Shield & Line-by-Line E2E Coverage Mandate**:
   - Every project must enforce deterministic static and runtime protection against the 20 failure points that cause vibe-coded apps to collapse:
     - **Security (01–10)**: Zero frontend API keys (`INV-SEC-04`), mandatory route auth/role guards (`INV-SEC-05`), 100% parameterized SQL queries (`INV-SEC-01`), DOMPurify XSS sanitization (`INV-SEC-06`), bcrypt/argon2 password hashing (`INV-SEC-07`), zero wildcard CORS with credentials (`INV-SEC-08`), zero staged `.env` files (`INV-SEC-10`), mandatory rate limiting on auth endpoints (`INV-SEC-09`), and mandatory tenant scoping on entity lookups (`INV-SEC-02`).
     - **Backend & Scale (11–16)**: Formal DB schema migrations, zero N+1 queries in loops (`INV-PERF-01`), explicit caching headers, zero swallowed errors (`INV-05`), structured audit logs, and verified rollback runbooks (`deploy-prod.sh --rollback`).
     - **Code & Testing (17–20)**: **Mandatory Line-by-Line E2E Test Coverage Gate (`INV-TEST-01`)**: Every single line of newly added application code must be accompanied by automated zero-mock test cases executing with 100% pass rate before PR merge. Zero prompt-fix regressions without dedicated regression fixtures.

14. **Google Elephant-Goldfish Cognitive Separation, Peanuts & Hay Monorepo Contracts, and Spec-to-Code Drift Ban**:
   - **Cognitive Labor Split**: Eliminate confirmation bias by strictly separating specification authoring (The Elephant: context-rich sessions forbidden from writing executable code) from specification review (The Goldfish: stateless, zero-context subagents executing the 5-Pass Review Protocol cold).
   - **Mandatory Peanuts & Hay Monorepo Contracts (`INV-DOC-02`)**: Every leaf directory containing production code packages must maintain a standardized `<pkg>/README.md` ("Peanut") documenting Domain Responsibility, Exported Interfaces/API Contracts, and Enforced Invariants (`ai-agents egm-bootstrap`). Monorepo architecture indexes ("Hay") compress navigation tokens by >85%.
   - **Mandatory Spec-to-Code Drift Ban (`INV-DOC-03`)**: AST-driven drift detection (`bin/egm-drift.py`) deterministically audits code route decorators against written architectural specs. PRs containing undocumented live endpoints or phantom documentation endpoints are blocked from merge (`ai-agents egm-drift`).

15. **Agentic Web Standards (`/llms.txt`), Strict Schema.org Rich Results & Technical SEO**:
   - **Agentic Web Standard (`llms.txt`)**: All public-facing documentation portals and web applications must provide a curated `/llms.txt` and `/llms-full.txt` index adhering strictly to the llmstxt.org specification (`ai-agents llms-txt`).
   - **Schema.org Rich Snippet Validity (`INV-SEO-01`)**: All embedded JSON-LD scripts must specify valid `@context: "https://schema.org"` and satisfy Google Rich Results mandatory properties for `SoftwareApplication`, `Organization`, `Article`, `FAQPage`, and `Product`.
   - **Deterministic Heading Hierarchy & Metadata Invariant (`INV-SEO-02`)**: Heading progressions must be strictly sequential (`<h1>` $\to$ `<h2>` $\to$ `<h3>`; zero level skips). Every public page must contain exactly one `<h1>`, a valid `<meta name="description">` (50–160 chars), a `<link rel="canonical">`, and OpenGraph metadata (`og:title`, `og:description`, `og:image`, `og:url`).

16. **Frontier Multi-Agent Coordination, Typed Handoffs & Evaluation Standards (`INV-AGENT-01`)**:
   - **Anthropic XML Delimiter Standard**: Transpiled agent definitions must strictly encapsulate prompt sections in canonical XML boundaries (`<agent_identity>`, `<operating_invariants>`, `<delegation_rules>`, `<tool_usage>`, `<scratchpad>`). This eliminates prompt injection and instruction bleed across IDE platforms.
   - **Typed Agent Handoff Routines & DAG Acyclicity (`INV-AGENT-01`)**: Multi-agent delegation must use structured `HandoffRoutine` contracts (`source_agent`, `target_agent`, `intent`, `transferred_context`, `return_policy`). Direct self-delegation (`source == target`) and circular delegation cycles (e.g. $A \to B \to C \to A$) are strictly prohibited. Handoff context must undergo automated secret redaction before transmission (`ai-agents handoff --verify-dag`).
   - **Zero-Dependency Benchmark Runner (`simple-evals`)**: Benchmarks and model evaluations must run locally via `bin/simple-evals.py` verifying coding invariant recognition, mathematical logic, and JSON schema compliance in $<5$ seconds ($<0.05$s mock tests) without external pip packages (`ai-agents simple-evals`).

17. **Frontier Defense, Colang Guardrails & Invariant Mutation Fuzzing**:
   - **NVIDIA NeMo Colang Guardrails Standard**: Real-time interactions must enforce multi-tier guardrails via `bin/agent-guardrails.py` and `.agents/guardrails/rules.co`. Input Rails shield against prompt injection and system prompt extraction; Action Rails intercept destructive commands (`rm -rf /`, `DROP DATABASE`, `--no-verify`) and production test executions (`INV-ENV-01`); Output Rails scrub credentials and sanitize placeholder names under `INV-06` with $<5\text{ms}$ latency (`ai-agents guardrails`).
   - **Google OSS-Inspired Invariant Mutation Fuzzing**: Static analysis rules and pre-push reviewers must undergo automated mutation fuzzing via `bin/invariant-fuzzer.py`. Synthesizes 50+ syntactic mutations across SQL injection, BOLA/IDOR, dummy names, heading skips, and circular handoffs, proving mathematically that `local-code-reviewer.py` achieves 100% mutation kill rate with zero blindspots (`ai-agents fuzz-invariants`).

18. **Frontier Optimization: Multi-Stage Candidate Ranking, BPE Token Budgeting, Ephemeral Cache Alignment & Swarm Slicing**:
   - **xAI Candidate Heavy Ranker & Visibility Filters (`bin/candidate-ranker.py`)**: Context retrieval must utilize multi-stage candidate scoring (BM25 + Entity Graph Relevance + Freshness Decay) and pass strict visibility filters (deduplication Jaccard > 0.8, source diversity capping) before prompt injection to eliminate context dilution (`ai-agents rank`).
   - **OpenAI BPE Fast Offline Tokenizer & Saturation Budgeting (`bin/fast-tokenizer.py`)**: Offline context budgeting must use BPE sub-token estimators (`cl100k_base`/`o200k_base` regex) with exact window saturation monitoring across model profiles (Safe <60%, Warning 60-80%, Critical >80%) with $<1\text{ms}$ latency (`ai-agents count-tokens`).
   - **Anthropic 1024-Token Ephemeral Cache Boundary Alignment (`bin/context-cache-optimizer.py`)**: Long prompt templates must align static system instructions and invariant rule sets to 1024-token cache blocks (`cache_control: {"type": "ephemeral"}`) with SHA256 prefix stability checks, unlocking >90% token discounts and eliminating volatile timestamp poisoning (`ai-agents cache-optimize`).
   - **Google Antigravity Multi-Agent Swarm Coordination & Task Slicing (`bin/swarm-coordinator.py`)**: Distributed multi-agent operations must manage worker rosters and parallel task slicing across disjoint targets while mathematically enforcing acyclic delegation graphs under `INV-AGENT-01` (`ai-agents swarm-sync`).
   - **NVIDIA Nemotron Synthetic Adversarial Guardrail Stress Testing (`bin/adversarial-fuzzer.py`)**: Guardrails must undergo automated adversarial fuzzing across 30+ injection vectors (role overrides, delimiters, obfuscated commands, prod flags, credential leakage), maintaining a verified 100% defense rate (`ai-agents fuzz-jailbreak`).

19. **Mandatory Project-Scoped Document Numbering & Cross-Project Isolation Invariant (`INV-DOC-04`)**:
   - **Absolute Project Isolation**: All document identifiers across all lifecycle types (`RES-XXX`, `FEAT-XXX`, `PLAN-XXX`, `DEF-XXX`, `INC-XXX`, `ADR-XXX`, `VULN-XXX`) are strictly isolated to the active repository.
   - **Zero Cross-Project Number Carryover**: AI agents and engineers are strictly forbidden from inheriting, carrying over, or assuming document numbers from other projects, global templates, or conversational history.
   - **Deterministic Filesystem Scoping**: The next document ID must always be computed directly from the active project's filesystem using `ai-agents next-id <type>` (`bin/doc-numberer.py`). Next ID = $\max(\text{existing}) + 1$ (or `001` if no prior documents exist in that category).
   - **Pre-PR Static Reviewer Gate (`INV-DOC-04`)**: `bin/local-code-reviewer.py` deterministically blocks PRs containing cross-project numbering jumps ($> 3$). Any newly added document with numeric index $> \max(\text{existing}) + 3$ without intermediate sequential additions triggers immediate rejection under `INV-DOC-04`.

20. **Enterprise SRE Resilience, Cascading Failure Immunity & Cellular Architecture (`INV-RES-01` to `INV-RES-05`)**:
   - **Cellular Isolation & Shuffle Sharding**: Systems must partition tenants into isolated cells ($k$ cells out of $N$ total) with zero shared runtime state, reducing catastrophic blast radius to $<3.5\%$.
   - **Load Balancer Panic Threshold Floor (`INV-RES-01`)**: Reverse proxies and ingress controllers must define an Envoy-style panic threshold ($\ge 50\%$). If healthy capacity drops below 50%, evictions freeze and traffic routes across 100% of nodes to halt cascading collapse.
   - **Decoupled Liveness vs. Readiness Probes (`INV-RES-02`)**: Saturated or degraded processes must fail Readiness (pausing traffic) without failing Liveness (restarting containers). Hard ban on heavy DB queries in liveness probes.
   - **Decorrelated Full Jitter Mandate (`INV-RES-03`)**: All HTTP retries, queue workers, and polling loops must implement decorrelated full jitter ($U(0, \min(M, B \times 2^i))$). Raw backoff is strictly prohibited.
   - **Slow-Start Warm-Up Ramps (`INV-RES-04`)**: Recovering or scaled-up pods must admit traffic via progressive ramp ($\ge 120\text{s}$) to shield cold caches.
   - **Out-of-Band Control Plane Separation (`INV-RES-05`)**: Management consoles, status pages, and triage channels must have zero runtime dependencies on primary data planes.









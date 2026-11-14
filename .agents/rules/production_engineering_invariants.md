# Production Engineering & Enterprise Framework Invariants

> **Custodian**: `@engineering-manager`, `@fullstack-developer`, `@devops-sre`  
> **Origin**: Synthesized from `affaan-m/ecc`, `mohi-devhub/antivibe`, and `ktaletsk/learn-codebase`  
> **Scope**: All services, frontend frameworks, backend APIs, and distributed worker pipelines.

---

## 1. Web Framework & SSR Hydration Invariants (Next.js, React)

1. **Hydration Integrity**:
   - Client-side and server-rendered HTML must match deterministically on initial mount.
   - Non-deterministic values (e.g. `Date.now()`, `Math.random()`, `window.innerWidth`, client `localStorage`) must **never** be rendered directly during initial SSR pass. They must defer to an explicit `useEffect` mount phase with an empty dependency array.
   - `suppressHydrationWarning` is prohibited except for third-party browser extensions injecting DOM elements (e.g. password managers).
2. **Server Components vs Client Components**:
   - Keep `"use client"` at the furthest leaves of the DOM component tree.
   - Server components must never import client-only APIs (`window`, `document`, React context providers).
   - Sensitive backend tokens, database clients, or internal API URLs must never be passed to client components.
3. **Effect Cleanup & Memory Leaks**:
   - Every `useEffect` that establishes a WebSocket, event listener, `setInterval`, or AbortController must return an explicit cleanup function.
   - Unhandled async promises in `useEffect` must track component mount status or bind to an `AbortSignal`.

---

## 2. Asynchronous Concurrency & Worker Invariants (Node.js, Python, Go)

1. **Async Event Loop & Thread Pool Exhaustion**:
   - In Node.js / Python asyncio, CPU-bound tasks (crypto hashing, image compression, large JSON parsing) must **never** run on the main event loop thread; offload to worker threads or background processes.
   - In Go, never spawn unmanaged goroutines without a bound `context.Context` and a cancellation signal.
2. **Unhandled Promise Rejections & Process Crashing**:
   - Top-level async handlers must be wrapped in structured try/catch blocks.
   - Register explicit global process traps (`unhandledRejection`, `uncaughtException`, `SIGTERM`, `SIGINT`) that trigger graceful connection draining before shutdown.
3. **Database Connection Pool Exhaustion**:
   - Every database transaction checkout must be bound to a strict timeout context ($< 5\text{s}$).
   - Connections must return to the pool in a mandatory `finally` / `defer` block.
   - Connection pool sizes must be explicitly configured and capped relative to compute container memory: $\text{Pool Max} \le \text{DB Max Connections} / \text{Instances}$.

---

## 3. Distributed State, Session & Serialization Invariants

1. **Session Serialization Safety**:
   - Session objects and job queue payloads must serialize strictly as pure JSON or Protocol Buffers.
   - Never serialize runtime stateful instances (sockets, database handles, functions, cyclic references).
   - Payload schemas must support additive, backward-compatible fields. Deleting or renaming existing fields without versioned migration is strictly prohibited.
2. **Distributed Lock Expiry & Fencing**:
   - All distributed locks (Redis Redlock, PostgreSQL advisory locks) must have a deterministic TTL.
   - Mutating state operations guarded by distributed locks must verify fencing tokens or monotonic version counters to defeat split-brain race conditions.

---

## 4. Error Handling & API Contract Boundaries

1. **No Silent Error Swallowing**:
   - Empty catch blocks (`catch (e) {}` or `except: pass`) are strictly forbidden and will fail PR CI gates.
   - Errors must either be handled and recovered from with a valid fallback, or logged with structured stack traces and rethrown as categorized domain errors.
2. **Stable JSON API Error Shapes**:
   - All error responses must adhere to the standard error contract:
     ```json
     {
       "error": {
         "code": "INVALID_TENANT_SCOPE",
         "message": "Tenant identifier does not match authorization context.",
         "details": [],
         "trace_id": "00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01"
       }
     }
     ```
   - Never expose raw database errors, internal file paths, or ORM stack traces in production API responses.

---

## 5. The 12 Anti-Vibe Coding & Code Integrity Invariants

1. **Zero Synthetic / Mock Data in Production Code**:
   - Mock datasets, synthetic split distributions, fake company names (`Acme Corp`, `Dummy Ltd`), placeholder employee profiles (`John Doe`), dummy PAN/TAN/CIN/DIN numbers, fake SRNs, and synthetic challans/receipts are STRICTLY PROHIBITED outside of `tests/` and `fixtures/`.
   - Production code must query live database models, invoke verified upstream APIs, or raise an explicit domain error (`MissingDataError`, `UnconfiguredTenantError`) if data is absent.
2. **Zero Hardcoded Magic Financial Constants & Tax Overrides**:
   - Financial calculations, tax percentages (GST, TDS, EPF, ESI), threshold limits, and monetary amounts must NEVER be hardcoded as magic literals (e.g. `11800.00`, `18%`, `0.10`). They must resolve dynamically from tenant tax masters, regulatory rate tables, or line-item transaction ledgers.
3. **Real Database Aggregations Over Synthetic Split Math**:
   - Never approximate periodic numbers (e.g. quarterly TDS, monthly depreciation) by dividing an annual figure by $N$ (e.g. `total / 4`) unless explicitly mandated by statutory amortisation rules. Figures must be aggregated bottom-up from atomic transaction records.
4. **Dynamic Context Resolution Over Insecure Fallbacks**:
   - Never inject fallback tenant credentials, dummy bank account numbers, or default secrets when dynamic context is missing. Missing credentials must fail fast with authorization exceptions.
5. **Genuine Verification Pipelines Over Fake Compliance Stubs**:
   - Never return dummy compliant states (e.g. `return "COMPLIANT"`, `status = "VERIFIED"`) without executing the full statutory rule validation pipeline. If prerequisites are missing, return `"INCOMPLETE"` or `"REQUIRES_REVIEW"` with actionable audit discrepancies.
6. **Zero Fictitious Entity Identities**:
   - Never hardcode fictional company names (`Acme Corp`), dummy director names (`John Doe`), placeholder DINs (`00000000`), fake CINs, or mock PAN/TANs in business documents.
7. **Immediate Deletion of Dead Legacy Export Paths**:
   - Deprecated export formats or obsolete integration packages must be cleanly removed or explicitly gated behind migration flags, never left running as unmaintained attack surfaces.
8. **Socratic Architectural Justification ("Why over What")**:
   - Non-trivial business algorithms, distributed handlers, and architectural abstractions must include an architectural docstring explaining *why* this design pattern was chosen, what trade-offs were considered, and why simpler alternatives were rejected.
9. **Null & Empty State Integrity (Zero Blind Defaults)**:
   - Prohibits masking missing data with blind silent defaults (`or []`, `or {}`, `or 0`) when the field represents a mandatory relational foreign key or statutory prerequisite. Missing dependencies must raise explicit domain exceptions.
10. **State Machine & Idempotency Invariants**:
    - Every mutating database transaction, state transition, or payout export must define explicit idempotency keys and state transition guards (e.g. a statutory return cannot transition from `FILED` back to `DRAFT`).
11. **Active Recall & Predictive Boundary Tests**:
    - Test suites must not consist solely of "happy path" checks against synthetic data. Tests must explicitly prove boundary conditions: zero amounts, negative values, boundary dates (leap years, fiscal year crossover March 31 / April 1), maximum string lengths, and database rollback behaviors.
12. **Strict API Contracts & Mass Assignment Shield**:
    - All API endpoints must enforce strict input validation models (Pydantic / Zod) with `extra = "forbid"` to prevent mass assignment, unexpected parameter injection, or arbitrary column updates.

---

## 6. The 10 Frontend & UI Anti-Vibe Invariants

Derived from NeuralDev's *Unslop UI* framework and `skills.rest/skill/anti-vibe-review`, frontend code must eliminate AI design homogenization:

1. **Zero AI Slop Gradients**: Prohibits gratuitous purple-to-indigo or cyan-to-magenta gradient blobs on cards, buttons, or backgrounds. Colors must derive strictly from living brand design tokens.
2. **Zero Buzzword Microcopy ("No AI Filler")**: Prohibits generic AI marketing copy ("Supercharge your workflow", "Next-gen platform", "Unleash the power of AI", "Seamless experience", "All-in-one tool"). Copy must describe concrete metrics, outcomes, or domain actions.
3. **Zero Clone-Trooper 3-Card Grids**: Prohibits 3 identical cards with centered Lucide icons, identical padding, and identical secondary buttons. Layouts must employ asymmetric bento grids, varied visual weight, or structured tables.
4. **Zero Missing Interactive States (The 7-State Matrix)**: Every interactive component (buttons, inputs, cards, tables) must define all 7 states: `Default`, `Hover`, `Focus-Visible`, `Active`, `Disabled`, `Loading (Skeleton)`, and `Empty State`.
5. **Zero Arbitrary Magic CSS Values**: Prohibits ad-hoc inline Tailwind brackets (`p-[17px]`, `rounded-[23px]`, `text-[#7c3aed]`). All values must adhere to the 4px/8px coordinate matrix and registered design tokens.
6. **Mobile Viewport Resiliency (375px Floor)**: Prohibits horizontal scrolling overflows on 375px mobile screens. Responsive typography must wrap or scale down smoothly; minimum 44x44px touch targets.
7. **Redesign Preservation Gate (Zero Dropped Functionality)**: When refactoring or restyling UI, 100% of event handlers (`onClick`, `onSubmit`), forms, inputs, routes (`<Link href="...">`), and accessibility attributes (`aria-*`, `role`) must be preserved.
8. **Real Data Presentation Over Static Mock SVGs**: Prohibits hardcoding static SVG sparklines, dummy avatar photos, or fake star ratings to simulate live dynamic dashboards. Charts and metrics must bind to real props or display loading skeletons.
9. **Tabular Numeric Alignment**: Prohibits proportional numbers in financial ledgers, counters, tables, or metric cards. Use `tabular-nums` and monospace numeric fonts to ensure column decimals align.
10. **WCAG 2.1 AA Contrast Minimum**: Prohibits low-contrast light-gray text on dark backgrounds or white text on pastel buttons. Maintain minimum 4.5:1 for body copy and 3:1 for large headers/interactive elements.

---

## 7. Multi-Domain Business Logic & Industry Invariants

Anti-vibe invariants extend across all operational domains beyond banking and fintech:

1. **E-Commerce & Retail (`INV-DOM-01`)**:
   - Inventory decrements must enforce row-level locks or atomic conditional queries (`UPDATE inventory SET stock = stock - :qty WHERE id = :id AND stock >= :qty`). Zero race condition overselling.
   - Discount stacking must enforce non-negative floor caps (`total >= 0`) and coupon priority ordering.
   - Currency calculations must use integer minor units (cents, paise) or arbitrary-precision `Decimal` to eliminate floating-point arithmetic errors.
2. **Healthcare & Clinical EHR (`INV-DOM-02`)**:
   - Zero unencrypted Protected Health Information (PHI) in log statements or telemetry spans.
   - Medication dosages must validate against minimum and maximum safety bounds before order dispatch.
   - Every read of a patient medical record must synchronously emit a non-repudiable HIPAA access audit log.
3. **Logistics & Fleet Telematics (`INV-DOM-03`)**:
   - Latitude/longitude must validate within realistic boundaries ($-90 \le \text{lat} \le 90$, $-180 \le \text{lon} \le 180$).
   - Hardcoded `(0.0, 0.0)` Null Island coordinates are strictly prohibited as fallback values.
   - Shipment status transitions must follow realistic physical progression (`MANIFESTED -> PICKED_UP -> IN_TRANSIT -> OUT_FOR_DELIVERY -> DELIVERED`).
4. **SaaS Platforms & Multi-Tenancy (`INV-DOM-04`)**:
   - Resource provisioning must validate active tenant quotas and seat licensing before creation.
   - Outbound webhooks must dispatch with an HMAC-SHA256 signature and UNIX timestamp for replay protection.
5. **HR & Payroll Invariants**:
   - Leave deductions must verify non-negative balance ceilings.
   - Salary disbursements must synchronously compute statutory deductions and tax withholding.

---

## 8. Universal Dummy Name Ban & Ephemeral Staging Mandate

1. **Universal Dummy & Placeholder Name Ban (`INV-06`)**:
   - Absolute ban on fictional placeholder names (`Acme Corp`, `Dummy Company`, `Fake Co`, `John Doe`, `Jane Doe`, `foo`, `bar`, `test product`, `test@example.com`) across code, models, fixtures, docs, and UI components.
   - Test fixtures and seed scripts must use the **Authentic Domain Entity Standard** (e.g. `Vanguard Logistics Ltd`, `Meridian Health Systems`, `Aura Diagnostics Inc`).
2. **Mandatory Ephemeral Staging Lifecycle (`INV-ENV-01`)**:
   - Absolute ban on running test suites, pytest, jest, or database seed scripts against production environments (`NODE_ENV=production`, `PROD_DB`).
   - All tests and seed insertions must execute in an ephemeral staging container that is **started, tested, verified, and immediately destroyed and deleted** (`rules/staging_ephemeral_test_standard.md`).
   - Production deployment mandates a valid, fresh (<1 hour) Staging Attestation Certificate signed by the Engineering Manager.

---

## 9. Multi-Agent Coordination & Delegation Invariants

1. **Agent Handoff & Delegation Acyclicity (`INV-AGENT-01`)**:
   - Multi-agent collaboration must strictly execute via structured `HandoffRoutine` contracts specifying `source_agent`, `target_agent`, `intent`, `transferred_context`, and `return_policy`.
   - Direct self-delegation (`source_agent == target_agent`) is strictly prohibited to prevent infinite self-referential execution loops.
   - Delegation chains must form a strict Directed Acyclic Graph (DAG). Circular delegation cycles (e.g. $A \to B \to C \to A$) are blocked statically and at runtime.
   - Transferred context must undergo automated regex secret scrubbing (`sk-*`, `ghp_*`, `AKIA*`, JWT, DB URIs) prior to serialization.

---

## 10. Colang Multi-Tier Guardrails & Invariant Mutation Assurance

1. **Multi-Tier Runtime Guardrails**:
   - Agent inputs must evaluate through Input Rails blocking prompt injections and instruction override attempts in $<5\text{ms}$.
   - Agent tool and shell actions must evaluate through Action Rails blocking destructive system commands (`rm -rf /`, `DROP DATABASE`) and production test suites (`INV-ENV-01`).
   - Agent outputs must evaluate through Output Rails scrubbing API tokens and replacing dummy names under `INV-06`.
2. **Automated Mutation Fuzzing Assurance**:
   - Static analysis rules and reviewers must undergo automated mutation fuzzing (`bin/invariant-fuzzer.py`) achieving 100% mutation kill rate.

---

## 11. Frontier Multi-Stage Ranking, BPE Token Budgeting & Swarm Invariants

1. **Candidate Generation & Visibility Filters**:
   - Context ingestion must use multi-stage retrieval (BM25 + Entity Boost + Freshness Decay) and apply visibility filters (Jaccard deduplication threshold 0.8, source diversity capping) to prevent context saturation.
2. **Offline BPE Token Saturation Budgeting**:
   - Offline token counting must employ BPE regex token estimation with saturation alerts (Safe <60%, Warning 60-80%, Critical >80%) with $<1\text{ms}$ latency.
3. **Prompt Cache Breakpoint Alignment**:
   - Static prompt prefixes must align to 1024-token cache blocks with SHA256 prefix stability checks and zero volatile tokens (timestamps, UUIDs).
4. **Swarm Coordination & Task Partitioning**:
   - Parallel agent operations must partition tasks across disjoint slices with acyclic handoff validation under `INV-AGENT-01`.
5. **Continuous Adversarial Guardrail Stress Testing**:
   - Guardrails must achieve 100% defense rate against 30+ synthetic adversarial injection and escape vectors (`bin/adversarial-fuzzer.py`).

---

## 12. Project-Scoped Document Numbering & Cross-Project Isolation Invariants

1. **Mandatory Project-Scoped Document Numbering (`INV-DOC-04`)**:
   - All document identifiers across all lifecycle categories (`RES-XXX`, `FEAT-XXX`, `PLAN-XXX`, `DEF-XXX`, `INC-XXX`, `ADR-XXX`, `VULN-XXX`) are strictly isolated to the active repository.
   - Cross-project number bleed is strictly prohibited: an agent or engineer working in a downstream project (e.g. `b00k5`) must never inherit ticket numbers from an upstream or parent repository (e.g. `ai-agents`).
   - Dynamic Next-ID Protocol: Every new document ID must be computed directly by scanning the local filesystem via `bin/doc-numberer.py` (`ai-agents next-id <type>`). Next ID = $\max(\text{existing}) + 1$ (or `001` if no documents exist in that category).
   - Pre-Push Reviewer Gate: `bin/local-code-reviewer.py` deterministically rejects any PR introducing a document ID where $\text{new\_id} > \max(\text{existing}) + 3$ without intermediate sequential additions, preventing foreign ticket leaks from merging.

---

## 13. Enterprise SRE Resilience, Cascading Failure Immunity & Cellular Architecture Invariants

1. **Load Balancer Panic Threshold Floor (`INV-RES-01`)**:
   - Ingress proxies, API gateways, and upstream load balancer definitions must enforce an Envoy-style panic threshold ($\ge 50\%$).
   - If healthy upstream capacity drops below the threshold, the proxy must freeze node evictions and distribute traffic across 100% of endpoints, preventing cascading collapse.
2. **Liveness vs. Readiness Probe Decoupling (`INV-RES-02`)**:
   - High memory pressure, queue saturation, or downstream latency must fail Readiness (pausing ingress traffic) without failing Liveness (triggering container reboots).
   - Prohibits heavy database queries (`SELECT`, `db.query`) or external network calls inside liveness probe handlers.
3. **Decorrelated Full Jitter Mandate (`INV-RES-03`)**:
   - All client retries, worker loops, and distributed polling routines must implement decorrelated full jitter ($U(0, \min(M, B \times 2^i))$). Raw backoff without jitter is strictly blocked.
4. **Slow-Start Traffic Ramp (`INV-RES-04`)**:
   - Recovering nodes or newly provisioned capacity must admit traffic via a progressive ramp ($\ge 120\text{s}$) to allow connection pools, caches, and JIT bytecode to stabilize.
5. **Out-of-Band Control Plane Separation (`INV-RES-05`)**:
   - Administrative dashboards, telemetry aggregators, status pages, and emergency communication channels must maintain zero runtime dependencies on primary data planes.




# FEAT-002: AI-Agents Skills & Anti-Vibe Invariants Integration into aryix/0rbt-architect

> **Lifecycle Stage**: Stage 2 (Product Specification)  
> **Status**: APPROVED  
> **Target Version**: `v1.1.0`  
> **RICE Score**: 84.0 (Reach: 8 | Impact: 9 | Confidence: 7 | Effort: 6)  
> **Lead**: Product Manager (`@product-manager`) & System Architect (`@architect`)

---

## 1. Problem Statement

Generalist coding LLMs (GPT-4o, Claude 3.5 Sonnet, vanilla Qwen 2.5) frequently generate "vibe-coded" systems that look plausible in prototypes but fail catastrophically in production:
- Omitting tenant scopes on database lookups (`INV-SEC-02` BOLA / IDOR).
- Omitting client idempotency keys on payment and order endpoints (`INV-SEC-09`).
- Using raw exponential backoff loops that trigger cascading thundering herds (`INV-RES-03`).
- Placing heavy relational queries inside Kubernetes liveness probes (`INV-RES-02`).
- Hardcoding static mock placeholders (`Acme Corp`, `foo`, `bar`) instead of domain-authentic logic.

While `0rbt`'s corpus provides 2,065 real-world post-mortems and engineering blogs, raw text alone is descriptive rather than prescriptive. To transform `aryix/0rbt-architect` into an authoritative systems design and review assistant, we must integrate the prescriptive invariants and skills developed across the `ai-agents` ecosystem.

---

## 2. Target Personas & Use Cases

1. **AI Coding Assistants (Cursor, Copilot, Claude Code, Cline)**:
   - Queries `aryix/0rbt-architect` via local Ollama API to review proposed architectures before generating scaffolding.
2. **Staff / Principal Engineers & Tech Leads**:
   - Uses `ollama run aryix/0rbt-architect` to stress-test PRDs, Architecture Decision Records (ADRs), and disaster recovery plans.
3. **Startup Founders & Small-Scale Platform Teams**:
   - Translates Big Tech distributed complexity (Spanner, Kafka, micro-meshes) into robust, cost-effective startup architectures (PostgreSQL, Redis, Caddy) for <$100/mo.

---

## 3. Product Requirements & Acceptance Criteria

### A. Invariant Dataset Synthesis
- [ ] Synthesize $\ge 500$ high-quality instruction-tuning pairs derived from the 20 Anti-Vibe Invariants (`rules/production_engineering_invariants.md`) and SRE resilience rules (`INV-RES-01` through `INV-RES-05`).
- [ ] Incorporate domain-specific scenarios across:
  - Financial Ledgers & Payments (double-entry, dynamic tax rates, idempotency).
  - High-Concurrency E-Commerce (atomic inventory locks, coupon stack limits).
  - Distributed Systems Resilience (panic floors, liveness decoupling, decorrelated jitter, warm-up ramps).
  - Multi-Tenant SaaS (tenant isolation, webhook HMAC verification).
  - AppSec & DevSecOps (parameterized SQL, DOMPurify XSS defense, zero frontend API keys).

### B. Modelfile System Prompt Optimization
- [ ] Encode the core invariant constraints and the Big Tech vs. Lean Startup translation mandate in under 1,024 tokens to maximize prompt cache efficiency.
- [ ] Rebuild `aryix/0rbt-architect` in local Ollama and verify runtime parameters (`temperature: 0.2`, `top_p: 0.9`, `num_ctx: 8192`).

### C. Automated Evaluation Harness
- [ ] Implement `bin/eval-architect-invariants.py` executing 20 deterministic architectural challenges.
- [ ] Require $\ge 90\%$ pass rate on detecting missing idempotency keys, unkeyed retries, liveness probe coupling, and tenant boundary leaks.

### D. Governance & Code Hygiene
- [ ] Zero dummy/placeholder names (`INV-06`).
- [ ] Zero cloud tokens ($0 tokens); all synthesis and evals run locally via Ollama.
- [ ] Strict two-axis and local code reviewer approval before merge.

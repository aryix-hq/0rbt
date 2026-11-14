# FEAT-003: Comprehensive AI-Agents 255 Skills & Red Team Suite Integration into aryix/0rbt-architect

> **Lifecycle Stage**: Stage 2 (Product Specification)  
> **Status**: APPROVED  
> **Target Version**: `v1.2.0`  
> **RICE Score**: 92.0 (Reach: 9 | Impact: 10 | Confidence: 8 | Effort: 7)  
> **Lead**: Principal Architect (`@architect`) & Principal Red Team Lead (`@red-team`)

---

## 1. Problem Statement

While `aryix/0rbt-architect` v1.1 successfully embedded 4,169 empirical engineering post-mortems and the 20 Anti-Vibe Production Invariants (SRE resilience, API idempotency, tenant scoping, SQL parameterization), it lacked direct instruction-tuning across the extensive catalog of **255 specialized skills in `ai-agents`**.

In particular, the model had blindspots in:
1. **Adversarial Red Team Tradecraft (60+ skills)**: Active exploitation vectors, container breakouts (`/var/run/docker.sock`, `SYS_ADMIN`), Kubernetes privilege escalation, AWS IAM `PassRole` chaining, Windows Active Directory attacks (Kerberoasting, DCSync, ADCS ESC1-ESC8), EDR evasion (SysWhispers indirect syscalls), and AI-specific exploits (prompt injection, RAG poisoning).
2. **Bug Hunter & Vulnerability Triage (35+ skills)**: The mandatory 7-Question Validation Gate, CVSS v3.1 mathematical scoring, Bugcrowd VRT mapping, and complex protocol desyncs (HTTP request smuggling CL.TE/TE.CL, web cache poisoning, race condition limit-overruns).
3. **Advanced Domain Systems & Media Engineering**: Chaos engineering blast-radius containment, server hardening with dynamic Vault credentials, WebXR spatial computing, and programmatic animation (Remotion, Manim, Blender).

By integrating the full 255 skills from `ai-agents`, `aryix/0rbt-architect` becomes a dual-hat powerhouse: an uncompromising **Principal Systems Architect** and an adversarial **Red Team Security Specialist** who can simultaneously design scalable systems and probe them for zero-day vulnerabilities.

---

## 2. Target Personas & Use Cases

1. **Staff Systems Architects & DevSecOps Leads**:
   - Reviews infrastructure proposals, cloud topologies, and container manifests against both scalability bottlenecks and container breakout paths.
2. **Red Team Operators & Bug Bounty Researchers**:
   - Queries `aryix/0rbt-architect` to model attack paths, generate non-destructive proof-of-concept scripts, compute exact CVSS vectors, and pass the 7-Question Validation Gate.
3. **Autonomous AI Coding Agents (Cursor, Claude Code, Cline, Windsurf)**:
   - Queries the local Ollama model (`aryix/0rbt-architect`) before generating scaffolding to catch both operational flaws (`INV-RES-03` thundering herds) and security flaws (`INV-SEC-02` BOLA, JWT none-algorithm, SSRF cloud metadata reachability).

---

## 3. Product Requirements & Acceptance Criteria

### A. Full 255 Skills Extraction & Dataset Synthesis
- [ ] Build `bin/synthesize-all-skills-dataset.py` to parse all 255 skills located in the active `ai-agents` skills repository.
- [ ] Cluster skills into 8 core architectural and operational domains:
  1. Offensive Red Team & Adversarial Tradecraft (60+ skills)
  2. Bug Hunter & Vulnerability Validation Gate (35+ skills)
  3. System & Distributed Systems Architecture (25+ skills)
  4. Engineering Management, Governance & Invariants (30+ skills)
  5. Creative Engineering, Media & Motion Synthesis (30+ skills)
  6. Search Intelligence & Technical SEO (20+ skills)
  7. Reconnaissance & OSINT Intelligence (15+ skills)
  8. Product Strategy, Growth & Enterprise Statecraft (35+ skills)
- [ ] Generate $\ge 1,000$ high-signal instruction-tuning pairs with authentic scenario prompts, attack mechanics/operational workflows, empirical precedents, and defensive fixes.
- [ ] Strictly enforce `INV-06` (Universal Dummy Name Ban) across all synthesized test fixtures, using realistic tech organizations and infrastructure entities.
- [ ] Merge synthesized pairs into `dataset/instruction_tuning_v1.jsonl`, expanding the dataset to $\ge 5,700$ total pairs.

### B. Modelfile Evolution: The Dual-Hat Architect & Red Team Model
- [ ] Upgrade `Modelfile` system prompt to embed:
  - The Big Tech vs. Lean Startup Translation Mandate.
  - The 20 Anti-Vibe Production Invariants & SRE Resilience.
  - The Adversarial Red Team & Exploitation Defense Doctrine.
  - The Bug Hunter 7-Question Validation Gate & CVSS Scoring.
  - The Standardized 4-Part Review Output Protocol.
- [ ] Keep the system instructions optimized for high prompt-cache efficiency (<1,500 tokens).
- [ ] Rebuild `aryix/0rbt-architect` in local Ollama via Apple Silicon Metal GPU at $0 cloud tokens.

### C. Evaluation & Verification Suite
- [ ] Expand `bin/eval-architect-invariants.py` with dedicated Red Team and Bug Hunter benchmark dilemmas (Container breakout, SSRF IMDSv2 defense, Deserialization defense, Prompt injection guardrails).
- [ ] Achieve $\ge 90\%$ pass rate across the comprehensive benchmark suite.
- [ ] Pass `./bin/audit-secrets.sh` (zero credentials, zero private paths).
- [ ] Pass `bin/local-code-reviewer.py --strict` with 0 blockers and 0 warnings.
- [ ] Pass `bin/two-axis-reviewer.py --base main` with APPROVED verdict.
- [ ] Push the updated model to Ollama Hub (`ollama push aryix/0rbt-architect`).

# PLAN-003: AI-Agents Skills & Anti-Vibe Invariants Integration into aryix/0rbt-architect

> **Lifecycle Stage**: Stage 3 (Phased Implementation Plan)  
> **Status**: APPROVED  
> **Target Branch**: `feat/skills-invariants-integration`  
> **Created**: 2026-11-14  
> **Model Identifier**: `aryix/0rbt-architect`  
> **Upstream Feature**: [`wiki/features/FEAT-002-AI-AGENTS-SKILLS-AND-INVARIANTS-INTEGRATION.md`](../features/FEAT-002-AI-AGENTS-SKILLS-AND-INVARIANTS-INTEGRATION.md)  
> **Planning Trio Sign-off**:
> - [x] Product Manager (`@product-manager`)
> - [x] System Architect (`@architect`)
> - [x] Technical Project Manager (`@project-manager`)

---

## 1. Executive Summary & Architecture Strategy

This plan governs the integration of `ai-agents` domain skills, the 20 Anti-Vibe Production Engineering Invariants, and SRE resilience doctrine (`INV-RES-01` to `INV-RES-05`) into `aryix/0rbt-architect`. By pairing empirical post-mortem knowledge from 2,065 engineering blogs with deterministic failure shields, `aryix/0rbt-architect` becomes an active defense engine against vibe-coded production outages.

---

## 2. Autoplan 4-Stage Review Gate Synthesis

### Stage 1: CEO Strategic Scoping Review (`@ceo`)
- **Scoping Mode**: `selective`
- **Core Value Proposition**: The premier open-source architect LLM that catches architecture flaws, race conditions, and scalability bottlenecks before code commit.
- **Scope Cuts**:
  - Excluded internal CLI orchestrator mechanics and machine paths to keep the dataset 100% universal.
  - Excluded UI animation / video production skills to maintain focus strictly on backend, distributed systems, security, and SRE architecture.

### Stage 2: Developer Ergonomics & Standardized Output (`@ui-ux`)
- Every architectural evaluation output from `aryix/0rbt-architect` must follow the standardized 4-part structure:
  1. **Verdict & Risk Severity**: `SAFE`, `FRAGILE`, or `SEV-1 OUTAGE RISK`.
  2. **Violated Production Invariants**: Explicit citing of violated rules (e.g., `INV-RES-03 Decorrelated Jitter`, `INV-SEC-09 Idempotency`).
  3. **Empirical Big Tech Outage Precedent**: Real-world precedent from Netflix, Stripe, AWS, or Cloudflare.
  4. **Hardened Production Code Fix**: Concrete, runnable Python/SQL/Go snippets with zero placeholder names.

### Stage 3: DevEx & Architecture Review (`@architect`)
- **Synthesis Engine**: Implement `bin/synthesize-skills-dataset.py` to extract rules and invariants into paired ChatML instruction datasets.
- **Prompt Token Budget**: Keep Modelfile system prompt $<1,024$ tokens for cache alignment under Anthropic and Ollama standards.
- **Dataset Expansion**: Append synthesized pairs to `dataset/instruction_tuning_v1.jsonl` (expanding from 2,065 to 2,600+ pairs).

### Stage 4: Engineering Manager & Living Milestones (`@engineering-manager`)
- **Definition of Done (DoD)**:
  1. `bin/synthesize-skills-dataset.py` runs with zero mocks and generates validated instruction pairs.
  2. `dataset/instruction_tuning_v1.jsonl` validated with zero syntax errors.
  3. `Modelfile` updated, rebuilt into `aryix/0rbt-architect`, and live verified via Ollama API.
  4. `bin/eval-architect-invariants.py` benchmark harness achieves $\ge 90\%$ detection rate across 20 test vectors.
  5. `local-code-reviewer.py --strict` and `two-axis-reviewer.py` pass with 0 blockers and 0 warnings.

---

## 3. Living Milestones & Work Breakdown Structure (WBS)

```
┌────────────────────────────────────────────────────────────────────────┐
│                   PLAN-003 EXECUTION WORKFLOW                          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┴───────────────────────────────┐
    ▼                                                               ▼
[Phase 1: Invariant Synthesis]                              [Phase 2: Modelfile Upgrade]
Extract 20 Anti-Vibe Invariants &                           Distill compact invariant constraints
SRE Resilience into ChatML pairs                            into prompt (<1,024 tokens)
    │                                                               │
    └───────────────────────────────┬───────────────────────────────┘
                                    │
                                    ▼
                        [Phase 3: Dataset Merge]
                        Combine blog corpus with invariants
                        into dataset/instruction_tuning_v1.jsonl
                                    │
                                    ▼
                        [Phase 4: Eval Harness]
                        Build bin/eval-architect-invariants.py
                        Verify >=90% detection score on live model
                                    │
                                    ▼
                        [Phase 5: Review & Publish]
                        Run two-axis review, push to GitHub,
                        and update Hugging Face documentation
```

### Phase Breakdown

| Phase | Milestone Description | Lead Agent | Target Deliverable |
| :---: | :--- | :--- | :--- |
| **Phase 1** | Invariant & Skills Dataset Synthesizer | `@fullstack-developer` | `bin/synthesize-skills-dataset.py` generating 500+ pairs |
| **Phase 2** | Modelfile System Prompt Upgrade | `@architect` | Updated `Modelfile` (<1,024 tokens), rebuilt Ollama model |
| **Phase 3** | Dataset Integration & Validation | `@documentation-manager` | Combined `dataset/instruction_tuning_v1.jsonl` (2,600+ pairs) |
| **Phase 4** | Invariant Benchmark Evaluation Suite | `@qa` | `bin/eval-architect-invariants.py` with 20 real test cases |
| **Phase 5** | Two-Axis Audit, Commit & Push | `@engineering-manager` | Pass all invariant linters, commit, and push |

---

## 4. Associated Living Artifacts
- **Feature Specification**: [`wiki/features/FEAT-002-AI-AGENTS-SKILLS-AND-INVARIANTS-INTEGRATION.md`](../features/FEAT-002-AI-AGENTS-SKILLS-AND-INVARIANTS-INTEGRATION.md)
- **Active Task Board**: [`wiki/TASK_BOARD.md`](../TASK_BOARD.md)
- **Knowledge Memory**: [`wiki/memory.md`](../memory.md)
- **Production Invariants**: [`.agents/rules/production_engineering_invariants.md`](../../.agents/rules/production_engineering_invariants.md)

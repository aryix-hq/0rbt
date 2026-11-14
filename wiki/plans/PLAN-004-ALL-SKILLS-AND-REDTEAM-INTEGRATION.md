# PLAN-004: Comprehensive AI-Agents 255 Skills & Red Team Suite Integration into aryix/0rbt-architect

> **Lifecycle Stage**: Stage 3 (Phased Implementation Plan)  
> **Status**: APPROVED  
> **Target Branch**: `feat/all-skills-redteam-integration`  
> **Created**: 2026-11-14  
> **Model Identifier**: `aryix/0rbt-architect`  
> **Upstream Feature**: [`wiki/features/FEAT-003-ALL-SKILLS-AND-REDTEAM-INTEGRATION.md`](../features/FEAT-003-ALL-SKILLS-AND-REDTEAM-INTEGRATION.md)  
> **Planning Trio Sign-off**:
> - [x] Product Manager (`@product-manager`)
> - [x] System Architect (`@architect`)
> - [x] Technical Project Manager (`@project-manager`)

---

## 1. Executive Summary & Architecture Strategy

This plan governs the end-to-end integration of all **255 skills from `ai-agents`** into `aryix/0rbt-architect`. By combining 4,169 empirical engineering post-mortems with 255 specialized skills across Red Team offensive security, Bug Hunter validation gates, SRE resilience, and creative code engineering, `aryix/0rbt-architect` evolves into the industry's first unified **Staff Systems Architect & Adversarial Red Team Lead**.

---

## 2. Autoplan 4-Stage Review Gate Synthesis

### Stage 1: CEO Strategic Scoping Review (`@ceo`)
- **Scoping Mode**: `selective`
- **Core Value Proposition**: A dual-hat model that does not merely design software architectures, but immediately red-teams them with the rigor of principal penetration testers and bug hunters.
- **Scope Directives**:
  - Ingest all 255 skill definitions from `ai-agents`.
  - Maintain the $0 cloud token mandate by synthesizing, training, and evaluating entirely via local Python engines and Apple Silicon Metal GPU.
  - Ban any fictional dummy names (`INV-06`). All test scenarios, fixtures, and PoCs must use domain-authentic realistic tech entities.

### Stage 2: Developer Ergonomics & Standardized Output (`@ui-ux`)
- The output structure from `aryix/0rbt-architect` must retain its crisp, standardized 4-part format:
  1. **Verdict & Risk Severity**: `SAFE`, `FRAGILE`, or `SEV-1 OUTAGE / EXPLOIT RISK`.
  2. **Violated Invariant / Attack Vector**: Explicit citation of violated production invariants (e.g. `INV-SEC-09`) or attack vectors (e.g. `Container Breakout via docker.sock`, `SSRF via IMDSv1`).
  3. **Empirical Big Tech Precedent**: Real-world outage or security breach precedent (Capital One SSRF, Tesla K8s cryptocurrency breakout, Cloudflare regex CPU exhaustion).
  4. **Hardened Production Code Fix**: Runnable, defensive code with zero placeholders.

### Stage 3: DevEx & Architecture Review (`@architect`)
- **Automated Skill Harvester (`bin/synthesize-all-skills-dataset.py`)**:
  - Dynamically reads all 255 `SKILL.md` documents.
  - Extracts operational steps, attack mechanisms, and defensive invariants.
  - Generates ChatML instruction pairs for each skill.
- **Prompt Token Budget**:
  - Keep `Modelfile` system prompt concise and structured to fit within Ollama's efficient context cache.
- **Dataset Expansion**:
  - Merge the synthesized skill pairs with the existing 4,719 pairs in `dataset/instruction_tuning_v1.jsonl`, surpassing 5,700 total pairs.

### Stage 4: Engineering Manager & Living Milestones (`@engineering-manager`)
- **Definition of Done (DoD)**:
  1. `bin/synthesize-all-skills-dataset.py` processes all 255 skills without runtime exceptions.
  2. `dataset/all_skills_instruction_dataset.jsonl` contains $\ge 1,000$ validated instruction pairs.
  3. `dataset/instruction_tuning_v1.jsonl` unified with $\ge 5,700$ total pairs.
  4. `Modelfile` upgraded with the Red Team and Bug Hunter doctrine and rebuilt into `aryix/0rbt-architect`.
  5. Expanded benchmark suite (`bin/eval-architect-invariants.py`) achieves $\ge 90\%$ pass rate across architectural and adversarial test vectors.
  6. Quality gates pass: `./bin/audit-secrets.sh`, `python3 bin/local-code-reviewer.py --strict`, `python3 bin/two-axis-reviewer.py --base main`.
  7. Updated model published to Ollama Hub (`ollama push aryix/0rbt-architect`).

---

## 3. Phased Implementation Milestones

- [ ] **Milestone 1: Automated 255-Skill Synthesizer Engine**
  - Implement `bin/synthesize-all-skills-dataset.py`.
  - Traverse all 255 folders in `~/.gemini/config/plugins/ai-agents/skills/`.
  - Generate $\ge 1,000$ instruction pairs adhering strictly to `INV-06`.

- [ ] **Milestone 2: Dataset Integration & Hygiene**
  - Export `dataset/all_skills_instruction_dataset.jsonl`.
  - Merge with `dataset/instruction_tuning_v1.jsonl` ($\ge 5,700$ total pairs).
  - Update `dataset/README.md` with the new skill clusters and counts.

- [ ] **Milestone 3: Modelfile Evolution & Local Ollama Rebuild**
  - Upgrade `Modelfile` system prompt to embed the Red Team & Bug Hunter doctrine.
  - Rebuild `aryix/0rbt-architect` locally on Metal GPU ($0 cloud tokens).

- [ ] **Milestone 4: Comprehensive Benchmark Suite & Live Evaluation**
  - Expand `bin/eval-architect-invariants.py` with Red Team test cases (Container breakouts, SSRF, Deserialization, Prompt injection).
  - Verify $\ge 90\%$ pass rate.

- [ ] **Milestone 5: Verification, Ollama Hub Release & Remote Push**
  - Run `./bin/audit-secrets.sh`, `bin/local-code-reviewer.py --strict`, and `bin/two-axis-reviewer.py`.
  - Push updated model to Ollama Hub (`https://ollama.com/aryix/0rbt-architect`).
  - Commit and push branch to GitHub.

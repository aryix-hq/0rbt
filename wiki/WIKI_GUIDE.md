# Project Wiki & Tracking Guide

> **Core Principle**: Zero Random Coding. Every line of code written in this repository must originate through the structured **4-Stage Product & Engineering Lifecycle** and map to a tracked record.

---

## 1. Wiki Directory Structure
```
wiki/
├── ARCHITECTURE.md       # Live system topology, components & ADRs (Maintained by @architect)
├── DATABASE_SCHEMA.md    # Live entity schemas, migrations & RLS (Maintained by @database-architect)
├── DEPLOYMENT.md         # Live container runbooks & preview deploy guide (Maintained by @devops-sre)
├── FAQS.md               # Live troubleshooting & operational FAQs (Maintained by @documentation-manager)
├── USER_GUIDE.md         # Live user flows, API usage & manuals (Maintained by @client-advocate & @pm)
├── TASK_BOARD.md         # Active Sprint & Kanban Status
├── research/             # Stage 1: Discovery briefs, user friction & spikes (RES-001.md...)
├── features/             # Stage 2: Feature specs with RICE scoring (FEAT-001.md...)
├── plans/                # Stage 3: Phased living implementation plans (PLAN-001.md...)
├── defects/              # Stage 4: Defect investigations & verification (DEF-001.md...)
├── incidents/            # Outage reports, 5-Whys post-mortems & timeline (INC-001.md...)
├── vulnerabilities/      # Security disclosures & CISO remediation proof (VULN-001.md...)
├── adr/                  # Architecture Decision Records (ADR-001.md...)
├── ops/                  # Infrastructure operational runbooks
└── templates/            # Standard templates for all records
```

---

## 2. The 4-Stage Product & Engineering Lifecycle

```
[ Stage 1: Research & Discovery ]
       │  (@research, @client-advocate, @architect -> wiki/research/RES-XXX.md)
       ▼
[ Stage 2: Product Scoping & RICE ]
       │  (@product-manager -> wiki/features/FEAT-XXX.md with RICE score)
       ▼
[ Stage 3: Phased Project Planning ]
       │  (Planning Trio -> wiki/plans/PLAN-XXX.md + living Architecture & DB Schema)
       ▼
[ Stage 4: Phased Execution & Gating ]
          (@fullstack-developer, @qa, @engineering-manager -> code, tests, defects, PR)
```

1. **Stage 1 (Research & Discovery)**:
   - Identify user pain points, domain constraints, client advocacy notes, and technical spikes.
   - Authored in `wiki/research/RES-XXX.md` using `wiki/templates/RESEARCH_NOTE.md`.
2. **Stage 2 (Product Requirements & RICE Prioritization)**:
   - Product Manager (`@product-manager`) translates research findings into feature requirements.
   - Features receive an explicit **RICE Score** ($R \times I \times C / E$) and testable User Acceptance Criteria (UAC).
   - Authored in `wiki/features/FEAT-XXX.md`.
3. **Stage 3 (Phased Project Planning)**:
   - The Planning Trio (`@product-manager`, `@architect`, `@project-manager`) breaks the feature into sequential phases.
   - `@project-manager` authors a phased Implementation Plan (`wiki/plans/PLAN-XXX.md`) tracking phase milestones live (`[PENDING]`, `[IN PROGRESS]`, `[COMPLETED]`).
   - Living Architecture (`wiki/ARCHITECTURE.md`) and Database Schema (`wiki/DATABASE_SCHEMA.md`) are updated with proposed contracts.
4. **Stage 4 (Phased Execution & Verification)**:
   - Developer creates branch `feat/FEAT-XXX`.
   - Implementation proceeds strictly phase by phase using local Ollama (`qwen2.5-coder:14b` via `bin/local-coder.sh`) at $0 tokens.
   - Zero-mock tests execute. Any regression is logged as a live defect record in `wiki/defects/DEF-XXX.md`.
   - Ephemeral preview build tested via `bin/deploy-preview.sh`.
   - Engineering Manager (`@engineering-manager`) reviews PR and grants merge approval.
   - Session context cleanly reset via `ai-agents session reset --feature FEAT-XXX`.

---

## 3. Public vs. Private Repository Disclosure Standard

When projects utilize public or open-source GitHub repositories, follow the **Tiered Disclosure Model**:

### 🟢 Public-Safe Artifacts (Committed to Git)
* **High-Level Architecture (`wiki/ARCHITECTURE.md`)**: C4 Level 1/2 conceptual diagrams, component topologies, and public API interfaces.
* **Guides & Runbooks (`USER_GUIDE.md`, `DEPLOYMENT.md`, `FAQS.md`)**: Developer onboarding, container setup, and CLI commands.
* **Keep a Changelog (`CHANGELOG.md`)**: Sanitized customer-facing summaries of releases.
* **Templates (`wiki/templates/`)**: Clean record blueprints.

### 🔴 Confidential Local Artifacts (Excluded via `.gitignore`)
To prevent zero-day vulnerability weaponization, attack surface mapping, and intellectual property leakage, the following files MUST be excluded from Git:
* **Active & Historical Defects (`wiki/defects/DEF-*.md`)**: Prevents exposing reproduction steps and unpatched flaws to attackers.
* **Security Disclosures (`wiki/vulnerabilities/VULN-*.md`, `wiki/incidents/INC-*.md`)**: Kept strictly internal.
* **Commercial Discovery & RICE Notes (`wiki/research/RES-*.md`)**: Protects competitive business strategy.
* **Detailed Production Relational Schemas**: Low-level database table definitions, RLS bypass internals, and connection credentials.
* **Local Agent Memory**: `.agents/memory/sessions/`, `.agents/memory/token_ledger.json`, and `.agents/mode`.

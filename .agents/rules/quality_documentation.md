# Quality, Documentation & Wiki Rules

1. **The 4-Stage Lifecycle & Living Document Progression**:
   - **Stage 1 (Research & Discovery)**: `@research` and `@client-advocate` document findings, user pain points, and technical spikes in `wiki/research/RES-XXX.md`.
   - **Stage 2 (Product Scoping & RICE)**: `@product-manager` ingests research and defines feature specs in `wiki/features/FEAT-XXX.md` with explicit RICE scores (Reach × Impact × Confidence / Effort).
   - **Stage 3 (Phased Project Planning)**: The Planning Trio (`@product-manager`, `@architect`, `@project-manager`) decomposes features into a phased living plan in `wiki/plans/PLAN-XXX.md`, while `@architect` updates `wiki/ARCHITECTURE.md` and `@database-architect` updates `wiki/DATABASE_SCHEMA.md`.
   - **Stage 4 (Phased Execution & Verification)**: Execution occurs strictly phase by phase. Implementation plan phase statuses (`[PENDING]`, `[IN PROGRESS]`, `[COMPLETED]`) and feature specs update live as phases deliver.

2. **Mandatory Live Documentation & 5 UML Invariants**:
   - Every project must maintain 5 living, renderable Mermaid UML diagrams:
     a. **System Topology (`flowchart TD`)** in `wiki/ARCHITECTURE.md`: Maintained by `@architect`.
     b. **Sequence & Data Flow (`sequenceDiagram`)** in `wiki/ARCHITECTURE.md` and feature plans: Maintained by `@architect`.
     c. **Entity-Relationship Model (`erDiagram`)** in `wiki/DATABASE_SCHEMA.md`: Maintained by `@database-architect`.
     d. **Class & Domain Hierarchy (`classDiagram`)** in `wiki/DOMAIN_MODELS.md`: Maintained by `@fullstack-developer`.
     e. **State Machines & Lifecycle (`stateDiagram-v2`)** in `wiki/STATE_MACHINES.md`: Maintained by `@architect`.
   - **Defects Ledger (`wiki/defects/DEF-XXX.md`)**: Maintained by `@qa`. Every test failure must be logged as a live defect record tracking status from `Open` to `Remediated`.
   - **Runbooks & Guides**: Deployment (`wiki/DEPLOYMENT.md`), FAQs (`wiki/FAQS.md`), and User Guide (`wiki/USER_GUIDE.md`).
   - Code changes lacking corresponding live diagram and doc updates will be rejected at the EM review gate.

3. **Zero-Token Local Documentation Invariant**:
   - All documentation drafting, phase status updates, wiki authoring, and defect logs MUST be executed via local Ollama (`bin/local-coder.sh` / `qwen2.5-coder:14b`) at $0 cloud tokens to preserve cloud context budgets and credits.

4. **Changelog Integrity**:
   - Every merged PR must update `CHANGELOG.md` following Keep a Changelog standards (`Added`, `Changed`, `Fixed`, `Security`).

5. **Zero-Mock Verification Mandate**:
   - All tests must execute against real containers or isolated test instances. Never mock database queries or auth tokens.

6. **Public vs. Private Repository Classification Standard**:
   - High-level C4 conceptual diagrams, sanitized schemas, user guides, and sanitized `CHANGELOG.md` notes belong in public Git repositories.
   - Raw defect ledgers (`wiki/defects/DEF-*.md`), zero-day incidents (`wiki/incidents/INC-*.md`), vulnerability reports (`wiki/vulnerabilities/VULN-*.md`), commercial discovery notes (`wiki/research/RES-*.md`), and local session memory (`.agents/memory/sessions/`, `token_ledger.json`) MUST be gitignored to prevent zero-day exploit disclosure, attack surface mapping, and commercial IP leakage.

7. **Mandatory Project-Scoped Document Numbering Protocol (`INV-DOC-04`)**:
   - Every document in `wiki/` (`RES-XXX`, `FEAT-XXX`, `PLAN-XXX`, `DEF-XXX`, `INC-XXX`, `ADR-XXX`, `VULN-XXX`) must have its identifier computed strictly from the active repository's filesystem.
   - Run `ai-agents next-id <type>` (or `bin/doc-numberer.py next <type>`) before creating any document.
   - Never inherit, assume, or carry over document numbers from other projects, global templates, or conversational context. Next ID = max(existing) + 1 (or 001 if directory is empty).
   - Pre-push review gate `INV-DOC-04` blocks any PR introducing numeric jumps > 3 over the repository max.

# Adversarial Lifecycle Integration Rules

1. **Stage 1 (Research & Threat Modeling)**:
   - For all features touching external inputs, authentication, database persistence, or IPC networks, `@appsec` and `@ciso` must conduct a STRIDE threat assessment documented in `wiki/research/RES-*.md` or `wiki/research/THREAT-*.md`.
   - Identify threat vectors (MITRE ATT&CK classifications) and define required defensive mitigations before feature approval.

2. **Stage 2 (Product Specifications & Security Criteria)**:
   - `@product-manager` must include explicit adversarial acceptance criteria in `wiki/features/FEAT-*.md` (e.g., "Must reject malformed JWTs", "Must enforce tenant ID isolation across all multi-tenant queries", "Must resist SSRF against 169.254.169.254").

3. **Stage 3 (Planning & Penetration Gates)**:
   - Planning Trio (`@architect`, `@fullstack-developer`, `@qa`) must incorporate an explicit adversarial verification milestone in `wiki/plans/PLAN-*.md` prior to the Definition of Done (DoD).
   - Reserve local execution cycles (`jimscard/whiterabbit-neo` or `deepseek-coder-v2:16b`) for exploit validation tests.

4. **Stage 4 (Execution, Verification & Hardening)**:
   - **Adversarial Emulation**: `@red-team` or `@appsec` drafts and executes non-destructive test scripts reproducing identified attack vectors against preview containers.
   - **Remediation**: If an exploit succeeds, `@fullstack-developer` implements defensive patches immediately.
   - **Defect Logging**: Any unmitigated vulnerability is logged to `wiki/defects/DEF-*.md` with severity and CVSS estimates.
   - **Regression Gate**: `@qa` incorporates verified exploit proofs as automated zero-mock regression tests before PR approval from the Engineering Manager.


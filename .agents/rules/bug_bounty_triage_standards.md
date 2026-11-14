# Bug Bounty Triage & Vulnerability Verification Standards

1. **The Mandatory 7-Question Validation Gate**:
   - Every security finding submitted by `@bug-hunter` or engineering subagents must pass all 7 criteria before filing:
     1. **Asset & Endpoint**: Exact FQDN, URI path, HTTP verb, and vulnerable parameter or header.
     2. **VRT/CWE Taxonomy**: Precise mapping to Bugcrowd/HackerOne VRT category and CWE ID.
     3. **Root Cause**: Specific software defect (e.g., missing input sanitization, broken access control, prototype pollution).
     4. **Deterministic Non-Destructive PoC**: Repeatable curl command or script with zero destructive side-effects.
     5. **Realistic Business Impact**: Actual worst-case compromise scenario without speculative theoretical escalation.
     6. **CVSS v3.1 Scoring**: Complete vector string (AV/AC/PR/UI/S/C/I/A) without score inflation.
     7. **Defensive Remediation Diff**: Concrete code-level patch fixing the vulnerability at the source.
   - Any finding failing a single criterion is flagged as an unverified draft or discarded as a false positive.

2. **Non-Destructive Proof-of-Concept Mandate**:
   - Exploit verification must remain strictly non-destructive:
     - Use benign math evaluations for injection verification (e.g., `{{7*7}}=49`).
     - Use harmless benign canaries (`whoami`, `id`, `echo test`) rather than intrusive payloads.
     - For IDOR/BOLA, test only across authorized dual test accounts controlled by the audit harness; never access, modify, or delete real third-party tenant records.
     - Never execute denial-of-service loops, memory exhaustion, or database drops.

3. **VRT Taxonomy & CVSS Realism**:
   - Align severity strictly with industry standard definitions (P1 Critical through P5 Informational).
   - Base metrics must reflect realistic access prerequisites (e.g., if an attack requires administrative credentials, `PR:H` must be specified).
   - Invariants apply across all target microservices and external perimeter audits.


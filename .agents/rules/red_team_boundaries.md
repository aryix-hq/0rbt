# Red Team Boundaries & Authorized Scope Rules

1. **Strict Scope Authorization**:
   - All offensive security operations, penetration testing, and exploit simulations must operate strictly within user-authorized boundaries: local Docker preview containers, mock servers, loopback addresses (`127.0.0.1`), or explicitly approved staging environments.
   - Probing, port-scanning, fuzzing, or exploiting any third-party, client-production, or unauthorized external infrastructure is strictly prohibited.
   - If a target endpoint or domain is ambiguous, execution must halt and require explicit operator confirmation before firing payloads.

2. **Non-Destructive Principle**:
   - Exploitation proofs must employ minimal, non-destructive indicators:
     - Arbitrary Command Execution: Execute safe telemetry queries (e.g., `id`, `whoami`, `uname -a`, or creating timestamped `/tmp/canary_*.txt`).
     - SQL Injection: Use benign schema introspection (`SELECT 1`, `version()`) or non-destructive boolean/sleep probes. Never drop, truncate, or overwrite database tables.
     - File Upload / Path Traversal: Read benign metadata (`/etc/issue`, non-sensitive configs) or upload inert non-executable marker files.
     - Low-Level & Memory Corruption: Stop at crash verification or control-flow redirect to dummy canary targets (`ret2win` test stubs). Never release persistent rootkits or kernel panic payloads.

3. **Credential & Secret Sanitization**:
   - Any discovered credentials, session cookies, private keys, or API tokens extracted during testing must be immediately redacted with `[REDACTED_SECRET]` before printing to logs, transcripts, or git commits.
   - Discoveries must be reported directly to `@ciso` and documented as remediation tickets in `wiki/defects/DEF-*.md`.

4. **Transient Test Artifacts**:
   - Every script, payload binary, temporary FIFO, or test user account created during adversarial testing must be purged upon test conclusion.
   - Ensure `bin/audit-secrets.sh` runs post-test to verify zero remnant secrets in the tree.


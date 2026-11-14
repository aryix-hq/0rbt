# Git Workflow & Pull Request Rules

1. **Branch Protection Policy**:
   - Committing directly to `main` (or `master`) is strictly prohibited.
   - All work must be developed on branches: `feat/<ticket-id>`, `fix/<ticket-id>`, or `refactor/<ticket-id>`.

2. **Pull Request Protocol**:
   - Every code modification requires an open Pull Request targeting `main`.
   - The Pull Request must fill out the standard `PULL_REQUEST_TEMPLATE.md`.
   - Every PR must link directly to an existing Wiki Feature Spec or Defect Record.

3. **Engineering Manager (EM) Approval Gate**:
   - Merging is blocked without explicit sign-off from the **Engineering Manager**.
   - EM verification checklist:
     - Automated test suite passes on isolated Staging / QA environment (`bin/deploy-staging.sh --qa --test-and-exit`). Zero testing against production.
     - Architecture conforms to System Architect specifications and stateless microservices contracts.
     - **Anti-Vibe Code Review Verification**: Run `bin/local-code-reviewer.py --strict --llm` confirming 0 Blockers across all 12 Anti-Vibe Invariants (zero synthetic mocks, zero magic tax numbers, zero `/ 4` splits, zero blind defaults, zero fake compliance stubs).
     - **Anti-Slop UI Verification (if frontend changes)**: Confirmed 5-Pass De-slopping Protocol (zero purple AI gradients, zero buzzword copy, zero arbitrary magic CSS, and 100% event handler/route preservation).
     - Security, PII, and secret sanitization confirmed by DevSecOps / CISO.
     - Documentation updated (`CHANGELOG.md` and Wiki).

4. **Commit Standards**:
   - Use conventional commit messages: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`.
   - Rebase cleanly against latest `main` before merge.

5. **Local Git Operations via Ollama**:
   - Conventional commit messages, diff summaries, branch naming, and PR descriptions must be generated locally using `local-git.sh` / Ollama at $0 cloud tokens.

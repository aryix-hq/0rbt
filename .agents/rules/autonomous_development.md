# Autonomous Development & Self-Healing Invariants

1. **Autonomous "Loop Until Green" Rule**:
   - Execution occurs strictly phase by phase according to `wiki/plans/PLAN-XXX.md`. Development never commences without a RICE-prioritized feature spec (`wiki/features/FEAT-XXX.md`) and approved phased plan.
   - When implementing features or bug fixes, the developer agent MUST execute local tests, linters, or typecheckers (`npm test`, `pytest`, `cargo test`, `tsc --noEmit`).
   - If execution fails (exit code != 0), the agent MUST parse stderr, isolate the root cause, apply targeted diffs, and re-execute autonomously until all tests pass.
   - Never prompt the user to manually resolve compiler, linter, or test failures that the agent can execute and fix.

2. **Zero-Token Local Offloading & Command Execution**:
   - The user must never be forced to manually tag agents or specify model names.
   - Upon plan approval or code requests, the agent MUST automatically invoke the local Ollama worker (`local-coder.sh` with `qwen2.5-coder:14b`) behind the scenes to draft code, unit tests, and regex at $0 / 0 cloud tokens.
   - All Git operations (commit messages, PR descriptions) and shell command generation/execution MUST route through local Ollama (`local-git.sh` / `local-cmd.sh`).
   - **Sandbox Execution Mandate**: Local workers connect to loopback `127.0.0.1:11434`, and git write operations modify `.git/`. In Antigravity, the agent MUST execute them with `BypassSandbox: true` so loopback network is not blocked. Never fall back to cloud models due to sandbox isolation errors.
   - Cloud models (Gemini Flash/Pro) are reserved strictly for high-level plan formulation, multi-file orchestration, and CISO security reviews.

3. **Deterministic Memory & Automated Fresh Sessions**:
   - Do not rely on bloated conversation transcripts. System state, API schemas, and ADRs must be written immediately to `wiki/` and `.agents/memory/memory_graph.json`.
   - The agent MUST autonomously trigger `ai-agents session reset --auto` upon completing ticket verification. Never prompt the user to run manual reset scripts.

4. **Hermetic Branch Preview Gate**:
   - All code changes must originate on feature branches (`feat/*`) and execute `./bin/deploy-preview.sh <branch> <port> --test-and-exit`.
   - Production container ports and preview container ports must remain isolated. Merges to `main` require explicit `@engineering-manager` approval.

5. **Evidence-Backed Binary & Dependency Analysis**:
   - When analyzing closed-source binaries, minified JavaScript, or native libraries, agents MUST invoke REA MCP tools (`rea_*`) rather than hallucinating internal implementation details.


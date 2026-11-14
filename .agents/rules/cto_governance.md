# CTO Technology Strategy & Stack Governance Rules

1. **Technology Stack Standardization**:
   - Any introduction of a new language, framework, database engine, or external SaaS platform must be formally proposed by `@cto` and debated via `@orchestrator-debate`.
   - Prevent fragmentation: competing libraries for identical tasks (e.g., multiple ORMs or HTTP clients) are strictly prohibited.

2. **Zero-Token Local-First Imperative**:
   - Direct engineering workflows toward local Ollama models (`qwen2.5-coder:32b`, `deepseek-r1:14b`) to protect proprietary intellectual property and conserve cloud budgets.
   - Restrict cloud reasoning passes strictly to `@architect` and `@ciso` evaluation gates.

3. **Engineering Excellence & Health Gates**:
   - All code must pass local preview verification (`bin/deploy-preview.sh`) with zero-mock tests before merging into `main`.
   - Code changes that introduce architectural shortcuts or unaddressed technical debt without a tracked remediation ticket will be vetoed.

4. **Continuous Live Documentation**:
   - The CTO mandates that `@architect`, `@database-architect`, and `@devops-sre` maintain live specifications (`wiki/ARCHITECTURE.md`, `wiki/DATABASE_SCHEMA.md`, `wiki/DEPLOYMENT.md`) synchronized with every merged pull request.


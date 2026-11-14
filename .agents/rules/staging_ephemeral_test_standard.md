# Mandatory Ephemeral Staging Lifecycle & Protected Production Standard

> **Custodian**: `@engineering-manager`, `@devops-sre`, `@qa`  
> **Authority**: Non-negotiable project-wide hard rule (`rules/AGENTS.md` Rule 5)  
> **Scope**: All microservices, frontend applications, and database pipelines.

---

## 1. The Core Invariant: Zero Test or Seed on Production

1. **Absolute Ban on Production Testing**:
   - Automated test runners (`pytest`, `jest`, `playwright`, `vitest`, `k6`), seed scripts, and fixture injections are **strictly forbidden** from targeting production domains, clusters, or production database instances.
   - Any script, pipeline step, or command that attempts to run tests or inject test data against a production environment (`NODE_ENV=production`, `ENV=prod`, `PROD_DB`) is automatically intercepted and terminated with a non-zero exit code (`INV-ENV-01`).

2. **Zero Synthetic / Mock Data in Production Databases**:
   - Production databases receive only schema migrations and legitimate operational records. Fictitious test entities, synthetic seed users, or dummy mock rows are prohibited in production databases.

---

## 2. The 5-Phase Ephemeral Staging Lifecycle

Whenever ANY testing is conducted, or ANY seed data is added, it must execute within a temporary, isolated staging environment that follows the deterministic 5-phase lifecycle:

```
[Phase 1: Start]    Spin up dedicated staging container & isolated database schema
       ↓
[Phase 2: Seed]     Inject domain-authentic test fixtures (zero dummy/Acme names)
       ↓
[Phase 3: Test]     Execute complete zero-mock regression & contract test suite
       ↓
[Phase 4: Attest]   Generate cryptographically signed Staging Attestation Certificate
       ↓
[Phase 5: Delete]   Destroy, drop, and delete the staging container & test database
```

### Phase 1: Start Ephemeral Staging
Spin up an isolated staging container with isolated port allocation and dedicated database schema:
```bash
./bin/deploy-staging.sh --ephemeral [branch-name] [port]
```

### Phase 2: Domain-Authentic Seeding
Inject realistic test fixtures adhering to the **Authentic Domain Entity Standard** (zero `Acme Corp`, `John Doe`, or `test product` names). Seeds must represent genuine business operations (e.g. `Vanguard Logistics Ltd`, `Meridian Health Systems`).

### Phase 3: Zero-Mock Test Execution
Execute automated integration tests, boundary verifications, and API contract suites against the ephemeral staging URL:
```bash
STAGING_URL=http://127.0.0.1:[port] pytest tests/integration/ -v
```

### Phase 4: Staging Attestation Signing
Upon 100% test pass rate, the staging pipeline automatically generates a signed attestation certificate:
```json
{
  "attestation_id": "STG-ATTEST-20261108-ABCD1234",
  "timestamp": "2026-11-08T10:38:00Z",
  "branch": "feat/my-feature",
  "commit_sha": "a1b2c3d4e5f6...",
  "test_results": {
    "total_tests": 68,
    "passed": 68,
    "failed": 0
  },
  "ephemeral_staging_port": 8089,
  "status": "VERIFIED_READY_FOR_PROD"
}
```
Exported to `.agents/deploy/STAGING_ATTESTATION.json`.

### Phase 5: Mandatory Destruction & Deletion
Immediately following test completion, the staging container, volume bindings, and test database **must be destroyed**:
```bash
# Automated via --ephemeral flag
docker rm -f [staging-container-id]
docker volume prune -f
```
Zero orphaned containers, zero open test ports, zero lingering test databases.

---

## 3. Protected Production Gate (`bin/deploy-prod.sh`)

Deploying to production requires meeting three non-negotiable gates:
1. **Fresh Staging Attestation**: A valid `.agents/deploy/STAGING_ATTESTATION.json` generated $< 1\text{ hour}$ ago with 100% test pass rate.
2. **Zero Test / Seed Execution**: The production deployment script strictly prohibits running any test suite or database seed script.
3. **Engineering Manager Sign-Off**: Explicit review verification that main branch invariants (`INV-01` through `INV-DOM-04`) are clean.

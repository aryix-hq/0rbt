# Branch Preview, Staging & QA Deployment Rules

1. **Production Isolation Mandate (Never Touch Prod)**:
   - Production (`prod`) is strictly protected and untouchable by automated test runs, preview scripts, or pull requests.
   - All pre-merge verification and automated testing must execute in dedicated **Staging (`--env staging`)** or **QA (`--env qa`)** environments.
   - Any script targeting `prod` directly is automatically blocked and redirected to `staging`. Production updates occur exclusively via verified, EM-approved semantic releases (`bin/release.sh`).

2. **Automated Staging & QA Deployment Pipeline (`bin/deploy-staging.sh`)**:
   - Before submitting a PR or cutting a release, verify in isolated staging or QA:
     - QA test verification: `./bin/deploy-staging.sh --qa --test-and-exit`
     - Pre-production staging: `./bin/deploy-staging.sh --staging [branch-name] [port]`
   - The pipeline performs:
     1. Syntax checks and strict type verification (`tsc --noEmit`, `node --check`, or `python -m py_compile`).
     2. DevSecOps secret scanning and dependency vulnerability gates.
     3. Ephemeral Staging/QA container spin-up with synthetic test seeds (isolated from prod DB).
     4. Live healthcheck validation on Staging/QA HTTP endpoints.
     5. End-to-end integration and boundary testing.
     6. Automatic teardown for QA test runs or persistent preview URL for staging.

3. **Deployment Failure Enforcement**:
   - Any failure during staging or QA build/test halts the deployment pipeline immediately.
   - PR merge is blocked until staging/QA deployment passes cleanly with zero warnings.

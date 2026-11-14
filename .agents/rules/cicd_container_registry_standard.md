# CI/CD Docker Container Build & GHCR Publishing Standard

> **Custodian**: `@devops-sre`, `@devsecops`, `@engineering-manager`  
> **Registry Standard**: GitHub Container Registry (`ghcr.io`)  
> **Scope**: All software repositories, microservices, and client projects maintained or initialized by `ai-agents`.

---

## 1. Architectural Mandate

Every project under autonomous engineering governance must implement an automated Continuous Integration & Continuous Delivery (CI/CD) pipeline that builds Docker container images and publishes them to the **GitHub Container Registry (`ghcr.io`)**.

Manual container builds, local unversioned image pushes, or publishing to unverified ad-hoc registries are strictly prohibited.

---

## 2. Registry Configuration & Authentication

1. **Registry Endpoint**:
   - Host: `ghcr.io`
   - Repository Namespace: `ghcr.io/${{ github.repository_owner }}/${{ github.repository }}` (all lowercase).
2. **Zero External Secrets**:
   - Authentication must use GitHub Actions native token: `${{ secrets.GITHUB_TOKEN }}`.
   - External registry accounts (Docker Hub, AWS ECR, GCP Artifact Registry) must not be used unless explicitly mandated by enterprise multi-cloud policy.
3. **Workflow Permissions**:
   - The workflow file must explicitly grant write access to packages:
     ```yaml
     permissions:
       contents: read
       packages: write
       security-events: write  # for Trivy SARIF reporting
     ```

---

## 3. Image Tagging Taxonomy

Images published to GHCR must strictly adhere to the following deterministic tag taxonomy:

| Git Event | Trigger Condition | Published Docker Image Tags | Purpose |
| :--- | :--- | :--- | :--- |
| **Pull Request** | PR opened / synchronized | `pr-<PR_NUMBER>` (optional / internal only) | Pre-merge verification & ephemeral preview testing |
| **Merge to Main** | Push to `main` branch | `latest`<br>`sha-<7_CHAR_COMMIT_SHA>` | Production deployment & immutable rollback target |
| **Semantic Release** | Git tag `vX.Y.Z` created | `X.Y.Z` (exact)<br>`X.Y` (floating minor)<br>`X` (floating major) | Formal versioned customer / partner releases |

---

## 4. Build Performance & Caching Invariants

1. **GitHub Actions Cache (`type=gha`)**:
   - All builds must configure Buildx layer caching:
     ```yaml
     cache-from: type=gha
     cache-to: type=gha,mode=max
     ```
   - Target incremental build duration: $< 90\text{ seconds}$.
2. **Strict `.dockerignore`**:
   - Every project must include a `.dockerignore` file at root level excluding:
     - `.git/`
     - `.agents/memory/*.db` (vector store and sqlite artifacts)
     - `node_modules/`, `venv/`, `__pycache__/`, `.pytest_cache/`
     - `.env*`, `*.pem`, `*.key` (credential leakage prevention)
     - `tmp/`, `coverage/`, `dist/`

---

## 5. DevSecOps Security Gate (Trivy Scan)

1. **Automated Vulnerability Scanning**:
   - Built container images must be scanned with Aquasecurity Trivy in the CI/CD pipeline before promotion.
2. **Severity Thresholds**:
   - Vulnerabilities classified as `CRITICAL` without an available upstream fix must be triaged via an exemption record or fail the build.
3. **SARIF Export**:
   - Scan findings must be uploaded to GitHub Advanced Security / Security tab via `github/codeql-action/upload-sarif`.

---

## 6. Staging-Only Verification Gate (Never Touch Prod)

1. **Mandatory Staging Testing**:
   - Automated testing suites, integration tests, contract verification, and DAST scans within the CI/CD pipeline must execute strictly against an isolated Staging or QA container environment (`bin/deploy-staging.sh --qa --test-and-exit`).
2. **Production Immunity Invariant**:
   - The CI/CD pipeline and automated agent test runners are strictly blocked from connecting to production endpoints, production secrets, or live production databases. Testing never touches production.
3. **Image Promotion Gate**:
   - Promotion of container images to production tags or releases requires 100% green verification on the staging container build.

---

## 7. Project Scaffolding Invariant

When `ai-agents init-project [DIR]` or `ai-agents ci init` runs, it must verify and deploy:
1. `.github/workflows/docker-publish.yml`
2. `.dockerignore`
3. `Dockerfile` (scaffolded if missing)
4. `bin/deploy-staging.sh` and `bin/deploy-preview.sh`

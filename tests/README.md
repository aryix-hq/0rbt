# Automated Test Harnesses Domain (`tests`)

> **Package / Component**: Zero-Mock Automated Regression & Invariant Verification Suite  
> **Contract Standard**: Peanuts & Hay Leaf Contract (`INV-DOC-02`)  
> **Status**: Active  

---

## 1. Domain Responsibility
The `tests/` package maintains executable zero-mock test suites for the repository. It verifies:
1. Continuous engineering blog feed registry schema and HTTPS compliance (`INV-CFG-01`, `INV-CFG-02`).
2. Canonical URL normalization and deterministic SHA-256 deduplication hashing (`INV-BLOG-01`).
3. Substance gate filtering (`INV-BLOG-02`).
4. Syntactic n8n workflow canvas validity and zero plaintext secrets (`INV-N8N-01`).
5. 4-Dimensional AI Synthesis JSON schema conformance (`INV-BLOG-03`).

---

## 2. Exported Test Suites
- `test_blog_pipeline.py`: Comprehensive test runner executing all 5 pipeline verification suites.

---

## 3. Enforced Invariants
- **`INV-TEST-01` (Zero-Mock Coverage)**: All newly added application packages must maintain automated test coverage executing with 100% pass rates before PR merge.
- **`INV-ENV-01` (Zero Production Testing)**: Tests are strictly forbidden from running against production environments.

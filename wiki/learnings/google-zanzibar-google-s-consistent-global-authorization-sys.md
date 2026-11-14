# Google: Zanzibar: Google's Consistent Global Authorization System at Scale

> **Organization**: Google  
> **Domain**: Access Control & Global Security  
> **Published**: 2021-05-15  
> **Source URL**: [https://research.google/pubs/pub48190/](https://research.google/pubs/pub48190/)  
> **Pattern**: `Relationship-Based Access Control (ReBAC) with TrueTime Consistency`  

---

## 1. Problem Statement & Operational Dilemma
Managing authorization checks across Google Docs, Drive, YouTube, and Cloud at 10 million QPS across billions of objects while preventing the 'New Enemy' stale permission bug.

---

## 2. Production Architecture & Solution Breakdown
Created Zanzibar, a global relationship-based authorization engine. Expresses permissions as tuple relationships (`object#relation@user`). Uses Google Spanner TrueTime to issue cryptographic consistency tokens (zookies), ensuring authorization decisions respect causal ordering.

### Enforced Invariants
- `INV-AUTH-01: Revocation of permissions must be immediately respected globally (no stale grants)`
- `INV-AUTH-02: Authorization latency must evaluate in under 10ms at p95 across distributed data centers`

### Trade-offs & Operational Costs
Requires globally synchronized hardware atomic clocks (TrueTime) and complex graph traversal algorithms.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Implementing full Zanzibar ReBAC for applications with fewer than 100,000 users causes immense architecture bloat.
- **Pragmatic Small-Scale Architecture**: Use PostgreSQL Role-Based Access Control (RBAC) with indexed role tables and JWT claims verified at the API gateway.
- **Estimated Savings**: $15,000/mo in distributed authorization microservice infrastructure

### Actionable Implementation Checklist
1. Define explicit roles (admin, editor, viewer)
1. Enforce role checks in API middleware
1. Index (tenant_id, user_id, role) in Postgres

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-SEC-05: All API routes must enforce explicit authorization guards and reject unauthorized actors`

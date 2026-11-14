# Meta: Scaling Memcached at Facebook: Leases, Cold Cache Warmers and Pools

> **Organization**: Meta  
> **Domain**: Caching & High-Throughput Storage  
> **Published**: 2021-04-12  
> **Source URL**: [https://engineering.fb.com/2021/04/12/core-infra/scaling-memcached-at-facebook/](https://engineering.fb.com/2021/04/12/core-infra/scaling-memcached-at-facebook/)  
> **Pattern**: `Distributed Cache Lease Allocation & Thundering Herd Defense`  

---

## 1. Problem Statement & Operational Dilemma
Handling billions of cache requests per second caused severe 'Thundering Herd' events when popular cache keys expired, crashing downstream MySQL database clusters under concurrent read spikes.

---

## 2. Production Architecture & Solution Breakdown
Invented Memcached Leases. When a cache miss occurs, the cache assigns a 64-bit lease token to a single client, giving it 10 seconds to compute and write the value. Subsequent clients are instructed to wait or return slightly stale data, preventing database stampedes.

### Enforced Invariants
- `INV-CACHE-03: Exactly one client recomputes an expired cache key; concurrent clients wait or receive stale data`
- `INV-CACHE-04: Cache writes must verify lease tokens to prevent stale set race conditions`

### Trade-offs & Operational Costs
Slight staleness tolerated for read queries during cache refill windows.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Deploying custom memcached C++ forks across thousands of servers is unfeasible for small teams.
- **Pragmatic Small-Scale Architecture**: Use Redis with distributed locks (`SET key val NX EX 10`) or singleflight pattern in Go/Python.
- **Estimated Savings**: $7,000/mo in database over-provisioning costs

### Actionable Implementation Checklist
1. Implement Redis SETNX with TTL for cache recomputation
1. Return cached stale value if recomputation is in flight
1. Add jitter to cache TTLs

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-RES-03: All caching layers must enforce jittered expiration TTLs to eliminate thundering herd stampedes`

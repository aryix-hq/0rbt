# Shopify: Shopify Pod Architecture: Resilient Flash Sales and Blast Radius Isolation

> **Organization**: Shopify  
> **Domain**: Multi-Tenant Architecture & Resilience  
> **Published**: 2023-11-20  
> **Source URL**: [https://shopify.engineering/pod-architecture-flash-sales](https://shopify.engineering/pod-architecture-flash-sales)  
> **Pattern**: `Cellular Multi-Tenant Sharding (Pod Isolation)`  

---

## 1. Problem Statement & Operational Dilemma
Massive Black Friday flash sales from mega-merchants generated traffic spikes of 100x baseline, threatening to saturate shared databases and crash uninvolved merchants.

---

## 2. Production Architecture & Solution Breakdown
Partitioned Shopify's infrastructure into self-contained, fully independent 'Pods'. Each pod contains its own compute nodes, MySQL shards, and Redis instances. Merchants are assigned to specific pods; an outage in one pod affects only a tiny fraction of merchants.

### Enforced Invariants
- `INV-CELL-01: Pods share zero runtime database or cache state (zero cross-pod coupling)`
- `INV-CELL-02: Ingress routing router must be stateless and route purely on tenant identifier`

### Trade-offs & Operational Costs
Cross-pod data aggregation (analytics, global search) requires asynchronous change-data-capture pipelines.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Building cellular pod routing and multi-region sharded databases requires dozens of platform engineers.
- **Pragmatic Small-Scale Architecture**: Enforce PostgreSQL Row-Level Security (RLS) with tenant_id indexes and set tenant query rate-limits in Redis.
- **Estimated Savings**: $25,000/mo in infrastructure and multi-cluster orchestration overhead

### Actionable Implementation Checklist
1. Add tenant_id to all tables
1. Enable Postgres Row Level Security (RLS)
1. Add composite indexes (tenant_id, id)

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-RES-02: Tenant architectures must enforce strict blast radius boundaries with cellular isolation`

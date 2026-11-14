# GitHub: GitHub's MySQL High Availability at Scale: Zero Split-Brain with Orchestrator

> **Organization**: GitHub  
> **Domain**: Database Reliability & High Availability  
> **Published**: 2021-06-10  
> **Source URL**: [https://github.blog/engineering/platform-security/github-mysql-high-availability-orchestrator](https://github.blog/engineering/platform-security/github-mysql-high-availability-orchestrator)  
> **Pattern**: `Raft-Coordinated Automated Database Topology Manager & Failover`  

---

## 1. Problem Statement & Operational Dilemma
Unplanned primary database hardware crashes caused service outages and risked split-brain data corruption when multiple nodes claimed primary write status simultaneously.

---

## 2. Production Architecture & Solution Breakdown
Deployed Orchestrator with Raft consensus across three independent availability zones. Enforced semi-synchronous replication (lossless semantics), automated VIP re-pointing via Consul, and mandatory fencing/stonith scripts to isolate failed primaries.

### Enforced Invariants
- `INV-DB-01: Exactly one primary node accepts writes; split-brain strictly prevented via Raft quorum`
- `INV-DB-02: Lossless semi-synchronous replication guarantees zero uncommitted data loss upon failover`

### Trade-offs & Operational Costs
Slightly increased write latency due to semi-synchronous network round-trip acknowledgments.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Managing custom Raft consensus clusters, Consul healthchecks, and Orchestrator daemons for small databases is prone to human error.
- **Pragmatic Small-Scale Architecture**: Use managed PostgreSQL with automatic multi-AZ failover (Amazon RDS, Google Cloud SQL, or Neon) with read replicas.
- **Estimated Savings**: $12,000/mo in dedicated DBA and distributed consensus infrastructure costs

### Actionable Implementation Checklist
1. Enable Multi-AZ replication on managed Postgres
1. Configure client connection pool retry with backoff
1. Set statement_timeout to 5s

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-RES-01: High-availability topology engines must enforce Raft quorum before promoting replacement primaries`

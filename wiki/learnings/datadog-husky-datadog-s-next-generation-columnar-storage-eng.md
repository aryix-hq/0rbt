# Datadog: Husky: Datadog's Next-Generation Columnar Storage Engine for Metrics

> **Organization**: Datadog  
> **Domain**: Telemetry & Columnar Data Storage  
> **Published**: 2023-08-22  
> **Source URL**: [https://www.datadoghq.com/blog/engineering/husky-datadog-columnar-storage-engine/](https://www.datadoghq.com/blog/engineering/husky-datadog-columnar-storage-engine/)  
> **Pattern**: `Decoupled Cloud-Native Columnar Storage for High-Cardinality Metrics`  

---

## 1. Problem Statement & Operational Dilemma
Ingesting tens of trillions of metric points daily with high-cardinality tags caused Cassandra and traditional time-series database clusters to suffer catastrophic disk I/O and compaction stalls.

---

## 2. Production Architecture & Solution Breakdown
Architected Husky, a decoupled columnar storage engine backed by cloud object storage (S3). Separated write ingestion, compaction, and query execution tiers. Employs dictionary compression, roaring bitmaps, and vectorized Parquet-style chunks.

### Enforced Invariants
- `INV-METRIC-01: Compute tiers must remain 100% stateless; all telemetry state externalizes to object storage`
- `INV-METRIC-02: Queries must scan only relevant compressed columnar chunks via partition metadata pruning`

### Trade-offs & Operational Costs
Higher query latency for uncompressed real-time data compared to in-memory hot caches.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Writing a custom columnar database engine is unnecessary for metrics below 1 billion points/day.
- **Pragmatic Small-Scale Architecture**: Use VictoriaMetrics, TimescaleDB, or ClickHouse with automated chunk retention policies.
- **Estimated Savings**: $18,000/mo in dedicated storage cluster infrastructure

### Actionable Implementation Checklist
1. Deploy ClickHouse or VictoriaMetrics
1. Set retention policy to 30 days for raw metrics
1. Enable zstd compression on metric tables

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-RES-04: Metrics ingestion tiers must decouple buffering queues from persistent columnar storage`

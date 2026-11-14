# AWS: Amazon S3 Strong Read-After-Write Consistency: Under the Hood

> **Organization**: AWS  
> **Domain**: Distributed Storage & High Availability  
> **Published**: 2021-03-01  
> **Source URL**: [https://aws.amazon.com/blogs/aws/amazon-s3-strong-consistency-2021](https://aws.amazon.com/blogs/aws/amazon-s3-strong-consistency-2021)  
> **Pattern**: `Strong Consistency in Massively Distributed Key-Value Object Storage`  

---

## 1. Problem Statement & Operational Dilemma
S3 historically provided eventual consistency for overwrite PUTs and DELETEs, forcing application developers to build complex caching layers or DynamoDB lock tables to prevent reading stale objects.

---

## 2. Production Architecture & Solution Breakdown
Re-architected S3's metadata tier with formal TLA+ mathematical modeling, synchronous replication across Availability Zones, and atomic metadata versioning. Delivered strong read-after-write consistency with zero impact on latency or availability.

### Enforced Invariants
- `INV-STORAGE-01: Successful PUT must immediately be visible to subsequent GET across all regions and nodes`
- `INV-STORAGE-02: Zero performance degradation in read/write throughput during metadata consensus`

### Trade-offs & Operational Costs
Extensive multi-year re-engineering of internal replication and consensus engines.

---

## 3. Big Tech vs. Lean Startup Playbook
- **Why Big Tech Infra is Overkill**: Building custom consensus algorithms for blob storage when standard object stores now provide it natively.
- **Pragmatic Small-Scale Architecture**: Rely directly on S3 or MinIO with bucket versioning enabled and store object URIs in PostgreSQL.
- **Estimated Savings**: $3,000/mo in custom caching and consistency verification code

### Actionable Implementation Checklist
1. Enable S3 bucket versioning
1. Store S3 key and ETag in PostgreSQL
1. Use pre-signed URLs with 15-minute expirations

---

## 4. `ai-agents` Codebase Rule Evolution
- **Rule Proposal**: `INV-SEC-04: Object storage access must utilize time-limited pre-signed URLs; zero static bucket credentials on frontend`

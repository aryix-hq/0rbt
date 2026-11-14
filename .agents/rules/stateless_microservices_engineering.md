# Stateless Microservices & Anti-"Vibe Coding" Engineering Standard

All code produced by software engineers and architects must follow microservices design, stateless compute tiers, and defensive engineering invariants. Naive "vibe coding"—dumping coupled logic, happy-path assumptions, and unverified mock schemas into codebases—is strictly prohibited.

## 1. Architectural Integrity & Statelessness
- **Stateless Compute**: Services must remain 100% stateless. In-memory sessions, sticky sessions, and local filesystem dependencies are forbidden. All state externalizes to PostgreSQL or Redis.
- **Microservices & Separation of Concerns**: Strict layering (Controller $\to$ Service $\to$ Repository). Business logic, UI, and persistence never mingle. Bounded domain contexts communicate via stable, versioned API contracts (`/api/v1/`) with explicit schemas.
- **Polyglot Durability**: Relational normalization in PostgreSQL, NoSQL/Redis for fast key-value caches and locks, and Transactional Outbox for decoupled event streaming (Kafka/RabbitMQ/Redis Streams).

## 2. Defensive Engineering & Edge Cases
- **Non-Happy Paths**: Every network and external call must define timeout budgets, exponential backoff retries, and circuit breakers. Failures must execute transactional rollbacks (`BEGIN...COMMIT/ROLLBACK`).
- **Mandatory Idempotency**: All state-mutating endpoints (`POST`, `PUT`, `PATCH`) must support an `Idempotency-Key` header, caching execution outcomes in Redis to prevent duplicate processing.
- **Strict Boundary Validation**: Ingress payloads must validate against strict runtime schemas (Zod/Pydantic) before reaching business logic. Reject malformed JSON, oversized payloads, and invalid types immediately.
- **Concurrency & Races**: Use row-level locking (`SELECT ... FOR UPDATE`) or optimistic concurrency control (`WHERE version = :current`) to prevent lost updates and race conditions.

## 3. Security & Supply Chain Hygiene
- **BOLA / IDOR Defense**: Authentication is insufficient; authorization is mandatory. Every query for tenant data must enforce tenant scoping: `WHERE id = :id AND tenant_id = :tenant_id`.
- **Zero Plaintext Secrets**: Hardcoding tokens, connection strings, or keys is an automatic PR rejection. Inject exclusively from environment or HashiCorp Vault.
- **Supply Chain Guard**: Hallucinated or unmaintained packages ("slopsquatting") are strictly barred. Inspect package health and license compatibility before adding dependencies.
- **Sanitization Invariants**: Parameterize 100% of SQL queries; escape HTML outputs against XSS; validate URLs against private IP ranges (SSRF defense).

## 4. Performance, Observability & Dual-Scale Deployment
- **Algorithmic Efficiency**: Audit Big-O complexity. Nested loops ($O(N^2)+$) on unbounded collections are forbidden.
- **Query Optimization**: Mandatory cursor or limit-offset pagination on all list endpoints. Eliminate N+1 queries using eager loading or batching.
- **End-to-End Observability**: Emit structured JSON logs with W3C `traceparent` context. Track Prometheus RED/USE metrics and SLOs.
- **Dual-Scale Sizing**: Software must run identically at small scale on a developer laptop / self-managed VPS (<2GB RAM via Docker Compose and Redis Streams) or scale to enterprise multi-AZ Kubernetes without code changes.

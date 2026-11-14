# Stripe: Designing Robust Idempotent APIs: Preventing Double Charges at Scale

> **Canonical URL**: https://stripe.com/blog/engineering/designing-robust-idempotent-apis  
> **Pattern**: Idempotency with Two-Phase Locking  
> **Hash**: `4553f678d6f885909a8ba302ef1481e7bbbbe94606cc13a19ad684b2b1957273`  
> **Ingested**: 2026-11-14 14:23:37  

---

## 1. Executive Problem & Solution Breakdown
- **Problem**: Preventing double charges in payment systems due to transient network timeouts and race conditions.
- **Solution**: Stripe uses a two-phase transactional lock in PostgreSQL and Redis. Upon receiving an idempotency key, the server attempts an atomic INSERT into an idempotency table with a UNIQUE constraint. If a duplicate is in-flight, downstream requests acquire a short-lived distributed mutex and poll for the original response. Once the initial charge succeeds, the exact HTTP response is saved and replayed for subsequent retries.
- **Trade-offs**: Increased complexity in handling distributed transactions and managing distributed locks.
- **System Invariants**:
  - Each transaction is processed only once, even in the face of race conditions.
  - The exact HTTP response is saved and replayed for subsequent retries.

---

## 2. Big Tech vs. Lean Startup Client Playbook
- **Big Tech Overkill**: For small-scale companies, copying Stripe's massive setup is unnecessary and can lead to increased complexity and cost.
- **Small-Scale Client Architecture**: Implement idempotency using a combination of Postgres, Redis, and simple workers. Use a similar two-phase locking mechanism with a UNIQUE constraint in Postgres and a distributed mutex in Redis. Save the exact HTTP response and replay it for subsequent retries.
- **Estimated Savings**: Monthly savings can be significant by preventing double charges and reducing the need for manual intervention.
- **Actionable Steps**:
  - Identify all mutating POST transactions that require idempotency.
  - Set up a Postgres table with a UNIQUE constraint for idempotency keys.
  - Implement a Redis-based distributed mutex with a TTL.
  - Save the exact HTTP response and replay it for subsequent retries.

---

## 3. LinkedIn Thought Leadership Drafts
### Hook 1 (Contrarian)
> Stripe's solution to preventing double charges is not just about locking; it's about ensuring that every transaction is idempotent, even in the face of race conditions across distributed systems.

### Hook 2 (Narrative)
> Imagine a scenario where a customer's payment request times out due to a network issue. Without idempotency, the customer could be charged twice. Stripe's approach ensures that the payment is processed only once, even if the request is retried multiple times.

### Post Body
```markdown
Stripe's approach to preventing double charges in payment systems is a testament to the importance of idempotency in distributed systems. The core challenge lies in handling race conditions where two identical requests arrive simultaneously across different API gateway nodes before the first transaction has completed writing to the database.

Stripe resolves this by using a two-phase transactional lock in PostgreSQL and Redis. Upon receiving an idempotency key, the server attempts an atomic INSERT into an idempotency table with a UNIQUE constraint. If a duplicate is currently in-flight, downstream requests acquire a short-lived distributed mutex (TTL 10s) and poll for the original response. Once the initial charge succeeds, the exact HTTP status code, headers, and JSON response payload are saved into the idempotency record. Subsequent retries instantly replay the cached response without executing duplicate payment gateway transactions.

**Key Takeaways:**
- Implementing idempotency is crucial for preventing double charges in payment systems.
- Use a two-phase transactional lock in PostgreSQL and Redis to handle race conditions.
- Save the exact HTTP response to replay subsequent retries without executing duplicate transactions.

#Stripe #Idempotency #PaymentSystems #DistributedSystems
```

---

## 4. ai-agents Codebase Evolution
- **Target Skills**: devops-sre, database-architect
- **Proposed Rule**: `INV-001: Implement a rule to detect and resolve race conditions in distributed systems using two-phase locking with Postgres and Redis.`

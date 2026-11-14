# Uber: Saga Pattern for Distributed Trip State Machines across 50 Microservices

> **Canonical URL**: https://www.uber.com/blog/engineering/saga-pattern-distributed-transactions  
> **Pattern**: Saga Pattern  
> **Hash**: `a63b65a7bb02461798d531ea2cb02860957a795097b6635b5e7e8cc55f76f558`  
> **Ingested**: 2026-11-14 14:24:32  

---

## 1. Executive Problem & Solution Breakdown
- **Problem**: Coordinating driver dispatch, passenger reservation, surge pricing, and credit card holds across 50 microservices using two-phase commit over HTTP microservices due to blocking locks and latency cascades.
- **Solution**: Uber transitioned to an Orchestrated Saga Pattern backed by Kafka event streams. The Saga Orchestrator manages forward progress through a deterministic Finite State Machine (FSM). For every mutating step, an explicit compensating transaction is registered. If any downstream service fails or times out, the orchestrator executes compensating actions in reverse order, maintaining eventual consistency across microservices without distributed table locks.
- **Trade-offs**: The trade-off is between immediate consistency and eventual consistency. While the Saga Pattern ensures eventual consistency, it may introduce a delay in resolving inconsistencies.
- **System Invariants**:
  - Eventual consistency across all microservices
  - Deterministic Finite State Machine (FSM) for managing forward progress
  - Compensating transactions for each mutating step

---

## 2. Big Tech vs. Lean Startup Client Playbook
- **Big Tech Overkill**: Copying Uber's massive setup, which involves 50 microservices and Kafka event streams, is not feasible for a 5-50 person company due to the complexity and resource requirements.
- **Small-Scale Client Architecture**: For a smaller scale, you can implement a simplified version of the Saga Pattern using a combination of Postgres, Redis, and simple workers. Use Postgres for transactional consistency, Redis for managing state, and simple workers to handle compensating transactions.
- **Estimated Savings**: Monthly savings can be significant by avoiding the overhead of maintaining a complex distributed system and leveraging existing technologies like Postgres and Redis.
- **Actionable Steps**:
  - Identify critical business processes that require coordination across services.
  - Set up a Postgres database for transactional consistency.
  - Use Redis to manage the state of the Saga.
  - Implement simple workers to handle compensating transactions in case of failures.

---

## 3. LinkedIn Thought Leadership Drafts
### Hook 1 (Contrarian)
> Uber's transition from two-phase commit to the Saga Pattern showcases the counterintuitive shift from blocking locks to event-driven consistency, highlighting the importance of embracing asynchronous architectures in distributed systems.

### Hook 2 (Narrative)
> In the realm of real-time ride coordination, Uber faced the monumental challenge of maintaining consistency across 50 microservices without resorting to the latency-inducing two-phase commit. Their journey from a naive approach to a robust Saga Pattern, backed by Kafka event streams, is a testament to the power of embracing event-driven architectures.

### Post Body
```markdown
Uber's transition from two-phase commit to the Saga Pattern showcases the counterintuitive shift from blocking locks to event-driven consistency, highlighting the importance of embracing asynchronous architectures in distributed systems.

In the realm of real-time ride coordination, Uber faced the monumental challenge of maintaining consistency across 50 microservices without resorting to the latency-inducing two-phase commit. Their journey from a naive approach to a robust Saga Pattern, backed by Kafka event streams, is a testament to the power of embracing event-driven architectures.

For CTOs and senior engineers, the key takeaway is that distributed transactions can be managed effectively without distributed locks by leveraging event-driven patterns like the Saga, ensuring eventual consistency and scalability.

**Key Points:**

- **Problem:** Coordinating driver dispatch, passenger reservation, surge pricing, and credit card holds across 50 microservices using two-phase commit was impractical due to blocking locks and latency cascades.

- **Solution:** Transitioning to an Orchestrated Saga Pattern backed by Kafka event streams allowed Uber to manage forward progress through a deterministic Finite State Machine (FSM) and execute compensating actions in reverse order in case of failures.

- **Benefits:** This approach maintains eventual consistency without distributed table locks, ensuring scalability and reliability in a highly distributed environment.

- **Lessons Learned:** Embrace event-driven architectures and asynchronous patterns like the Saga for managing distributed transactions, avoiding the pitfalls of traditional two-phase commit.
```

---

## 4. ai-agents Codebase Evolution
- **Target Skills**: devops-sre, database-architect
- **Proposed Rule**: `INV-001: Event-Driven Pattern Detection Rule - This rule will analyze the codebase and recommend the use of event-driven patterns like the Saga for managing distributed transactions, ensuring eventual consistency and scalability.`

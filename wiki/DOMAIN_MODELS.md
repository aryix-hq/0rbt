# Living Domain Models & Class Specifications

> **Custodian**: Core Software Engineer & Staff Architect (`@fullstack-developer`, `@architect`)  
> **Status**: Living Domain Specification  
> **Last Synchronized**: 2026-10-21  

This document serves as the living source of truth for all domain entities, value objects, aggregate roots, service interfaces, and repository contracts across the codebase.

---

## 1. Domain Entities & Class Hierarchy

```mermaid
classDiagram
    direction TB

    class AggregateRoot {
        <<Abstract>>
        +UUID id
        +int version
        +List~DomainEvent~ domainEvents
        +addDomainEvent(DomainEvent event)
        +clearDomainEvents()
    }

    class Tenant {
        +TenantId id
        +string name
        +string slug
        +TenantStatus status
        +DateTime createdAt
        +activate()
        +suspend(string reason)
    }

    class User {
        +UserId id
        +TenantId tenantId
        +Email email
        +UserRole role
        +DateTime createdAt
        +changeRole(UserRole newRole)
    }

    class IdempotencyRecord {
        +IdempotencyKey key
        +TenantId tenantId
        +string requestHash
        +int responseStatus
        +string responseBody
        +DateTime lockedAt
        +DateTime expiresAt
        +isExpired() bool
        +matchesHash(string incomingHash) bool
    }

    class OutboxMessage {
        +UUID id
        +TenantId tenantId
        +string eventType
        +string payloadJson
        +OutboxStatus status
        +int retryCount
        +DateTime createdAt
        +markPublished()
        +markFailed()
    }

    class ITenantRepository {
        <<Interface>>
        +findById(TenantId id) Tenant
        +findBySlug(string slug) Tenant
        +save(Tenant tenant)
    }

    class IUserRepository {
        <<Interface>>
        +findById(TenantId tenantId, UserId id) User
        +findByEmail(TenantId tenantId, Email email) User
        +save(User user)
    }

    class IOutboxRepository {
        <<Interface>>
        +save(OutboxMessage message)
        +fetchPending(int batchSize) List~OutboxMessage~
    }

    class IEventBus {
        <<Interface>>
        +publish(string topic, string payloadJson)
    }

    AggregateRoot <|-- Tenant
    AggregateRoot <|-- User
    Tenant "1" *-- "many" User : contains
    Tenant "1" *-- "many" OutboxMessage : partitions
    ITenantRepository ..> Tenant : persists
    IUserRepository ..> User : persists
    IOutboxRepository ..> OutboxMessage : persists
```

---

## 2. Layered Clean Architecture Decoupling

```mermaid
classDiagram
    direction LR

    class IngressController {
        <<Presentation Layer>>
        +handleRequest(HttpRequest req) HttpResponse
    }

    class DomainService {
        <<Application Layer>>
        +executeCommand(Command cmd) Result
    }

    class DomainRepository {
        <<Infrastructure Layer>>
        +query(Query q) Entity
        +save(Entity e)
    }

    IngressController --> DomainService : Invokes DTO
    DomainService --> DomainRepository : Injects Interface
```

---

## 3. Core Value Object Invariants
1. **Immutability**: All Value Objects (`TenantId`, `UserId`, `Email`, `Money`, `IdempotencyKey`) are strictly immutable and validated at construction.
2. **Identity Equality**: Entities are compared strictly by their unique identity (`id`), while Value Objects are compared by value equality.
3. **Tenant Boundary Protection**: Domain aggregates never cross tenant boundaries. A repository query must require an explicit `TenantId` parameter.


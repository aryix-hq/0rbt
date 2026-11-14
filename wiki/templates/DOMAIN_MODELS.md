# Living Domain Models & Class Specifications

> **Custodian**: Core Software Engineer & Staff Architect (`@fullstack-developer`, `@architect`)  
> **Status**: Living Domain Specification  
> **Last Synchronized**: {{DATE}}  

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

    class {{ENTITY_NAME}} {
        +UUID id
        +UUID tenantId
        +string name
        +string status
        +DateTime createdAt
        +executeAction()
    }

    class I{{ENTITY_NAME}}Repository {
        <<Interface>>
        +findById(UUID tenantId, UUID id) {{ENTITY_NAME}}
        +save({{ENTITY_NAME}} entity)
    }

    AggregateRoot <|-- {{ENTITY_NAME}}
    I{{ENTITY_NAME}}Repository ..> {{ENTITY_NAME}} : persists
```

---

## 2. Layered Architecture Invariants
- **Controller**: Parses and validates HTTP/CLI ingress via runtime schema (Zod/Pydantic).
- **Service**: Executes domain logic, coordinates transactions, and enforces tenant scoping.
- **Repository**: Persists aggregate state to PostgreSQL or document store via typed interfaces.


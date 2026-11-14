# Data & Persistence Domain (`data`)

> **Package / Component**: Local SQLite Storage & Embedding Indexes  
> **Contract Standard**: Peanuts & Hay Leaf Contract (`INV-DOC-02`)  
> **Status**: Active  

---

## 1. Domain Responsibility
The `data/` package isolates runtime SQLite databases, deduplication indexes, and vector embeddings generated from monitored engineering blogs.

---

## 2. Exported Files & Schemas
- **`engineering_intelligence.db`**:
  - `processed_articles`: Tracks canonical URLs, SHA-256 hashes, timestamps, and extracted content.
  - `engineering_learnings`: Stores 4-dimensional synthesis data (architectural patterns, client blueprints, LinkedIn drafts, and `ai-agents` evolution rules).
  - `knowledge_embeddings`: 768-dimensional vector representations generated via Ollama (`nomic-embed-text`) for zero-token local RAG queries.

---

## 3. Enforced Invariants
- **`INV-DATA-01` (Clean Storage)**: Binary `.db` files must not contain unencrypted secrets or credentials.
- **`INV-DATA-02` (ACID Integrity)**: Write operations must execute within transactional boundaries with WAL journaling enabled.

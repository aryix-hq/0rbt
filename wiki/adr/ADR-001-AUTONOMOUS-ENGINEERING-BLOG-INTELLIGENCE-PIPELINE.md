# ADR-001: Architecture for Autonomous Engineering Blog Intelligence Pipeline

- **Status**: Accepted
- **Deciders**: System Architect (`@architect`), Engineering Manager (`@engineering-manager`), Database Architect (`@database-architect`)
- **Date**: 2026-11-14

---

## 1. Context and Problem Statement
Monitoring 60+ premier technology engineering blogs manually is infeasible, while naive RSS scrapers suffer from payload truncation, duplicate posts, marketing fluff, and lack of actionable extraction. We require an automated, production-grade intelligence pipeline that ingests, deduplicates, extracts, and synthesizes engineering insights into four distinct value streams (LinkedIn content, architectural knowledge base, lean client advisory, and `ai-agents` codebase evolution).

---

## 2. Decision Drivers
- **Idempotency & Deduplication**: Must guarantee zero duplicate notifications or re-processing of the same article even across cross-posted Medium domains or tracking URL variants.
- **Payload Completeness**: Must handle truncated RSS feeds by falling back to clean full-text HTML extraction without incurring heavy headless browser overhead.
- **Multi-Dimensional AI Value Extraction**: Must extract 4 decoupled outputs in a single LLM execution pass using a strictly validated JSON schema.
- **Zero-Cloud-Token Option**: Must seamlessly support local execution via Ollama (`qwen2.5-coder:14b`) at \$0 cost, as well as cloud models (Gemini Flash) when higher context capacity is needed.
- **Fail-Safe Observability**: External feed timeouts or scraping errors must not crash the entire polling cycle.

---

## 3. Considered Options
1. **Option 1: Ad-hoc Standalone Python Daemon**: Write a custom Python daemon running in systemd or Docker.
2. **Option 2: Monolithic Single n8n Workflow with Embedded Scripts**: Build a single massive n8n workflow with hardcoded URLs and in-node prompts.
3. **Option 3: Modular n8n Pipeline with Externalized Feed Registry & Structured 4-Dimensional Schema**: Maintain an externalized, version-controlled JSON feed registry (`config/engineering_blogs_registry.json`), an n8n workflow pipeline with dedicated nodes for canonical hash deduplication, full-text extraction, structured LLM synthesis, and multi-channel dispatch.

---

## 4. Decision Outcome
- **Chosen Option**: **Option 3: Modular n8n Pipeline with Externalized Feed Registry & Structured 4-Dimensional Schema**.
- **Rationale**:
  - Provides visual orchestration, native credential management, and robust error trigger mechanisms via n8n.
  - Externalizing the blog registry (`config/engineering_blogs_registry.json`) enables adding or removing blogs without touching workflow logic or risking canvas corruption.
  - Using a single multi-dimensional JSON schema reduces LLM round-trips from 4 to 1, slashing execution latency and token costs by ~70%.

---

## 5. Consequences & Invariants

### Positive Impact
- Ingestion of 60+ tier-1 engineering blogs is completely automated and decoupled.
- Canonical URL normalization strips UTM parameters, query strings, and protocol differences before computing `SHA256(canonical_url)`.
- LinkedIn drafts, architectural notes, and client blueprints are generated synchronously with zero duplication.
- Real-world distributed systems breakthroughs directly feed back into `ai-agents` invariant rules and test fixtures.

### Negative Trade-offs / Debt Incurred
- High-volume polling of 60+ endpoints requires polite request pacing (jittered delays) and proper `User-Agent` headers to prevent HTTP 429 rate-limiting.
- Medium and Cloudflare-protected blogs occasionally rotate markup; the extraction fallback must degrade gracefully to the RSS description if full-text scraping encounters an anti-bot challenge.

### System Invariants Established
- **`INV-BLOG-01` (Canonical Deduplication)**: Every ingested article URL must undergo canonicalization (lowercase host, strip query params, strip anchors) and be hashed via `SHA256`. Articles with existing hashes in the deduplication store must be discarded before LLM invocation.
- **`INV-BLOG-02` (Substance Gate)**: Articles with fewer than 300 words or identified as pure event announcements/marketing copy must be dropped before synthesis.
- **`INV-BLOG-03` (Structured Multi-Output Contract)**: All LLM synthesis responses must strictly adhere to the 4-Dimensional JSON schema (LinkedIn, Architecture, Small-Scale Client, and `ai-agents` Evolution).

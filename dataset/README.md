# 0rbt Architecture Corpus & Instruction-Tuning Dataset (v1.0)

Curated public open-source engineering dataset comprising **2,065 authentic engineering blog posts** and **5,869 architecture diagrams** harvested across premier technology engineering organizations.

## Dataset Structure

- **`engineering_corpus_2000.jsonl`**: Complete tabular JSONL corpus containing raw substantive text, company metadata, domain categorization, word counts, and diagram links.
- **`instruction_tuning_v1.jsonl`**: ChatML/Alpaca formatted instruction-tuning pairs for fine-tuning specialized reasoning models (`aryix/0rbt-architect`).
- **`data/images/`**: Local cache of high-resolution system architecture diagrams and flowcharts (gitignored to preserve repository size).

## Company Distribution

| Company | Article Count |
| :--- | :--- |
| Datadog | 517 |
| Cloudflare | 502 |
| GitHub | 483 |
| Shopify | 421 |
| AWS | 106 |
| Dropbox | 11 |
| Meta | 11 |
| Slack | 10 |
| Google | 1 |
| Netflix | 1 |
| Stripe | 1 |
| Uber | 1 |

## Engineering Category Breakdown

| Category | Count |
| :--- | :--- |
| Observability & Metric Aggregation | 1,632 |
| Edge Compute & Distributed Systems | 325 |
| Databases & Storage Systems | 73 |
| Developer Infrastructure & CI/CD | 14 |
| AI/ML Infrastructure | 5 |
| Security & Cryptography | 5 |
| Access Control & Global Security | 1 |
| Caching & High-Throughput Storage | 1 |
| Database Reliability & High Availability | 1 |
| Distributed Storage & High Availability | 1 |
| Edge Compute & Proxy Architecture | 1 |
| Multi-Tenant Architecture & Resilience | 1 |
| Observability & Distributed Tracing | 1 |
| Payment Systems & Idempotency | 1 |
| Real-Time Collaboration & Distributed Caching | 1 |
| Real-Time Matching & Distributed Transactions | 1 |
| Telemetry & Columnar Data Storage | 1 |

## Anti-Vibe Invariants & Hygiene

- **Zero Synthetic Placeholders (`INV-06`)**: All articles, companies, and failure post-mortems originate from authentic tech publications. Zero synthetic dummy names (`Acme Corp`, `Fake Co`, `John Doe`).
- **Substance Guarantee**: Only articles exceeding 150 words with verified technical depth are included.
- **Reproducible Pipeline**: Harvested via `bin/bulk-harvest-2000.py` and continuous n8n workflow.

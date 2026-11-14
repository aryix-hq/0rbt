# 0rbt Architecture Corpus & Instruction-Tuning Dataset (v1.0)

Curated public open-source engineering dataset comprising **4,169 authentic engineering blog posts** and **11,936 architecture diagrams** harvested across premier technology engineering organizations.

## Dataset Structure

- **`engineering_corpus_2000.jsonl`**: Complete tabular JSONL corpus containing raw substantive text, company metadata, domain categorization, word counts, and diagram links (**4,169 articles**).
- **`instruction_tuning_v1.jsonl`**: Complete ChatML formatted instruction-tuning dataset combining 4,169 empirical engineering blog pairs, 550 Anti-Vibe Invariant pairs, and 789 AI-Agents Skills & Red Team pairs (**5,508 total pairs**).
- **`all_skills_instruction_dataset.jsonl`**: Standalone dataset of 789 instruction-tuning pairs derived across all 252 specialized `ai-agents` skills (Red Team, Bug Hunting, SRE, Architecture, SEO, Media) (**789 pairs**).
- **`invariants_instruction_dataset.jsonl`**: Standalone dataset of 550 instruction-tuning pairs derived strictly from the 20 Anti-Vibe Invariants and SRE resilience doctrine (**550 pairs**).
- **`data/images/`**: Local cache of high-resolution system architecture diagrams and flowcharts (gitignored to preserve repository size, **11,936 images**).

## Company Distribution

| Company | Article Count |
| :--- | :--- |
| Cloudflare | 909 |
| Datadog | 903 |
| GitHub | 844 |
| Meta | 833 |
| Shopify | 443 |
| AWS | 159 |
| Dropbox | 31 |
| GitLab | 22 |
| Docker | 11 |
| Slack | 10 |
| Google | 1 |
| Netflix | 1 |
| Stripe | 1 |
| Uber | 1 |

## Engineering Category Breakdown

| Category | Count |
| :--- | :--- |
| Observability & Metric Aggregation | 2,850 |
| Edge Compute & Distributed Systems | 718 |
| Developer Infrastructure & CI/CD | 235 |
| Databases & Storage Systems | 136 |
| AI/ML Infrastructure | 132 |
| Distributed Systems & Systems Scale | 47 |
| Security & Cryptography | 38 |
| Cloud Infrastructure & Orchestration | 2 |
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

- **Zero Synthetic Placeholders (`INV-06`)**: All articles, companies, and failure post-mortems originate from authentic tech publications. Zero synthetic placeholder names.
- **Substance Guarantee**: Only articles exceeding 150 words with verified technical depth are included.
- **Reproducible Pipeline**: Harvested via `bin/bulk-harvest-2000.py` and continuous n8n workflow.

---
language:
- en
license: cdla-permissive-2.0
task_categories:
- question-answering
- text-generation
tags:
- software-engineering
- system-design
- architecture
- distributed-systems
- postmortems
- 0rbt
size_categories:
- 1K<n<10K
---

# 🪐 0rbt: Curated Engineering Post-Mortems & Architectural Invariants Dataset

> **Repository**: [github.com/aryix-hq/0rbt](https://github.com/aryix-hq/0rbt)  
> **Target Model**: `aryix/0rbt-architect`  
> **License**: [CDLA-Permissive-2.0](https://cdla.dev/permissive-2-0/)  
> **Curator**: 0rbt Open Source Community  

---

## 📖 Dataset Summary

The `0rbt` dataset contains real-world distributed systems dilemmas, outage root causes, production invariants, and architectural solutions synthesized from premier technology companies (Netflix, Stripe, Uber, Google, Meta, GitHub, Datadog, Cloudflare, AWS, etc.).

Unlike generic coding datasets that focus on syntax or leetcode puzzles, this dataset explicitly models **architectural decision-making, failure prevention, and downscale translation** ("Big Tech $\to$ Lean Startup").

---

## 🗂 Files & Splits

- `engineering_postmortems_v1.jsonl`: Full structured records with 16 architectural fields.
- `instruction_tuning_v1.jsonl`: Formatted in Alpaca/ShareGPT format (`instruction`, `input`, `output`) ready for fine-tuning open-weights models (e.g. Qwen 2.5, Llama 3.1).

---

## 📐 Data Fields

| Field | Type | Description |
| :--- | :--- | :--- |
| `id` | string | Unique 0rbt record ID (e.g. `0rbt-000001`) |
| `company` | string | Engineering organization (e.g. `Netflix`, `Stripe`, `Uber`) |
| `title` | string | Official article title |
| `category` | string | Architecture domain (e.g. `Observability`, `Payment Systems`, `Ledgers`) |
| `canonical_url` | string | Original published blog post URL |
| `core_architectural_pattern` | string | Precise name of system design pattern |
| `problem_statement` | string | Technical bottleneck or failure condition |
| `solution_breakdown` | string | Step-by-step description of production implementation |
| `system_invariants` | list | List of non-negotiable operational invariants |
| `trade_offs` | string | Complexity, latency, or memory sacrifices incurred |
| `big_tech_overkill` | string | Why copying this directly is dangerous for startups |
| `small_scale_implementation` | string | Pragmatic alternative using Postgres, Redis, or simple workers |
| `estimated_cost_savings` | string | Monthly savings vs enterprise SaaS |
| `ai_agents_rule` | string | Production invariant rule for AI coding agents |

---

## 🧪 Usage with Hugging Face `datasets`

```python
from datasets import load_dataset

dataset = load_dataset("json", data_files="dataset/instruction_tuning_v1.jsonl")
print(dataset[0])
```

---

## ⚖️ License & Attribution

This dataset is distributed under the **Community Data License Agreement – Permissive – Version 2.0 (CDLA-Permissive-2.0)**. Article excerpts are summarized for transformative educational and research analysis under fair use.

# PLAN-002: Open-Source Launch, Public Dataset & aryix/0rbt-architect Model Release

> **Lifecycle Stage**: Stage 3 (Phased Project Planning)  
> **Status**: COMPLETED  
> **Target Branch**: `feat/eng-blog-intelligence-pipeline`  
> **Created**: 2026-11-14  
> **Target Repository**: `https://github.com/aryix-hq/0rbt`  
> **Model Identifier**: `aryix/0rbt-architect`  
> **Upstream PRD**: [`wiki/prd.md`](../prd.md)  
> **Planning Trio Sign-off**:
> - [x] Product Manager (`@product-manager`)
> - [x] System Architect (`@architect`)
> - [x] Technical Project Manager (`@project-manager`)

---

## 1. Executive Summary & Objective

Prepare `0rbt` for public release on `https://github.com/aryix-hq/0rbt`, curate an open-source dataset of real-world distributed systems dilemmas and post-mortems, launch Phase A (`aryix/0rbt-architect` Ollama Modelfile), and establish the Phase B fine-tuning and quantization pipeline for Hugging Face Hub.

---

## 2. Living Phase & Milestone Tracker

| Phase | Milestone Description | Lead Agent(s) | Status | Evidence / Link |
| :---: | :--- | :--- | :---: | :---: |
| **Phase 1** | Public Repository Cleanup, Governance & Legal | `@documentation-manager`, `@open-source-observer` | `[COMPLETED]` | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` |
| **Phase 2** | Phase A: `aryix/0rbt-architect` Ollama Modelfile | `@architect`, `@ollama-orchestrator` | `[COMPLETED]` | `Modelfile`, `bin/build-ollama-model.sh` |
| **Phase 3** | Historical Archive Crawlers & Dataset Exporter | `@fullstack-developer`, `@devops-sre` | `[COMPLETED]` | `bin/crawl-historical-archives.py`, `bin/export-hf-dataset.py`, `dataset/` |
| **Phase 4** | Phase B: Hugging Face Fine-Tuning Pipeline | `@architect`, `@ai-psychologist` | `[COMPLETED]` | `training/train_lora.py`, `training/export_gguf.py`, `training/README.md` |
| **Phase 5** | Pre-Push Security Audit & Verification Gate | `@devsecops`, `@engineering-manager` | `[COMPLETED]` | Two-Axis Review & Local Code Reviewer PASS |

---

## 3. Associated Living Artifacts
- **Primary PRD**: [`wiki/prd.md`](../prd.md)
- **Implementation Plan Artifact**: `opensource_launch_dataset_and_model_plan.md`
- **Active Task Board**: [`wiki/TASK_BOARD.md`](../TASK_BOARD.md)
- **Knowledge Memory**: [`wiki/memory.md`](../memory.md)

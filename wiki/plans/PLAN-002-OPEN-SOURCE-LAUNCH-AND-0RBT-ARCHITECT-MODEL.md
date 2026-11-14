# PLAN-002: Open-Source Launch, 2,000+ Post-Mortem Dataset & 0rbt/architect Model Release

> **Lifecycle Stage**: Stage 3 (Phased Project Planning)  
> **Status**: IN_PROGRESS  
> **Target Branch**: `feat/oss-launch-and-model-release`  
> **Created**: 2026-11-14  
> **Target Repository**: `https://github.com/aryix-hq/0rbt`  
> **Upstream PRD**: [`wiki/prd.md`](../prd.md)  
> **Planning Trio Sign-off**:
> - [x] Product Manager (`@product-manager`)
> - [x] System Architect (`@architect`)
> - [x] Technical Project Manager (`@project-manager`)

---

## 1. Executive Summary & Objective

Prepare `0rbt` for public release on `https://github.com/aryix-hq/0rbt`, curate an open-source dataset of 2,000+ real-world distributed systems dilemmas and post-mortems, launch Phase A (`0rbt/architect` Ollama Modelfile), and establish the Phase B fine-tuning pipeline for Hugging Face Hub.

---

## 2. Living Phase & Milestone Tracker

| Phase | Milestone Description | Lead Agent(s) | Status | Evidence / Link |
| :---: | :--- | :--- | :---: | :---: |
| **Phase 1** | Public Repository Cleanup, Governance & Legal | `@documentation-manager`, `@open-source-observer` | `[PENDING]` | `README.md`, `LICENSE`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md` |
| **Phase 2** | Phase A: `0rbt/architect` Ollama Modelfile | `@architect`, `@ollama-orchestrator` | `[PENDING]` | `Modelfile`, `bin/build-ollama-model.sh` |
| **Phase 3** | Historical Archive Crawlers & 2,000+ Dataset | `@fullstack-developer`, `@devops-sre` | `[PENDING]` | `bin/crawl-historical-archives.py`, `bin/export-hf-dataset.py` |
| **Phase 4** | Phase B: Hugging Face Fine-Tuning Pipeline | `@architect`, `@ai-psychologist` | `[PENDING]` | `training/train_lora.py`, `dataset/README.md` |
| **Phase 5** | Pre-Push Security Audit & Remote Push Gate | `@devsecops`, `@engineering-manager` | `[PENDING]` | Two-Axis Review & Signed Staging Attestation |

---

## 3. Associated Living Artifacts
- **Primary PRD**: [`wiki/prd.md`](../prd.md)
- **Implementation Plan Artifact**: [`opensource_launch_dataset_and_model_plan.md`](file:///Users/adithya/.gemini/antigravity/brain/b3244977-8c80-4765-9d28-f7e3adc4e912/opensource_launch_dataset_and_model_plan.md)
- **Active Task Board**: [`wiki/TASK_BOARD.md`](../TASK_BOARD.md)
- **Knowledge Memory**: [`wiki/memory.md`](../memory.md)

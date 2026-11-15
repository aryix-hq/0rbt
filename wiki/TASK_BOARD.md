# Sprint & Feature Task Board

> Maintained by Technical Project Manager (`@project-manager`) via local Ollama ($0 tokens).

## Stage 1: Research & Discovery
- [x] `RES-001`: Autonomous Engineering Blog Intelligence Pipeline (Lead: `@research`, `@client-advocate`)

## Stage 2: Product Backlog (RICE Prioritized)
- [x] `FEAT-001`: Autonomous Engineering Blog Intelligence Pipeline (RICE Score: `85.5`) (Lead: `@product-manager`)
- [x] `FEAT-002`: AI-Agents Skills & Anti-Vibe Invariants Model Integration (RICE Score: `84.0`) (Lead: `@product-manager`)
- [x] `FEAT-003`: Complete 255-Skill AI-Agents Suite & Offensive Red Team Integration (RICE Score: `88.0`) (Lead: `@product-manager`, `@architect`)
- [ ] `FEAT-004`: Neural Weights Fine-Tuning, LoRA Merging & Ollama Hub Release (RICE Score: `89.5`) (Lead: `@product-manager`, `@architect`)

## Stage 3: Phased Project Planning
- [x] `PLAN-001`: Autonomous Engineering Blog Intelligence Pipeline (Planning Trio: `@product-manager`, `@architect`, `@project-manager`)
- [x] `PLAN-002`: Open-Source Launch, Public Dataset & `aryix/0rbt-architect` Model Release (Planning Trio: `@product-manager`, `@architect`, `@project-manager`)
- [x] `PLAN-003`: AI-Agents Skills & Anti-Vibe Invariants Integration into aryix/0rbt-architect (Planning Trio: `@product-manager`, `@architect`, `@project-manager`)
- [x] `PLAN-004`: Complete 255-Skill AI-Agents Suite, Offensive Red Team Ingestion & 32K Native Context Upgrade (Planning Trio: `@product-manager`, `@architect`, `@project-manager`)
- [ ] `PLAN-005`: Model Fine-Tuning, LoRA Merging, GGUF Quantization & Ollama Hub Release (Planning Trio: `@product-manager`, `@architect`, `@project-manager`)

## Stage 4: Active Execution & Verification
- [ ] `PLAN-005`: Phase 1 - Upstream Sync & Dataset Organization (`skills/architecture-tradeoff-analysis`, `stride-threat-modeling`, `INV-ARCH-01`)
- [ ] `PLAN-005`: Phase 2 - Fine-Tuning Execution Pipeline (Pathway A: Local MLX on M4 Pro / Pathway B: Cloud GPU Unsloth)
- [ ] `PLAN-005`: Phase 3 - LoRA Merging & GGUF Quantization (`models/0rbt-architect-q4_k_m.gguf`)
- [ ] `PLAN-005`: Phase 4 - Modelfile Wiring & Local Ollama Rebuild (`aryix/0rbt-architect`)
- [ ] `PLAN-005`: Phase 5 - Head-to-Head Benchmark Validation (`bin/benchmark-50.py --live`)
- [ ] `PLAN-005`: Phase 6 - Ollama Hub Weight Publication (`ollama push aryix/0rbt-architect`)

## Completed (EM Approved PR & Merged)
- [x] `PLAN-004`: Phase 1 - 255-Skill AST Ingestion & Instruction Dataset Expansion (`bin/synthesize-all-skills-dataset.py`, 5,508 ChatML pairs)
- [x] `PLAN-004`: Phase 2 - Modelfile System Prompt Grounding, 3-Tier Hierarchy & 32K Context Upgrade (`Modelfile`, `num_ctx 32768`)
- [x] `PLAN-004`: Phase 3 - Local Ollama Model Rebuild & Hub Manifest Push (`aryix/0rbt-architect:latest` pushed to Ollama Hub)
- [x] `PLAN-004`: Phase 4 - 50-Scenario Staff Benchmark Suite & Head-to-Head Comparative Evaluator (`bin/benchmark-50.py` with `--compare-base`)
- [x] `PLAN-004`: Phase 5 - Static Invariant Code Reviewer Gate & Branch Push (`feat/all-skills-redteam-integration`)

## Stage 4: Active Execution & Verification
- [x] `PLAN-001` / `FEAT-001`: Phase 1 - Blog Registry & ADR definition (`config/engineering_blogs_registry.json`, `wiki/adr/ADR-001.md`)
- [x] `PLAN-001` / `FEAT-001`: Phase 2 - n8n Workflow Topology & 4D Synthesis Engine (`n8n/engineering_blogs_pipeline.json`)
- [x] `PLAN-001` / `FEAT-001`: Phase 3 - Zero-Mock Automated Pipeline Test Suite (`bin/test-blog-pipeline.py`)
- [x] `PLAN-001` / `FEAT-001`: Phase 4 - Living Context Synchronization & EM Gate (Active on branch `feat/eng-blog-intelligence-pipeline`)
- [x] `PLAN-002`: Open-Source Scaffolding (`LICENSE`, `README.md`, `CONTRIBUTING.md`, issue templates)
- [x] `PLAN-002`: Historical Archive Crawler & Hugging Face Dataset Exporter (`bin/crawl-historical-archives.py`, `bin/export-hf-dataset.py`, `dataset/`)
- [x] `PLAN-002`: Phase A Local Ollama Model `aryix/0rbt-architect` (`Modelfile`, `bin/build-ollama-model.sh`)
- [x] `PLAN-002`: Phase B Fine-Tuning & Quantization Pipeline (`training/train_lora.py`, `training/export_gguf.py`, `training/README.md`)

## Completed (EM Approved PR & Merged)
- [x] Initial Project Setup, Mode Switching & 4-Stage Lifecycle Engine

# FEAT-004: Neural Weights Fine-Tuning, LoRA Merging & Ollama Hub Release

> **Lifecycle Stage**: Stage 2 (Product Specification)  
> **Status**: APPROVED  
> **Lead**: `@product-manager`, `@architect`  
> **RICE Score**: `89.5` (Reach: 10,000+, Impact: 3.0, Confidence: 90%, Effort: 3 Sprints)  
> **Target Release**: `aryix/0rbt-architect:latest` (GGUF Neural Weights)  

---

## 1. Problem Statement & User Need

While `aryix/0rbt-architect` currently provides robust architectural and security reasoning through its native 32K context window and system prompt (`Modelfile`), its underlying weights remain identical to the base foundation model (`qwen2.5-coder:14b`). 

When an external user installs the model from Ollama Hub (`ollama run ARYIX/0rbt-architect`), they do not have access to our local SQLite database (`data/engineering_intelligence.db`). Consequently, the model cannot recall the specific details, failure mechanics, and implementation benchmarks of our 4,169 crawled engineering post-mortems unless those learnings are **permanently baked into the neural network weights**.

Furthermore, recent improvements to `ai-agents` (including the 8-Step Principal Architecture Method, ATAM trade-off analysis, monotonic fencing tokens, STRIDE threat modeling, and `INV-ARCH-01` architecture guard rules) must be ingested into our dataset before fine-tuning.

---

## 2. Product Objectives & Target Metrics

1. **Parametric Memory of 4,169 Blogs & 255 Skills**:
   - Permanently bake the 5,500+ ChatML instruction pairs into the model's neural weights.
   - Users can query specific post-mortem lessons (Netflix, Stripe, Uber, Cloudflare, Meta) zero-shot with zero external tools or RAG.
2. **Dual-Pathway Fine-Tuning Execution**:
   - Provide a **$0 Local Apple Silicon M4 Pro path** using MLX (`mlx-lm`) within the machine's 24 GB Unified Memory.
   - Provide a **Fast Cloud GPU path** using Unsloth / PyTorch on a single A100/L40S (~45 minutes).
3. **Seamless GGUF Quantization & Packaging**:
   - Merge the LoRA adapter into base weights and quantize to `Q4_K_M` GGUF format (~9.0 GB).
   - Package into Ollama with native `PARAMETER num_ctx 32768`.
4. **Verified Performance Uplift**:
   - Achieve $\ge 90\%$ pass rate on the 50-Scenario Staff Benchmark (`bin/benchmark-50.py --live`).
   - Demonstrate statistically significant uplift in post-mortem recall and architectural trade-off analysis over vanilla `qwen2.5-coder:14b`.
5. **Direct Ollama Hub Publication**:
   - Push updated GGUF weights layers to `ollama.com/aryix/0rbt-architect:latest` with zero namespace fragmentation.

---

## 3. Scope & User Stories

### User Story 1: Zero-RAG Architecture & Post-Mortem Recall
*As a systems engineer using `ollama run ARYIX/0rbt-architect`, I want the model to answer complex distributed systems failure questions by citing real-world engineering post-mortems (e.g. Netflix cache stampede, Cloudflare CPU regex exhaustion, Stripe idempotency) directly from its neural weights without requiring internet access or a vector database.*

### User Story 2: Principled ATAM & STRIDE Threat Modeling
*As a principal architect evaluating a new microservice design, I want the model to systematically evaluate Quality Attribute Scenarios (QAS) using ATAM and map trust boundaries with STRIDE threat modeling, enforcing monotonic fencing tokens on distributed leases.*

### User Story 3: Lightweight, High-Speed Local Inference
*As a developer working on an Apple Silicon laptop, I want the published `Q4_K_M` GGUF model to run with full Metal GPU acceleration at $>30\text{ tokens/sec}$ with full 32K context.*

---

## 4. Acceptance Criteria & Definition of Done (DoD)

- [ ] **AC-1**: Ingest latest `ai-agents` architecture skills (`architecture-tradeoff-analysis`, `stride-threat-modeling`, `architecture-guard.py`, `INV-ARCH-01`) into the training dataset.
- [ ] **AC-2**: Master dataset `dataset/instruction_tuning_v1.jsonl` contains $\ge 5,600$ valid, schema-compliant ChatML pairs with zero dummy placeholder names (`INV-06`).
- [ ] **AC-3**: Fine-tuning pipeline (`training/train_lora.py` and `training/train_mlx.py`) runs with zero-mock regression test passing.
- [ ] **AC-4**: LoRA adapter merges cleanly into FP16 base model with zero NaN/Inf layer weights.
- [ ] **AC-5**: GGUF conversion and quantization generates valid `models/0rbt-architect-q4_k_m.gguf` (size: 8.8–9.2 GB).
- [ ] **AC-6**: `Modelfile` points to the newly quantized GGUF weights and builds cleanly via `ollama create aryix/0rbt-architect`.
- [ ] **AC-7**: Live 50-scenario benchmark achieves $\ge 85\%$ pass rate with verified uplift over vanilla `qwen2.5-coder:14b`.
- [ ] **AC-8**: Model pushed to Ollama Hub (`ollama.com/aryix/0rbt-architect`) and verified via `ollama pull`.

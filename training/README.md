# Model Training & Quantization Domain (`training`)

> **Package / Component**: Fine-Tuning Pipeline & Quantization Export Engine  
> **Contract Standard**: Peanuts & Hay Leaf Contract (`INV-DOC-02`)  
> **Status**: Active  

---

## 1. Domain Responsibility
The `training/` package provides deterministic routines for supervised fine-tuning (SFT) and GGUF quantization of the specialized `aryix/0rbt-architect` model. It ingests instruction tuning pairs generated from real-world engineering blog post-mortems and produces Hugging Face LoRA adapters and GGUF model binaries for local Ollama and llama.cpp execution.

---

## 2. Exported Interfaces & Scripts
- **`training/train_lora.py`**:
  - Executes 4-bit QLoRA fine-tuning using Hugging Face `trl` (`SFTTrainer`), `peft` (`LoraConfig`), and `bitsandbytes`.
  - Formats Alpaca/JSONL instruction pairs into ChatML / Qwen prompt conventions with explicit architectural system prompts.
  - CLI Arguments:
    - `--base-model <hf_repo>`: Base Hugging Face model (default: `Qwen/Qwen2.5-Coder-14B-Instruct`).
    - `--epochs <int>`: Number of training epochs (default: `3`).
    - `--batch-size <int>`: Per-device batch size (default: `4`).
    - `--lr <float>`: Learning rate (default: `2e-4`).
    - `--dry-run`: Validates dataset formatting without initializing heavy weights.
    - `--mock-test`: Zero-token test verification of formatting logic and tokenizers.
- **`training/export_gguf.py`**:
  - Merges trained LoRA adapters back into base model weights.
  - Converts Hugging Face weights to GGUF format and applies quantization (`q4_k_m`, `q8_0`, `f16`).
  - CLI Arguments:
    - `--adapter <path>`: Directory containing trained LoRA adapter.
    - `--output <path>`: Target `.gguf` file destination.
    - `--quantization <format>`: Quantization method (default: `q4_k_m`).
    - `--mock-test`: Zero-dependency test verification.

---

## 3. Enforced Invariants
- **`INV-TRN-01` (Synthetic Placeholder Name Ban)**: All instruction templates, system prompts, and training data must be free of placeholder names (`INV-06`). Authentic engineering case studies and realistic architectures are strictly required.
- **`INV-TRN-02` (Deterministic ChatML Formatting)**: Prompts must adhere strictly to `<|im_start|>system`, `<|im_start|>user`, and `<|im_start|>assistant` token boundaries to prevent model hallucination and token bleed.
- **`INV-TRN-03` (Zero-Token Mock Verification)**: Training and export scripts must maintain self-contained `--mock-test` routines that run in `<1s` without GPU or network dependencies.

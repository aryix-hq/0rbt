# Hybrid Multi-Model Assignment & Token Conservation Rules

1. **4-Tier Federated Multi-Model Architecture**:
   - The organization orchestrates four complementary model engines:
     1. **Local Ollama (M4 Pro Unified Memory)**: Default worker tier ($0 / 0 Cloud Tokens). Executes routine code drafting, git synthesis (`local-git.sh`), shell command crafting (`local-cmd.sh`), syntax verification, and unit test loops.
     2. **Anthropic Claude (Sonnet / Haiku)**: Flagship agentic coding, deep architectural reasoning, and CISO security boundary review.
     3. **Google Gemini (Flash / Pro)**: 1M+ token context window for full-repository log audits, Diátaxis documentation, and multimodal UI inspection.
     4. **OpenAI / GPT-OSS (GPT-4o / o3-mini)**: Strict schema outputs, consensus arbitration in multi-agent debates, and structured JSON contracts.

2. **Supported Execution Modes (`ai-agents mode <mode>`)**:
   - `local`  : 100% local Ollama execution ($0 cloud tokens on Apple Silicon Metal).
   - `hybrid` : (Recommended) Local Ollama for code/git/cmd worker agents; Claude/Gemini/GPT for review gates.
   - `claude` : Direct routing to Anthropic Claude models.
   - `gemini` : Direct routing to Google Gemini models.
   - `openai` : Direct routing to OpenAI or compatible GPT-OSS endpoints.
   - `auto`   : Dynamic context-aware routing based on agent role & task scope.

3. **Persona-to-Model Role Mapping Matrix**:
   - **`@architect` & `@ciso`**: Claude 3.7 / 3.5 Sonnet (Fallback: Gemini Pro). System topology, cross-cutting contracts, ACID invariants, and threat modeling.
   - **`@bug-hunter` & `@red-team`**: Claude Sonnet / local Ollama `jimscard/whiterabbit-neo`. Dynamic exploit verification and 7-Question Gate triage.
   - **`@orchestrator-debate`**: OpenAI GPT-4o / o3-mini (Fallback: Claude Sonnet). Dialectic multi-agent consensus and devil's advocacy.
   - **`@devops-sre` & `@documentation-manager`**: Gemini 2.0 Flash (1M+ token context for massive logs, OpenAPI specs, and repos).
   - **`@fullstack-developer`, `@qa`, `@privacy-engineer`**: Local Ollama `qwen2.5-coder:14b` ($0 tokens, Metal GPU acceleration).
   - **`@motion-designer`, `@video-editor`, `@3d-diffusion-specialist`, `@voice-synthesizer`**:
     - Narrative storyboards, screenwriting & witty copy: Local Ollama `mistral-nemo:12b` ($\tau = 0.75 - 0.85$, $0 tokens).
     - Structural creative coding (Manim, Remotion, Blender bpy, FCPXML, Typst): Local Ollama `qwen2.5-coder:14b` or `32b` ($\tau = 0.15 - 0.20$, $0 tokens).
     - Real-time phonetic text normalization & Q-Map cue sync: Local Ollama `llama3.2:3b` ($\tau = 0.00 - 0.10$, sub-50ms latency, $0 tokens).

4. **Zero-Tagging Autonomous Execution**:
   - The user never needs to manually tag agents or specify model names.
   - In `local` mode: code drafting, commits, and shell commands route to Ollama (`local-coder.sh`, `local-git.sh`, `local-cmd.sh`).
   - In `hybrid` mode: routine tasks stay on Ollama; architectural review gates escalate automatically to Claude or Gemini.

5. **Hardware Reality & AirLLM Batch Execution Policy**:
   - On 24 GB Unified Memory workstations (e.g. Apple M4 Pro), models up to 14B–22B fit in RAM and run at interactive speeds (~40–60 tokens/sec via Metal).
   - Massive 70B+ open models cannot fit in 24 GB RAM for real-time interactive generation. AirLLM streams layers from SSD at ~0.5–2 tokens/sec and is strictly reserved for **asynchronous overnight batch jobs** (`/goal`). Interactive sessions leverage Claude/Gemini cloud intelligence or local 14B models.

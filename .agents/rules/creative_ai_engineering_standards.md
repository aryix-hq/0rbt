# Creative AI Engineering Standards & Multi-Modal Production Invariants

These standards govern all creative multimedia, generative audio, video editing, 3D mesh modeling, and animation pipelines within `ai-agents`. All subagents and automated engines must strictly adhere to these invariants.

---

## 1. The 5 Core Invariants of Creative Production

### Invariant 1: Local $0 Cloud Token Mandate
- Routine creative drafting, storyboarding, music bed generation (MusicGen), sound effects (AudioLDM 2), stem splitting (Demucs), video rotoscoping (SAM 2), depth estimation (Depth-Anything V2), 3D mesh reconstruction (TripoSR), and video compilation must execute locally on consumer workstations (Apple Silicon MPS / NVIDIA CUDA / CPU) at **$0 cloud token costs**.
- Cloud Pro models are strictly restricted to architectural review and CISO audit gates per Rule 2.

### Invariant 2: Rational Fractional Timebases (Zero-Drift Timeline Math)
- Floating-point timestamps (`0.033333s`) induce cumulative drift across long timelines.
- All video editing and timeline generators (`bin/media-editor.py`, `bin/creative-video-tools.py`, `bin/editorial-graphics.py`) must specify timecodes as integer rational fractions:
  - $24\text{ fps} \to 100 / 2400\text{s}$
  - $23.976\text{ fps} \to 1001 / 24000\text{s}$
  - $30\text{ fps} \to 100 / 3000\text{s}$
  - $60\text{ fps} \to 100 / 6000\text{s}$

### Invariant 3: Acoustic Loudness Mastering & Staging
- **Dialogue / Voiceover**: Integrated target $-14.0\text{ LUFS}$ (web streaming/video) or $-16.0\text{ LUFS}$ (podcasts), True Peak $\le -1.0\text{ dBFS}$.
- **Background Music Bed**: Integrated target $-24.0\text{ LUFS}$ to $-28.0\text{ LUFS}$ (ducked $-10\text{ to } -14\text{ dB}$ below dialogue).
- **Foley & Sound Effects**: Aligned to $-6.0\text{ dBFS}$ True Peak with sharp exponential decay to prevent master buss clipping.

### Invariant 4: Temperature & Sampling Calibration Matrix
Models must be invoked with domain-calibrated sampling temperatures to balance creativity with structural precision:

| Domain | Assigned Model | Temperature ($\tau$) | Top-P | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Narrative Storyboards & Scriptwriting** | `mistral-nemo:12b` | `0.75 – 0.85` | `0.90` | Conversational pacing, witty hooks, natural storytelling. |
| **Structural Creative Code (Manim, Remotion, Blender bpy, FCPXML, Typst)** | `qwen2.5-coder:14b` or `32b` | `0.15 – 0.20` | `0.95` | Absolute AST syntax precision, schema validation, zero hallucinated methods. |
| **Real-time Phonetic Normalization & Cue Sync** | `llama3.2:3b` | `0.00 – 0.10` | `1.00` | Deterministic text expansion (numbers, currencies) and sub-50ms latency. |

### Invariant 5: Anti-Slop Content Guardrails
- All creative text, scripts, and video narration must pass the anti-slop linter (`bin/humanizer.py` / `bin/creative-prompt-orchestrator.py`).
- Strict ban on generic AI filler words (*"delve"*, *"tapestry"*, *"testament"*, *"in today's fast-paced digital world"*, *"revolutionize"*, *"game-changer"*).
- Prefer direct, declarative, engineering-grounded technical explanations.

---

## 2. Ground Reality & Zero-Mock Testing Mandate (Rule 10)

- Every script in `bin/` must implement an offline `--mock-test` completing in **<0.05 seconds** with exit code 0.
- When local neural model weights are not present on the developer's machine, the engine must clearly report the exact 1-line installation or download command rather than silently generating fake data.

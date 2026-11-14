# Blender, ComfyUI & Local Latent Diffusion Standards

This standard governs all 3D asset generation, procedural scene scripting, depth-map extraction, and local latent diffusion pipelines executed by agents in this repository. All operations must run locally at **$0 cloud tokens**.

---

## 1. Headless Blender (`bpy`) Execution Standards

- **Headless Execution Only**: All Blender automation must run strictly headless in batch mode without a graphical display server:
  ```bash
  blender -b --factory-startup -P generate_scene.py -- [arguments]
  ```
- **Procedural Scene Construction**: Scripts must programmatically initialize clean scene graphs, purge default starter cubes, and set up explicit render engines:
  - Default to **EEVEE Next** or **Cycles** with deterministic sample counts (`cycles.samples = 64` for drafting, `128` for production).
- **Camera Staging & Isometric Rigs**:
  - Orthographic / Isometric camera transforms: Euler rotation `(54.736°, 0°, 45°)` with `camera.data.type = 'ORTHO'`.
  - Staged lighting: Standard 3-point key/fill/rim light setups or single high-angle directional sun lamps.
- **Pass Extraction**: Scripts generating depth passes for diffusion conditioning must normalize Z-depth to 16-bit PNG/EXR (`(z - min) / (max - min)`) to prevent clipping.

---

## 2. ComfyUI REST API & Node Graph Standards

- **Local Endpoint Isolation**: ComfyUI operations connect strictly to local instances:
  $$\text{Target URL} = \text{http://127.0.0.1:8188}$$
  Network calls outside the local loopback boundary are strictly prohibited.
- **Node Graph JSON Structure**: Payloads sent to `/prompt` must validate against standard ComfyUI DAG schema:
  - Node types: `CheckpointLoaderSimple`, `CLIPTextEncode`, `ControlNetLoader`, `ControlNetApplyAdvanced`, `KSampler`, `VAEDecode`, `SaveImage`.
  - Input link bindings: Strict node output index routing (`[node_id, slot_index]`).
- **Deterministic Sampling**:
  - Samplers: `dpmpp_2m_karras` or `euler_ancestral`.
  - Default steps: 20–30 steps for SD1.5 / SDXL; CFG scale between 6.0 and 8.0.
  - Consistent seed tracking for reproducible generation pipelines.

---

## 3. Hybrid 3D-to-Diffusion Conditioning Pipeline

```
[Blender bpy Script] ──> Render Geometry + Depth Pass (.png)
                                 │
                                 ▼
                     [ComfyUI ControlNet Depth]
                                 │
 [Positive/Negative Prompts] ───┼───> [KSampler] ──> [VAE Decode] ──> [Final Render]
                                 │
    [Checkpoint: SDXL/SD1.5] ───┘
```

- **Depth Map Preprocessing**: Depth maps generated in Blender bypass ComfyUI preprocessors (e.g., MiDaS, Depth Anything) to eliminate neural estimation noise; pass the raw geometric depth directly into `ControlNetApplyAdvanced`.
- **Strength Calibration**:
  - ControlNet strength: $0.80 - 1.00$ to preserve geometric edges.
  - Denoise strength: $0.70 - 0.90$ for creative texturing while retaining architectural silhouettes.

---

## 4. Hardware Sizing, Memory Isolation & Zero Cloud Fees

- **Local VRAM Caps**:
  - Models must load with `fp16` or `bf16` precision.
  - On 8GB/16GB unified memory (Apple Silicon / Metal) or 8GB VRAM (NVIDIA), enforce `--lowvram` or `--medvram` flags to prevent system out-of-memory kernel panics.
- **Zero Cloud API Subscriptions**: All model weights (Stable Diffusion, ControlNet, LoRAs) and compute must reside locally. PRs containing cloud diffusion API endpoints (Midjourney, Replicate, Stability Cloud) are rejected automatically.

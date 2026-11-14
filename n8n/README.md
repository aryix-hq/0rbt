# n8n Workflow Automation Engine (`n8n`)

> **Package / Component**: Workflow Orchestration & Data Pipeline Canvas  
> **Contract Standard**: Peanuts & Hay Leaf Contract (`INV-DOC-02`)  
> **Status**: Active  

---

## 1. Domain Responsibility
The `n8n/` package maintains executable, version-controlled JSON definitions of the automated engineering blog intelligence pipeline. It manages:
1. Scheduled cron triggers for continuous feed polling.
2. Canonical URL normalization and deterministic SHA-256 deduplication.
3. Clean full-text article extraction from truncated RSS items.
4. Structured 4-Dimensional AI Synthesis Chains.
5. Multi-channel dispatch (Telegram/Slack notifications, Git Markdown scribe, and `.agents` evolutionary rule queue).

---

## 2. Exported Workflows & Execution Topology
- **`engineering_blogs_pipeline.json`**:
  - `Schedule Trigger`: Runs every 3 hours (or configurable cron).
  - `Load Feed Registry`: Reads `config/engineering_blogs_registry.json`.
  - `Fetch Feed Updates`: HTTP/RSS Read node with `ETag` and `If-Modified-Since`.
  - `Deduplication Guard`: Computes `SHA256(canonical_url)` and checks persistent datatable.
  - `Content Extractor`: Cleans HTML and extracts structured markdown with code snippets.
  - `4D AI Synthesis Chain`: Invokes Ollama (`qwen2.5-coder:14b`) or Gemini Flash with a strictly validated 4-dimensional JSON schema.
  - `Multi-Destination Dispatch`: Dispatches to Telegram approval queue, appends to `wiki/learnings/`, and queues `ai-agents` rule proposals.
  - `Global Error Handler`: Captures failed execution context and notifies on-call.

---

## 3. Enforced Invariants
- **`INV-N8N-01` (Credential Separation)**: Workflow definitions must reference n8n Credential variables (`{{ $credentials.telegramApi }}`, `{{ $credentials.geminiApiKey }}`) and never embed plaintext secrets.
- **`INV-N8N-02` (Idempotent Execution)**: Any re-execution of a workflow must yield zero duplicate notifications or corrupted state.
- **`INV-N8N-03` (Fail-Safe Isolation)**: A timeout or 404 on an individual RSS feed must fail that specific branch without halting the polling of remaining feeds.

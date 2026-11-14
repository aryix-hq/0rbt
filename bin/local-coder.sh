#!/usr/bin/env bash
# ==============================================================================
# LOCAL CODER RUNNER (OLLAMA HYBRID WORKER)
# ==============================================================================
# Sends code generation & refactoring tasks directly to local Ollama.
# Ensures $0 / 0 Cloud Token consumption for code drafting.
# Supports domain-specific models:
#   - Reverse Engineering: deepseek-coder-v2:16b
#   - Red Teaming & Exploit Analysis: jimscard/whiterabbit-neo
#   - General Code: qwen2.5-coder:14b
# ==============================================================================
set -euo pipefail

# Resolve canonical script directory even if invoked through symlinks
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
MODEL="${OLLAMA_MODEL:-qwen2.5-coder:14b}"
OLLAMA_HOST="${OLLAMA_HOST:-http://127.0.0.1:11434}"

# Check execution mode (local vs cloud)
MODE="${AI_AGENTS_MODE:-}"
if [[ -z "${MODE}" ]]; then
  if [[ -f ".agents/mode" ]]; then
    MODE=$(cat ".agents/mode" | tr -d '[:space:]')
  elif [[ -f "${HOME}/.gemini/config/ai-agents-mode" ]]; then
    MODE=$(cat "${HOME}/.gemini/config/ai-agents-mode" | tr -d '[:space:]')
  else
    MODE="local"
  fi
fi

if [[ "${MODE}" == "cloud" ]]; then
  echo "[local-coder] Local LLM mode is switched OFF (Mode: cloud). Orchestrator should execute directly via cloud model."
  exit 2
fi

# Parse optional --model / -m flag
while [[ $# -gt 0 ]]; do
  case "$1" in
    -m|--model)
      RAW_MODEL="$2"
      case "${RAW_MODEL}" in
        research|reasoning|deepseek-r1|r1)
          MODEL="deepseek-r1:14b"
          ;;
        re|reverse-engineering|reverse_engineering|deepseek-coder|deepseek)
          MODEL="deepseek-coder-v2:16b"
          ;;
        security|red-team|red_team|whiterabbit|exploit)
          MODEL="jimscard/whiterabbit-neo"
          ;;
        coder|worker|default)
          MODEL="qwen2.5-coder:14b"
          ;;
        *)
          MODEL="${RAW_MODEL}"
          ;;
      esac
      shift 2
      ;;
    *)
      break
      ;;
  esac
done

PROMPT="${1:-}"
CONTEXT_FILE="${2:-}"

if [[ -z "${PROMPT}" ]]; then
  echo "Usage: local-coder.sh [--model <re|security|coder|name>] <prompt> [context_file]"
  exit 1
fi

PAYLOAD_PROMPT="${PROMPT}"
if [[ -n "${CONTEXT_FILE}" && -f "${CONTEXT_FILE}" ]]; then
  FILE_CONTENT=$(cat "${CONTEXT_FILE}")
  PAYLOAD_PROMPT="Context from ${CONTEXT_FILE}:
\`\`\`
${FILE_CONTENT}
\`\`\`

Instruction: ${PROMPT}
Output ONLY the replacement code or diff. No conversational preamble."
fi

# Query Ollama with automatic fallback if target model is not pulled yet
python3 -c "
import urllib.request, json, sys, os, subprocess

url = '${OLLAMA_HOST}/api/generate'
target_model = '${MODEL}'
fallback_model = 'qwen2.5-coder:14b'

def query_model(mod):
    payload = {
        'model': mod,
        'prompt': '''${PAYLOAD_PROMPT}''',
        'stream': False,
        'options': {
            'num_ctx': 4096 if 'deepseek' in mod else 8192
        }
    }
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
    return urllib.request.urlopen(req)

resp = None
used_model = target_model
try:
    resp = query_model(target_model)
except urllib.error.HTTPError as he:
    if he.code == 404 and target_model != fallback_model:
        sys.stderr.write(f'[local-coder] Model \"{target_model}\" not found in local Ollama; falling back to {fallback_model}...\n')
        used_model = fallback_model
        resp = query_model(fallback_model)
    else:
        raise
except Exception as e:
    err_str = str(e)
    sys.stderr.write(f'[local-coder] Error connecting to Ollama at {url}: {err_str}\n')
    if 'Operation not permitted' in err_str or 'Errno 1' in err_str:
        sys.stderr.write('[local-coder] NOTE: Antigravity terminal sandbox blocks loopback network (127.0.0.1:11434). Please re-run command with BypassSandbox: true.\n')
    sys.exit(1)

result = json.loads(resp.read().decode('utf-8'))
raw_response = result.get('response', '').strip()
if not raw_response and result.get('thinking'):
    raw_response = result.get('thinking', '').strip()
print(raw_response)

# Log token usage
prompt_tokens = result.get('prompt_eval_count', 0)
eval_tokens = result.get('eval_count', 0)
candidates = [
    os.path.join('${SCRIPT_DIR}', 'record-tokens.py'),
    os.path.expanduser('~/.local/bin/record-tokens.py')
]
record_script = next((c for c in candidates if os.path.exists(c)), None)
if record_script:
    subprocess.run([
        'python3', record_script,
        '--record',
        '--tool', 'local-coder',
        '--model', used_model,
        '--prompt-tokens', str(prompt_tokens),
        '--eval-tokens', str(eval_tokens)
    ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
"

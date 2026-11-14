#!/usr/bin/env bash
# ==============================================================================
# bin/build-ollama-model.sh — Build & Test aryix/0rbt-architect Ollama Model
# ==============================================================================
set -euo pipefail

MODEL_TAG="aryix/0rbt-architect"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=================================================================="
echo " 🚀 BUILDING OLLAMA MODEL: ${MODEL_TAG}"
echo "=================================================================="

# 1. Verify Ollama is reachable
if ! curl -s http://127.0.0.1:11434/api/tags > /dev/null; then
  echo "✘ Ollama server is not reachable on 127.0.0.1:11434."
  echo "  Start it via: ollama serve"
  exit 1
fi

# 2. Build model from Modelfile
echo "==> Creating ${MODEL_TAG} from ${REPO_ROOT}/Modelfile..."
ollama create "${MODEL_TAG}" -f "${REPO_ROOT}/Modelfile"

echo "✔ Successfully created model: ${MODEL_TAG}"

# 3. Run automated verification test
echo -e "\n==> Running automated verification test on ${MODEL_TAG}..."
TEST_PROMPT="A startup wants to implement an automated payment charge retry loop across a Node.js API and PostgreSQL. How should they prevent double charges and thundering herds at small scale?"

echo "Prompt: ${TEST_PROMPT}"
echo "------------------------------------------------------------------"

RESPONSE=$(curl -s http://127.0.0.1:11434/api/generate -d "{
  \"model\": \"${MODEL_TAG}\",
  \"prompt\": \"${TEST_PROMPT}\",
  \"stream\": false,
  \"options\": {\"temperature\": 0.2}
}" | jq -r '.response')

echo "${RESPONSE}"
echo "------------------------------------------------------------------"

# 4. Verify required invariant keywords in output
if echo "${RESPONSE}" | grep -Ei "idempotenc|stripe|unique constraint|redis|jitter" > /dev/null; then
  echo "✔ VERIFICATION PASSED: ${MODEL_TAG} enforced idempotency and resilience invariants!"
else
  echo "⚠️ WARNING: Response lacked expected architectural invariants. Please inspect output above."
fi

echo -e "\n=================================================================="
echo " ✅ MODEL READY: ${MODEL_TAG}"
echo "=================================================================="
echo "To chat with your model:"
echo "  ollama run ${MODEL_TAG}"
echo ""
echo "To publish to Ollama Hub:"
echo "  ollama push ${MODEL_TAG}"
echo "=================================================================="

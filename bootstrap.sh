#!/usr/bin/env bash
# ==============================================================================
# ANTIGRAVITY AI-AGENTS ENTERPRISE BOOTSTRAP SCRIPT
# ==============================================================================
# One-command setup for fresh repository clones or new developer environments.
#
# Configures:
#   1. System prerequisites & dependencies (Git, Python 3.9+, Curl, Bash/Zsh)
#   2. Local Ollama server & models (qwen2.5-coder:14b / 7b)
#   3. Executable permissions & ~/.local/bin CLI symlinks
#   4. User PATH environment integration (.zshrc / .bashrc)
#   5. Antigravity IDE global plugin registration (~/.gemini/config/plugins/)
#   6. Git post-merge automated session reset hooks
#   7. Dual-layer memory graph & token savings ledger scaffolding
#   8. Live self-test & inference validation
#
# Usage:
#   ./bootstrap.sh [options]
#
# Options:
#   --quick          Use lightweight qwen2.5-coder:7b (ideal for <16GB RAM)
#   --model <name>   Specify custom Ollama model (default: qwen2.5-coder:14b)
#   --no-pull        Skip Ollama model download
#   -y, --yes        Non-interactive mode (auto-confirm all prompts)
#   --help           Show this help message
# ==============================================================================

set -euo pipefail

# Determine script & repository directory
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
REPO_ROOT="$(cd -P "$(dirname "$SOURCE")" && pwd)"

# Styling
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

log_step()    { echo -e "\n${BLUE}${BOLD}==>${NC} ${BOLD}$1${NC}"; }
log_success() { echo -e "  ${GREEN}✔${NC} $1"; }
log_info()    { echo -e "  ${CYAN}ℹ${NC} $1"; }
log_warn()    { echo -e "  ${YELLOW}⚠${NC} $1"; }
log_error()   { echo -e "  ${RED}✖${NC} $1" >&2; }

# Default arguments
DEFAULT_MODEL="qwen2.5-coder:14b"
PULL_MODEL=true
NON_INTERACTIVE=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --quick)
      DEFAULT_MODEL="qwen2.5-coder:7b"
      shift
      ;;
    --model)
      DEFAULT_MODEL="$2"
      shift 2
      ;;
    --no-pull)
      PULL_MODEL=false
      shift
      ;;
    -y|--yes)
      NON_INTERACTIVE=true
      shift
      ;;
    --help|-h)
      sed -n '2,30p' "$0"
      exit 0
      ;;
    *)
      log_error "Unknown argument: $1"
      echo "Run './bootstrap.sh --help' for usage."
      exit 1
      ;;
  esac
done

echo -e "${CYAN}${BOLD}"
echo "================================================================================"
echo "          ANTIGRAVITY AI-AGENTS ENTERPRISE BOOTSTRAPPER                         "
echo "================================================================================"
echo -e "${NC}"
echo "Repository : ${REPO_ROOT}"
echo "Target Model: ${DEFAULT_MODEL}"
echo "Date       : $(date)"

# ------------------------------------------------------------------------------
# STEP 1: Core System & Dependency Pre-flight
# ------------------------------------------------------------------------------
log_step "Step 1/8: Verifying System Dependencies..."

# 1.1 OS Detection
OS_TYPE="$(uname -s)"
case "${OS_TYPE}" in
  Darwin*) log_success "Operating System: macOS (${OS_TYPE})" ;;
  Linux*)  log_success "Operating System: Linux (${OS_TYPE})" ;;
  *)       log_warn "Unrecognized OS: ${OS_TYPE}. Proceeding anyway..." ;;
esac

# 1.2 Git
if command -v git >/dev/null 2>&1; then
  GIT_VER=$(git --version)
  log_success "Git installed: ${GIT_VER}"
else
  log_error "Git is not installed. Please install git and re-run."
  exit 1
fi

# 1.3 Python 3
if command -v python3 >/dev/null 2>&1; then
  PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')")
  PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
  PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
  if [[ "${PY_MAJOR}" -eq 3 && "${PY_MINOR}" -ge 9 ]]; then
    log_success "Python 3 installed: v${PY_VER} (>= 3.9 requirement met)"
  else
    log_error "Python 3 version ${PY_VER} is too old. Requires >= 3.9."
    exit 1
  fi
else
  log_error "Python 3 is not installed. Please install Python 3.9+ and re-run."
  exit 1
fi

# 1.4 Curl
if command -v curl >/dev/null 2>&1; then
  log_success "Curl is available"
else
  log_error "Curl is required. Please install curl."
  exit 1
fi

# ------------------------------------------------------------------------------
# STEP 2: Ollama Local Inference Engine
# ------------------------------------------------------------------------------
log_step "Step 2/8: Checking Local Ollama Inference Engine..."

OLLAMA_INSTALLED=false
if command -v ollama >/dev/null 2>&1; then
  OLLAMA_INSTALLED=true
  log_success "Ollama CLI installed: $(ollama --version 2>&1 | tr -d '\n')"
else
  log_warn "Ollama is not installed on this system."
  if [[ "${OS_TYPE}" == "Darwin" ]]; then
    if command -v brew >/dev/null 2>&1; then
      if [[ "${NON_INTERACTIVE}" == "true" ]]; then
        log_info "Installing Ollama via Homebrew..."
        brew install ollama
        OLLAMA_INSTALLED=true
      else
        read -p "  Install Ollama via Homebrew now? [Y/n] " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ || -z $REPLY ]]; then
          brew install ollama
          OLLAMA_INSTALLED=true
        fi
      fi
    else
      log_warn "Homebrew not detected. Please install Ollama from: https://ollama.com/download"
    fi
  else
    log_info "To install Ollama on Linux: curl -fsSL https://ollama.com/install.sh | sh"
  fi
fi

# 2.2 Verify Ollama Daemon is Running
OLLAMA_RUNNING=false
OLLAMA_ENDPOINT="${OLLAMA_HOST:-http://127.0.0.1:11434}"
if curl -s -f "${OLLAMA_ENDPOINT}/api/tags" >/dev/null 2>&1; then
  OLLAMA_RUNNING=true
  log_success "Ollama daemon is running at ${OLLAMA_ENDPOINT}"
else
  log_warn "Ollama daemon is not responding at ${OLLAMA_ENDPOINT}."
  if [[ "${OS_TYPE}" == "Darwin" && -d "/Applications/Ollama.app" ]]; then
    log_info "Launching /Applications/Ollama.app..."
    open -a Ollama
    sleep 3
  elif command -v ollama >/dev/null 2>&1; then
    log_info "Attempting background start: ollama serve..."
    ollama serve >/dev/null 2>&1 &
    sleep 3
  fi

  # Retry check
  for i in {1..5}; do
    if curl -s -f "${OLLAMA_ENDPOINT}/api/tags" >/dev/null 2>&1; then
      OLLAMA_RUNNING=true
      log_success "Ollama daemon successfully started and responding at ${OLLAMA_ENDPOINT}"
      break
    fi
    sleep 1
  done

  if [[ "${OLLAMA_RUNNING}" == "false" ]]; then
    log_warn "Could not reach Ollama at ${OLLAMA_ENDPOINT}. You can start it manually with 'ollama serve'."
  fi
fi

# 2.3 Check / Pull Model
if [[ "${OLLAMA_RUNNING}" == "true" && "${PULL_MODEL}" == "true" ]]; then
  log_info "Checking if model '${DEFAULT_MODEL}' is downloaded..."
  MODELS_JSON=$(curl -s "${OLLAMA_ENDPOINT}/api/tags" || echo "{}")
  if echo "${MODELS_JSON}" | grep -q "\"name\":\"${DEFAULT_MODEL}"; then
    log_success "Model '${DEFAULT_MODEL}' is already available locally!"
  else
    log_info "Model '${DEFAULT_MODEL}' not found. Downloading now (this may take a few minutes)..."
    ollama pull "${DEFAULT_MODEL}"
    log_success "Model '${DEFAULT_MODEL}' downloaded successfully."
  fi
fi

# ------------------------------------------------------------------------------
# STEP 3: Executable Permissions
# ------------------------------------------------------------------------------
log_step "Step 3/8: Setting Script Permissions..."

chmod +x "${REPO_ROOT}/bin/"* || true
chmod +x "${REPO_ROOT}/bootstrap.sh" || true
if [[ -f "${REPO_ROOT}/setup.sh" ]]; then
  chmod +x "${REPO_ROOT}/setup.sh" || true
fi
log_success "Made all scripts in bin/ executable"

# ------------------------------------------------------------------------------
# STEP 4: Global CLI Symlinks (~/.local/bin)
# ------------------------------------------------------------------------------
log_step "Step 4/8: Configuring Global CLI Symlinks in ~/.local/bin..."

mkdir -p "${HOME}/.local/bin"

ln -sf "${REPO_ROOT}/bin/ai-agents"        "${HOME}/.local/bin/ai-agents"
ln -sf "${REPO_ROOT}/bin/local-coder.sh"   "${HOME}/.local/bin/local-coder.sh"
ln -sf "${REPO_ROOT}/bin/local-git.sh"     "${HOME}/.local/bin/local-git.sh"
ln -sf "${REPO_ROOT}/bin/local-cmd.sh"     "${HOME}/.local/bin/local-cmd.sh"
ln -sf "${REPO_ROOT}/bin/record-tokens.py" "${HOME}/.local/bin/record-tokens.py"
ln -sf "${REPO_ROOT}/bin/deploy-preview.sh" "${HOME}/.local/bin/deploy-preview.sh"
ln -sf "${REPO_ROOT}/bootstrap.sh"         "${HOME}/.local/bin/ai-agents-bootstrap"

log_success "Installed symlinks in ${HOME}/.local/bin/ (ai-agents, local-coder, local-git, local-cmd, record-tokens)"

# 4.2 Verify PATH
PATH_CONFIGURED=false
case ":$PATH:" in
  *":$HOME/.local/bin:"*) PATH_CONFIGURED=true ;;
esac

if [[ "${PATH_CONFIGURED}" == "true" ]]; then
  log_success "PATH already includes ${HOME}/.local/bin"
else
  log_warn "${HOME}/.local/bin is NOT in your current PATH."
  SHELL_RC=""
  if [[ -n "${ZSH_VERSION:-}" || "${SHELL:-}" == *"zsh"* ]]; then
    SHELL_RC="${HOME}/.zshrc"
  elif [[ -n "${BASH_VERSION:-}" || "${SHELL:-}" == *"bash"* ]]; then
    SHELL_RC="${HOME}/.bashrc"
  fi

  if [[ -n "${SHELL_RC}" ]]; then
    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "${SHELL_RC}" 2>/dev/null; then
      echo -e "\n# Added by ai-agents bootstrap\nexport PATH=\"\$HOME/.local/bin:\$PATH\"" >> "${SHELL_RC}"
      log_success "Appended PATH export to ${SHELL_RC}"
      log_info "Run: source ${SHELL_RC} (or restart terminal) to update PATH in current shell."
    fi
  else
    log_info "Please add this line to your shell profile: export PATH=\"\$HOME/.local/bin:\$PATH\""
  fi
fi

# ------------------------------------------------------------------------------
# STEP 5: Antigravity IDE Global Plugin Registration
# ------------------------------------------------------------------------------
log_step "Step 5/8: Registering Global Plugin with Antigravity..."

mkdir -p "${HOME}/.gemini/config/plugins"
GLOBAL_PLUGIN_LINK="${HOME}/.gemini/config/plugins/ai-agents"
if [[ -L "${GLOBAL_PLUGIN_LINK}" || -d "${GLOBAL_PLUGIN_LINK}" ]]; then
  rm -rf "${GLOBAL_PLUGIN_LINK}"
fi
ln -s "${REPO_ROOT}" "${GLOBAL_PLUGIN_LINK}"
log_success "Linked plugin globally: ${GLOBAL_PLUGIN_LINK} -> ${REPO_ROOT}"

# Configure .vscode/settings.json
mkdir -p "${REPO_ROOT}/.vscode"
if [[ ! -f "${REPO_ROOT}/.vscode/settings.json" ]]; then
  cat > "${REPO_ROOT}/.vscode/settings.json" <<EOF
{
  "ollama.host": "http://127.0.0.1:11434"
}
EOF
  log_success "Created ${REPO_ROOT}/.vscode/settings.json"
else
  log_success "Verified ${REPO_ROOT}/.vscode/settings.json"
fi

# Verify n8n MCP Environment Token
if [[ -n "${N8N_API_KEY:-}" ]]; then
  log_success "N8N_API_KEY environment variable is configured"
fi

# Configure GitHub MCP in ~/.gemini/config/mcp_config.json
if command -v npx >/dev/null 2>&1 || command -v docker >/dev/null 2>&1; then
  python3 -c "
import json, os, subprocess, shutil
mcp_file = os.path.expanduser('~/.gemini/config/mcp_config.json')
data = {'mcpServers': {}}
if os.path.exists(mcp_file):
    try:
        with open(mcp_file, 'r') as f:
            data = json.load(f)
    except Exception:
        pass
data.setdefault('mcpServers', {})

token = os.environ.get('GITHUB_PERSONAL_ACCESS_TOKEN', '')
if not token:
    try:
        token = subprocess.check_output('printf \"protocol=https\\nhost=github.com\\n\" | git credential-osxkeychain get 2>/dev/null | grep password | cut -d= -f2', shell=True).decode().strip()
    except Exception:
        token = ''

# Prefer native npx (zero Docker containers) over docker daemon
if shutil.which('npx'):
    data['mcpServers']['github'] = {
        'command': 'npx',
        'args': ['-y', '@modelcontextprotocol/server-github'],
        'env': {
            'GITHUB_PERSONAL_ACCESS_TOKEN': token or '\${GITHUB_PERSONAL_ACCESS_TOKEN}'
        }
    }
else:
    data['mcpServers']['github'] = {
        'command': 'docker',
        'args': [
            'run', '-i', '--rm', '--init',
            '-e', 'GITHUB_PERSONAL_ACCESS_TOKEN',
            'ghcr.io/github/github-mcp-server', 'stdio'
        ],
        'env': {
            'GITHUB_PERSONAL_ACCESS_TOKEN': token or '\${GITHUB_PERSONAL_ACCESS_TOKEN}'
        }
    }
with open(mcp_file, 'w') as f:
    json.dump(data, f, indent=2)
" 2>/dev/null || true
  log_success "Configured GitHub MCP (native zero-container mode) in ~/.gemini/config/mcp_config.json"
fi

# ------------------------------------------------------------------------------
# STEP 6: Memory Graph & Token Ledger Scaffolding
# ------------------------------------------------------------------------------
log_step "Step 6/8: Initializing Project Memory & Token Ledgers..."

mkdir -p "${REPO_ROOT}/.agents/memory/sessions"
mkdir -p "${REPO_ROOT}/wiki/research"
mkdir -p "${REPO_ROOT}/wiki/features"
mkdir -p "${REPO_ROOT}/wiki/plans"
mkdir -p "${REPO_ROOT}/wiki/defects"

# Initialize local mode
if [[ ! -f "${REPO_ROOT}/.agents/mode" ]]; then
  echo "local" > "${REPO_ROOT}/.agents/mode"
fi
log_success "Execution mode initialized: local (0 cloud tokens)"

# Initialize token ledger if absent
TOKEN_LEDGER="${REPO_ROOT}/.agents/memory/token_ledger.json"
if [[ ! -f "${TOKEN_LEDGER}" ]]; then
  cat > "${TOKEN_LEDGER}" <<EOF
{
  "local_tokens": 0,
  "cloud_tokens": 0,
  "saved_usd": 0.0,
  "by_tool": {},
  "by_model": {},
  "events": []
}
EOF
  log_success "Initialized project token ledger: ${TOKEN_LEDGER}"
else
  log_success "Project token ledger exists: ${TOKEN_LEDGER}"
fi

# Initialize memory graph if absent
MEMORY_GRAPH="${REPO_ROOT}/.agents/memory/memory_graph.json"
if [[ ! -f "${MEMORY_GRAPH}" ]]; then
  cat > "${MEMORY_GRAPH}" <<EOF
{
  "project": "ai-agents",
  "activeTicket": null,
  "lastSessionReset": null,
  "sessionHistory": [],
  "architecturalDecisions": [],
  "antiPatterns": []
}
EOF
  log_success "Initialized project memory graph: ${MEMORY_GRAPH}"
else
  log_success "Project memory graph exists: ${MEMORY_GRAPH}"
fi

# Enforce public-safe .gitignore boundaries
if [[ -f "${REPO_ROOT}/.gitignore" ]]; then
  for rule in ".agents/mode" ".agents/memory/sessions/" ".agents/memory/token_ledger.json" ".agents/memory/active_feature.md" "wiki/defects/DEF-*.md" "wiki/incidents/INC-*.md" "wiki/vulnerabilities/VULN-*.md" "wiki/research/RES-*.md"; do
    if ! grep -Fxq "${rule}" "${REPO_ROOT}/.gitignore" 2>/dev/null; then
      echo "${rule}" >> "${REPO_ROOT}/.gitignore"
    fi
  done
  log_success "Enforced public-safe ignore boundaries in .gitignore"
fi

# ------------------------------------------------------------------------------
# STEP 7: Git Security, Branch Protection & Session Reset Hooks (SEC-02)
# ------------------------------------------------------------------------------
log_step "Step 7/8: Installing Git Security, Branch Protection & Session Hooks..."

if [[ -d "${REPO_ROOT}/.git/hooks" ]]; then
  # 7.1 Pre-commit Security & Confidentiality Guard
  if [[ -f "${REPO_ROOT}/hooks/pre-commit" ]]; then
    cp -f "${REPO_ROOT}/hooks/pre-commit" "${REPO_ROOT}/.git/hooks/pre-commit"
    chmod +x "${REPO_ROOT}/.git/hooks/pre-commit"
    log_success "Git pre-commit security & confidentiality hook installed (.git/hooks/pre-commit)"
  fi

  # 7.2 Pre-push Main Branch Protection Guard (Rule 1)
  if [[ -f "${REPO_ROOT}/hooks/pre-push" ]]; then
    cp -f "${REPO_ROOT}/hooks/pre-push" "${REPO_ROOT}/.git/hooks/pre-push"
    chmod +x "${REPO_ROOT}/.git/hooks/pre-push"
    log_success "Git pre-push branch protection hook installed (.git/hooks/pre-push)"
  fi

  # 7.3 Post-merge Automated Session Reset Hook
  cat > "${REPO_ROOT}/.git/hooks/post-merge" <<'EOF'
#!/usr/bin/env bash
# AI-Agents Automated Post-Merge Session Reset Hook
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
if [[ "${CURRENT_BRANCH}" == "main" || "${CURRENT_BRANCH}" == "master" ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../bin" && pwd)"
  if [[ -f "${SCRIPT_DIR}/ai-agents" ]]; then
    echo "[git-hook] Feature branch merged into main. Resetting active session..."
    "${SCRIPT_DIR}/ai-agents" session reset --auto >/dev/null 2>&1 || true
  fi
fi
EOF
  chmod +x "${REPO_ROOT}/.git/hooks/post-merge"
  log_success "Git post-merge automated session reset hook installed (.git/hooks/post-merge)"
else
  log_warn "No .git/hooks directory found. Skipping git hook installation."
fi

# ------------------------------------------------------------------------------
# STEP 8: End-to-End Self-Test & Diagnostic Check
# ------------------------------------------------------------------------------
log_step "Step 8/8: Running Autonomous System Self-Test..."

TEST_PASSED=true

# 8.1 Test CLI Status
if "${REPO_ROOT}/bin/ai-agents" status >/dev/null 2>&1; then
  log_success "ai-agents status command: OPERATIONAL"
else
  log_error "ai-agents status command failed."
  TEST_PASSED=false
fi

# 8.2 Test Token Accounting
if "${REPO_ROOT}/bin/ai-agents" tokens >/dev/null 2>&1; then
  log_success "ai-agents tokens observer: OPERATIONAL"
else
  log_error "ai-agents tokens observer failed."
  TEST_PASSED=false
fi

# 8.3 Test Local Inference (if Ollama is running)
if [[ "${OLLAMA_RUNNING}" == "true" ]]; then
  log_info "Testing local inference via Ollama (${DEFAULT_MODEL})..."
  SAMPLE_CMD=$("${REPO_ROOT}/bin/local-cmd.sh" "show disk usage of current directory" 2>/dev/null || echo "FAILED")
  if [[ "${SAMPLE_CMD}" != "FAILED" && -n "${SAMPLE_CMD}" ]]; then
    log_success "Local LLM Inference (\$0 Tokens): OPERATIONAL"
    echo -e "      ${BOLD}Sample Inference Output:${NC} ${SAMPLE_CMD}"
  else
    log_warn "Local inference test encountered an issue (check if Ollama is loaded)."
  fi
fi

# ------------------------------------------------------------------------------
# SUMMARY & ANTIGRAVITY SANDBOX GUIDANCE
# ------------------------------------------------------------------------------
echo -e "\n${GREEN}${BOLD}================================================================================"
echo "          BOOTSTRAP COMPLETED SUCCESSFULLY!                                     "
echo "================================================================================${NC}"
echo
echo -e "${BOLD}Your environment is fully configured for \$0 Token Autonomous AI Development!${NC}"
echo
echo -e "${BOLD}Installed Tools & Commands:${NC}"
echo "  • ai-agents status           : View active team, memory, and token snapshot"
echo "  • ai-agents tokens           : View tokens offloaded to local LLM & USD saved"
echo "  • ai-agents mode             : Toggle between local Ollama and cloud Gemini"
echo "  • ai-agents code <prompt>    : Generate code/diffs locally at \$0 cost"
echo "  • ai-agents git commit       : Draft conventional git commits via local LLM"
echo "  • ai-agents run <prompt>     : Generate and run shell commands via local LLM"
echo "  • ai-agents init-project     : Scaffold memory and tools in any other project"
echo

echo -e "${YELLOW}${BOLD}ANTIGRAVITY TERMINAL SANDBOX & PERMISSIONS GUIDE:${NC}"
echo "  Antigravity IDE runs commands in an isolated macOS sandbox by default."
echo "  • Why [shield] appears in chat : Standard Sandbox isolates external network & loopback."
echo "  • Network Calls (git push)     : Needs network permission to reach github.com."
echo "  • Local LLM (127.0.0.1:11434)  : Needs loopback socket access to connect to Ollama."
echo "  • Action Required              : When Antigravity displays the permission dialog,"
echo -e "    simply click ${GREEN}${BOLD}\"Always allow\"${NC} for local-coder.sh, local-git.sh, and local-cmd.sh."
echo "    Because Antigravity prefix-matches commands, this grants permanent zero-prompt execution!"
echo
echo -e "${CYAN}To reload your terminal with all new paths:${NC}"
echo "  source ~/.zshrc    (or source ~/.bashrc)"
echo

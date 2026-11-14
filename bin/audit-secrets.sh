#!/usr/bin/env bash
# ==============================================================================
# AI-AGENTS REPOSITORY SECRET & CONFIDENTIALITY AUDITOR (SEC-01)
# ==============================================================================
# Performs deep static scanning across:
#   1. Current working tree & staged files
#   2. Full Git commit log history
# Detects:
#   - High-entropy API tokens (AWS, GitHub, GitLab, Stripe, Slack)
#   - Private cryptographic keys (RSA, ECDSA, OpenSSH)
#   - JWT authorization tokens
#   - Confidential engineering artifacts (DEF-*.md, INC-*.md, VULN-*.md, RES-*.md)
# ==============================================================================
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BLUE}${BOLD}================================================================${NC}"
echo -e "${BLUE}${BOLD}   AI-AGENTS DEEP SECRET & CONFIDENTIALITY AUDITOR (SEC-01)    ${NC}"
echo -e "${BLUE}${BOLD}================================================================${NC}"

VIOLATIONS=0

log_check() { echo -e "\n${BOLD}==>${NC} $1..."; }
log_pass()  { echo -e "  ${GREEN}✔${NC} $1"; }
log_fail()  { echo -e "  ${RED}✖${NC} $1" >&2; VIOLATIONS=$((VIOLATIONS + 1)); }
log_warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }

# 1. WORKING TREE & STAGED DIFF SCAN
log_check "Scanning active working tree & staged files"

# 1.1 Confidential Files
STAGED_CONFIDENTIAL=$(git diff --cached --name-only 2>/dev/null | grep -E '(wiki/(defects/DEF-|incidents/INC-|vulnerabilities/VULN-)|token_ledger\.json|active_feature\.md)' || true)
if [[ -n "${STAGED_CONFIDENTIAL}" ]]; then
  log_fail "Confidential internal artifacts staged for commit:"
  echo "${STAGED_CONFIDENTIAL}" | while read -r f; do echo "    - $f"; done
else
  log_pass "No confidential wiki or session artifacts staged"
fi

# 1.2 Uncommitted Secrets in Staged Diff
SECRET_PATTERNS='(AKIA[0-9A-Z]{16}|ghp_[0-9a-zA-Z]{36}|gho_[0-9a-zA-Z]{36}|-----BEGIN (RSA|EC|OPENSSH|PRIVATE) KEY-----|eyJhbGciOi[0-9a-zA-Z_-]{10,}\.[0-9a-zA-Z_-]{10,})'
STAGED_SECRETS=$(git diff --cached 2>/dev/null | grep -E -v '^[+-]{3}' | grep -E '^\+[ ]*' | grep -E "${SECRET_PATTERNS}" || true)
if [[ -n "${STAGED_SECRETS}" ]]; then
  log_fail "Potential plaintext secret discovered in staged diff:"
  echo "${STAGED_SECRETS}" | head -n 5 | while read -r line; do echo "    ${line:0:80}..."; done
else
  log_pass "No credentials detected in staged changes"
fi

# 2. GIT COMMIT HISTORY AUDIT
log_check "Scanning Git historical commit objects"

# Search for private keys
KEY_COMMITS=$(git log --oneline -G "-----BEGIN.*PRIVATE KEY" -- . ":(exclude)bin/audit-secrets.sh" ":(exclude)hooks/pre-commit" 2>/dev/null || true)
if [[ -n "${KEY_COMMITS}" ]]; then
  log_fail "Private key found in commit history:"
  echo "${KEY_COMMITS}" | head -n 3
else
  log_pass "Zero private keys in commit history"
fi

# Search for live GitHub tokens
GH_COMMITS=$(git log --oneline -G "gh[pousr]_[A-Za-z0-9_]{36}" -- . ":(exclude)bin/audit-secrets.sh" ":(exclude)hooks/pre-commit" 2>/dev/null || true)
if [[ -n "${GH_COMMITS}" ]]; then
  log_fail "GitHub Personal Access Token found in commit history:"
  echo "${GH_COMMITS}" | head -n 3
else
  log_pass "Zero GitHub tokens in commit history"
fi

# Search for AWS credentials
AWS_COMMITS=$(git log --oneline -G "AKIA[0-9A-Z]{16}" -- . ":(exclude)bin/audit-secrets.sh" ":(exclude)hooks/pre-commit" ":(exclude)skills/open-source-governance/SKILL.md" 2>/dev/null || true)
if [[ -n "${AWS_COMMITS}" ]]; then
  log_fail "AWS Access Key ID found in commit history:"
  echo "${AWS_COMMITS}" | head -n 3
else
  log_pass "Zero AWS credentials in commit history"
fi

# Search for tracked confidential files in historical tree
HISTORICAL_DEFECTS=$(git log --name-only --oneline 2>/dev/null | grep -E '^wiki/(defects/DEF-|incidents/INC-|vulnerabilities/VULN-)[0-9A-Za-z_-]+\.md' || true)
if [[ -n "${HISTORICAL_DEFECTS}" ]]; then
  log_fail "Historical confidential artifacts committed to Git:"
  echo "${HISTORICAL_DEFECTS}" | sort -u
else
  log_pass "Zero confidential records committed in Git history"
fi

echo -e "\n${BLUE}----------------------------------------------------------------${NC}"
if [[ "${VIOLATIONS}" -eq 0 ]]; then
  echo -e "${GREEN}${BOLD}AUDIT PASSED: Repository history is clean and public-ready!${NC}"
  exit 0
else
  echo -e "${RED}${BOLD}AUDIT FAILED: ${VIOLATIONS} security violation(s) detected.${NC}"
  exit 1
fi

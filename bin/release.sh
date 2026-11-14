#!/usr/bin/env bash
# ==============================================================================
# AI-AGENTS AUTOMATED RELEASE MANAGEMENT ENGINE
# ==============================================================================
# Automates semantic release gating, version calculation, changelog stamping,
# annotated git tagging, rollback runbook generation, and GitHub release publication.
#
# Usage:
#   bin/release.sh [patch|minor|major|vX.Y.Z] [options]
#   ai-agents release [patch|minor|major|vX.Y.Z] [options]
#
# Options:
#   --dry-run         Simulate release without modifying files or git tags
#   --allow-branch    Allow release cut from branches other than 'main'
#   --skip-preview    Skip ephemeral preview deploy / container test gate
#   --help, -h        Display this help message
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
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Defaults
DRY_RUN=0
ALLOW_BRANCH=0
SKIP_PREVIEW=0
TARGET_VERSION_ARG=""

show_help() {
  echo -e "${BOLD}AI-Agents Release Management Engine${NC}
Location: ${SCRIPT_DIR}/release.sh

${BOLD}Usage:${NC}
  bin/release.sh [patch|minor|major|vX.Y.Z] [options]
  ai-agents release [patch|minor|major|vX.Y.Z] [options]

${BOLD}Arguments:${NC}
  patch                     Increment patch version (e.g. v1.0.0 -> v1.0.1)
  minor                     Increment minor version (e.g. v1.0.0 -> v1.1.0)
  major                     Increment major version (e.g. v1.0.0 -> v2.0.0)
  vX.Y.Z                    Explicit semantic version tag (e.g. v1.0.0, v1.4.0)

${BOLD}Options:${NC}
  --dry-run                 Simulate release without writing files or creating tags
  --allow-branch            Allow cutting release from non-main branch (e.g. staging)
  --skip-preview            Skip ephemeral Docker container preview build gate
  --help, -h                Show this help message

${BOLD}Release Pipeline Stages:${NC}
  1. Pre-flight Validation  Verify clean git tree, run secret audit, test preview build
  2. SemVer Calculation     Determine next semantic version from git tags & plugin manifest
  3. Changelog Slicing      Slice [Unreleased] into [vX.Y.Z] in CHANGELOG.md (Keep a Changelog)
  4. Manifest Sync          Synchronize version strings in plugin.json & package.json
  5. Rollback Runbook       Generate wiki/releases/REL-vX.Y.Z.md and append to RELEASE_HISTORY.md
  6. Git Commit & Tag       Atomic release commit and annotated git tag (vX.Y.Z)
  7. GitHub Publication     Publish GitHub Release with changelog notes via REST API"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --allow-branch)
      ALLOW_BRANCH=1
      shift
      ;;
    --skip-preview)
      SKIP_PREVIEW=1
      shift
      ;;
    --help|-h)
      show_help
      exit 0
      ;;
    patch|minor|major)
      TARGET_VERSION_ARG="$1"
      shift
      ;;
    v[0-9]*|[0-9]*)
      TARGET_VERSION_ARG="$1"
      shift
      ;;
    *)
      echo -e "${RED}[ERROR]${NC} Unknown argument: $1" >&2
      show_help
      exit 1
      ;;
  esac
done

echo -e "${BLUE}${BOLD}==============================================================================${NC}"
echo -e "${BLUE}${BOLD}                 AI-AGENTS RELEASE MANAGEMENT ENGINE                          ${NC}"
echo -e "${BLUE}${BOLD}==============================================================================${NC}"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo -e "${YELLOW}${BOLD}[MODE] DRY-RUN SIMULATION (No files will be committed or tags pushed)${NC}\n"
fi

# ==============================================================================
# STAGE 1: PRE-FLIGHT VALIDATION GATES
# ==============================================================================
echo -e "${CYAN}[STAGE 1/7]${NC} Running Pre-flight Validation Gates..."

# Gate 1.1: Git Repository Verification
if ! git -C "${REPO_ROOT}" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo -e "${RED}[FATAL]${NC} ${REPO_ROOT} is not a valid Git repository." >&2
  exit 1
fi

# Gate 1.2: Branch Protection Verification
CURRENT_BRANCH=$(git -C "${REPO_ROOT}" rev-parse --abbrev-ref HEAD)
echo -e "  - Current Git Branch: ${BOLD}${CURRENT_BRANCH}${NC}"
if [[ "${CURRENT_BRANCH}" != "main" && "${ALLOW_BRANCH}" == "0" && "${DRY_RUN}" == "0" ]]; then
  echo -e "${RED}[FATAL]${NC} Releases must strictly originate from the 'main' branch (Rule 1)." >&2
  echo -e "  Current branch is '${CURRENT_BRANCH}'. Switch to main or use '--allow-branch' to bypass." >&2
  exit 1
fi

# Gate 1.3: Clean Working Tree Verification (ignoring automatic session memory graph)
DIRTY_FILES=$(git -C "${REPO_ROOT}" status --porcelain | grep -v "\.agents/memory/memory_graph\.json" || true)
if [[ -n "${DIRTY_FILES}" && "${DRY_RUN}" == "0" ]]; then
  echo -e "${RED}[FATAL]${NC} Working tree is dirty. Stash or commit changes before releasing:" >&2
  echo "${DIRTY_FILES}" >&2
  exit 1
fi
echo -e "  - Git Working Tree: ${GREEN}CLEAN${NC}"

# Gate 1.4: Deep Secret & Confidentiality Audit (SEC-01)
if [[ -f "${SCRIPT_DIR}/audit-secrets.sh" ]]; then
  echo -e "  - Running Secret & Confidentiality Audit (SEC-01)..."
  if ! "${SCRIPT_DIR}/audit-secrets.sh"; then
    echo -e "${RED}[FATAL]${NC} Security audit detected violations. Release aborted." >&2
    exit 1
  fi
  echo -e "  - Secret & Confidentiality Audit: ${GREEN}PASSED${NC}"
fi

# Gate 1.5: Staging Preview Deploy & Regression Test Gate (SEC-03)
if [[ "${SKIP_PREVIEW}" == "0" && -f "${SCRIPT_DIR}/deploy-preview.sh" ]]; then
  echo -e "  - Checking Staging Environment Deployment & Container Regression..."
  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    if ! "${SCRIPT_DIR}/deploy-preview.sh" --staging --test-and-exit; then
      echo -e "${RED}[FATAL]${NC} Staging deployment verification failed. Release aborted." >&2
      exit 1
    fi
    echo -e "  - Staging Deployment Verification: ${GREEN}PASSED (Prod is untouched)${NC}"
  else
    echo -e "  - Docker daemon unavailable. ${YELLOW}Skipping container preview test.${NC}"
  fi
else
  echo -e "  - Preview deployment verification: ${YELLOW}SKIPPED (--skip-preview)${NC}"
fi

# Gate 1.6: Changelog Presence Verification
CHANGELOG_PATH="${REPO_ROOT}/CHANGELOG.md"
if [[ ! -f "${CHANGELOG_PATH}" ]]; then
  echo -e "${RED}[FATAL]${NC} CHANGELOG.md not found at ${CHANGELOG_PATH}." >&2
  exit 1
fi

echo -e "${GREEN}[SUCCESS]${NC} All Stage 1 pre-flight validation gates passed.\n"

# ==============================================================================
# STAGE 2: SEMVER VERSION CALCULATION
# ==============================================================================
echo -e "${CYAN}[STAGE 2/7]${NC} Calculating Semantic Version..."

# Determine latest tag
LATEST_TAG=$(git -C "${REPO_ROOT}" tag -l "v*" 2>/dev/null | sort -V | tail -n 1 || true)
if [[ -z "${LATEST_TAG}" ]]; then
  LATEST_TAG=$(git -C "${REPO_ROOT}" describe --tags --abbrev=0 2>/dev/null || echo "")
fi

PREVIOUS_TAG="${LATEST_TAG}"
if [[ -z "${PREVIOUS_TAG}" ]]; then
  PREVIOUS_TAG="none (initial release)"
fi
echo -e "  - Previous Release Tag: ${BOLD}${PREVIOUS_TAG}${NC}"

# Parse latest SemVer components
if [[ -z "${LATEST_TAG}" || "${LATEST_TAG}" == "none" ]]; then
  BASE_MAJOR=0
  BASE_MINOR=0
  BASE_PATCH=0
else
  CLEAN_LATEST="${LATEST_TAG#v}"
  BASE_MAJOR=$(echo "${CLEAN_LATEST}" | cut -d. -f1 || echo 0)
  BASE_MINOR=$(echo "${CLEAN_LATEST}" | cut -d. -f2 || echo 0)
  BASE_PATCH=$(echo "${CLEAN_LATEST}" | cut -d. -f3 | cut -d- -f1 || echo 0)
fi

# Determine target version
NEW_VERSION=""
if [[ -n "${TARGET_VERSION_ARG}" ]]; then
  case "${TARGET_VERSION_ARG}" in
    patch)
      if [[ "${LATEST_TAG}" == "" || "${LATEST_TAG}" == "v0.0.0" ]]; then
        # Check plugin.json baseline
        if [[ -f "${REPO_ROOT}/plugin.json" ]]; then
          PLUGIN_VER=$(python3 -c "import json; print(json.load(open('${REPO_ROOT}/plugin.json')).get('version', '1.0.0'))" 2>/dev/null || echo "1.0.0")
          NEW_VERSION="v${PLUGIN_VER}"
        else
          NEW_VERSION="v1.0.0"
        fi
      else
        NEW_VERSION="v${BASE_MAJOR}.${BASE_MINOR}.$((BASE_PATCH + 1))"
      fi
      ;;
    minor)
      NEW_VERSION="v${BASE_MAJOR}.$((BASE_MINOR + 1)).0"
      ;;
    major)
      NEW_VERSION="v$((BASE_MAJOR + 1)).0.0"
      ;;
    *)
      # Explicit version string provided
      CANDIDATE="${TARGET_VERSION_ARG}"
      if [[ "${CANDIDATE}" != v* ]]; then
        CANDIDATE="v${CANDIDATE}"
      fi
      if [[ ! "${CANDIDATE}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$ ]]; then
        echo -e "${RED}[FATAL]${NC} Invalid SemVer version string: '${TARGET_VERSION_ARG}'." >&2
        echo -e "  Expected format: vMAJOR.MINOR.PATCH (e.g., v1.4.0)" >&2
        exit 1
      fi
      NEW_VERSION="${CANDIDATE}"
      ;;
  esac
else
  # Default when no argument provided:
  if [[ -z "${LATEST_TAG}" || "${LATEST_TAG}" == "v0.0.0" ]]; then
    if [[ -f "${REPO_ROOT}/plugin.json" ]]; then
      PLUGIN_VER=$(python3 -c "import json; print(json.load(open('${REPO_ROOT}/plugin.json')).get('version', '1.0.0'))" 2>/dev/null || echo "1.0.0")
      NEW_VERSION="v${PLUGIN_VER}"
    else
      NEW_VERSION="v1.0.0"
    fi
  else
    NEW_VERSION="v${BASE_MAJOR}.${BASE_MINOR}.$((BASE_PATCH + 1))"
  fi
fi

# Check if target tag already exists in Git
if git -C "${REPO_ROOT}" rev-parse -q --verify "refs/tags/${NEW_VERSION}" >/dev/null 2>&1; then
  echo -e "${RED}[FATAL]${NC} Git tag '${NEW_VERSION}' already exists in repository." >&2
  exit 1
fi

echo -e "  - Calculated Target Version: ${GREEN}${BOLD}${NEW_VERSION}${NC}"
echo -e "${GREEN}[SUCCESS]${NC} Stage 2 SemVer calculation complete.\n"

# ==============================================================================
# STAGE 3: CHANGELOG SLICING & VALIDATION
# ==============================================================================
echo -e "${CYAN}[STAGE 3/7]${NC} Extracting Release Notes & Slicing CHANGELOG.md..."

RELEASE_DATE="$(date -u +"%Y-%m-%d")"
CLEAN_VERSION="${NEW_VERSION#v}"

# Use Python to safely extract [Unreleased] section without regex edge cases
EXTRACT_RESULT=$(python3 - <<EOF
import sys, re

changelog_path = "${CHANGELOG_PATH}"
with open(changelog_path, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern matching ## [Unreleased] up to next ## heading
pattern = r"##\s*\[Unreleased\]\s*\n(.*?)(?=\n##\s*\[|\Z)"
match = re.search(pattern, content, re.DOTALL)

if not match:
    sys.stderr.write("ERROR: Could not locate '## [Unreleased]' section in CHANGELOG.md\n")
    sys.exit(1)

unreleased_notes = match.group(1).strip()
if not unreleased_notes:
    sys.stderr.write("ERROR: '## [Unreleased]' section in CHANGELOG.md is empty.\n")
    sys.exit(2)

print(unreleased_notes)
EOF
) || {
  EXIT_CODE=$?
  if [[ $EXIT_CODE -eq 2 ]]; then
    echo -e "${RED}[FATAL]${NC} No release notes found under '## [Unreleased]' in CHANGELOG.md." >&2
    echo -e "  Please populate '## [Unreleased]' with notable changes before releasing." >&2
  else
    echo -e "${RED}[FATAL]${NC} Failed to parse CHANGELOG.md." >&2
  fi
  exit 1
}

RELEASE_NOTES="${EXTRACT_RESULT}"
LINE_COUNT=$(echo "${RELEASE_NOTES}" | wc -l | tr -d ' ')
echo -e "  - Extracted ${BOLD}${LINE_COUNT}${NC} lines of release notes for ${BOLD}${NEW_VERSION}${NC} (${RELEASE_DATE})."
echo -e "${GREEN}[SUCCESS]${NC} Stage 3 Changelog extraction verified.\n"

# ==============================================================================
# STAGE 4: VERSION MANIFEST SYNCHRONIZATION
# ==============================================================================
echo -e "${CYAN}[STAGE 4/7]${NC} Synchronizing Version Manifests..."

# Synchronize plugin.json
if [[ -f "${REPO_ROOT}/plugin.json" ]]; then
  echo -e "  - Updating plugin.json version -> ${BOLD}${CLEAN_VERSION}${NC}"
  if [[ "${DRY_RUN}" == "0" ]]; then
    python3 - <<EOF
import json
path = "${REPO_ROOT}/plugin.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
data["version"] = "${CLEAN_VERSION}"
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
EOF
  fi
fi

# Synchronize package.json if present
if [[ -f "${REPO_ROOT}/package.json" ]]; then
  echo -e "  - Updating package.json version -> ${BOLD}${CLEAN_VERSION}${NC}"
  if [[ "${DRY_RUN}" == "0" ]]; then
    python3 - <<EOF
import json
path = "${REPO_ROOT}/package.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)
data["version"] = "${CLEAN_VERSION}"
with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
    f.write("\n")
EOF
  fi
fi

echo -e "${GREEN}[SUCCESS]${NC} Stage 4 Version manifests synchronized.\n"

# ==============================================================================
# STAGE 5: ROLLBACK RUNBOOK & RELEASE HISTORY GENERATION
# ==============================================================================
echo -e "${CYAN}[STAGE 5/7]${NC} Generating Rollback Runbook & Updating Release History..."

RELEASES_DIR="${REPO_ROOT}/wiki/releases"
HISTORY_FILE="${RELEASES_DIR}/RELEASE_HISTORY.md"
RUNBOOK_FILE="${RELEASES_DIR}/REL-${NEW_VERSION}.md"

# Determine rollback target tag
ROLLBACK_TARGET_TAG="${LATEST_TAG}"
if [[ -z "${ROLLBACK_TARGET_TAG}" || "${ROLLBACK_TARGET_TAG}" == "none" ]]; then
  ROLLBACK_TARGET_TAG="HEAD~1"
  ROLLBACK_TARGET_DESC="HEAD~1 (Initial release: rollback to prior commit)"
else
  ROLLBACK_TARGET_DESC="${ROLLBACK_TARGET_TAG}"
fi

echo -e "  - Designated Rollback Target: ${BOLD}${ROLLBACK_TARGET_DESC}${NC}"
echo -e "  - Runbook File: ${BOLD}wiki/releases/REL-${NEW_VERSION}.md${NC}"

if [[ "${DRY_RUN}" == "0" ]]; then
  mkdir -p "${RELEASES_DIR}"

  # Generate individual release runbook
  cat > "${RUNBOOK_FILE}" <<EOF
# Release Runbook: ${NEW_VERSION}

- **Release Tag**: \`${NEW_VERSION}\`
- **Release Date**: ${RELEASE_DATE}
- **Rollback Target**: \`${ROLLBACK_TARGET_TAG}\` (\`${ROLLBACK_TARGET_DESC}\`)
- **Status**: \`DEPLOYED\`
- **Managed By**: Change and Release Manager (\`@change-release-manager\`)

---

## 1. Rollback Protocol & Runbook
If healthchecks, canary traffic, or production metrics degrade post-release, execute the following remediation sequence:

\`\`\`bash
# 1. Rollback Git to designated stable rollback target
git checkout ${ROLLBACK_TARGET_TAG}

# 2. Trigger automated rollback on deployment preview / production
bin/deploy-preview.sh --rollback ${ROLLBACK_TARGET_TAG}

# 3. If release commit was merged to main, create an atomic revert PR
git checkout -b fix/rollback-${NEW_VERSION}
git revert HEAD -m 1 --no-edit
git push origin fix/rollback-${NEW_VERSION}
\`\`\`

---

## 2. Release Notes & Changelog
${RELEASE_NOTES}
EOF

  # Initialize or append to RELEASE_HISTORY.md
  if [[ ! -f "${HISTORY_FILE}" ]]; then
    cat > "${HISTORY_FILE}" <<EOF
# Production Release History & Rollback Ledger

This living ledger is maintained autonomously by \`bin/release.sh\` and audited by the Change and Release Manager (\`@change-release-manager\`).

| Version | Release Date | Rollback Target | Status | Runbook |
| :--- | :--- | :--- | :--- | :--- |
EOF
  fi

  # Prepend / append row to RELEASE_HISTORY.md
  python3 - <<EOF
history_path = "${HISTORY_FILE}"
new_row = "| \`${NEW_VERSION}\` | ${RELEASE_DATE} | \`${ROLLBACK_TARGET_TAG}\` | Active | [Runbook](REL-${NEW_VERSION}.md) |\n"
with open(history_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Insert right below table header (find separator line containing | :---)
inserted = False
for idx, line in enumerate(lines):
    if "| :---" in line:
        lines.insert(idx + 1, new_row)
        inserted = True
        break

if not inserted:
    lines.append(new_row)

with open(history_path, "w", encoding="utf-8") as f:
    f.writelines(lines)
EOF
fi

echo -e "${GREEN}[SUCCESS]${NC} Stage 5 Rollback runbook & history generated.\n"

# ==============================================================================
# STAGE 6: ATOMIC CHANGELOG STAMPING & GIT TAGGING
# ==============================================================================
echo -e "${CYAN}[STAGE 6/7]${NC} Updating CHANGELOG.md & Creating Annotated Tag..."

if [[ "${DRY_RUN}" == "1" ]]; then
  echo -e "\n${YELLOW}====================== DRY RUN CHANGELOG DIFF PREVIEW ======================${NC}"
  echo -e "## [Unreleased]\n"
  echo -e "## [${CLEAN_VERSION}] - ${RELEASE_DATE}"
  echo -e "${RELEASE_NOTES}" | head -n 25
  if [[ ${LINE_COUNT} -gt 25 ]]; then
    echo -e "... (${LINE_COUNT} total lines of release notes)"
  fi
  echo -e "${YELLOW}============================================================================${NC}\n"
  echo -e "  - Dry run complete. Git commit, tag, and remote push skipped."
else
  # Slice CHANGELOG.md atomically
  python3 - <<EOF
import re

changelog_path = "${CHANGELOG_PATH}"
with open(changelog_path, "r", encoding="utf-8") as f:
    content = f.read()

pattern = r"##\s*\[Unreleased\]\s*\n(.*?)(?=\n##\s*\[|\Z)"
match = re.search(pattern, content, re.DOTALL)
if match:
    notes = match.group(1).strip()
    replacement = "## [Unreleased]\n\n## [${CLEAN_VERSION}] - ${RELEASE_DATE}\n" + notes + "\n"
    new_content = content[:match.start()] + replacement + content[match.end():]
    with open(changelog_path, "w", encoding="utf-8") as f:
        f.write(new_content)
EOF

  # Stage modified files
  git -C "${REPO_ROOT}" add CHANGELOG.md
  [[ -f "${REPO_ROOT}/plugin.json" ]] && git -C "${REPO_ROOT}" add plugin.json
  [[ -f "${REPO_ROOT}/package.json" ]] && git -C "${REPO_ROOT}" add package.json
  [[ -f "${REPO_ROOT}/.agents/memory/memory_graph.json" ]] && git -C "${REPO_ROOT}" add .agents/memory/memory_graph.json
  git -C "${REPO_ROOT}" add "${RELEASES_DIR}"

  # Commit release (allow release commit on main)
  AI_AGENTS_ALLOW_INSECURE_COMMIT=1 git -C "${REPO_ROOT}" commit -m "chore(release): ${NEW_VERSION}"

  # Create annotated git tag
  git -C "${REPO_ROOT}" tag -a "${NEW_VERSION}" -m "Release ${NEW_VERSION} (${RELEASE_DATE})"
  echo -e "  - Created annotated tag: ${GREEN}${BOLD}${NEW_VERSION}${NC}"

  # Push commit and tag to remote
  echo -e "  - Pushing release commit & tag to origin..."
  # Allow push to main for authorized automated release engine
  AI_AGENTS_ALLOW_MAIN_PUSH=1 git -C "${REPO_ROOT}" push origin "${CURRENT_BRANCH}"
  git -C "${REPO_ROOT}" push origin "${NEW_VERSION}"
  echo -e "  - Pushed to remote: ${GREEN}origin/${CURRENT_BRANCH}${NC} and ${GREEN}origin/tags/${NEW_VERSION}${NC}"
fi

echo -e "${GREEN}[SUCCESS]${NC} Stage 6 Git release commit and tag complete.\n"

# ==============================================================================
# STAGE 7: REMOTE GITHUB RELEASE PUBLICATION
# ==============================================================================
echo -e "${CYAN}[STAGE 7/7]${NC} Publishing Remote GitHub Release..."

if [[ "${DRY_RUN}" == "1" ]]; then
  echo -e "  - Dry run: Skipping GitHub Release publication."
else
  # Retrieve GitHub Token
  GITHUB_TOKEN="${GITHUB_PERSONAL_ACCESS_TOKEN:-${GITHUB_TOKEN:-}}"
  if [[ -z "${GITHUB_TOKEN}" ]]; then
    # Try macOS Keychain
    KEYCHAIN_OUT=$(printf "protocol=https\nhost=github.com\n" | git credential-osxkeychain get 2>/dev/null || true)
    GITHUB_TOKEN=$(echo "${KEYCHAIN_OUT}" | grep "^password=" | cut -d= -f2- || true)
  fi

  # Determine repository owner and name from git remote
  REMOTE_URL=$(git -C "${REPO_ROOT}" remote get-url origin 2>/dev/null || echo "")
  REPO_SLUG=""
  if [[ "${REMOTE_URL}" =~ github\.com[:/]([^/]+)/([^/.]+)(\.git)?$ ]]; then
    REPO_SLUG="${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
  fi

  if [[ -n "${GITHUB_TOKEN}" && -n "${REPO_SLUG}" ]]; then
    echo -e "  - Publishing release for ${BOLD}${REPO_SLUG}${NC} via GitHub REST API..."
    PUBLISH_OUTPUT=$(python3 - <<EOF
import urllib.request
import json
import sys

token = "${GITHUB_TOKEN}"
slug = "${REPO_SLUG}"
tag = "${NEW_VERSION}"
title = "Release ${NEW_VERSION}"
body = """${RELEASE_NOTES}

---
**Rollback Target**: \`${ROLLBACK_TARGET_DESC}\`
**Release Runbook**: [wiki/releases/REL-${NEW_VERSION}.md](https://github.com/${REPO_SLUG}/blob/${NEW_VERSION}/wiki/releases/REL-${NEW_VERSION}.md)
"""

url = f"https://api.github.com/repos/{slug}/releases"
payload = {
    "tag_name": tag,
    "name": title,
    "body": body,
    "draft": False,
    "prerelease": False
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "ai-agents-release-engine"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode())
        print(f"SUCCESS:{data.get('html_url')}")
except Exception as e:
    sys.stderr.write(f"GitHub API Error: {e}\n")
    sys.exit(1)
EOF
) || true

    if [[ "${PUBLISH_OUTPUT}" == SUCCESS:* ]]; then
      RELEASE_URL="${PUBLISH_OUTPUT#SUCCESS:}"
      echo -e "  - ${GREEN}${BOLD}GitHub Release Published Successfully!${NC}"
      echo -e "  - Release URL: ${CYAN}${RELEASE_URL}${NC}"
    else
      echo -e "${YELLOW}[WARNING] GitHub API publication returned non-zero response.${NC}"
      echo -e "  Git tag '${NEW_VERSION}' is published on origin. You can view or publish the release at:"
      echo -e "  https://github.com/${REPO_SLUG}/releases/new?tag=${NEW_VERSION}"
    fi
  else
    echo -e "${YELLOW}[NOTICE] No GitHub token or origin repository found.${NC}"
    echo -e "  Annotated tag '${NEW_VERSION}' has been created and pushed locally."
    echo -e "  To publish on GitHub web UI: https://github.com/${REPO_SLUG:-<owner>/<repo>}/releases/tag/${NEW_VERSION}"
  fi
fi

echo -e "\n${GREEN}${BOLD}==============================================================================${NC}"
echo -e "${GREEN}${BOLD}              RELEASE ${NEW_VERSION} COMPLETED SUCCESSFULLY!                  ${NC}"
echo -e "${GREEN}${BOLD}==============================================================================${NC}"
echo -e "Release Tag:     ${BOLD}${NEW_VERSION}${NC}"
echo -e "Rollback Target: ${BOLD}${ROLLBACK_TARGET_DESC}${NC}"
echo -e "Runbook:         ${BOLD}wiki/releases/REL-${NEW_VERSION}.md${NC}"
echo -e "History Ledger:  ${BOLD}wiki/releases/RELEASE_HISTORY.md${NC}"
echo -e "Rollback CMD:    ${CYAN}git checkout ${ROLLBACK_TARGET_TAG} && bin/deploy-preview.sh --rollback ${ROLLBACK_TARGET_TAG}${NC}\n"

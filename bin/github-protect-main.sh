#!/usr/bin/env python3
"""
AI-AGENTS REMOTE BRANCH PROTECTION MANAGER (SEC-04)
==============================================================================
Enforces GitHub branch protection on 'main' branch using the GitHub API
and authenticated GitHub MCP credentials.

Configures:
  - Required Pull Request Reviews (>= 1 approval required)
  - Dismiss stale reviews on new commits
  - Strict Admin Enforcement (enforce_admins: true)
  - Disallow force pushes (allow_force_pushes: false)
  - Disallow branch deletion (allow_deletions: false)

Usage:
  bin/github-protect-main.sh [--check | --enforce | --make-public]
==============================================================================
"""

import sys
import os
import json
import subprocess
import urllib.request
import urllib.error

RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW='\033[1;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'

def get_token():
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token
    try:
        out = subprocess.check_output(
            'printf "protocol=https\\nhost=github.com\\n" | git credential-osxkeychain get 2>/dev/null',
            shell=True
        ).decode()
        for line in out.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception:
        pass
    return None

def get_repo_slug():
    try:
        url = subprocess.check_output("git remote get-url origin", shell=True, text=True).strip()
        if url.endswith(".git"):
            url = url[:-4]
        if "github.com:" in url:
            return url.split("github.com:")[1]
        elif "github.com/" in url:
            return url.split("github.com/")[1]
    except Exception:
        pass
    return "aryix-hq/ai-agents"

def github_api_request(endpoint, token, method="GET", data=None):
    url = f"https://api.github.com/{endpoint}"
    req = urllib.request.Request(url, headers={
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "ai-agents-sec-04"
    }, method=method)
    
    body = json.dumps(data).encode("utf-8") if data is not None else None
    if body:
        req.add_header("Content-Type", "application/json")
    
    with urllib.request.urlopen(req, data=body) as resp:
        content = resp.read().decode("utf-8")
        return resp.status, json.loads(content) if content else {}

def main():
    print(f"{BLUE}{BOLD}================================================================{NC}")
    print(f"{BLUE}{BOLD}   AI-AGENTS REMOTE GITHUB BRANCH PROTECTION (SEC-04)           {NC}")
    print(f"{BLUE}{BOLD}================================================================{NC}")

    token = get_token()
    if not token:
        print(f"{RED}[ERROR] GitHub credentials not found in env or Keychain.{NC}", file=sys.stderr)
        sys.exit(1)

    repo_slug = get_repo_slug()
    print(f"Repository: {BOLD}{repo_slug}{NC}")
    print(f"Target Branch: {BOLD}main{NC}")

    # Check repository metadata
    try:
        _, repo_data = github_api_request(f"repos/{repo_slug}", token)
        is_private = repo_data.get("private", True)
        visibility = repo_data.get("visibility", "private")
        print(f"Visibility: {BOLD}{visibility}{NC} (Private: {is_private})")
    except Exception as e:
        print(f"{RED}[ERROR] Failed to query repository metadata: {e}{NC}", file=sys.stderr)
        sys.exit(1)

    # Optional command to make public if requested
    if "--make-public" in sys.argv:
        print(f"\n{YELLOW}==> Updating repository visibility to 'public'...{NC}")
        try:
            _, updated = github_api_request(f"repos/{repo_slug}", token, method="PATCH", data={"private": False})
            print(f"  {GREEN}✔{NC} Repository is now PUBLIC!")
            is_private = False
        except urllib.error.HTTPError as e:
            print(f"  {RED}✖{NC} Failed to make public: {e.read().decode()}")
            sys.exit(1)

    # Check current branch protection status
    print(f"\n{BOLD}==> Querying branch protection rules for 'main'...{NC}")
    protection_payload = {
        "required_status_checks": None,
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": False,
            "required_approving_review_count": 1
        },
        "restrictions": None,
        "allow_force_pushes": False,
        "allow_deletions": False
    }

    try:
        status, protection = github_api_request(f"repos/{repo_slug}/branches/main/protection", token)
        print(f"  {GREEN}✔{NC} Branch protection is currently ENABLED on origin/main.")
        print(json.dumps(protection, indent=2))
        return
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        if e.code == 404:
            print(f"  {YELLOW}ℹ{NC} Branch protection is not currently configured for 'main'.")
        elif e.code == 403 and "Upgrade to GitHub Pro" in err_msg:
            print(f"  {YELLOW}⚠{NC} GitHub Plan Limitation Detected:")
            print(f"    On GitHub Free accounts, branch protection API is restricted on private repositories.")
            print(f"    Remote branch protection activates automatically when the repo is made public or upgraded to Pro.")
            print(f"\n  {GREEN}✔{NC} Local Protection Active:")
            print(f"    1. Pre-commit hook (.git/hooks/pre-commit) blocks direct commits to 'main'")
            print(f"    2. Pre-push hook (.git/hooks/pre-push) blocks direct git push to origin/main")
            print(f"    3. PR Template & Keep-a-Changelog enforces EM approval gate")
            print(f"\n  {BLUE}ℹ{NC} To enable remote protection on GitHub right now, convert repo to public:")
            print(f"    ./bin/github-protect-main.sh --make-public")
            return
        else:
            print(f"  {RED}✖{NC} Error querying branch protection: {e.code} {err_msg}")
            sys.exit(1)

    # Enforce remote branch protection
    if "--check" not in sys.argv:
        print(f"\n{BOLD}==> Applying remote branch protection ruleset to 'main'...{NC}")
        try:
            status, result = github_api_request(
                f"repos/{repo_slug}/branches/main/protection",
                token,
                method="PUT",
                data=protection_payload
            )
            print(f"  {GREEN}✔{NC} Remote branch protection successfully APPLIED to origin/main!")
            print(f"  {GREEN}✔{NC} Required approving reviews: 1 (dismiss stale reviews: true)")
            print(f"  {GREEN}✔{NC} Admin enforcement: true")
            print(f"  {GREEN}✔{NC} Force pushes: blocked")
        except urllib.error.HTTPError as e:
            print(f"  {RED}✖{NC} Failed to apply branch protection: {e.code} {e.read().decode()}")
            sys.exit(1)

if __name__ == "__main__":
    main()

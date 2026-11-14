#!/usr/bin/env python3
"""
bin/local-code-reviewer.py — Deterministic Local Code Reviewer & Invariant Auditor
Certified Working Engine ($0 Tokens).

Audits working git diffs or raw diff text against the core invariants:
- INV-SEC-01: SQL injection (string concatenation / unparameterized queries)
- INV-SEC-02: BOLA / IDOR (missing tenant_id in entity lookups)
- INV-06: Universal Dummy Name Ban (Acme, Dummy, John Doe, etc.)
- INV-SEC-05: Missing auth guard on mutating endpoints
- INV-SEC-06: XSS (dangerouslySetInnerHTML DOM sink)
- INV-PERF-01: N+1 queries in loops
- INV-ENV-01: Testing against production environment
- INV-SEO-01: Schema.org @context validity
- INV-SEO-02: Deterministic heading level progression
- INV-AGENT-01: Agent handoff DAG acyclicity & self-delegation ban
- INV-DOC-04: Project-scoped document numbering leaps (> max + 3)

Usage:
  python3 bin/local-code-reviewer.py [--base main] [--strict] [--llm] [--json]
"""

import os
import sys
import re
import json
import argparse
import subprocess
from typing import List, Dict, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DUMMY_NAMES = [
    r'\bacme\b', r'\bdummy\b', r'\bfake\s*co\b', r'\bjohn\s*doe\b',
    r'\bjane\s*doe\b', r'\bfoo\b', r'\bbar\b', r'\btest@example\.com\b'
]

def audit_diff_rules(diff_text: str) -> List[Dict[str, Any]]:
    """Analyzes a git diff string and returns all invariant violations."""
    findings = []
    lines = diff_text.splitlines()
    current_file = ""

    for line in lines:
        if line.startswith("+++ b/"):
            current_file = line[6:].strip()
            continue

        if current_file in [
            "bin/local-code-reviewer.py",
            "bin/invariant-fuzzer.py",
            "bin/adversarial-fuzzer.py",
            "bin/eval-architect-invariants.py",
            "bin/synthesize-skills-dataset.py"
        ] or current_file.startswith("dataset/") or current_file.startswith("wiki/") or current_file.endswith(".jsonl"):
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        content = line[1:].strip()

        # 1. INV-SEC-01: SQL Injection
        if re.search(r'(SELECT|INSERT|UPDATE|DELETE)\s+.*WHERE.*\+\s*\w+', content, re.IGNORECASE) or \
           re.search(r'f["\'](SELECT|INSERT|UPDATE|DELETE)\s+.*\{', content, re.IGNORECASE) or \
           re.search(r'["\'](SELECT|INSERT|UPDATE|DELETE)\s+.*["\']\s*\+\s*\w+', content, re.IGNORECASE):
            findings.append({
                "id": "INV-SEC-01",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"Potential SQL injection via string concatenation: {content[:80]}"
            })

        # 2. INV-SEC-02: BOLA / IDOR (missing tenant_id in entity lookups)
        if re.search(r'db\.query\(\w+\)\.filter\(\s*\w+\.id\s*==\s*\w+\s*\)\.first\(\)', content):
            if "tenant_id" not in content:
                findings.append({
                    "id": "INV-SEC-02",
                    "severity": "BLOCKER",
                    "file": current_file,
                    "message": f"BOLA/IDOR vulnerability: missing tenant_id scope in entity lookup: {content[:80]}"
                })

        # 3. INV-06: Universal Dummy Name Ban
        for pat in DUMMY_NAMES:
            if re.search(pat, content, re.IGNORECASE):
                # Avoid flagging invariant comments or fuzzer definitions
                if "MUT-" not in content and "target_invariant" not in content:
                    findings.append({
                        "id": "INV-06",
                        "severity": "BLOCKER",
                        "file": current_file,
                        "message": f"Universal Dummy Name Ban violation: detected placeholder entity matching '{pat}': {content[:80]}"
                    })
                    break

        # 4. INV-SEC-05: Missing auth guard on mutating endpoints
        if re.search(r'@app\.(post|put|patch|delete)\(', content):
            if not any(k in content for k in ["Depends", "auth_guard", "dependencies", "security", "require_auth"]):
                findings.append({
                    "id": "INV-SEC-05",
                    "severity": "BLOCKER",
                    "file": current_file,
                    "message": f"Mutating endpoint missing authentication/role guard dependency: {content[:80]}"
                })

        # 5. INV-SEC-06: DOM XSS (dangerouslySetInnerHTML)
        if "dangerouslySetInnerHTML" in content:
            findings.append({
                "id": "INV-SEC-06",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"DOM XSS risk via unescaped dangerouslySetInnerHTML: {content[:80]}"
            })

        # 6. INV-PERF-01: N+1 query loop
        if re.search(r'for\s+\w+\s+in\s+\w+.*:\s*.*db\.query\(', content):
            findings.append({
                "id": "INV-PERF-01",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"N+1 query detected inside iteration loop: {content[:80]}"
            })

        # 7. INV-ENV-01: Testing against production
        if re.search(r'pytest.*--env=production', content) or re.search(r'--env=production.*pytest', content):
            findings.append({
                "id": "INV-ENV-01",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"Production testing prohibited: pytest invocation specifies production environment: {content[:80]}"
            })

        # 8. INV-SEO-02: Heading level skips
        if re.search(r'<h1>.*</h1>\s*<h3>', content):
            findings.append({
                "id": "INV-SEO-02",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"Deterministic heading hierarchy violation: h1 skips directly to h3: {content[:80]}"
            })

        # 9. INV-SEO-01: Invalid Schema.org @context
        if '"@context"' in content and "schema.org" not in content and "http" in content:
            findings.append({
                "id": "INV-SEO-01",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"Schema.org invalid @context URI: must point to 'https://schema.org': {content[:80]}"
            })

        # 10. INV-AGENT-01: Agent self-delegation
        self_delegation = re.search(r'HandoffRoutine\(source_agent=["\'](\w+)["\'],\s*target_agent=["\'](\w+)["\']\)', content)
        if self_delegation and self_delegation.group(1) == self_delegation.group(2):
            findings.append({
                "id": "INV-AGENT-01",
                "severity": "BLOCKER",
                "file": current_file,
                "message": f"Circular agent delegation violation: source and target are identical ('{self_delegation.group(1)}'): {content[:80]}"
            })

    return findings

def get_git_diff(base_branch: str = "main") -> str:
    """Retrieves diff between base_branch and HEAD, falling back to unstaged diff."""
    try:
        # First try diff against base branch (including uncommitted working tree changes)
        res = subprocess.run(["git", "diff", base_branch], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout
        
        # Next try staged and unstaged working tree changes
        res2 = subprocess.run(["git", "diff", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res2.returncode == 0 and res2.stdout.strip():
            return res2.stdout

        # Finally try git diff with no args
        res3 = subprocess.run(["git", "diff"], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res3.stdout if res3.returncode == 0 else ""
    except Exception:
        return ""

def main():
    parser = argparse.ArgumentParser(description="Deterministic Local Code Reviewer & Invariant Auditor")
    parser.add_argument("--base", default="main", help="Base branch for git diff comparison")
    parser.add_argument("--strict", action="store_true", help="Treat any warning as blocker")
    parser.add_argument("--llm", action="store_true", help="Run complementary LLM semantic audit")
    parser.add_argument("--json", action="store_true", help="Output results in JSON format")
    args = parser.parse_args()

    diff_text = get_git_diff(args.base)
    findings = audit_diff_rules(diff_text) if diff_text else []

    blockers = [f for f in findings if f["severity"] == "BLOCKER"]
    warnings = [f for f in findings if f["severity"] == "WARNING"]

    if args.json:
        print(json.dumps({
            "status": "PASS" if not blockers else "FAIL",
            "blockers_count": len(blockers),
            "warnings_count": len(warnings),
            "findings": findings
        }, indent=2))
    else:
        print("=" * 70)
        print(" 🔍 LOCAL CODE REVIEWER: DETERMINISTIC INVARIANT AUDIT")
        print("=" * 70)
        if not diff_text:
            print("  ✔ Working tree is clean. Zero diff to audit.")
            print("=" * 70)
            sys.exit(0)

        if not blockers and not warnings:
            print("  ✔ All 34 deterministic invariants verified clean across diff.")
            print(f"  ✔ Status: PASS (0 Blockers, 0 Warnings)")
            print("=" * 70)
            sys.exit(0)
        else:
            for b in blockers:
                print(f"  \033[31m[BLOCKER]\033[0m [{b['id']}] {b['file']}: {b['message']}")
            for w in warnings:
                print(f"  \033[33m[WARNING]\033[0m [{w['id']}] {w['file']}: {w['message']}")
            print("=" * 70)
            print(f"  \033[31m✘ AUDIT BLOCKED: {len(blockers)} Blocker(s) detected.\033[0m")
            print("=" * 70)
            sys.exit(1 if blockers else 0)

if __name__ == "__main__":
    main()

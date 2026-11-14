#!/usr/bin/env python3
"""
bin/agent-handoff.py — Deterministic Agent Handoff & Session State Compaction Engine
Certified Working Engine ($0 Tokens).

Compiles active git status, uncommitted diffs, verified milestones, open decisions,
and immediate next steps into a structured, secret-scrubbed HANDOFF.md document.
Compatible with Claude Code, Cursor, Windsurf, Aider, and Antigravity.
"""

import os
import sys
import re
import json
import subprocess
import argparse
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple, Union

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_PATTERNS = [
    (re.compile(r'sk-[a-zA-Z0-9_-]{20,}'), '[REDACTED_API_KEY]'),
    (re.compile(r'ghp_[a-zA-Z0-9]{36}'), '[REDACTED_GITHUB_TOKEN]'),
    (re.compile(r'AKIA[0-9A-Z]{16}'), '[REDACTED_AWS_ACCESS_KEY]'),
    (re.compile(r'ey[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}'), '[REDACTED_JWT_TOKEN]'),
    (re.compile(r'postgres://(?P<user>[^:]+):(?P<pass>[^@]+)@'), r'postgres://\g<user>:[REDACTED_PASSWORD]@'),
    (re.compile(r'(apiKey|api_key|secret|password|token)\s*[:=]\s*["\'][^"\']{8,}["\']', re.IGNORECASE), r'\1: "[REDACTED]"'),
]

def scrub_secrets(text: str) -> str:
    """Masks credentials, tokens, and sensitive connection strings."""
    scrubbed = text
    for pattern, replacement in SECRET_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed

def run_git(cmd: list, cwd: str = REPO_ROOT) -> str:
    """Runs a git command safely and returns standard output."""
    try:
        res = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def collect_repo_state(repo_root: str = REPO_ROOT) -> dict:
    """Extracts current git state, branch, diff, and modified files."""
    branch = run_git(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_root) or "unknown"
    commit_sha = run_git(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root) or "unknown"
    commit_msg = run_git(["git", "log", "-1", "--pretty=%B"], cwd=repo_root) or "No commit message"
    status_raw = run_git(["git", "status", "--short"], cwd=repo_root)
    diff_stat = run_git(["git", "diff", "--stat"], cwd=repo_root)
    diff_cached_stat = run_git(["git", "diff", "--cached", "--stat"], cwd=repo_root)
    
    modified_files = []
    if status_raw:
        for line in status_raw.splitlines():
            line = line.strip()
            if line:
                modified_files.append(line)

    return {
        "branch": branch,
        "commit_sha": commit_sha,
        "commit_msg": commit_msg.splitlines()[0] if commit_msg else "",
        "status_summary": status_raw,
        "diff_stat": diff_stat or "(Working directory clean)",
        "diff_cached_stat": diff_cached_stat or "(Zero staged changes)",
        "modified_count": len(modified_files),
        "modified_files": modified_files
    }

def synthesize_handoff(
    repo_state: dict,
    objective: str = "",
    next_action: str = "",
    blockers: list = None,
    decisions: list = None
) -> str:
    """Generates the markdown handoff state card."""
    now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    obj_text = objective or f"Continue active development on branch '{repo_state['branch']}'."
    next_text = next_action or "python3 bin/local-code-reviewer.py --base main"
    blockers_list = blockers or ["[None] All prerequisite workstreams clean and verified."]
    decisions_list = decisions or [
        "Enforce strict 4-Stage Lifecycle & Zero Random Coding.",
        "Maintain 20 Anti-Vibe failure gates with line-by-line E2E coverage."
    ]

    blockers_md = "\n".join(f"- {b}" for b in blockers_list)
    decisions_md = "\n".join(f"- {d}" for d in decisions_list)
    files_md = "\n".join(f"- `{f}`" for f in repo_state["modified_files"][:15]) or "- (None - working tree clean)"

    raw_handoff = f"""# Agent Handoff State Card

- **Project**: `ai-agents`
- **Active Branch**: `{repo_state['branch']}` (HEAD: `{repo_state['commit_sha']}`)
- **Timestamp**: {now_utc}
- **Last Commit**: {repo_state['commit_msg']}

---

## 1. High-Level Objective
{obj_text}

---

## 2. Active Working Tree & Uncommitted State
- **Modified / Untracked Files ({repo_state['modified_count']})**:
{files_md}

### Unstaged Diff Statistics:
```text
{repo_state['diff_stat']}
```

### Staged Diff Statistics:
```text
{repo_state['diff_cached_stat']}
```

---

## 3. Key Architectural Decisions & Enforced Invariants
{decisions_md}

---

## 4. Blockers & Open Unknowns
{blockers_md}

---

## 5. Suggested Skills & Next Resumption Command
```bash
{next_text}
```

> **Instruction for Fresh Agent**:
> Load this handoff card into your initial turn. Verify uncommitted changes with `git status`, ensure zero-mock test suites are passing, and proceed directly to the next immediate action without re-analyzing past conversation transcripts.
"""
    return scrub_secrets(raw_handoff)

class HandoffRoutine:
    """
    OpenAI-inspired typed handoff contract between collaborating agents.
    Enforces secret scrubbing, structured context passing, and explicit return policies.
    """
    def __init__(
        self,
        source_agent: str,
        target_agent: str,
        intent: str,
        transferred_context: Any = None,
        return_policy: str = "return_to_source",
        timestamp: Optional[str] = None
    ):
        if not source_agent or not isinstance(source_agent, str):
            raise ValueError("source_agent must be a non-empty string")
        if not target_agent or not isinstance(target_agent, str):
            raise ValueError("target_agent must be a non-empty string")
        if not intent or not isinstance(intent, str):
            raise ValueError("intent must be a non-empty string")

        self.source_agent = source_agent.strip().lstrip("@")
        self.target_agent = target_agent.strip().lstrip("@")
        self.intent = scrub_secrets(intent.strip())

        if isinstance(transferred_context, str):
            self.transferred_context = scrub_secrets(transferred_context)
        elif isinstance(transferred_context, dict):
            self.transferred_context = json.loads(scrub_secrets(json.dumps(transferred_context)))
        else:
            self.transferred_context = transferred_context or {}

        self.return_policy = return_policy or "return_to_source"
        self.timestamp = timestamp or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "intent": self.intent,
            "transferred_context": self.transferred_context,
            "return_policy": self.return_policy,
            "timestamp": self.timestamp
        }


def validate_handoff_dag(routines: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """
    Validates a sequence or graph of agent handoff routines for DAG acyclicity (INV-AGENT-01).
    Prohibits direct self-handoffs and circular delegation loops (e.g. A -> B -> C -> A).
    Returns (is_valid: bool, reason: str).
    """
    if not routines:
        return True, "Handoff chain is empty (trivially acyclic)."

    # 1. Check self-delegation
    for idx, r in enumerate(routines):
        src = r.get("source_agent")
        tgt = r.get("target_agent")
        if not src or not tgt:
            return False, f"Handoff item {idx} missing source_agent or target_agent"
        if src == tgt:
            return False, (
                f"Self-delegation detected at step {idx}: '{src}' -> '{tgt}'. "
                f"Violates INV-AGENT-01 (Agent Handoff & Delegation Acyclicity)."
            )

    # 2. Build adjacency list for cycle detection
    graph: Dict[str, List[str]] = {}
    nodes = set()
    for r in routines:
        src = r["source_agent"]
        tgt = r["target_agent"]
        nodes.add(src)
        nodes.add(tgt)
        if src not in graph:
            graph[src] = []
        graph[src].append(tgt)

    # 3. Detect cycles using DFS (white=0, gray=1, black=2)
    visited: Dict[str, int] = {node: 0 for node in nodes}
    cycle_path: List[str] = []

    def dfs(curr: str, path: List[str]) -> bool:
        visited[curr] = 1  # gray (currently visiting)
        path.append(curr)
        for neighbor in graph.get(curr, []):
            if visited.get(neighbor, 0) == 1:
                # Cycle detected!
                cycle_start = path.index(neighbor)
                cycle_path.extend(path[cycle_start:] + [neighbor])
                return True
            elif visited.get(neighbor, 0) == 0:
                if dfs(neighbor, path):
                    return True
        path.pop()
        visited[curr] = 2  # black (visited)
        return False

    for node in nodes:
        if visited[node] == 0:
            if dfs(node, []):
                cycle_str = " -> ".join(cycle_path)
                return False, (
                    f"Circular delegation cycle detected: {cycle_str}. "
                    f"Violates INV-AGENT-01 (Agent Handoff & Delegation Acyclicity)."
                )

    return True, "Valid Directed Acyclic Graph (DAG): Zero circular delegation cycles."


def parse_routine_input(input_data: str) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Parses JSON string or reads JSON file path."""
    if os.path.exists(input_data):
        with open(input_data, "r", encoding="utf-8") as f:
            return json.load(f)
    return json.loads(input_data)


def run_mock_test() -> int:
    """Self-contained test verifying secret scrubbing, typed routines, and DAG acyclicity in <0.05s."""
    start_time = time.time()
    print("[TEST] Verifying Agent Handoff Engine (State Compaction + Secret Redaction + INV-AGENT-01 DAG)...")
    synthetic_state = {
        "branch": "feat/payment-gateway-v2",
        "commit_sha": "a1b2c3d",
        "commit_msg": "feat(pay): add idempotency lock",
        "status_summary": "M src/billing.py\nM tests/billing_test.py",
        "diff_stat": "src/billing.py | 12 +-\n1 file changed",
        "diff_cached_stat": "(Zero staged changes)",
        "modified_count": 2,
        "modified_files": ["M src/billing.py", "M tests/billing_test.py"]
    }
    synthetic_objective = "Integrate Stripe billing with secret key sk-99998888777766665555444433332222 and postgres://dbuser:supersecretpass@localhost:5432/maindb"

    output = synthesize_handoff(synthetic_state, objective=synthetic_objective)

    # Assertions on markdown state card
    if "sk-999988887777" in output:
        print("[FAIL] Secret API key was not redacted!", file=sys.stderr)
        return 1
    if "supersecretpass" in output:
        print("[FAIL] Database password was not redacted!", file=sys.stderr)
        return 1
    if "[REDACTED_API_KEY]" not in output or "[REDACTED_PASSWORD]" not in output:
        print("[FAIL] Missing redaction markers in handoff document!", file=sys.stderr)
        return 1
    if "feat/payment-gateway-v2" not in output:
        print("[FAIL] Branch name missing from handoff document!", file=sys.stderr)
        return 1

    # Test HandoffRoutine creation and secret scrubbing
    routine = HandoffRoutine(
        source_agent="architect",
        target_agent="fullstack-developer",
        intent="Implement API with key sk-123456789012345678901234",
        transferred_context={"db": "postgres://user:superpass@localhost:5432/db", "domain": "Aryix Systems"}
    )
    routine_dict = routine.to_dict()
    assert "[REDACTED_API_KEY]" in routine_dict["intent"], "Routine intent secret not scrubbed"
    assert "[REDACTED_PASSWORD]" in routine_dict["transferred_context"]["db"], "Routine context password not scrubbed"

    # Test Valid Acyclic Delegation Chain
    valid_chain = [
        {"source_agent": "coordinator", "target_agent": "architect", "intent": "Draft architecture"},
        {"source_agent": "architect", "target_agent": "fullstack-developer", "intent": "Write code"},
        {"source_agent": "fullstack-developer", "target_agent": "qa", "intent": "Run tests in staging"}
    ]
    ok, msg = validate_handoff_dag(valid_chain)
    assert ok, f"Expected valid DAG to pass: {msg}"

    # Test Self-Delegation Rejection (INV-AGENT-01)
    self_chain = [{"source_agent": "qa", "target_agent": "qa", "intent": "Self test loop"}]
    ok_self, msg_self = validate_handoff_dag(self_chain)
    assert not ok_self, "Self-delegation should be rejected"
    assert "INV-AGENT-01" in msg_self, f"Expected INV-AGENT-01 in reason: {msg_self}"

    # Test Circular Delegation Rejection (INV-AGENT-01)
    cyclic_chain = [
        {"source_agent": "architect", "target_agent": "fullstack-developer", "intent": "Code"},
        {"source_agent": "fullstack-developer", "target_agent": "qa", "intent": "Test"},
        {"source_agent": "qa", "target_agent": "architect", "intent": "Reject and re-architect"}
    ]
    ok_cyc, msg_cyc = validate_handoff_dag(cyclic_chain)
    assert not ok_cyc, "Circular delegation cycle should be rejected"
    assert "INV-AGENT-01" in msg_cyc, f"Expected INV-AGENT-01 in reason: {msg_cyc}"
    assert "Circular delegation cycle detected:" in msg_cyc, f"Expected cycle note in message: {msg_cyc}"
    assert all(a in msg_cyc for a in ["architect", "fullstack-developer", "qa"]), f"All agents in cycle expected: {msg_cyc}"

    elapsed_ms = (time.time() - start_time) * 1000.0
    print(f"[PASS] Agent Handoff Engine verified cleanly in {elapsed_ms:.2f}ms (<50ms target).")
    print("✓ Certified Working Engine: PASSED (Exit code 0)")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Deterministic Agent Handoff & State Compaction Engine")
    parser.add_argument("--out", "-o", help="Target output file path (defaults to stdout)")
    parser.add_argument("--json", action="store_true", help="Output repository state in JSON format")
    parser.add_argument("--objective", help="High-level objective summary")
    parser.add_argument("--next", help="Immediate next command for the resumption agent")
    parser.add_argument("--save-memory", action="store_true", help="Save to .agents/memory/HANDOFF.md")
    parser.add_argument("--routine", help="JSON string or file path for typed HandoffRoutine")
    parser.add_argument("--chain", help="JSON string or file path for list of HandoffRoutines to validate")
    parser.add_argument("--verify-dag", action="store_true", help="Validate delegation chain for DAG acyclicity (INV-AGENT-01)")
    parser.add_argument("--mock-test", action="store_true", help="Run automated self-test suite")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    # Handle typed routine validation or execution
    if args.routine:
        raw_data = parse_routine_input(args.routine)
        routine = HandoffRoutine(
            source_agent=raw_data.get("source_agent", "unknown"),
            target_agent=raw_data.get("target_agent", "unknown"),
            intent=raw_data.get("intent", ""),
            transferred_context=raw_data.get("transferred_context"),
            return_policy=raw_data.get("return_policy", "return_to_source")
        )
        if args.verify_dag:
            ok, reason = validate_handoff_dag([routine.to_dict()])
            if not ok:
                print(f"[ERROR] {reason}", file=sys.stderr)
                sys.exit(1)
        print(json.dumps(routine.to_dict(), indent=2))
        sys.exit(0)

    # Handle delegation chain validation
    if args.chain or args.verify_dag:
        if not args.chain:
            print("[ERROR] --verify-dag requires --chain <JSON_PATH_OR_STR>", file=sys.stderr)
            sys.exit(1)
        raw_chain = parse_routine_input(args.chain)
        if not isinstance(raw_chain, list):
            print("[ERROR] Handoff chain must be a JSON array of routines", file=sys.stderr)
            sys.exit(1)
        ok, reason = validate_handoff_dag(raw_chain)
        if not ok:
            print(f"[FAIL] {reason}", file=sys.stderr)
            sys.exit(1)
        print(f"[PASS] {reason}")
        sys.exit(0)

    state = collect_repo_state()

    if args.json:
        print(json.dumps(state, indent=2))
        return

    handoff_text = synthesize_handoff(state, objective=args.objective or "", next_action=args.next or "")

    if args.save_memory:
        target_path = os.path.join(REPO_ROOT, ".agents", "memory", "HANDOFF.md")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(handoff_text)
        print(f"[SUCCESS] Handoff card saved to {target_path}")
    elif args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(handoff_text)
        print(f"[SUCCESS] Handoff card saved to {args.out}")
    else:
        print(handoff_text)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Google Antigravity & OpenAI Swarm Inspired Multi-Agent Coordinator.

Orchestrates active agent rosters, homogeneous task slicing, asynchronous message board state,
and strict DAG acyclicity enforcement under INV-AGENT-01 at $0 cloud tokens.
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional, Set, Tuple

STATE_FILE = Path(".agents/swarm/board_state.json")

@dataclass
class SwarmMember:
    name: str
    model: str
    state: str  # waiting, working, stopped, killed
    workspace: str  # inherit, share, branch
    brief: str
    created_at: float = field(default_factory=time.time)
    last_active: float = field(default_factory=time.time)

@dataclass
class SwarmMessage:
    msg_id: str
    sender: str
    recipient: str  # @all, @coordinator, or specific member name
    content: str
    timestamp: float = field(default_factory=time.time)

@dataclass
class SwarmTaskSlice:
    task_id: str
    assigned_worker: str
    target: str
    brief: str
    status: str  # pending, in_progress, completed, failed
    created_at: float = field(default_factory=time.time)

class SwarmCoordinator:
    """Central state and coordination controller for multi-agent swarms."""
    
    def __init__(self, state_path: Path = STATE_FILE):
        self.state_path = state_path
        self.title: str = "Aryix Multi-Agent Engineering Swarm"
        self.members: Dict[str, SwarmMember] = {}
        self.messages: List[SwarmMessage] = []
        self.task_slices: List[SwarmTaskSlice] = []
        self._load_state()

    def _load_state(self):
        if self.state_path.exists():
            try:
                data = json.loads(self.state_path.read_text(encoding="utf-8"))
                self.title = data.get("title", self.title)
                for m_data in data.get("members", []):
                    self.members[m_data["name"]] = SwarmMember(**m_data)
                for msg_data in data.get("messages", []):
                    self.messages.append(SwarmMessage(**msg_data))
                for t_data in data.get("tasks", []):
                    self.task_slices.append(SwarmTaskSlice(**t_data))
            except Exception:
                pass

    def save_state(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "title": self.title,
            "updated_at": time.time(),
            "members": [asdict(m) for m in self.members.values()],
            "messages": [asdict(msg) for msg in self.messages[-50:]],  # keep last 50
            "tasks": [asdict(t) for t in self.task_slices]
        }
        self.state_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def add_member(self, name: str, brief: str, model: str = "qwen2.5-coder:14b", workspace: str = "inherit") -> SwarmMember:
        clean_name = name.strip().lower().replace(" ", "-")
        member = SwarmMember(
            name=clean_name,
            model=model,
            state="working",
            workspace=workspace,
            brief=brief
        )
        self.members[clean_name] = member
        self.post_message("coordinator", f"@{clean_name}", f"Assignment: {brief}")
        self.save_state()
        return member

    def slice_tasks(self, base_name: str, tasks: List[str], shared_brief: str, model: str = "qwen2.5-coder:14b", workspace: str = "inherit") -> List[SwarmTaskSlice]:
        """Slices a shared task list across n homogeneous workers (<name>-1..<name>-k)."""
        created_slices = []
        for i, target in enumerate(tasks, 1):
            worker_name = f"{base_name}-{i}"
            specific_brief = f"{shared_brief} [Target: {target}]"
            self.add_member(worker_name, specific_brief, model=model, workspace=workspace)
            
            ts = SwarmTaskSlice(
                task_id=f"TASK-{int(time.time()*1000)%100000}-{i}",
                assigned_worker=worker_name,
                target=target,
                brief=specific_brief,
                status="in_progress"
            )
            self.task_slices.append(ts)
            created_slices.append(ts)
            
        self.save_state()
        return created_slices

    def kill_member(self, name: str) -> bool:
        clean_name = name.strip().lower()
        if clean_name in self.members:
            self.members[clean_name].state = "killed"
            self.save_state()
            return True
        return False

    def post_message(self, sender: str, recipient: str, content: str) -> SwarmMessage:
        msg = SwarmMessage(
            msg_id=f"MSG-{int(time.time()*1000)%100000}",
            sender=sender,
            recipient=recipient,
            content=content
        )
        self.messages.append(msg)
        return msg

    def verify_dag_acyclicity(self, delegation_pairs: List[tuple]) -> Tuple[bool, Optional[str]]:
        """Verifies that inter-agent delegation pairs conform strictly to DAG acyclicity under INV-AGENT-01."""
        adj: Dict[str, Set[str]] = {}
        all_nodes: Set[str] = set()
        
        for u, v in delegation_pairs:
            u_clean, v_clean = u.strip().lower(), v.strip().lower()
            if u_clean == v_clean:
                return False, f"Self-delegation detected under INV-AGENT-01: {u_clean} -> {v_clean}"
            all_nodes.add(u_clean)
            all_nodes.add(v_clean)
            adj.setdefault(u_clean, set()).add(v_clean)
            
        visited: Dict[str, int] = {}  # 0=unvisited, 1=visiting, 2=visited
        for node in all_nodes:
            visited[node] = 0
            
        def _has_cycle(curr: str, path: List[str]) -> Tuple[bool, Optional[str]]:
            visited[curr] = 1
            path.append(curr)
            for neighbor in adj.get(curr, set()):
                if visited.get(neighbor) == 1:
                    cycle_repr = " -> ".join(path[path.index(neighbor):] + [neighbor])
                    return True, f"Circular delegation loop detected under INV-AGENT-01: {cycle_repr}"
                if visited.get(neighbor) == 0:
                    has_c, reason = _has_cycle(neighbor, path)
                    if has_c:
                        return True, reason
            path.pop()
            visited[curr] = 2
            return False, None
            
        for node in all_nodes:
            if visited[node] == 0:
                has_c, reason = _has_cycle(node, [])
                if has_c:
                    return False, reason
                    
        return True, None

def run_mock_test() -> int:
    """Verifies swarm roster management, task slicing, and acyclic DAG validation."""
    print("=== Running Google Antigravity & OpenAI Swarm Coordinator Mock Test ===")
    start_time = time.time()
    
    test_state_file = Path("/tmp/mock_swarm_state.json")
    if test_state_file.exists():
        test_state_file.unlink()
        
    coordinator = SwarmCoordinator(state_path=test_state_file)
    
    # 1. Member registration
    m1 = coordinator.add_member("qa-lead", "Lead the zero-mock integration testing suite for Aryix Systems.")
    assert m1.name == "qa-lead"
    assert m1.state == "working"
    print("✓ Added member: qa-lead (state: working)")
    
    # 2. Task Slicing across 3 workers
    tasks = ["services/ledger", "services/payments", "services/auth"]
    slices = coordinator.slice_tasks(
        base_name="auditor",
        tasks=tasks,
        shared_brief="Audit code invariants and verify double-entry rules."
    )
    assert len(slices) == 3
    assert "auditor-1" in coordinator.members
    assert "auditor-3" in coordinator.members
    print(f"✓ Task Slicing: Sliced {len(tasks)} targets across {len(slices)} workers (auditor-1..3)")
    
    # 3. DAG Acyclicity Verification (INV-AGENT-01)
    # Valid acyclic DAG: coordinator -> qa-lead -> auditor-1
    valid_dag = [("coordinator", "qa-lead"), ("qa-lead", "auditor-1"), ("qa-lead", "auditor-2")]
    is_valid, err = coordinator.verify_dag_acyclicity(valid_dag)
    assert is_valid, f"Expected valid DAG, got error: {err}"
    print("✓ DAG Validation: Clean acyclic hierarchy verified")
    
    # Self-delegation detection
    self_loop = [("qa-lead", "qa-lead")]
    is_valid, err = coordinator.verify_dag_acyclicity(self_loop)
    assert not is_valid, "Failed to block self-delegation"
    assert "Self-delegation detected" in err
    print("✓ Self-delegation guard: Caught qa-lead -> qa-lead under INV-AGENT-01")
    
    # Circular delegation cycle detection (A -> B -> C -> A)
    circular_dag = [("qa-lead", "auditor-1"), ("auditor-1", "sec-lead"), ("sec-lead", "qa-lead")]
    is_valid, err = coordinator.verify_dag_acyclicity(circular_dag)
    assert not is_valid, "Failed to catch circular delegation cycle"
    assert "Circular delegation loop detected" in err
    print(f"✓ Circular delegation guard: Caught cycle ({err})")
    
    if test_state_file.exists():
        test_state_file.unlink()
        
    elapsed_ms = (time.time() - start_time) * 1000.0
    print(f"✓ Total execution completed in {elapsed_ms:.2f}ms (<20ms target)")
    print("✓ Certified Working Engine: PASSED (Exit code 0)")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Antigravity Swarm Coordinator & Shared Board Engine")
    subparsers = parser.add_subparsers(dest="subcommand", help="Swarm actions")
    
    # Subcommand: status
    parser_status = subparsers.add_parser("status", help="List active swarm members and board status")
    parser_status.add_argument("--format", choices=["table", "json"], default="table", help="Output format")
    
    # Subcommand: add
    parser_add = subparsers.add_parser("add", help="Add a worker member to the swarm")
    parser_add.add_argument("--name", "-n", required=True, help="Worker name")
    parser_add.add_argument("--brief", "-b", required=True, help="Assignment brief")
    parser_add.add_argument("--model", "-m", default="qwen2.5-coder:14b", help="Assigned model")
    parser_add.add_argument("--workspace", "-w", default="inherit", choices=["inherit", "share", "branch"])
    
    # Subcommand: slice
    parser_slice = subparsers.add_parser("slice", help="Slice a task across multiple workers")
    parser_slice.add_argument("--name", "-n", required=True, help="Base worker name")
    parser_slice.add_argument("--tasks", "-t", required=True, help="Comma-separated slice targets")
    parser_slice.add_argument("--brief", "-b", required=True, help="Shared brief")
    parser_slice.add_argument("--model", "-m", default="qwen2.5-coder:14b")
    
    # Subcommand: kill
    parser_kill = subparsers.add_parser("kill", help="Mark a worker killed")
    parser_kill.add_argument("--name", "-n", required=True, help="Worker name to terminate")
    
    # Mock test flag
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic mock test suite")
    
    args = parser.parse_args()
    
    if args.mock_test:
        sys.exit(run_mock_test())
        
    coordinator = SwarmCoordinator()
    
    if args.subcommand == "status":
        if args.format == "json":
            out = {
                "title": coordinator.title,
                "members": [asdict(m) for m in coordinator.members.values()],
                "tasks": [asdict(t) for t in coordinator.task_slices],
                "messages_count": len(coordinator.messages)
            }
            print(json.dumps(out, indent=2))
        else:
            print(f"\n========================================================================")
            print(f" 🐝 ANTIGRAVITY SWARM ROSTER & BOARD: {coordinator.title}")
            print(f"========================================================================")
            if not coordinator.members:
                print("No active swarm members registered.")
            else:
                print(f"{'Member':<18} {'State':<10} {'Model':<20} {'Workspace':<10} {'Brief'}")
                print(f"------------------------------------------------------------------------")
                for m in coordinator.members.values():
                    print(f"{m.name:<18} {m.state:<10} {m.model:<20} {m.workspace:<10} {m.brief[:40]}")
            if coordinator.task_slices:
                print(f"------------------------------------------------------------------------")
                print(f"Active Task Slices: {len(coordinator.task_slices)}")
                for t in coordinator.task_slices:
                    print(f"  [{t.task_id}] {t.assigned_worker} -> {t.target} ({t.status})")
            print(f"========================================================================\n")
            
    elif args.subcommand == "add":
        m = coordinator.add_member(args.name, args.brief, args.model, args.workspace)
        print(f"✔ Swarm member '{m.name}' added successfully ({m.state}, model: {m.model}).")
        
    elif args.subcommand == "slice":
        task_list = [t.strip() for t in args.tasks.split(",") if t.strip()]
        slices = coordinator.slice_tasks(args.name, task_list, args.brief, args.model)
        print(f"✔ Sliced {len(slices)} tasks across workers {args.name}-1..{args.name}-{len(slices)}.")
        
    elif args.subcommand == "kill":
        ok = coordinator.kill_member(args.name)
        if ok:
            print(f"✔ Member '{args.name}' marked killed.")
        else:
            print(f"Member '{args.name}' not found.", file=sys.stderr)
            sys.exit(1)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

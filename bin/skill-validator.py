#!/usr/bin/env python3
"""
skill-validator.py - Static Agent Skill & Front-Matter Contract Validator

Inspired by bregman-arie/devops-sre-skills schema standards.
Enforces declarative safety contracts, tool whitelists, and rollback procedures
across SKILL.md documents to ensure safe autonomous agent execution.

Usage:
    python3 bin/skill-validator.py skills/sre-k8s-triage/SKILL.md
    python3 bin/skill-validator.py --lint-all
    python3 bin/skill-validator.py --strict
    python3 bin/skill-validator.py --mock-test
"""

import sys
import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

VALID_SAFETY_LEVELS = {"read_only", "mutating_reversible", "mutating_irreversible"}

class SkillValidationError:
    def __init__(self, file_path: str, code: str, message: str, is_fatal: bool = True):
        self.file_path = file_path
        self.code = code
        self.message = message
        self.is_fatal = is_fatal

    def to_dict(self) -> Dict[str, Any]:
        return {
            "file": self.file_path,
            "code": self.code,
            "message": self.message,
            "fatal": self.is_fatal
        }

def parse_yaml_front_matter(content: str) -> Tuple[Optional[Dict[str, Any]], str, List[str]]:
    """Extract and parse YAML front matter between triple-dash fences."""
    errors = []
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, content, ["File does not start with triple-dash (---) front matter fence."]

    end_idx = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break

    if end_idx == -1:
        return None, content, ["Unterminated front matter fence; missing closing (---)."]

    front_matter_lines = lines[1:end_idx]
    body_content = "\n".join(lines[end_idx + 1:])

    # Simple zero-dependency YAML parser for key-value and simple lists
    data: Dict[str, Any] = {}
    current_list_key = None

    for line_num, line in enumerate(front_matter_lines, start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Check list item
        list_match = re.match(r"^-\s+(.+)$", stripped)
        if list_match:
            if current_list_key and isinstance(data.get(current_list_key), list):
                val = list_match.group(1).strip().strip('"').strip("'")
                data[current_list_key].append(val)
                continue
            else:
                errors.append(f"Line {line_num}: List item without parent key.")
                continue

        # Key-value
        kv_match = re.match(r"^([a-zA-Z0-9_\-]+)\s*:\s*(.*)$", stripped)
        if kv_match:
            key = kv_match.group(1).strip()
            val = kv_match.group(2).strip()
            # If value is empty or inline list
            if val == "":
                data[key] = []
                current_list_key = key
            elif val.startswith("[") and val.endswith("]"):
                # Inline array [a, b, c]
                items = [x.strip().strip('"').strip("'") for x in val[1:-1].split(",") if x.strip()]
                data[key] = items
                current_list_key = None
            else:
                # Strip quotes and trailing inline comments
                if " #" in val:
                    val = val.split(" #")[0].strip()
                val = val.strip('"').strip("'")
                data[key] = val
                current_list_key = None
        else:
            errors.append(f"Line {line_num}: Unparseable front matter syntax: '{line}'")

    return data, body_content, errors

def validate_skill_file(file_path: Path, strict: bool = False) -> List[SkillValidationError]:
    """Validate a single SKILL.md file against safety and schema standards."""
    errors: List[SkillValidationError] = []

    if not file_path.exists():
        return [SkillValidationError(str(file_path), "FILE_NOT_FOUND", "Target file does not exist.")]

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [SkillValidationError(str(file_path), "READ_ERROR", f"Could not read file: {e}")]

    data, body, parse_errors = parse_yaml_front_matter(content)
    for pe in parse_errors:
        errors.append(SkillValidationError(str(file_path), "YAML_PARSE_ERROR", pe))

    if data is None:
        return errors

    # Check skill name / id
    name = data.get("name") or data.get("id")
    if not name:
        errors.append(SkillValidationError(str(file_path), "MISSING_NAME", "Missing required 'name' or 'id' in front matter."))
    else:
        # Check kebab-case
        if not re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", str(name)):
            errors.append(SkillValidationError(str(file_path), "INVALID_NAME_FORMAT", f"Skill name '{name}' must be kebab-case."))

        # Check folder name match if inside a directory
        parent_dir_name = file_path.parent.name
        if parent_dir_name != "skills" and parent_dir_name != str(name):
            # Warning or error if directory doesn't match
            errors.append(SkillValidationError(
                str(file_path),
                "NAME_DIR_MISMATCH",
                f"Skill name '{name}' does not match parent directory '{parent_dir_name}'.",
                is_fatal=False
            ))

    # Check description
    desc = data.get("description")
    if not desc or len(str(desc).strip()) < 10:
        errors.append(SkillValidationError(str(file_path), "INVALID_DESCRIPTION", "Description must be at least 10 characters long."))

    # Check safety level
    safety = data.get("safety")
    if strict or safety is not None:
        if not safety:
            errors.append(SkillValidationError(str(file_path), "MISSING_SAFETY", "Strict mode requires 'safety' attribute (read_only, mutating_reversible, mutating_irreversible)."))
        elif safety not in VALID_SAFETY_LEVELS:
            errors.append(SkillValidationError(str(file_path), "INVALID_SAFETY", f"Invalid safety '{safety}'. Allowed: {sorted(list(VALID_SAFETY_LEVELS))}"))

    # Check mutating rollback requirements
    if safety in ("mutating_reversible", "mutating_irreversible"):
        rollback = data.get("rollback_procedure")
        has_rollback_section = bool(re.search(r"(?i)^#{1,3}\s+.*rollback", body, re.MULTILINE))
        if not rollback and not has_rollback_section:
            errors.append(SkillValidationError(
                str(file_path),
                "MISSING_ROLLBACK",
                f"Skill declared as '{safety}' but lacks 'rollback_procedure' in front matter or ## Rollback heading in body."
            ))

    # Check tools allowed
    tools = data.get("tools_allowed")
    if strict and (tools is None or not isinstance(tools, list)):
        errors.append(SkillValidationError(str(file_path), "MISSING_TOOLS_ALLOWED", "Strict mode requires 'tools_allowed' list in front matter."))

    return errors

def validate_all_skills(repo_root: Path, strict: bool = False) -> Tuple[int, int, List[SkillValidationError]]:
    """Scan all skills in repo_root/skills."""
    skills_dir = repo_root / "skills"
    if not skills_dir.exists():
        return 0, 0, [SkillValidationError(str(skills_dir), "DIR_NOT_FOUND", "Directory skills/ does not exist.")]

    all_errors = []
    total_skills = 0
    passed_skills = 0

    for skill_file in sorted(skills_dir.glob("*/SKILL.md")):
        total_skills += 1
        errs = validate_skill_file(skill_file, strict=strict)
        fatal_errs = [e for e in errs if e.is_fatal]
        if not fatal_errs:
            passed_skills += 1
        all_errors.extend(errs)

    return total_skills, passed_skills, all_errors

def run_mock_test() -> int:
    """Run fast self-test verifying skill validation logic."""
    print("========================================================================")
    print(" 🛡️ RUNNING AGENT SKILL VALIDATOR MOCK TEST ($0 TOKENS)")
    print("========================================================================")

    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        # 1. Valid Read-Only Skill
        valid_dir = tmp_path / "k8s-pod-triage"
        valid_dir.mkdir()
        valid_file = valid_dir / "SKILL.md"
        valid_file.write_text("""---
name: k8s-pod-triage
description: Diagnostic runbook for Kubernetes pods stuck in CrashLoopBackOff or Pending states.
safety: read_only
tools_allowed:
  - kubectl
  - curl
---
# Kubernetes Pod Triage Runbook
Diagnostic procedure for pods.
""")
        errs1 = validate_skill_file(valid_file, strict=True)
        assert len([e for e in errs1 if e.is_fatal]) == 0, f"Valid skill failed: {[e.message for e in errs1]}"
        print("  ✔ Check 1: Valid read-only skill verified clean.")

        # 2. Mutating Skill with Rollback
        mut_dir = tmp_path / "scale-deployment"
        mut_dir.mkdir()
        mut_file = mut_dir / "SKILL.md"
        mut_file.write_text("""---
name: scale-deployment
description: Safely scale a deployment up or down during load anomalies.
safety: mutating_reversible
tools_allowed:
  - kubectl
rollback_procedure: "Scale deployment back to previous replica count using kubectl scale."
---
# Scale Deployment
Procedure...
""")
        errs2 = validate_skill_file(mut_file, strict=True)
        assert len([e for e in errs2 if e.is_fatal]) == 0, f"Mutating skill with rollback failed: {[e.message for e in errs2]}"
        print("  ✔ Check 2: Mutating skill with rollback verified clean.")

        # 3. Invalid: Mutating without Rollback
        bad_mut_dir = tmp_path / "delete-node"
        bad_mut_dir.mkdir()
        bad_mut_file = bad_mut_dir / "SKILL.md"
        bad_mut_file.write_text("""---
name: delete-node
description: Dangerously terminate an unresponsive cluster node.
safety: mutating_irreversible
tools_allowed:
  - kubectl
---
# Delete Node
No rollback mentioned anywhere.
""")
        errs3 = validate_skill_file(bad_mut_file, strict=True)
        assert any(e.code == "MISSING_ROLLBACK" for e in errs3), "Failed to detect missing rollback."
        print("  ✔ Check 3: Mutating skill without rollback correctly caught.")

        # 4. Invalid: Malformed YAML front matter
        mal_dir = tmp_path / "malformed-skill"
        mal_dir.mkdir()
        mal_file = mal_dir / "SKILL.md"
        mal_file.write_text("""No front matter here.
# Just Heading
""")
        errs4 = validate_skill_file(mal_file, strict=False)
        assert any(e.code == "YAML_PARSE_ERROR" for e in errs4), "Failed to catch missing front matter."
        print("  ✔ Check 4: Missing YAML front matter correctly caught.")

        # 5. Invalid: Invalid safety level
        bad_safe_dir = tmp_path / "bad-safe"
        bad_safe_dir.mkdir()
        bad_safe_file = bad_safe_dir / "SKILL.md"
        bad_safe_file.write_text("""---
name: bad-safe
description: Something with bad safety value.
safety: dangerous_execute
tools_allowed:
  - rm
---
# Heading
""")
        errs5 = validate_skill_file(bad_safe_file, strict=True)
        assert any(e.code == "INVALID_SAFETY" for e in errs5), "Failed to catch invalid safety level."
        print("  ✔ Check 5: Invalid safety level correctly rejected.")

    print("------------------------------------------------------------------------")
    print(" ✅ ALL 5 SKILL VALIDATOR ASSERTIONS PASSED ($0 TOKENS).")
    print("========================================================================")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Static Agent Skill & Front-Matter Contract Validator")
    parser.add_argument("path", nargs="?", help="Path to SKILL.md file or skill folder")
    parser.add_argument("--lint-all", action="store_true", help="Lint all skills in repository")
    parser.add_argument("--strict", action="store_true", help="Enforce strict safety and tools_allowed schema")
    parser.add_argument("--mock-test", action="store_true", help="Run automated self-test")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    repo_root = Path(__file__).resolve().parent.parent

    if args.lint_all or not args.path:
        total, passed, errors = validate_all_skills(repo_root, strict=args.strict)
        fatal_count = len([e for e in errors if e.is_fatal])
        warn_count = len([e for e in errors if not e.is_fatal])

        if args.json:
            print(json.dumps({
                "total": total,
                "passed": passed,
                "fatal_errors": fatal_count,
                "warnings": warn_count,
                "errors": [e.to_dict() for e in errors]
            }, indent=2))
        else:
            print("========================================================================")
            print(f" 🛡️ AGENT SKILLS AUDIT: {passed}/{total} SKILLS VALIDATED CLEAN")
            print("========================================================================")
            for err in errors:
                tag = "[FATAL]" if err.is_fatal else "[WARN]"
                print(f"  {tag} {err.file_path}: ({err.code}) {err.message}")
            print("------------------------------------------------------------------------")
            if fatal_count == 0:
                print(f" [✔] ALL {total} AGENT SKILLS VERIFIED COMPLIANT ($0 TOKENS).")
            else:
                print(f" [✘] {fatal_count} FATAL SKILL DEFECTS DETECTED.")
        sys.exit(1 if fatal_count > 0 else 0)

    target_path = Path(args.path)
    if target_path.is_dir():
        target_path = target_path / "SKILL.md"

    errors = validate_skill_file(target_path, strict=args.strict)
    fatal_count = len([e for e in errors if e.is_fatal])

    if args.json:
        print(json.dumps([e.to_dict() for e in errors], indent=2))
    else:
        if not errors:
            print(f"✔ Skill file {target_path} is valid and compliant.")
        else:
            for err in errors:
                tag = "[FATAL]" if err.is_fatal else "[WARN]"
                print(f"{tag} ({err.code}) {err.message}")
    sys.exit(1 if fatal_count > 0 else 0)

if __name__ == "__main__":
    main()

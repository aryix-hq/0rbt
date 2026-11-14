#!/usr/bin/env python3
"""Project-Scoped Document Numbering Engine & Cross-Project Isolation Invariant (INV-DOC-04).

Enforces strictly project-specific document identifiers across:
  wiki/research/       (RES-XXX)
  wiki/features/       (FEAT-XXX)
  wiki/plans/          (PLAN-XXX)
  wiki/defects/        (DEF-XXX)
  wiki/incidents/      (INC-XXX)
  wiki/adr/            (ADR-XXX)
  wiki/vulnerabilities/(VULN-XXX)

Guarantees that an agent or engineer never carries over numbering from other
repositories, conversational history, or global templates.
Next ID = max(existing) + 1 (or 001 if directory has no prior documents).
"""

import os
import sys
import re
import json
import time
import argparse
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

DOC_TYPES = {
    "research": {
        "prefix": "RES",
        "dir": "wiki/research",
        "template": "wiki/templates/RESEARCH_NOTE.md",
        "name": "Research Note"
    },
    "feature": {
        "prefix": "FEAT",
        "dir": "wiki/features",
        "template": "wiki/templates/FEATURE_SPEC.md",
        "name": "Feature Specification"
    },
    "plan": {
        "prefix": "PLAN",
        "dir": "wiki/plans",
        "template": "wiki/templates/IMPLEMENTATION_PLAN.md",
        "name": "Implementation Plan"
    },
    "defect": {
        "prefix": "DEF",
        "dir": "wiki/defects",
        "template": "wiki/templates/DEFECT_RECORD.md",
        "name": "Defect Record"
    },
    "incident": {
        "prefix": "INC",
        "dir": "wiki/incidents",
        "template": "wiki/templates/INCIDENT_RECORD.md",
        "name": "Incident Record"
    },
    "adr": {
        "prefix": "ADR",
        "dir": "wiki/adr",
        "template": "wiki/templates/ARCHITECTURE_DECISION_RECORD.md",
        "name": "Architecture Decision Record"
    },
    "vuln": {
        "prefix": "VULN",
        "dir": "wiki/vulnerabilities",
        "template": "wiki/templates/VULNERABILITY_RECORD.md",
        "name": "Vulnerability Record"
    }
}

ALIASES = {
    "res": "research",
    "research": "research",
    "feat": "feature",
    "feature": "feature",
    "features": "feature",
    "plan": "plan",
    "plans": "plan",
    "def": "defect",
    "defect": "defect",
    "defects": "defect",
    "inc": "incident",
    "incident": "incident",
    "incidents": "incident",
    "adr": "adr",
    "adrs": "adr",
    "vuln": "vuln",
    "vulnerability": "vuln",
    "vulnerabilities": "vuln"
}


def normalize_doc_type(raw_type: str) -> Optional[str]:
    """Normalizes document type alias to canonical key."""
    return ALIASES.get(raw_type.lower().strip())


def sanitize_title_to_slug(title: str) -> str:
    """Converts a human title into an UPPER-KEBAB-CASE slug for file naming."""
    clean = re.sub(r'[^a-zA-Z0-9\s_-]', '', title).strip()
    slug = re.sub(r'[\s_]+', '-', clean).upper()
    return slug or "DOCUMENT"


def scan_existing_ids(project_root: Path, doc_type_key: str) -> List[Tuple[int, str]]:
    """Scans target wiki directory for existing document IDs and filenames.
    
    Returns a sorted list of tuples (integer_id, filename).
    """
    type_info = DOC_TYPES[doc_type_key]
    target_dir = project_root / type_info["dir"]
    prefix = type_info["prefix"]

    if not target_dir.exists() or not target_dir.is_dir():
        return []

    pattern = re.compile(rf'^{prefix}-(\d+)', re.IGNORECASE)
    results = []

    for entry in target_dir.iterdir():
        if entry.is_file() and entry.suffix == ".md":
            if entry.name.upper() == "README.MD":
                continue
            match = pattern.match(entry.name)
            if match:
                try:
                    num = int(match.group(1))
                    results.append((num, entry.name))
                except ValueError:
                    continue

    results.sort(key=lambda x: x[0])
    return results


def calculate_next_id(project_root: Path, doc_type_key: str) -> Tuple[str, int, str]:
    """Calculates the next project-specific document ID.
    
    Returns:
        (formatted_id, next_integer, prefix)
        e.g. ("RES-007", 7, "RES")
    """
    type_info = DOC_TYPES[doc_type_key]
    prefix = type_info["prefix"]
    existing = scan_existing_ids(project_root, doc_type_key)

    if not existing:
        next_int = 1
    else:
        max_existing = max(num for num, _ in existing)
        next_int = max_existing + 1

    formatted_id = f"{prefix}-{next_int:03d}"
    return formatted_id, next_int, prefix


def scaffold_document(
    project_root: Path,
    doc_type_key: str,
    title: str,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Scaffolds a new project-specific document file from local template."""
    type_info = DOC_TYPES[doc_type_key]
    target_dir = project_root / type_info["dir"]
    target_dir.mkdir(parents=True, exist_ok=True)

    formatted_id, next_int, prefix = calculate_next_id(project_root, doc_type_key)
    slug = sanitize_title_to_slug(title)
    filename = f"{formatted_id}-{slug}.md" if slug else f"{formatted_id}.md"
    file_path = target_dir / filename

    if file_path.exists():
        raise FileExistsError(f"Target document already exists: {file_path}")

    # Read template if available
    template_path = project_root / type_info["template"]
    today_str = time.strftime("%Y-%m-%d")

    if template_path.exists():
        content = template_path.read_text(encoding="utf-8")
        # Replace placeholders
        content = re.sub(rf'#{prefix}-XXX', f"#{formatted_id}", content)
        content = re.sub(rf'{prefix}-XXX', formatted_id, content)
        content = content.replace("[Research Initiative Title]", title)
        content = content.replace("[Feature Title]", title)
        content = content.replace("[Implementation Plan Title]", title)
        content = content.replace("[Defect Title]", title)
        content = content.replace("[Incident Title]", title)
        content = content.replace("[ADR Title]", title)
        content = content.replace("YYYY-MM-DD", today_str)
    else:
        # Canonical fallback scaffold
        content = f"""# {formatted_id}: {title}

- **Initiative**: {title}
- **Document ID**: `{formatted_id}`
- **Type**: {type_info['name']}
- **Status**: Draft
- **Created**: {today_str}

---

## 1. Overview & Objective
[Document summary and scope]

---

## 2. Technical Invariants & Requirements
- Enforce project-scoped invariants.
"""

    if not dry_run:
        file_path.write_text(content, encoding="utf-8")

    return {
        "id": formatted_id,
        "integer_id": next_int,
        "prefix": prefix,
        "type": doc_type_key,
        "filename": filename,
        "path": str(file_path),
        "relative_path": str(file_path.relative_to(project_root)),
        "created": not dry_run
    }


def audit_project_documents(
    project_root: Path,
    max_gap_threshold: int = 3
) -> Dict[str, Any]:
    """Audits all document types in the project for gaps, duplicates, or anomalies."""
    report = {
        "project_root": str(project_root),
        "timestamp": time.time(),
        "total_documents": 0,
        "categories": {},
        "violations": [],
        "passed": True
    }

    for key, info in DOC_TYPES.items():
        existing = scan_existing_ids(project_root, key)
        prefix = info["prefix"]
        cat_data = {
            "name": info["name"],
            "prefix": prefix,
            "directory": info["dir"],
            "count": len(existing),
            "max_id": existing[-1][0] if existing else 0,
            "next_id": (existing[-1][0] + 1) if existing else 1,
            "gaps": [],
            "duplicates": [],
            "jump_violations": []
        }
        report["total_documents"] += len(existing)

        # Check duplicates
        id_counts = {}
        for num, fname in existing:
            id_counts[num] = id_counts.get(num, 0) + 1
        for num, count in id_counts.items():
            if count > 1:
                cat_data["duplicates"].append({"id": f"{prefix}-{num:03d}", "count": count})
                report["violations"].append(
                    f"Duplicate ID {prefix}-{num:03d} detected ({count} files) in {info['dir']}"
                )

        # Check sequence gaps
        if existing:
            unique_nums = sorted(list(set(num for num, _ in existing)))
            # If the lowest starts above threshold (e.g. repo started at 45 instead of 1)
            if unique_nums[0] > max_gap_threshold:
                cat_data["jump_violations"].append({
                    "type": "initial_jump",
                    "lowest_id": unique_nums[0],
                    "threshold": max_gap_threshold
                })
                report["violations"].append(
                    f"Initial sequence in {info['dir']} starts at {prefix}-{unique_nums[0]:03d} "
                    f"(expected 001..{max_gap_threshold:03d}). Possible foreign context leak!"
                )

            for i in range(1, len(unique_nums)):
                prev = unique_nums[i - 1]
                curr = unique_nums[i]
                diff = curr - prev
                if diff > 1:
                    cat_data["gaps"].append({"from": prev, "to": curr, "missing": diff - 1})
                    if diff > max_gap_threshold:
                        cat_data["jump_violations"].append({
                            "type": "internal_jump",
                            "from": prev,
                            "to": curr,
                            "gap": diff - 1
                        })
                        report["violations"].append(
                            f"Abnormal sequence jump in {info['dir']} from {prefix}-{prev:03d} to {prefix}-{curr:03d} "
                            f"(gap of {diff - 1} > threshold {max_gap_threshold}). Violates INV-DOC-04!"
                        )

        report["categories"][key] = cat_data

    if report["violations"]:
        report["passed"] = False

    return report


def run_mock_test() -> int:
    """Self-verifying deterministic test suite for doc-numberer.py (<20ms)."""
    t0 = time.perf_counter()
    print("=" * 72)
    print(" 🧪 RUNNING PROJECT-SCOPED DOCUMENT NUMBERING MOCK TEST (INV-DOC-04)")
    print("=" * 72)

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "wiki" / "research").mkdir(parents=True)
        (root / "wiki" / "features").mkdir(parents=True)

        # Case 1: Empty project directory -> must start at 001
        res_id, num, prefix = calculate_next_id(root, "research")
        assert res_id == "RES-001" and num == 1, f"Expected RES-001, got {res_id}"
        print("  ✔ Case 1: Empty directory correctly returns RES-001.")

        # Case 2: Populate downstream project simulation (e.g. b00k5 with RES-001..006)
        for i in range(1, 7):
            (root / "wiki" / "research" / f"RES-{i:03d}-NOTE.md").write_text("# Note")
        
        res_id2, num2, _ = calculate_next_id(root, "research")
        assert res_id2 == "RES-007" and num2 == 7, f"Expected RES-007, got {res_id2}"
        print("  ✔ Case 2: Existing sequence (RES-001..006) strictly yields RES-007.")

        # Case 3: Scaffolding a document
        result = scaffold_document(root, "research", "Customer Invoice Reconciliation")
        assert result["id"] == "RES-007"
        assert "RES-007-CUSTOMER-INVOICE-RECONCILIATION.md" in result["filename"]
        created_file = Path(result["path"])
        assert created_file.exists()
        assert "RES-007" in created_file.read_text()
        print(f"  ✔ Case 3: Scaffolding created {result['filename']} successfully.")

        # Case 4: Verify next ID increments after scaffolding
        res_id3, num3, _ = calculate_next_id(root, "research")
        assert res_id3 == "RES-008" and num3 == 8, f"Expected RES-008, got {res_id3}"
        print("  ✔ Case 4: Sequential increment verified (RES-008).")

        # Case 5: Audit clean state
        audit_res = audit_project_documents(root)
        assert audit_res["passed"] is True, "Expected audit to pass on clean sequence"
        print("  ✔ Case 5: Audit reports clean sequence for normal project.")

        # Case 6: Simulate foreign context leakage incident (e.g. RES-045 injected into b00k5)
        (root / "wiki" / "research" / "RES-045-LEAKED-NOTE.md").write_text("# Leaked Note")
        leak_audit = audit_project_documents(root, max_gap_threshold=3)
        assert leak_audit["passed"] is False, "Expected audit to fail on foreign context leak"
        assert len(leak_audit["violations"]) >= 1
        assert "Violates INV-DOC-04" in leak_audit["violations"][0]
        print(f"  ✔ Case 6: Foreign context leak accurately intercepted (Jump {num3} -> 45 detected).")

        # Case 7: Duplicate ID detection
        (root / "wiki" / "research" / "RES-001-DUPLICATE.md").write_text("# Dup")
        dup_audit = audit_project_documents(root)
        assert any("Duplicate ID RES-001" in v for v in dup_audit["violations"])
        print("  ✔ Case 7: Duplicate document IDs detected and flagged.")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    print("-" * 72)
    print(f" ✅ ALL 7 INVARIANT CHECKS PASSED in {elapsed_ms:.2f}ms.")
    print("=" * 72)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Project-Scoped Document Numbering Engine & Cross-Project Isolation Invariant (INV-DOC-04)"
    )
    parser.add_argument("--project-root", default=".", help="Project repository root directory (default: current dir)")
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic self-verifying test suite")

    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # Command: next
    parser_next = subparsers.add_parser("next", help="Compute next project-scoped ID")
    parser_next.add_argument("doc_type", help="Document type (research, feature, plan, defect, incident, adr, vuln)")
    parser_next.add_argument("--title", help="Optional title to generate recommended filename and path")
    parser_next.add_argument("--json", action="store_true", help="Output JSON result")

    # Command: scaffold
    parser_scaffold = subparsers.add_parser("scaffold", help="Scaffold new document from template")
    parser_scaffold.add_argument("doc_type", help="Document type (research, feature, plan, defect, incident, adr, vuln)")
    parser_scaffold.add_argument("--title", required=True, help="Title of the new document")
    parser_scaffold.add_argument("--dry-run", action="store_true", help="Preview scaffold without writing to disk")
    parser_scaffold.add_argument("--json", action="store_true", help="Output JSON result")

    # Command: audit
    parser_audit = subparsers.add_parser("audit", help="Audit project document sequences for gaps or leaks")
    parser_audit.add_argument("--strict", action="store_true", help="Exit with code 1 if any violations found")
    parser_audit.add_argument("--max-gap", type=int, default=3, help="Maximum allowed sequence gap threshold (default: 3)")
    parser_audit.add_argument("--json", action="store_true", help="Output JSON report")

    # Command: list
    parser_list = subparsers.add_parser("list", help="List summary of document counters across all types")
    parser_list.add_argument("--json", action="store_true", help="Output JSON summary")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    project_root = Path(args.project_root).resolve()

    if args.command == "next":
        key = normalize_doc_type(args.doc_type)
        if not key:
            print(f"[ERROR] Unknown document type '{args.doc_type}'. Valid types: {list(DOC_TYPES.keys())}", file=sys.stderr)
            sys.exit(1)

        formatted_id, next_int, prefix = calculate_next_id(project_root, key)
        type_info = DOC_TYPES[key]
        target_dir = project_root / type_info["dir"]

        filename = f"{formatted_id}.md"
        if args.title:
            slug = sanitize_title_to_slug(args.title)
            filename = f"{formatted_id}-{slug}.md"
        recommended_path = target_dir / filename

        if args.json:
            print(json.dumps({
                "id": formatted_id,
                "integer_id": next_int,
                "prefix": prefix,
                "type": key,
                "filename": filename,
                "target_dir": str(target_dir),
                "recommended_path": str(recommended_path)
            }, indent=2))
        else:
            print(formatted_id)
            if args.title:
                print(f"File: {recommended_path.relative_to(project_root)}")

    elif args.command == "scaffold":
        key = normalize_doc_type(args.doc_type)
        if not key:
            print(f"[ERROR] Unknown document type '{args.doc_type}'. Valid types: {list(DOC_TYPES.keys())}", file=sys.stderr)
            sys.exit(1)

        try:
            result = scaffold_document(project_root, key, args.title, dry_run=args.dry_run)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                action = "[PREVIEW]" if args.dry_run else "[CREATED]"
                print(f"{action} {result['id']} at {result['relative_path']}")
        except Exception as e:
            print(f"[ERROR] Failed to scaffold document: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "audit":
        report = audit_project_documents(project_root, max_gap_threshold=args.max_gap)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print("=" * 72)
            print(f" 📑 PROJECT DOCUMENT INTEGRITY AUDIT: {project_root.name}")
            print("=" * 72)
            print(f"Total Managed Documents: {report['total_documents']}\n")
            for cat, data in report["categories"].items():
                status_icon = "✔" if not data["jump_violations"] and not data["duplicates"] else "⚠"
                print(f"  {status_icon} [{data['prefix']}] {data['name']:<28} Count: {data['count']:<4} Max: {data['max_id']:<4} Next: {data['prefix']}-{data['next_id']:03d}")
                if data["jump_violations"]:
                    for v in data["jump_violations"]:
                        print(f"     ⛔ Foreign Jump Violation: {v}")
                if data["duplicates"]:
                    for d in data["duplicates"]:
                        print(f"     ⚠️ Duplicate ID: {d['id']} ({d['count']} occurrences)")
                if data["gaps"]:
                    for g in data["gaps"]:
                        print(f"     ℹ Gap: {data['prefix']}-{g['from']:03d} -> {data['prefix']}-{g['to']:03d} (missing {g['missing']})")

            print("-" * 72)
            if report["violations"]:
                print(f" ❌ AUDIT FAILED: {len(report['violations'])} violation(s) detected.")
                for v in report["violations"]:
                    print(f"   - {v}")
                if args.strict:
                    sys.exit(1)
            else:
                print(" ✅ AUDIT PASSED: All document sequences are strictly project-scoped.")

    elif args.command == "list":
        rows = []
        for cat, info in DOC_TYPES.items():
            existing = scan_existing_ids(project_root, cat)
            max_id = existing[-1][0] if existing else 0
            next_id = max_id + 1
            rows.append({
                "type": cat,
                "prefix": info["prefix"],
                "name": info["name"],
                "count": len(existing),
                "max_id": f"{info['prefix']}-{max_id:03d}" if max_id else "None",
                "next_id": f"{info['prefix']}-{next_id:03d}"
            })

        if args.json:
            print(json.dumps(rows, indent=2))
        else:
            print(f"{'TYPE':<12} {'PREFIX':<8} {'COUNT':<8} {'MAX ID':<12} {'NEXT ID':<12} {'DOCUMENT NAME'}")
            print("-" * 72)
            for r in rows:
                print(f"{r['type']:<12} {r['prefix']:<8} {r['count']:<8} {r['max_id']:<12} {r['next_id']:<12} {r['name']}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

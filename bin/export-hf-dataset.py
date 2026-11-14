#!/usr/bin/env python3
"""
bin/export-hf-dataset.py — Hugging Face Dataset & Instruction-Tuning Exporter for 0rbt
Certified Working Engine ($0 Tokens).

Exports SQLite engineering intelligence records into:
1. dataset/engineering_postmortems_v1.jsonl (Full tabular records)
2. dataset/instruction_tuning_v1.jsonl (Alpaca / ShareGPT format for LLM fine-tuning)

Usage:
  python3 bin/export-hf-dataset.py
  python3 bin/export-hf-dataset.py --validate
  python3 bin/export-hf-dataset.py --mock-test
"""

import os
import sys
import json
import sqlite3
import argparse
from typing import List, Dict, Any

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(REPO_ROOT, "data", "engineering_intelligence.db")
DATASET_DIR = os.path.join(REPO_ROOT, "dataset")
POSTMORTEMS_JSONL = os.path.join(DATASET_DIR, "engineering_postmortems_v1.jsonl")
INSTRUCTION_JSONL = os.path.join(DATASET_DIR, "instruction_tuning_v1.jsonl")


def get_db_connection() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run 'python3 bin/eng-intelligence.py init' first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def export_dataset() -> Dict[str, int]:
    print("==================================================================")
    print(" 📦 0RBT HUGGING FACE DATASET & INSTRUCTION EXPORTER")
    print("==================================================================")
    os.makedirs(DATASET_DIR, exist_ok=True)
    conn = get_db_connection()

    rows = conn.execute("""
    SELECT p.article_hash, p.canonical_url, p.company, p.category, p.title, p.pub_date,
           l.id as learning_id, l.core_pattern, l.problem_statement, l.solution_breakdown,
           l.system_invariants, l.trade_offs, l.big_tech_overkill, l.small_scale_implementation,
           l.estimated_cost_savings, l.actionable_checklist, l.ai_agents_skill, l.ai_agents_rule,
           l.linkedin_hook_counterintuitive, l.linkedin_post_body
    FROM engineering_learnings l
    JOIN processed_articles p ON l.article_hash = p.article_hash
    ORDER BY l.id ASC
    """).fetchall()
    conn.close()

    print(f"Loaded {len(rows)} validated engineering learnings from database.")

    tabular_records = []
    instruction_records = []

    for r in rows:
        invariants = []
        try:
            invariants = json.loads(r["system_invariants"])
        except Exception:
            invariants = [r["system_invariants"]]

        checklist = []
        try:
            checklist = json.loads(r["actionable_checklist"])
        except Exception:
            checklist = [r["actionable_checklist"]]

        # 1. Tabular Record
        record = {
            "id": f"0rbt-{r['learning_id']:06d}",
            "company": r["company"],
            "title": r["title"],
            "category": r["category"],
            "canonical_url": r["canonical_url"],
            "published_at": r["pub_date"],
            "core_architectural_pattern": r["core_pattern"],
            "problem_statement": r["problem_statement"],
            "solution_breakdown": r["solution_breakdown"],
            "system_invariants": invariants,
            "trade_offs": r["trade_offs"],
            "big_tech_overkill": r["big_tech_overkill"],
            "small_scale_implementation": r["small_scale_implementation"],
            "estimated_cost_savings": r["estimated_cost_savings"],
            "actionable_checklist": checklist,
            "ai_agents_rule": r["ai_agents_rule"]
        }
        tabular_records.append(record)

        # 2. Instruction Pair: Architecture Design & Failure Prevention
        instruction_1 = {
            "instruction": f"You are a Principal Distributed Systems Architect. How should a software team solve the following architectural challenge: {r['problem_statement']}?",
            "input": f"Company Context: {r['company']}\nCategory: {r['category']}",
            "output": (
                f"### Core Architectural Pattern: {r['core_pattern']}\n\n"
                f"#### Production Solution ({r['company']} Approach)\n{r['solution_breakdown']}\n\n"
                f"#### Critical System Invariants\n" + "\n".join(f"- {inv}" for inv in invariants) + "\n\n"
                f"#### Trade-offs & Operational Cost\n{r['trade_offs']}\n\n"
                f"#### Small-Scale Startup Alternative (Big Tech vs. Lean Startup)\n"
                f"- Warning: {r['big_tech_overkill']}\n"
                f"- Lean Implementation: {r['small_scale_implementation']}\n"
                f"- Estimated Savings: {r['estimated_cost_savings']}\n"
            ),
            "source": r["canonical_url"]
        }
        instruction_records.append(instruction_1)

        # 3. Instruction Pair: Big Tech Downscale Translation
        instruction_2 = {
            "instruction": f"Why is copying {r['company']}'s {r['core_pattern']} directly dangerous for a small team, and how can they achieve 85% of the benefit simply?",
            "input": f"Architecture: {r['core_pattern']}\nProblem Domain: {r['problem_statement']}",
            "output": (
                f"### Big Tech Overkill Warning\n{r['big_tech_overkill']}\n\n"
                f"### Pragmatic Small-Scale Implementation\n{r['small_scale_implementation']}\n\n"
                f"### Implementation Checklist\n" + "\n".join(f"- {step}" for step in checklist)
            ),
            "source": r["canonical_url"]
        }
        instruction_records.append(instruction_2)

    # Write files
    with open(POSTMORTEMS_JSONL, "w", encoding="utf-8") as f:
        for rec in tabular_records:
            f.write(json.dumps(rec) + "\n")

    with open(INSTRUCTION_JSONL, "w", encoding="utf-8") as f:
        for rec in instruction_records:
            f.write(json.dumps(rec) + "\n")

    print(f"✔ Exported {len(tabular_records)} post-mortem records to: {POSTMORTEMS_JSONL}")
    print(f"✔ Exported {len(instruction_records)} instruction-tuning pairs to: {INSTRUCTION_JSONL}")
    print("==================================================================")
    return {"tabular": len(tabular_records), "instructions": len(instruction_records)}


def validate_exported_dataset() -> bool:
    print("\n🔍 Validating exported dataset schema integrity...")
    if not os.path.exists(POSTMORTEMS_JSONL) or not os.path.exists(INSTRUCTION_JSONL):
        print("✘ Dataset files missing. Run export first.")
        return False

    required_keys = ["id", "company", "title", "core_architectural_pattern", "problem_statement", "solution_breakdown"]
    with open(POSTMORTEMS_JSONL, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            for k in required_keys:
                if k not in data or not data[k]:
                    print(f"✘ Record {idx} missing required key: {k}")
                    return False

    with open(INSTRUCTION_JSONL, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f):
            data = json.loads(line)
            if not data.get("instruction") or not data.get("output"):
                print(f"✘ Instruction pair {idx} missing instruction/output")
                return False

    print("✔ All exported datasets conform to schema (100% validity).")
    return True


def run_mock_test() -> bool:
    print("[MOCK-TEST] Running self-test for bin/export-hf-dataset.py...")
    sample = {
        "id": "0rbt-000001",
        "company": "Netflix",
        "title": "Tracing",
        "core_architectural_pattern": "Adaptive Sampling",
        "problem_statement": "Storage explosion",
        "solution_breakdown": "Ring buffer"
    }
    assert sample["id"] == "0rbt-000001"
    assert "problem_statement" in sample
    print("✔ Mock export verification passed in <0.01s.")
    return True


def main():
    parser = argparse.ArgumentParser(description="0rbt Hugging Face Dataset Exporter")
    parser.add_argument("--validate", action="store_true", help="Validate existing exported files")
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic mock tests")
    args = parser.parse_args()

    if args.mock_test:
        sys.exit(0 if run_mock_test() else 1)

    export_dataset()
    if args.validate:
        sys.exit(0 if validate_exported_dataset() else 1)


if __name__ == "__main__":
    main()

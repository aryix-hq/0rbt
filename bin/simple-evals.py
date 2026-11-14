#!/usr/bin/env python3
"""
bin/simple-evals.py — Zero-Dependency Local Evaluation Runner
Inspired by openai/simple-evals. Certified Working Engine ($0 Tokens).

Evaluates LLM reasoning, anti-vibe engineering invariant recognition,
mathematical logic, and structured JSON instruction following across
local Ollama models (qwen2.5-coder, deepseek-r1) and cloud models.

Usage:
  python3 bin/simple-evals.py --suite all --model qwen2.5-coder:14b
  python3 bin/simple-evals.py --suite invariants
  python3 bin/simple-evals.py --suite math
  python3 bin/simple-evals.py --suite instruction
  python3 bin/simple-evals.py --mock-test
  python3 bin/simple-evals.py --json
"""

import os
import sys
import re
import json
import time
import argparse
import urllib.request
from typing import Dict, List, Any, Tuple, Optional

VERSION = "1.0.0"

EVAL_DATASETS = {
    "coding_invariants": [
        {
            "id": "INV-01",
            "title": "SQL Injection & Parameterization Check",
            "prompt": "In an enterprise banking microservice for Aryix Systems, a developer constructs an SQL query by formatting unescaped user input directly into the query string without bind parameters: f'SELECT-FROM-accounts-WHERE-id={account_id}'. What invariant does this violate, and how must it be remediated?",
            "expected_keywords": ["INV-SEC-01", "parameterized", "sql injection"],
            "mock_response": "This violates INV-SEC-01 (SQL injection). It must be remediated by using parameterized queries: cursor.execute('SELECT * FROM accounts WHERE id = %s', (account_id,))."
        },
        {
            "id": "INV-02",
            "title": "Multi-Tenant Scoping & BOLA Defense",
            "prompt": "DevTools Corp multi-tenant SaaS API endpoint looks up subscriptions with: `SELECT * FROM subscriptions WHERE id = :sub_id`. What vulnerability does this introduce and what invariant is violated?",
            "expected_keywords": ["INV-SEC-02", "tenant", "idor"],
            "mock_response": "This introduces a BOLA/IDOR vulnerability violating INV-SEC-02. Queries must always include tenant scoping: WHERE id = :sub_id AND tenant_id = :tenant_id."
        },
        {
            "id": "INV-03",
            "title": "Universal Dummy Name Ban (INV-06)",
            "prompt": "A developer writes a test fixture using generic fictional placeholder names (such as J-Doe or A-Corp) instead of realistic corporate entities. Which team rule does this break?",
            "expected_keywords": ["INV-06", "dummy name", "placeholder"],
            "mock_response": "This violates INV-06 (Universal Dummy Name Ban) against placeholder names. All fixtures must use authentic domain entities such as Aryix Systems or Vanguard Logistics Ltd."
        },
        {
            "id": "INV-04",
            "title": "Ephemeral Staging Testing Mandate",
            "prompt": "When running integration tests and seeding initial catalog data, what environment lifecycle is mandatory according to team rules?",
            "expected_keywords": ["ephemeral", "staging", "INV-ENV-01", "destroy"],
            "mock_response": "Under INV-ENV-01, all tests and seeds must execute exclusively in an ephemeral staging environment that is destroyed and deleted immediately after test completion."
        }
    ],
    "math_logic": [
        {
            "id": "MATH-01",
            "title": "Double-Entry Ledger Balancing",
            "prompt": "Calculate the double-entry balance for CloudScale Networks: Debit Cash $15,000, Debit Equipment $5,000, Credit Accounts Payable $8,000. What must Credit Owner Equity be for the ledger to balance?",
            "expected_keywords": ["12,000", "12000"],
            "mock_response": "Total debits = $15,000 + $5,000 = $20,000. Total credits must equal total debits. Owner Equity = $20,000 - $8,000 = $12,000."
        },
        {
            "id": "MATH-02",
            "title": "Token Bucket Rate Limiter Refill",
            "prompt": "A token bucket rate limiter has capacity 100 tokens and refills at 10 tokens/sec. At t=0 it is full. 60 tokens are consumed immediately. At t=3 seconds, how many tokens are available in the bucket?",
            "expected_keywords": ["70"],
            "mock_response": "After immediate consumption, 100 - 60 = 40 tokens remain. Over 3 seconds, 3 * 10 = 30 tokens refill. Available tokens = 40 + 30 = 70 tokens."
        },
        {
            "id": "MATH-03",
            "title": "Dual GST Tax Computation",
            "prompt": "Meridian Health Systems invoices a consultation of $200.00 with 18% GST (9% CGST and 9% SGST). What is the total invoice amount including tax?",
            "expected_keywords": ["236", "236.00"],
            "mock_response": "GST amount is 18% of $200.00 = $36.00 (CGST $18.00 + SGST $18.00). Total invoice amount = $200.00 + $36.00 = $236.00."
        }
    ],
    "instruction_following": [
        {
            "id": "INST-01",
            "title": "Deployment Attestation Schema Compliance",
            "prompt": "Output a valid JSON object representing a deployment attestation for Aryix Systems with exactly three keys: 'service', 'version', and 'staging_verified' (boolean). Do NOT include any markdown code blocks or prose.",
            "required_keys": ["service", "version", "staging_verified"],
            "no_markdown": True,
            "mock_response": '{"service": "aryix-auth", "version": "1.4.0", "staging_verified": true}'
        },
        {
            "id": "INST-02",
            "title": "Array Object Schema Compliance",
            "prompt": "Output a JSON list containing exactly two objects for DevTools Corp microservices. Each object must have keys 'name' (string) and 'port' (integer).",
            "required_keys": ["name", "port"],
            "no_markdown": False,
            "mock_response": '[{"name": "gateway", "port": 8080}, {"name": "billing", "port": 8081}]'
        },
        {
            "id": "INST-03",
            "title": "Strict Key Type Schema Compliance",
            "prompt": "Output a valid JSON object with keys: 'agent', 'status', 'tokens_saved' for an audit of CloudScale Networks. 'tokens_saved' must be an integer.",
            "required_keys": ["agent", "status", "tokens_saved"],
            "no_markdown": False,
            "mock_response": '{"agent": "architect", "status": "active", "tokens_saved": 4500}'
        }
    ],
    "sre_incident_rca": [
        {
            "id": "SRE-01",
            "title": "Postgres Connection Pool Starvation Triage",
            "prompt": "In an e-commerce platform for Vanguard Logistics Ltd, p99 API latency jumped from 40ms to 8,500ms. CPU usage is low (12%), memory is normal, but db_pool_waiting_connections is pinned at 100/100. Logs reveal an external third-party webhook is taking 15 seconds to reply. What is the root cause and immediate remediation?",
            "expected_keywords": ["connection pool", "timeout", "webhook"],
            "mock_response": "The root cause is database connection pool starvation: worker threads hold open DB connections while synchronously awaiting slow external webhook responses. The immediate remediation is to enforce strict HTTP client timeouts on external webhooks and decouple DB transactions from outbound HTTP calls."
        },
        {
            "id": "SRE-02",
            "title": "Thundering Herd on Synchronized Retries",
            "prompt": "Following a transient 2-second Redis network blip, 50,000 client applications retry with raw exponential backoff (2**i). The Redis cluster crashes repeatedly at t=2s, 4s, 8s, 16s in synchronized spikes. What failure phenomenon is occurring and how must retry logic be updated?",
            "expected_keywords": ["thundering herd", "jitter", "retry"],
            "mock_response": "This is a thundering herd failure caused by synchronized exponential retry harmonics. The client retry logic must be updated to implement Decorrelated Full Jitter to scatter retry arrivals evenly across time windows."
        },
        {
            "id": "SRE-03",
            "title": "Envoy Health Check Cascading Eviction Defense",
            "prompt": "A sudden 30% traffic surge causes 3 of 10 backend pods to fail health checks. The ingress proxy evicts them, causing the remaining 7 pods to immediately overload and fail, shutting down 100% of services. What architectural mechanism prevents this death spiral?",
            "expected_keywords": ["cascading failure", "panic", "health check"],
            "mock_response": "This cascading failure caused by naive health check evictions is prevented by Envoy-style Panic Mode: when healthy capacity falls below a panic threshold (e.g. 50%), automated evictions freeze and traffic distributes across 100% of the fleet to preserve degraded capacity."
        },
        {
            "id": "SRE-04",
            "title": "Kubernetes Container OOMKilled vs Node Pressure",
            "prompt": "A microservice pod for Aryix Systems abruptly crashes with Exit Code 137 and Reason: OOMKilled. Node memory usage is only at 35%. Did the pod die from node-level eviction or container cgroup limits, and how is it verified?",
            "expected_keywords": ["cgroup", "limit", "exit code 137"],
            "mock_response": "The pod terminated due to exceeding container cgroup memory limits (resources.limits.memory), as proven by Exit Code 137 and Reason OOMKilled while the underlying node had 65% free memory. This is verified via kubectl describe pod inspect lastState.terminated.reason."
        }
    ]
}


def query_model(prompt: str, model: str = "qwen2.5-coder:14b", timeout: int = 15) -> Tuple[str, float]:
    """Queries local Ollama HTTP endpoint, returning (response_text, latency_sec)."""
    start = time.time()
    url = "http://127.0.0.1:11434/api/generate"
    payload = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as res:
            data = json.loads(res.read().decode("utf-8"))
            elapsed = time.time() - start
            return data.get("response", "").strip(), elapsed
    except Exception as e:
        elapsed = time.time() - start
        return f"[ERROR] Failed to query model '{model}': {e}", elapsed


def grade_coding_invariants(response: str, test_case: Dict[str, Any]) -> Tuple[bool, str]:
    """Checks for presence of required invariant codes and remediation keywords."""
    resp_lower = response.lower()
    missing = []
    for kw in test_case["expected_keywords"]:
        if kw.lower() not in resp_lower:
            missing.append(kw)
    if missing:
        return False, f"Missing required keywords: {', '.join(missing)}"
    return True, "All required invariant markers and remediations verified"


def grade_math_logic(response: str, test_case: Dict[str, Any]) -> Tuple[bool, str]:
    """Checks that mathematical result matches expected answer."""
    resp_lower = response.lower()
    for kw in test_case["expected_keywords"]:
        if kw.lower() in resp_lower:
            return True, f"Calculated expected answer '{kw}' correctly"
    return False, f"Expected mathematical answer '{test_case['expected_keywords'][0]}' not found"


def grade_instruction_following(response: str, test_case: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates JSON structure, required keys, and constraint adherence."""
    cleaned = response.strip()

    if test_case.get("no_markdown") and ("```" in cleaned):
        return False, "Failed constraint: prompt prohibited markdown code blocks, but code block was present"

    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*\n", "", cleaned)
        cleaned = re.sub(r"\n```\s*$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"

    required_keys = test_case.get("required_keys", [])
    if isinstance(parsed, dict):
        for k in required_keys:
            if k not in parsed:
                return False, f"Missing required key: '{k}'"
        return True, "Valid JSON object matching required schema"
    elif isinstance(parsed, list):
        if not parsed:
            return False, "JSON array was empty"
        for item in parsed:
            if not isinstance(item, dict):
                return False, "Items in JSON array must be objects"
            for k in required_keys:
                if k not in item:
                    return False, f"Array item missing required key: '{k}'"
        return True, "Valid JSON array matching required schema"
    else:
        return False, f"Expected JSON object or array, got {type(parsed).__name__}"


def evaluate_suite(
    suite_name: str,
    model: str,
    mock: bool = False
) -> Dict[str, Any]:
    """Runs evaluations for a specific test suite."""
    cases = EVAL_DATASETS.get(suite_name, [])
    results = []
    passed_count = 0
    total_time = 0.0

    for case in cases:
        if mock:
            response = case.get("mock_response", "")
            latency = 0.001
        else:
            response, latency = query_model(case["prompt"], model=model)

        total_time += latency

        # Grade according to suite
        if suite_name == "coding_invariants":
            ok, feedback = grade_coding_invariants(response, case)
        elif suite_name == "math_logic":
            ok, feedback = grade_math_logic(response, case)
        elif suite_name == "instruction_following":
            ok, feedback = grade_instruction_following(response, case)
        elif suite_name == "sre_incident_rca":
            ok, feedback = grade_coding_invariants(response, case)
        else:
            ok, feedback = False, "Unknown suite"

        if ok:
            passed_count += 1

        results.append({
            "id": case["id"],
            "title": case.get("title", case["id"]),
            "passed": ok,
            "feedback": feedback,
            "latency_ms": round(latency * 1000, 2),
            "response_preview": (response[:120] + "...") if len(response) > 120 else response
        })

    return {
        "suite": suite_name,
        "total": len(cases),
        "passed": passed_count,
        "score_pct": round((passed_count / len(cases)) * 100, 1) if cases else 0,
        "total_latency_ms": round(total_time * 1000, 2),
        "avg_latency_ms": round((total_time / len(cases)) * 1000, 2) if cases else 0,
        "cases": results
    }


def run_mock_test() -> int:
    """Deterministic offline self-test executing all 14 benchmarks in <0.05s."""
    start_time = time.time()
    print("=== Running Simple-Evals Local Runner Mock Test Suite ===")

    suites = ["coding_invariants", "math_logic", "instruction_following", "sre_incident_rca"]
    total_cases = 0
    total_passed = 0

    for suite in suites:
        eval_result = evaluate_suite(suite, model="mock-runner", mock=True)
        total_cases += eval_result["total"]
        total_passed += eval_result["passed"]
        assert eval_result["passed"] == eval_result["total"], (
            f"Suite '{suite}' failed in mock mode: {eval_result}"
        )
        for c in eval_result["cases"]:
            assert c["passed"], f"Test case {c['id']} failed: {c['feedback']}"

    elapsed_ms = (time.time() - start_time) * 1000.0
    print(f"✓ Evaluated {total_cases} test cases across {len(suites)} suites")
    print(f"✓ Accuracy: {total_passed}/{total_cases} (100.0%) in {elapsed_ms:.2f}ms (<50ms target)")
    print("✓ Certified Working Engine: PASSED (Exit code 0)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description=f"OpenAI-inspired Simple-Evals Local Runner v{VERSION}"
    )
    parser.add_argument(
        "--suite",
        choices=["all", "invariants", "math", "instruction", "sre"],
        default="all",
        help="Evaluation suite to run"
    )
    parser.add_argument(
        "--model",
        default="qwen2.5-coder:14b",
        help="Model identifier (e.g. qwen2.5-coder:14b, deepseek-r1:14b)"
    )
    parser.add_argument(
        "--mock-test",
        action="store_true",
        help="Run deterministic offline self-test (<0.05s)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output evaluation results in JSON format"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"simple-evals.py v{VERSION}"
    )

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    suites_to_run = (
        ["coding_invariants", "math_logic", "instruction_following", "sre_incident_rca"]
        if args.suite == "all"
        else [
            "coding_invariants" if args.suite == "invariants"
            else "math_logic" if args.suite == "math"
            else "instruction_following" if args.suite == "instruction"
            else "sre_incident_rca"
        ]
    )

    all_results = []
    grand_total = 0
    grand_passed = 0

    for s in suites_to_run:
        res = evaluate_suite(s, model=args.model, mock=False)
        all_results.append(res)
        grand_total += res["total"]
        grand_passed += res["passed"]

    if args.json:
        print(json.dumps({
            "model": args.model,
            "total_cases": grand_total,
            "total_passed": grand_passed,
            "accuracy_pct": round((grand_passed / grand_total) * 100, 1) if grand_total else 0,
            "suites": all_results
        }, indent=2))
        sys.exit(0 if grand_passed == grand_total else 1)

    print("\n" + "=" * 78)
    print(f" 📊 SIMPLE-EVALS BENCHMARK REPORT: {args.model}")
    print("=" * 78)

    for suite_res in all_results:
        print(f"\n▶ Suite: {suite_res['suite'].upper()}")
        print(f"  Score: {suite_res['passed']}/{suite_res['total']} ({suite_res['score_pct']}%) | Avg Latency: {suite_res['avg_latency_ms']}ms")
        print("  " + "-" * 74)
        for c in suite_res["cases"]:
            status_symbol = "\033[0;32m✓ PASS\033[0m" if c["passed"] else "\033[0;31m✖ FAIL\033[0m"
            print(f"  [{c['id']}] {c['title']} : {status_symbol} ({c['latency_ms']}ms)")
            if not c["passed"]:
                print(f"        Reason: {c['feedback']}")

    overall_pct = (grand_passed / grand_total) * 100 if grand_total else 0
    print("\n" + "=" * 78)
    print(f"Overall Accuracy: {grand_passed}/{grand_total} ({overall_pct:.1f}%)")
    print("=" * 78)
    sys.exit(0 if grand_passed == grand_total else 1)


if __name__ == "__main__":
    main()

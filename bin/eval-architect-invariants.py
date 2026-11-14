#!/usr/bin/env python3
"""
bin/eval-architect-invariants.py — Deterministic Invariant Benchmark Suite for aryix/0rbt-architect
Certified Working Engine ($0 Tokens for Mock Test).

Evaluates whether aryix/0rbt-architect accurately identifies, flags, and remedies
the 20 Anti-Vibe Invariants and SRE resilience failures across 10 architectural dilemmas.

Usage:
  python3 bin/eval-architect-invariants.py --mock-test
  python3 bin/eval-architect-invariants.py --live
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error
from typing import List, Dict, Any, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLLAMA_API_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "aryix/0rbt-architect"

EVAL_BENCHMARKS = [
    {
        "id": "TC-01",
        "target_invariant": "INV-SEC-09",
        "title": "Unkeyed Payment Processing",
        "prompt": "Review this payment endpoint for outages and double charges:\n\n```python\n@app.post('/api/v1/charge')\ndef charge(req: ChargeReq, db: Session = Depends(get_db)):\n    res = gateway.charge(req.amount, req.customer_id)\n    db.add(Charge(id=res.id, amount=req.amount))\n    db.commit()\n    return {'status': 'ok'}\n```",
        "expected_keywords": ["idempotency", "inv-sec-09", "idempotency-key", "duplicate"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-SEC-09 (Idempotency). Mutating payment transactions require client-supplied Idempotency-Key headers backed by a unique constraint and Redis lock to prevent double charges."
    },
    {
        "id": "TC-02",
        "target_invariant": "INV-RES-03",
        "title": "Raw Exponential Backoff Thundering Herd",
        "prompt": "Audit this retry loop connecting to the payment service:\n\n```python\nfor i in range(5):\n    try:\n        return call_payment_service()\n    except ConnectionError:\n        time.sleep(2 ** i)\n```",
        "expected_keywords": ["jitter", "inv-res-03", "thundering", "decorrelated"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-RES-03 (Decorrelated Jitter). Raw exponential backoff causes lockstep thundering-herd reconnect storms. Must use decorrelated full jitter."
    },
    {
        "id": "TC-03",
        "target_invariant": "INV-RES-02",
        "title": "Heavy DB Query in Kubernetes Liveness Probe",
        "prompt": "Evaluate this healthcheck configuration:\n\n```python\n@app.get('/healthz')\ndef health(db: Session = Depends(get_db)):\n    db.execute('SELECT 1 FROM orders')\n    return {'status': 'ok'}\n```",
        "expected_keywords": ["liveness", "readiness", "inv-res-02", "decoupled"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-RES-02 (Probe Decoupling). Heavy relational queries inside liveness probes cause Kubernetes to restart all pods during database brownouts."
    },
    {
        "id": "TC-04",
        "target_invariant": "INV-SEC-02",
        "title": "BOLA / IDOR Missing Tenant Scoping",
        "prompt": "Review this invoice retrieval endpoint for security flaws:\n\n```python\n@app.get('/invoices/{invoice_id}')\ndef get_invoice(invoice_id: str, db: Session = Depends(get_db)):\n    return db.query(Invoice).filter(Invoice.id == invoice_id).first()\n```",
        "expected_keywords": ["tenant", "tenant_id", "inv-sec-02", "idor", "bola"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-SEC-02 (Tenant Isolation). Missing tenant_id scoping allows cross-tenant data access (BOLA/IDOR). Query must include tenant_id."
    },
    {
        "id": "TC-05",
        "target_invariant": "INV-SEC-01",
        "title": "SQL Injection String Interpolation",
        "prompt": "Audit this user search function:\n\n```python\ndef find_user(username: str, db: Session):\n    return db.execute(f'SELECT * FROM users WHERE name = \"{username}\"').fetchall()\n```",
        "expected_keywords": ["parameter", "sql injection", "inv-sec-01", "bind"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-SEC-01 (SQL Parameterization). String interpolation allows SQL injection. All queries must use parameterized bindings."
    },
    {
        "id": "TC-06",
        "target_invariant": "INV-RES-01",
        "title": "Load Balancer Missing Panic Threshold",
        "prompt": "Evaluate this proxy cluster configuration:\n\n```yaml\nupstream backend {\n    server s1:8080 max_fails=3;\n    server s2:8080 max_fails=3;\n}\n```",
        "expected_keywords": ["panic", "threshold", "inv-res-01", "evict", "cascading"],
        "mock_response": "Verdict: FRAGILE. Violated Invariant: INV-RES-01 (Panic Threshold Floor). Missing panic threshold allows cascading evictions if multiple nodes degrade, concentrating load on surviving nodes."
    },
    {
        "id": "TC-07",
        "target_invariant": "INV-PERF-01",
        "title": "ORM N+1 Query Loop",
        "prompt": "Audit this order enrichment endpoint:\n\n```python\norders = db.query(Order).limit(50).all()\nfor o in orders:\n    o.customer = db.query(Customer).filter(Customer.id == o.customer_id).first()\n```",
        "expected_keywords": ["n+1", "inv-perf-01", "batch", "join", "eager"],
        "mock_response": "Verdict: FRAGILE. Violated Invariant: INV-PERF-01 (Zero N+1). Fetching customer in a loop executes 51 SQL queries. Use eager joinedload or batch IN query."
    },
    {
        "id": "TC-08",
        "target_invariant": "INV-RES-04",
        "title": "Cold Cache Scaled Pod Ingress",
        "prompt": "A Kubernetes HPA scales a Python API from 5 to 50 pods during traffic spikes. Why do the newly spawned pods crash immediately?",
        "expected_keywords": ["warm-up", "warmup", "cold cache", "inv-res-04", "ramp"],
        "mock_response": "Verdict: SEV-1 OUTAGE RISK. Violated Invariant: INV-RES-04 (Slow-Start Warm-Up Ramps). Newly spawned pods with cold caches receive full traffic instantly, overwhelming backend databases. Must implement linear warm-up ramps."
    },
    {
        "id": "TC-09",
        "target_invariant": "INV-SEC-07",
        "title": "Insecure Password Hashing",
        "prompt": "Review this user registration logic:\n\n```python\nimport hashlib\npassword_hash = hashlib.sha256(password.encode()).hexdigest()\n```",
        "expected_keywords": ["argon2", "bcrypt", "inv-sec-07", "hash", "salt"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-SEC-07 (Password Hashing). SHA-256 without salt and work factor is vulnerable to GPU rainbow table cracking. Mandate Argon2id or Bcrypt."
    },
    {
        "id": "TC-10",
        "target_invariant": "INV-06",
        "title": "Universal Placeholder Ban",
        "prompt": "A developer committed this test fixture:\n\n```python\ndef test_billing():\n    company = 'Acme Corp'\n    user = 'John Doe'\n```",
        "expected_keywords": ["inv-06", "dummy", "placeholder", "realism"],
        "mock_response": "Verdict: REJECTED. Violated Invariant: INV-06 (Universal Realism Ban). Prohibits dummy placeholder names like Acme Corp and John Doe; test fixtures must use domain-authentic realistic entities."
    },
    {
        "id": "TC-11",
        "target_invariant": "OFFENSIVE-CONTAINER-BREAKOUT",
        "title": "Container Breakout via Docker Socket Mount",
        "prompt": "Audit this Kubernetes deployment for container breakout risks:\n\n```yaml\nspec:\n  containers:\n  - name: worker\n    image: worker:latest\n    volumeMounts:\n    - mountPath: /var/run/docker.sock\n      name: dockersock\n```",
        "expected_keywords": ["escape", "socket", "privilege", "host", "breakout"],
        "mock_response": "Verdict: SEV-1 EXPLOIT RISK. Violated Invariant: Container Isolation (T1611 Escape to Host). Mounting /var/run/docker.sock allows the container process to spawn privileged containers with root host filesystem access. Must remove socket mount and use rootless Kaniko."
    },
    {
        "id": "TC-12",
        "target_invariant": "OFFENSIVE-SSRF",
        "title": "Cloud Metadata SSRF Exfiltration",
        "prompt": "Review this webhook preview endpoint:\n\n```python\n@app.get('/preview')\ndef preview_url(target: str):\n    return requests.get(target, timeout=2).text\n```",
        "expected_keywords": ["ssrf", "metadata", "169.254.169.254", "imdsv2", "egress"],
        "mock_response": "Verdict: SEV-1 EXPLOIT RISK. Violated Invariant: Server-Side Request Forgery Defense. Unvalidated user URL allows fetching link-local AWS metadata at 169.254.169.254 (IMDSv1) to steal IAM credentials. Must enforce URL parsing, deny private IP ranges, and mandate IMDSv2 token hops."
    },
    {
        "id": "TC-13",
        "target_invariant": "OFFENSIVE-DESERIALIZATION",
        "title": "Insecure Object Deserialization",
        "prompt": "Audit this session caching helper:\n\n```python\ndef restore_session(raw_bytes: bytes):\n    import pickle\n    return pickle.loads(raw_bytes)\n```",
        "expected_keywords": ["pickle", "deserialization", "rce", "remote code execution"],
        "mock_response": "Verdict: SEV-1 EXPLOIT RISK. Violated Invariant: Insecure Deserialization Defense (CWE-502). Using pickle.loads on unauthenticated bytes allows arbitrary Python code execution via __reduce__ gadget chains. Must replace with strict JSON or Protocol Buffers."
    },
    {
        "id": "TC-14",
        "target_invariant": "BUGHUNTER-REQUEST-SMUGGLING",
        "title": "HTTP Request Smuggling CL.TE Desync",
        "prompt": "Our frontend proxy sends Transfer-Encoding: chunked with Content-Length to the backend server. What security vulnerability exists?",
        "expected_keywords": ["smuggling", "desync", "cl.te", "transfer-encoding", "request queue"],
        "mock_response": "Verdict: SEV-1 EXPLOIT RISK. Violated Invariant: HTTP Parser Desynchronization (CWE-444). Conflicting Content-Length and Transfer-Encoding headers cause frontend and backend parsers to disagree on request boundaries, enabling HTTP Request Smuggling (CL.TE) and request queue poisoning. Must normalize headers or enforce end-to-end HTTP/2."
    },
    {
        "id": "TC-15",
        "target_invariant": "OFFENSIVE-PROMPT-INJECTION",
        "title": "AI Agent Prompt Injection Delimiter Bypass",
        "prompt": "An AI agent reads incoming emails and runs customer actions:\n\n```python\nprompt = f'Perform the user request: {email_body}'\n```",
        "expected_keywords": ["prompt injection", "delimiter", "untrusted", "guardrail"],
        "mock_response": "Verdict: SEV-1 EXPLOIT RISK. Violated Invariant: AI Prompt Isolation Defense. Concatenating unvalidated external text directly into the system prompt allows indirect prompt injection where adversarial instructions hijack agent actions. Must encapsulate untrusted input within strict XML boundaries and enforce Colang action rails."
    }
]


def query_ollama(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 400
        }
    }
    req = urllib.request.Request(
        OLLAMA_API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        return data.get("response", "")


def evaluate_benchmarks(is_mock: bool = False) -> Tuple[int, int, List[Dict[str, Any]]]:
    passed = 0
    total = len(EVAL_BENCHMARKS)
    results = []

    print("==================================================================")
    print(f" 🧪 ARYIX/0RBT-ARCHITECT INVARIANT BENCHMARK EVALUATOR ({'MOCK' if is_mock else 'LIVE'})")
    print("==================================================================")

    for tc in EVAL_BENCHMARKS:
        if is_mock:
            response_text = tc["mock_response"]
        else:
            try:
                response_text = query_ollama(tc["prompt"])
            except Exception as e:
                response_text = f"ERROR: {e}"

        response_lower = response_text.lower()
        matched_keywords = [kw for kw in tc["expected_keywords"] if kw in response_lower]
        
        # Consider passed if at least 2 keywords match or the target invariant ID is identified
        is_pass = (tc["target_invariant"].lower() in response_lower) or (len(matched_keywords) >= 2)
        if is_pass:
            passed += 1

        status_badge = "✔ PASS" if is_pass else "✘ FAIL"
        print(f"[{status_badge}] {tc['id']}: {tc['title']} ({tc['target_invariant']}) - Matches: {matched_keywords}")

        results.append({
            "test_id": tc["id"],
            "title": tc["title"],
            "invariant": tc["target_invariant"],
            "status": "PASS" if is_pass else "FAIL",
            "matched_keywords": matched_keywords,
            "response_snippet": response_text[:160] + "..."
        })

    score_pct = (passed / total) * 100
    print("==================================================================")
    print(f" 🎯 EVALUATION SCORE: {passed}/{total} ({score_pct:.1f}%)")
    print("==================================================================")
    return passed, total, results


def main():
    parser = argparse.ArgumentParser(description="Deterministic Invariant Benchmark Suite for aryix/0rbt-architect")
    parser.add_argument("--mock-test", action="store_true", help="Run offline self-test in <0.05s ($0 tokens)")
    parser.add_argument("--live", action="store_true", help="Run live evaluation against local Ollama model")

    args = parser.parse_args()

    if args.mock_test or not args.live:
        passed, total, _ = evaluate_benchmarks(is_mock=True)
        sys.exit(0 if passed == total else 1)

    passed, total, _ = evaluate_benchmarks(is_mock=False)
    sys.exit(0 if (passed / total) >= 0.9 else 1)


if __name__ == "__main__":
    main()

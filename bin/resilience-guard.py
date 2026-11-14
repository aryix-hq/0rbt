#!/usr/bin/env python3
"""Enterprise SRE Resilience, Cellular Architecture & Cascading Failure Guard (INV-RES-01..05).

Provides deterministic algorithms for:
1. Shuffle Sharding & Combinatorial Blast-Radius Isolation
2. Envoy-Style Panic Mode & Minimum Healthy Capacity Floors
3. Adaptive Concurrency Limiting via Little's Law (AIMD)
4. Decorrelated Full Jitter Backoff Simulation (Thundering Herd Suppression)
5. Slow-Start Warm-Up Traffic Ramps (Cold-Cache Protection)

Pure Python 3.12 standard library. Zero cloud tokens. Executes in <20ms.
"""

import os
import sys
import math
import json
import time
import random
import hashlib
import argparse
from typing import Dict, List, Tuple, Any, Optional


def compute_combinations(n: int, k: int) -> int:
    """Computes binomial coefficient n choose k."""
    if k < 0 or k > n:
        return 0
    return math.comb(n, k)


def shuffle_shard(total_nodes: int, k: int, tenant_id: Optional[str] = None) -> Dict[str, Any]:
    """Computes shuffle sharding allocation and combinatorial blast-radius metrics."""
    if total_nodes <= 0 or k <= 0 or k > total_nodes:
        raise ValueError(f"Invalid parameters: total_nodes={total_nodes}, k={k}")

    total_combinations = compute_combinations(total_nodes, k)
    # Probability that two distinct tenants share the exact same k nodes: 1 / C(N, k)
    exact_overlap_prob = 1.0 / total_combinations if total_combinations > 0 else 0.0
    
    # Blast radius if 1 node experiences complete failure:
    # A single node failure impacts (k / N) fraction of tenants
    single_node_blast_pct = (k / total_nodes) * 100.0

    assigned_nodes = []
    if tenant_id:
        # Deterministic cell selection based on SHA-256 hash of (tenant_id, node_index)
        scores = []
        for node_idx in range(total_nodes):
            seed = f"{tenant_id}:cell:{node_idx}".encode("utf-8")
            digest = hashlib.sha256(seed).hexdigest()
            scores.append((digest, node_idx))
        scores.sort(key=lambda x: x[0])
        assigned_nodes = sorted([node_idx for _, node_idx in scores[:k]])

    return {
        "total_nodes": total_nodes,
        "k_per_tenant": k,
        "total_combinations": total_combinations,
        "exact_overlap_probability": exact_overlap_prob,
        "single_node_blast_radius_pct": round(single_node_blast_pct, 2),
        "tenant_id": tenant_id,
        "assigned_nodes": assigned_nodes
    }


def panic_check(total_endpoints: int, healthy_endpoints: int, panic_threshold: float = 0.5) -> Dict[str, Any]:
    """Evaluates cluster health against Envoy Panic Threshold.
    
    If healthy ratio falls below panic_threshold (default 50%), panic mode activates,
    halting evictions and routing traffic across 100% of endpoints to prevent cascading collapse.
    """
    if total_endpoints <= 0:
        return {
            "total_endpoints": 0,
            "healthy_endpoints": 0,
            "healthy_ratio": 0.0,
            "panic_mode": False,
            "routing_policy": "NO_ENDPOINTS",
            "active_traffic_endpoints": 0,
            "status": "CRITICAL_EMPTY"
        }

    healthy_ratio = healthy_endpoints / total_endpoints
    panic_active = healthy_ratio < panic_threshold

    if panic_active:
        routing_policy = "ROUTE_100_PERCENT_ALL_ENDPOINTS"
        active_traffic_endpoints = total_endpoints
        explanation = (
            f"Healthy endpoints dropped to {healthy_endpoints}/{total_endpoints} ({healthy_ratio*100:.1f}%), "
            f"breaching panic threshold ({panic_threshold*100:.0f}%). "
            f"Panic mode ACTIVE: Load balancer froze evictions to prevent cascading collapse."
        )
    else:
        routing_policy = "ROUTE_HEALTHY_ONLY"
        active_traffic_endpoints = healthy_endpoints
        explanation = (
            f"Healthy endpoints at {healthy_endpoints}/{total_endpoints} ({healthy_ratio*100:.1f}%). "
            f"Normal routing active across {healthy_endpoints} healthy instances."
        )

    return {
        "total_endpoints": total_endpoints,
        "healthy_endpoints": healthy_endpoints,
        "healthy_ratio": round(healthy_ratio, 3),
        "panic_threshold": panic_threshold,
        "panic_mode": panic_active,
        "routing_policy": routing_policy,
        "active_traffic_endpoints": active_traffic_endpoints,
        "explanation": explanation
    }


def concurrency_limit(
    baseline_latency_ms: float,
    current_latency_ms: float,
    current_limit: int = 100,
    beta: float = 0.8
) -> Dict[str, Any]:
    """Calculates dynamic concurrency ceiling via Little's Law using Additive Increase / Multiplicative Decrease (AIMD)."""
    if baseline_latency_ms <= 0:
        baseline_latency_ms = 50.0

    threshold_latency_ms = baseline_latency_ms * 1.10

    if current_latency_ms <= threshold_latency_ms:
        # Service is healthy -> Additive Increase (+1)
        new_limit = current_limit + 1
        action = "INCREASE"
        shedding_required = False
        shedding_pct = 0.0
    else:
        # Service latency degrading -> Multiplicative Decrease (* beta)
        new_limit = max(1, int(current_limit * beta))
        action = "THROTTLE"
        shedding_required = True
        shedding_pct = round((1.0 - (new_limit / current_limit)) * 100.0, 1)

    return {
        "baseline_latency_ms": baseline_latency_ms,
        "current_latency_ms": current_latency_ms,
        "threshold_latency_ms": round(threshold_latency_ms, 2),
        "previous_limit": current_limit,
        "new_limit": new_limit,
        "action": action,
        "shedding_required": shedding_required,
        "shedding_percentage": shedding_pct,
        "status": "HEALTHY" if not shedding_required else "SATURATED"
    }


def jitter_sim(
    num_clients: int = 1000,
    max_attempts: int = 4,
    base_ms: float = 1000.0,
    cap_ms: float = 30000.0,
    bucket_size_ms: float = 100.0,
    seed: int = 42
) -> Dict[str, Any]:
    """Simulates reconnecting clients comparing raw exponential backoff vs decorrelated full jitter.
    
    Demonstrates that full jitter suppresses the thundering herd by spreading retries uniformly.
    """
    rng = random.Random(seed)
    total_buckets = int(30000 // bucket_size_ms) + 1

    raw_buckets = [0] * total_buckets
    jitter_buckets = [0] * total_buckets

    for client in range(num_clients):
        # Accumulate time across attempts
        raw_t = 0.0
        jitter_t = 0.0
        for attempt in range(max_attempts):
            # Raw exponential backoff
            raw_backoff = min(cap_ms, base_ms * (2 ** attempt))
            raw_t += raw_backoff
            bucket_idx = int(raw_t // bucket_size_ms)
            if bucket_idx < total_buckets:
                raw_buckets[bucket_idx] += 1

            # Decorrelated Full Jitter: Uniform(0, min(cap, base * 2^i))
            jitter_backoff = rng.uniform(0, min(cap_ms, base_ms * (2 ** attempt)))
            jitter_t += jitter_backoff
            j_bucket_idx = int(jitter_t // bucket_size_ms)
            if j_bucket_idx < total_buckets:
                jitter_buckets[j_bucket_idx] += 1

    raw_peak = max(raw_buckets) if raw_buckets else 0
    jitter_peak = max(jitter_buckets) if jitter_buckets else 0
    reduction_pct = ((raw_peak - jitter_peak) / raw_peak * 100.0) if raw_peak > 0 else 0.0

    return {
        "num_clients": num_clients,
        "max_attempts": max_attempts,
        "raw_peak_spike_requests": raw_peak,
        "jitter_peak_spike_requests": jitter_peak,
        "spike_reduction_percentage": round(reduction_pct, 1),
        "raw_buckets_sample": raw_buckets[:10],
        "jitter_buckets_sample": jitter_buckets[:10],
        "thundering_herd_suppressed": reduction_pct >= 50.0
    }


def slow_start(duration_sec: float = 180.0, elapsed_sec: float = 0.0, curve: str = "linear") -> Dict[str, Any]:
    """Calculates traffic weight for newly booted or recovering instances during warm-up."""
    if duration_sec <= 0:
        duration_sec = 180.0

    ratio = max(0.0, min(1.0, elapsed_sec / duration_sec))

    if curve == "sigmoidal":
        # Logistic S-curve centered at 0.5
        # Maps 0.0 -> ~0.02, 0.5 -> 0.5, 1.0 -> ~0.98
        w = 1.0 / (1.0 + math.exp(-6.0 * (ratio - 0.5)))
    else:
        # Linear ramp with a 1% floor
        w = max(0.01, ratio)

    weight_pct = round(w * 100.0, 2)
    is_fully_warmed = elapsed_sec >= duration_sec

    return {
        "duration_sec": duration_sec,
        "elapsed_sec": elapsed_sec,
        "curve": curve,
        "weight_factor": round(w, 4),
        "traffic_weight_pct": weight_pct,
        "is_fully_warmed": is_fully_warmed,
        "status": "WARMED" if is_fully_warmed else "RAMPING"
    }


def run_mock_test() -> int:
    """Deterministic self-verifying test suite for resilience-guard.py (<20ms)."""
    t0 = time.perf_counter()
    print("=" * 72)
    print(" 🛡️ RUNNING ENTERPRISE RESILIENCE & CASCADING FAILURE GUARD MOCK TEST")
    print("=" * 72)

    # Test 1: Shuffle Sharding Combinatorics
    res1 = shuffle_shard(total_nodes=8, k=2, tenant_id="tenant_alpha")
    assert res1["total_combinations"] == 28, f"Expected 28 combinations, got {res1['total_combinations']}"
    assert len(res1["assigned_nodes"]) == 2, f"Expected 2 nodes, got {res1['assigned_nodes']}"
    assert res1["single_node_blast_radius_pct"] == 25.0, f"Expected 25.0% blast, got {res1['single_node_blast_radius_pct']}"
    # Verify deterministic hash
    res1_repeat = shuffle_shard(total_nodes=8, k=2, tenant_id="tenant_alpha")
    assert res1["assigned_nodes"] == res1_repeat["assigned_nodes"], "Hash allocation must be deterministic"
    print(f"  ✔ Check 1: Shuffle Sharding verified (N=8, k=2 -> 28 combinations, assigned: {res1['assigned_nodes']}).")

    # Test 2: Panic Mode Thresholds
    # Normal capacity (8/10 healthy = 80% > 50%)
    res2_norm = panic_check(total_endpoints=10, healthy_endpoints=8, panic_threshold=0.5)
    assert res2_norm["panic_mode"] is False
    assert res2_norm["active_traffic_endpoints"] == 8
    # Degrading below threshold (4/10 healthy = 40% < 50%)
    res2_panic = panic_check(total_endpoints=10, healthy_endpoints=4, panic_threshold=0.5)
    assert res2_panic["panic_mode"] is True
    assert res2_panic["routing_policy"] == "ROUTE_100_PERCENT_ALL_ENDPOINTS"
    assert res2_panic["active_traffic_endpoints"] == 10
    print("  ✔ Check 2: Envoy Panic Mode verified (4/10 healthy triggers 100% fleet routing).")

    # Test 3: Little's Law Concurrency Limiting (AIMD)
    # Healthy case
    res3_inc = concurrency_limit(baseline_latency_ms=50.0, current_latency_ms=52.0, current_limit=100)
    assert res3_inc["action"] == "INCREASE" and res3_inc["new_limit"] == 101
    # Degraded case (latency 120ms > 50*1.1 = 55ms)
    res3_dec = concurrency_limit(baseline_latency_ms=50.0, current_latency_ms=120.0, current_limit=100, beta=0.8)
    assert res3_dec["action"] == "THROTTLE" and res3_dec["new_limit"] == 80
    assert res3_dec["shedding_required"] is True
    print("  ✔ Check 3: Little's Law AIMD Concurrency verified (+1 on healthy, -20% on degraded).")

    # Test 4: Decorrelated Full Jitter Simulation
    res4 = jitter_sim(num_clients=1000, max_attempts=4, base_ms=1000.0, cap_ms=30000.0)
    assert res4["thundering_herd_suppressed"] is True
    assert res4["spike_reduction_percentage"] >= 50.0, f"Expected >=50% spike reduction, got {res4['spike_reduction_percentage']}%"
    print(f"  ✔ Check 4: Decorrelated Full Jitter verified (Peak spike reduced by {res4['spike_reduction_percentage']}%).")

    # Test 5: Slow-Start Traffic Ramp
    res5_start = slow_start(duration_sec=180.0, elapsed_sec=0.0)
    assert res5_start["traffic_weight_pct"] == 1.0, f"Expected 1.0% initial floor, got {res5_start['traffic_weight_pct']}%"
    res5_mid = slow_start(duration_sec=180.0, elapsed_sec=90.0)
    assert res5_mid["traffic_weight_pct"] == 50.0, f"Expected 50.0% mid-ramp, got {res5_mid['traffic_weight_pct']}%"
    res5_done = slow_start(duration_sec=180.0, elapsed_sec=180.0)
    assert res5_done["traffic_weight_pct"] == 100.0 and res5_done["is_fully_warmed"] is True
    print("  ✔ Check 5: Slow-Start Traffic Ramp verified (1% -> 50% -> 100% over 180s).")

    elapsed_ms = (time.perf_counter() - t0) * 1000
    print("-" * 72)
    print(f" ✅ ALL 5 RESILIENCE INVARIANT ALGORITHMS PASSED in {elapsed_ms:.2f}ms.")
    print("=" * 72)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Enterprise SRE Resilience, Cellular Architecture & Cascading Failure Guard"
    )
    parser.add_argument("--mock-test", action="store_true", help="Run deterministic self-verifying test suite")

    subparsers = parser.add_subparsers(dest="command", help="Sub-command to execute")

    # Subcommand: shuffle-shard
    p_shard = subparsers.add_parser("shuffle-shard", help="Compute shuffle sharding cell allocation and blast radius")
    p_shard.add_argument("--nodes", type=int, default=8, help="Total number of available isolated cells/nodes (default: 8)")
    p_shard.add_argument("--k", type=int, default=2, help="Number of cells assigned per tenant (default: 2)")
    p_shard.add_argument("--tenant", help="Optional tenant identifier for deterministic cell mapping")
    p_shard.add_argument("--json", action="store_true", help="Output JSON result")

    # Subcommand: panic-check
    p_panic = subparsers.add_parser("panic-check", help="Evaluate Envoy panic mode threshold routing")
    p_panic.add_argument("--total", type=int, required=True, help="Total endpoints in upstream cluster")
    p_panic.add_argument("--healthy", type=int, required=True, help="Number of currently healthy endpoints")
    p_panic.add_argument("--threshold", type=float, default=0.5, help="Panic threshold ratio (default: 0.5)")
    p_panic.add_argument("--json", action="store_true", help="Output JSON result")

    # Subcommand: concurrency-limit
    p_conc = subparsers.add_parser("concurrency-limit", help="Calculate adaptive Little's Law concurrency limit")
    p_conc.add_argument("--baseline-ms", type=float, default=50.0, help="Baseline p95 service latency in ms")
    p_conc.add_argument("--current-ms", type=float, required=True, help="Current measured latency in ms")
    p_conc.add_argument("--current-limit", type=int, default=100, help="Current in-flight concurrency limit")
    p_conc.add_argument("--beta", type=float, default=0.8, help="Multiplicative decrease factor (default: 0.8)")
    p_conc.add_argument("--json", action="store_true", help="Output JSON result")

    # Subcommand: jitter-sim
    p_jit = subparsers.add_parser("jitter-sim", help="Simulate raw backoff vs decorrelated full jitter")
    p_jit.add_argument("--clients", type=int, default=1000, help="Number of reconnecting clients (default: 1000)")
    p_jit.add_argument("--attempts", type=int, default=5, help="Number of retry attempts (default: 5)")
    p_jit.add_argument("--json", action="store_true", help="Output JSON result")

    # Subcommand: slow-start
    p_slow = subparsers.add_parser("slow-start", help="Calculate traffic weight during cold-start warm-up")
    p_slow.add_argument("--duration", type=float, default=180.0, help="Total warm-up duration in seconds (default: 180)")
    p_slow.add_argument("--elapsed", type=float, required=True, help="Elapsed warm-up time in seconds")
    p_slow.add_argument("--curve", choices=["linear", "sigmoidal"], default="linear", help="Warm-up curve type")
    p_slow.add_argument("--json", action="store_true", help="Output JSON result")

    args = parser.parse_args()

    if args.mock_test:
        sys.exit(run_mock_test())

    if args.command == "shuffle-shard":
        res = shuffle_shard(total_nodes=args.nodes, k=args.k, tenant_id=args.tenant)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Total Nodes (N)        : {res['total_nodes']}")
            print(f"Nodes Per Tenant (k)   : {res['k_per_tenant']}")
            print(f"Total Unique Combos    : {res['total_combinations']}")
            print(f"Exact Overlap Prob     : {res['exact_overlap_probability']:.6f} ({res['exact_overlap_probability']*100:.4f}%)")
            print(f"Single Node Blast Radius: {res['single_node_blast_radius_pct']}% of tenants")
            if res['tenant_id']:
                print(f"Tenant '{res['tenant_id']}' assigned to cells: {res['assigned_nodes']}")

    elif args.command == "panic-check":
        res = panic_check(total_endpoints=args.total, healthy_endpoints=args.healthy, panic_threshold=args.threshold)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            status_badge = "🚨 PANIC MODE ACTIVE" if res['panic_mode'] else "✔ NORMAL"
            print(f"Status           : {status_badge}")
            print(f"Healthy Endpoints: {res['healthy_endpoints']}/{res['total_endpoints']} ({res['healthy_ratio']*100:.1f}%)")
            print(f"Routing Policy   : {res['routing_policy']}")
            print(f"Active Endpoints : {res['active_traffic_endpoints']}")
            print(f"Note             : {res['explanation']}")

    elif args.command == "concurrency-limit":
        res = concurrency_limit(
            baseline_latency_ms=args.baseline_ms,
            current_latency_ms=args.current_ms,
            current_limit=args.current_limit,
            beta=args.beta
        )
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Status        : {res['status']}")
            print(f"Latency       : {res['current_latency_ms']}ms (Baseline: {res['baseline_latency_ms']}ms)")
            print(f"Action        : {res['action']}")
            print(f"Limit Change  : {res['previous_limit']} -> {res['new_limit']}")
            if res['shedding_required']:
                print(f"Shedding Required: Drop {res['shedding_percentage']}% of non-critical traffic")

    elif args.command == "jitter-sim":
        res = jitter_sim(num_clients=args.clients, max_attempts=args.attempts)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Clients Simulated    : {res['num_clients']}")
            print(f"Raw Peak Arrival     : {res['raw_peak_spike_requests']} req/s")
            print(f"Jitter Peak Arrival  : {res['jitter_peak_spike_requests']} req/s")
            print(f"Peak Spike Reduction : {res['spike_reduction_percentage']}%")
            print(f"Thundering Herd Suppressed: {res['thundering_herd_suppressed']}")

    elif args.command == "slow-start":
        res = slow_start(duration_sec=args.duration, elapsed_sec=args.elapsed, curve=args.curve)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Status        : {res['status']}")
            print(f"Warm-Up Window: {res['elapsed_sec']:.1f}s / {res['duration_sec']:.1f}s")
            print(f"Traffic Weight: {res['traffic_weight_pct']}%")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
